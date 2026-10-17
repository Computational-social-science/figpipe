"""Extract a structured, traceable layout from the Nature PDF corpus.

WHY THIS REPLACES THE OLD DETECTOR
    The previous figure-band detector was a heuristic that merged overlapping
    drawing/image rectangles. AUDIT.md and LEARNINGS.md both flagged it as the
    project's weakest point: it reported a band width distribution that nobody
    could trust, because the bands were guessed from vector drawing extents.
    This script uses docling (IBM, a professional document-understanding model)
    to obtain element types, bounding boxes and reading order from the document
    model itself, and pairs each figure with its caption by geometry. Where the
    tool is uncertain, the uncertainty is recorded rather than smoothed away.

WHAT IS PRODUCED, PER PAPER
    corpus/extracted/<paper_id>/
      pages/page_0001.png     one high-resolution render per PDF page (for VLM use)
      figures/fig_001.png     the figure crop docling resolved, at `images_scale`
      layout.json             every element: type, bbox, reading order, page
      content.md              the document as readable markdown
      figures_meta.json       figure <-> caption <-> page <-> bbox <-> kind
      manifest.json           provenance: source path, sha256, tool versions

COORDINATES (stated explicitly because two conventions meet here)
    * PDF points, origin BOTTOM-LEFT, y increasing upward: this is docling's
      `BoundingBox` frame and the native PDF frame. Verified empirically: a page
      masthead sits at y=761 on a 791 pt page, and body text descends in y.
    * Pixel boxes for cropping use origin TOP-LEFT, y downward, because that is
      what image libraries use. `bbox_px` is derived from the PDF box, not
      measured separately, so the two cannot disagree.

CAPTION PAIRING (the part that must be right)
    Nature places figure captions BELOW the figure and table captions ABOVE the
    table. Multi-line captions can arrive as several consecutive CAPTION items
    (a continuation block), so consecutive caption items are merged before
    pairing. A figure is paired with the nearest caption block on the same page
    that sits below it and overlaps it horizontally; a table is paired the same
    way but above. Every pair records the rule used and the measured gap, so a
    wrong pair is diagnosable instead of invisible. Unpaired pictures are NOT
    silently dropped: they are listed in layout.json and counted in the manifest.

USAGE
    python scripts/extract_corpus.py --limit 5
    python scripts/extract_corpus.py --papers nature_2024_nllb200
    python scripts/extract_corpus.py --resume          # skip finished papers
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_SRC = r"D:\2026-AI4S"
OUT_ROOT = os.path.join(ROOT, "corpus", "extracted")

# Sister journals that must not enter the corpus. The rule is applied to the
# PDF's own metadata and page-0 masthead, not merely to the filename, because a
# Nature paper may cite "Nature Communications" in its text.
EXCLUDE_PATTERNS = [
    (r"nature\s+communications", "Nature Communications"),
    (r"\bnpj\b", "npj"),
    (r"scientific\s+reports", "Scientific Reports"),
    (r"national\s+science\s+review", "National Science Review"),
]

# A picture smaller than this is a logo, bullet glyph or inline decoration, not
# a data figure. 40x40 pt = 1600 pt^2 is roughly 1/300 of a Nature page.
MIN_FIGURE_AREA_PT2 = 1600.0
MIN_FIGURE_SIDE_PT = 25.0


# --------------------------------------------------------------------------- #
# pure helpers (no docling import: cheap to unit-test)
# --------------------------------------------------------------------------- #
def sha256_file(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def slugify(name: str, maxlen: int = 60) -> str:
    stem = os.path.splitext(name)[0]
    stem = stem.lstrip("!").strip()
    stem = re.sub(r"[^0-9A-Za-z]+", "_", stem).strip("_").lower()
    stem = re.sub(r"_+", "_", stem)
    return stem[:maxlen].strip("_")


def paper_id_for(name: str, md5: str) -> str:
    """Stable, filesystem-safe id. The md5 suffix keeps ids unique even when two
    different PDFs share a truncated filename."""
    return f"{slugify(name)}_{md5[:8]}"


def bbox_dict(bb, page_h: float) -> dict:
    """Convert a docling BoundingBox (points, bottom-left origin) to a plain
    record, and add the top-left pixel-free normalised form used for cropping."""
    l, t, r, b = float(bb.l), float(bb.t), float(bb.r), float(bb.b)
    # docling may report t/b in either order; normalise so t is the upper edge
    top, bottom = max(t, b), min(t, b)
    return {
        "l": round(l, 2), "t": round(top, 2), "r": round(r, 2), "b": round(bottom, 2),
        "w": round(r - l, 2), "h": round(top - bottom, 2),
        "coord": "pdf_points_bottomleft",
    }


def bbox_px(bb: dict, page_h_pt: float, scale: float) -> dict:
    """Pixel box with origin top-left, derived from the PDF box."""
    return {
        "x0": int(round(bb["l"] * scale)),
        "y0": int(round((page_h_pt - bb["t"]) * scale)),
        "x1": int(round(bb["r"] * scale)),
        "y1": int(round((page_h_pt - bb["b"]) * scale)),
        "scale": scale,
        "coord": "pixels_topleft",
    }


def is_real_figure(bb: dict) -> bool:
    if bb["w"] < MIN_FIGURE_SIDE_PT or bb["h"] < MIN_FIGURE_SIDE_PT:
        return False
    return (bb["w"] * bb["h"]) >= MIN_FIGURE_AREA_PT2


def figure_kind_from_caption(caption: str) -> str:
    """Classify a caption by the label Nature puts in front of it."""
    c = caption.strip()
    low = c.lower()
    if re.match(r"^(extended\s+data\s+)?fig(ure)?\.?\s*\d", low):
        return "extended_data_figure" if "extended data" in low else "figure"
    if re.match(r"^(supplementary\s+)?fig(ure)?\.?\s*\d", low):
        return "supplementary_figure"
    if re.match(r"^(extended\s+data\s+)?table\s*\d", low):
        return "extended_data_table" if "extended data" in low else "table"
    if re.match(r"^(supplementary\s+)?table\s*\d", low):
        return "supplementary_table"
    if low.startswith("box"):
        return "box"
    return "figure"


def caption_label_form(caption: str) -> str:
    """The literal label prefix, e.g. 'Fig. 1', 'Figure 1', 'Extended Data Fig. 2'.

    WHY THIS IS RECORDED SEPARATELY FROM `kind`
    A Nature issue contains more than the Article. A 'News & Views' piece in the
    front matter carries its own standalone 'Figure 1 |' (spelled out), while the
    Article's figures are labelled 'Fig. 1 |' (abbreviated). Both are real
    figures, and their numbers legitimately collide. Without this distinction a
    numbering check reports a false duplicate; with it, the collision is
    explained rather than hidden.
    """
    m = re.match(r"^\s*((?:Extended\s+Data\s+|Supplementary\s+)?"
                 r"(?:Fig(?:ure)?\.?|Table|Box)\s*\d+)",
                 caption.strip(), re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def figure_number_from_caption(caption: str):
    m = re.match(r"^\s*(?:extended\s+data\s+|supplementary\s+)?"
                 r"(?:fig(?:ure)?\.?|table|box)\s*(\d+)",
                 caption.strip(), re.I)
    return int(m.group(1)) if m else None


def overlaps_horizontally(a: dict, b: dict, tol: float = 2.0) -> bool:
    return (min(a["r"], b["r"]) - max(a["l"], b["l"])) > -tol


def merge_caption_blocks(caps: list, vgap_pt: float = 26.0) -> list:
    """Merge consecutive CAPTION items into blocks.

    docling splits a long Nature caption at column/paragraph breaks, so
    'Fig. 3 | ...' and 'the sentences evaluated for ...' arrive as two items.
    Two caption items belong to the same block when they are horizontally
    aligned and vertically adjacent (the gap between them is small compared
    with normal body leading). Sorting is top-to-bottom.
    """
    if not caps:
        return []
    caps = sorted(caps, key=lambda c: -c["bbox"]["t"])
    blocks = [{"items": [caps[0]], "bbox": dict(caps[0]["bbox"]),
               "text": caps[0]["text"]}]
    for c in caps[1:]:
        cur = blocks[-1]
        prev = cur["items"][-1]
        gap = prev["bbox"]["b"] - c["bbox"]["t"]      # positive: c is below prev
        if overlaps_horizontally(prev["bbox"], c["bbox"]) and -2.0 <= gap <= vgap_pt:
            cur["items"].append(c)
            cur["text"] = (cur["text"].rstrip() + " " + c["text"].lstrip()).strip()
            nb = cur["bbox"]
            nb["b"] = min(nb["b"], c["bbox"]["b"])
            nb["l"] = min(nb["l"], c["bbox"]["l"])
            nb["r"] = max(nb["r"], c["bbox"]["r"])
            nb["w"] = round(nb["r"] - nb["l"], 2)
            nb["h"] = round(nb["t"] - nb["b"], 2)
        else:
            blocks.append({"items": [c], "bbox": dict(c["bbox"]), "text": c["text"]})
    return blocks


def pair_caption(target_bb: dict, blocks: list, where: str,
                 max_gap_pt: float = 260.0) -> tuple:
    """Pair one figure/table box with the nearest caption block.

    `where` is 'below' for figures (caption under the figure) or 'above' for
    tables (caption over the table). Returns (block, gap) or (None, None).
    A negative gap means slight overlap, which is common when a caption starts
    inside the image's reported box; overlap up to `tol` is accepted.
    """
    best, best_gap = None, None
    for blk in blocks:
        b = blk["bbox"]
        if not overlaps_horizontally(target_bb, b):
            continue
        if where == "below":
            gap = target_bb["b"] - b["t"]        # caption top below figure bottom
        else:
            gap = b["b"] - target_bb["t"]        # caption bottom above figure top
        if gap < -12.0 or gap > max_gap_pt:
            continue
        if best is None or gap < best_gap:
            best, best_gap = blk, gap
    return best, best_gap


def classify_pdf(path: str) -> dict:
    """Journal identity from the PDF's own metadata + page-0 masthead."""
    import pymupdf

    rec = {"path": path, "name": os.path.basename(path),
           "size_bytes": os.path.getsize(path),
           "md5": hashlib.md5(open(path, "rb").read()).hexdigest()}
    try:
        doc = pymupdf.open(path)
        rec["n_pages"] = doc.page_count
        rec["metadata"] = {k: v for k, v in (doc.metadata or {}).items() if v}
        rec["page0_size_pt"] = [round(doc[0].rect.width, 2),
                                round(doc[0].rect.height, 2)]
        txt = doc[0].get_text()[:4000] if doc.page_count else ""
        doc.close()
    except Exception as e:                                    # noqa: BLE001
        rec["n_pages"] = None
        rec["metadata"] = {}
        rec["page0_size_pt"] = None
        rec["error"] = f"{type(e).__name__}: {e}"
        txt = ""
    rec["page0_text_head"] = txt[:600]

    decisive_hay = (json.dumps(rec["metadata"]) + "\n" + txt[:1500]).lower()
    hits = sorted({label for pat, label in EXCLUDE_PATTERNS
                   if re.search(pat, decisive_hay)})
    rec["excluded"] = bool(hits)
    rec["excluded_reason"] = (f"journal identity in metadata/page-0: {', '.join(hits)}"
                              if hits else None)
    rec["journal_doi"] = next(
        (m.group(0) for m in re.finditer(r"10\.1038/s41586-\d{3}-\d{4,5}-[0-9a-z]",
                                         json.dumps(rec["metadata"]) + txt, re.I)), None)
    return rec


def build_inventory() -> dict:
    """Find every NATURE-named PDF, dedupe by content, classify, keep Nature proper."""
    files = []
    for root, _dirs, names in os.walk(CORPUS_SRC):
        for n in names:
            if n.lower().endswith(".pdf") and "nature" in n.lower():
                files.append(os.path.join(root, n))
    files.sort()
    recs = [classify_pdf(p) for p in files]

    by_md5 = {}
    for r in recs:
        by_md5.setdefault(r["md5"], []).append(r)
    unique = []
    for _h, group in by_md5.items():
        group.sort(key=lambda r: len(r["name"]))
        keep = dict(group[0])
        keep["duplicate_paths"] = [g["path"] for g in group[1:]]
        keep["n_copies"] = len(group)
        unique.append(keep)
    unique.sort(key=lambda r: r["name"])

    kept = [r for r in unique if not r["excluded"]]
    for r in kept:
        r["paper_id"] = paper_id_for(r["name"], r["md5"])
    return {
        "source_root": CORPUS_SRC,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "n_files_found": len(files),
        "n_unique_by_md5": len(unique),
        "n_kept": len(kept),
        "n_excluded": len(unique) - len(kept),
        "exclude_rules": [p for p, _ in EXCLUDE_PATTERNS],
        "kept": kept,
        "excluded": [r for r in unique if r["excluded"]],
    }


# --------------------------------------------------------------------------- #
# extraction
# --------------------------------------------------------------------------- #
def render_pages(pdf_path: str, out_dir: str, dpi: int = 200) -> list:
    """Render every page to PNG with PyMuPDF. Returns relative paths."""
    import pymupdf

    os.makedirs(out_dir, exist_ok=True)
    rel = []
    doc = pymupdf.open(pdf_path)
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)
    for i, page in enumerate(doc, start=1):
        name = f"page_{i:04d}.png"
        page.get_pixmap(matrix=mat, alpha=False).save(os.path.join(out_dir, name))
        rel.append(f"pages/{name}")
    doc.close()
    return rel


def extract_paper(rec: dict, out_root: str, dpi: int = 200,
                  images_scale: float = 2.0, do_ocr: bool = False) -> dict:
    """Run docling on one PDF and write the five artefacts. Returns a summary."""
    import docling
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    t_start = time.time()
    pdf_path = rec["path"]
    pid = rec["paper_id"]
    pdir = os.path.join(out_root, pid)
    os.makedirs(pdir, exist_ok=True)
    for sub in ("pages", "figures"):
        os.makedirs(os.path.join(pdir, sub), exist_ok=True)

    # ---- 1. page renders (independent of docling; always produced) ----
    page_pngs = render_pages(pdf_path, os.path.join(pdir, "pages"), dpi=dpi)

    # ---- 2. document model ----
    opts = PdfPipelineOptions()
    opts.do_ocr = do_ocr
    opts.do_table_structure = True
    opts.generate_picture_images = True
    opts.images_scale = images_scale
    try:
        opts.generate_table_images = True
    except Exception:                                          # noqa: BLE001
        pass
    conv = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    res = conv.convert(pdf_path)
    doc = res.document

    # ---- 3. page geometry ----
    page_geom = {}
    for pno, pg in doc.pages.items():
        page_geom[int(pno)] = {"w": float(pg.size.width), "h": float(pg.size.height)}

    # ---- 4. collect elements in reading order ----
    elements = []
    pictures, tables, captions = [], [], []
    ro = 0
    for item, level in doc.iterate_items():
        prov = getattr(item, "prov", None)
        if not prov:
            continue
        p = prov[0]
        pno = int(p.page_no)
        geom = page_geom.get(pno, {"w": 595.28, "h": 790.87})
        bb = bbox_dict(p.bbox, geom["h"])
        label = str(getattr(item, "label", "") or "")
        text = getattr(item, "text", "") or ""
        el = {
            "reading_order": ro, "page": pno, "label": label,
            "bbox": bb, "bbox_norm": {
                "l": round(bb["l"] / geom["w"], 5), "t": round(bb["t"] / geom["h"], 5),
                "r": round(bb["r"] / geom["w"], 5), "b": round(bb["b"] / geom["h"], 5)},
            "text": text[:4000], "text_len": len(text), "level": level,
            "element_id": f"p{pno}_e{ro}",
        }
        elements.append(el)
        ro += 1
        if label == "picture":
            pictures.append({"el": el, "item": item})
        elif label == "table":
            tables.append({"el": el, "item": item})
        elif label == "caption":
            captions.append({"el": el, "item": item})

    # ---- 5. caption blocks per page ----
    caps_by_page = {}
    for c in captions:
        caps_by_page.setdefault(c["el"]["page"], []).append(
            {"bbox": c["el"]["bbox"], "text": c["el"]["text"],
             "element_id": c["el"]["element_id"]})
    blocks_by_page = {pg: merge_caption_blocks(cs)
                      for pg, cs in caps_by_page.items()}
    used_blocks = set()

    # ---- 6. figures: crop, pair, classify ----
    figures = []
    uncaptioned = []
    os.makedirs(os.path.join(pdir, "figures"), exist_ok=True)
    fig_n = 0
    for rec_pic in pictures:
        el = rec_pic["el"]
        bb = el["bbox"]
        geom = page_geom.get(el["page"], {"w": 595.28, "h": 790.87})
        real = is_real_figure(bb)
        block, gap = pair_caption(bb, blocks_by_page.get(el["page"], []), "below")
        if block is not None:
            key = (el["page"], block["items"][0]["element_id"])
            if key in used_blocks:
                block = None                       # one caption cannot serve two
            else:
                used_blocks.add(key)
        if block is None:
            uncaptioned.append({"page": el["page"], "bbox": bb,
                                "real_figure_size": real,
                                "element_id": el["element_id"]})
            continue
        if not real:
            # A caption next to a sub-40 pt box is a caption for something else
            # (a table note, a logo legend); do not emit it as a figure.
            uncaptioned.append({"page": el["page"], "bbox": bb,
                                "real_figure_size": False,
                                "reason": "below minimum figure size",
                                "element_id": el["element_id"]})
            continue

        fig_n += 1
        fid = f"fig_{fig_n:03d}"
        img_rel = None
        img_size = None
        img = getattr(rec_pic["item"], "image", None)
        if img is not None:
            try:
                pil = img.pil_image
                img_rel = f"figures/{fid}.png"
                pil.save(os.path.join(pdir, "figures", f"{fid}.png"))
                img_size = list(pil.size)
            except Exception as e:                             # noqa: BLE001
                img_rel = None
                img_size = None
                uncaptioned.append({"page": el["page"], "bbox": bb,
                                    "reason": f"image extract failed: {e}",
                                    "element_id": el["element_id"]})
        kind = figure_kind_from_caption(block["text"])
        figures.append({
            "figure_id": fid,
            "kind": kind,
            "label_form": caption_label_form(block["text"]),
            "figure_number": figure_number_from_caption(block["text"]),
            "page": el["page"],
            "bbox": bb,
            "bbox_px": bbox_px(bb, geom["h"], images_scale),
            "image_path": img_rel,
            "image_size_px": img_size,
            "caption": block["text"],
            "caption_page": el["page"],
            "caption_bbox": block["bbox"],
            "caption_element_ids": [i["element_id"] for i in block["items"]],
            "caption_n_items": len(block["items"]),
            "pairing": {"rule": "nearest_caption_block_below",
                        "gap_pt": None if gap is None else round(gap, 2)},
            "element_id": el["element_id"],
            "reading_order": el["reading_order"],
        })

    # ---- 7. tables: same pairing but caption ABOVE ----
    table_recs = []
    tab_n = 0
    for rec_tab in tables:
        el = rec_tab["el"]
        bb = el["bbox"]
        geom = page_geom.get(el["page"], {"w": 595.28, "h": 790.87})
        block, gap = pair_caption(bb, blocks_by_page.get(el["page"], []), "above")
        if block is not None:
            key = (el["page"], block["items"][0]["element_id"])
            if key in used_blocks:
                block = None
            else:
                used_blocks.add(key)
        tab_n += 1
        tid = f"table_{tab_n:03d}"
        table_recs.append({
            "table_id": tid,
            "page": el["page"],
            "bbox": bb,
            "caption": block["text"] if block else None,
            "caption_bbox": block["bbox"] if block else None,
            "caption_page": el["page"] if block else None,
            "pairing": {"rule": "nearest_caption_block_above",
                        "gap_pt": None if gap is None else round(gap, 2),
                        "paired": block is not None},
            "element_id": el["element_id"],
        })

    # ---- 8. write layout.json ----
    layout = {
        "paper_id": pid,
        "source_pdf": pdf_path,
        "source_sha256": sha256_file(pdf_path),
        "source_name": rec["name"],
        "n_pages": len(page_pngs),
        "page_size_pt": rec.get("page0_size_pt"),
        "coordinate_note": ("bbox is PDF points with origin at the BOTTOM-LEFT, "
                            "y increasing upward; bbox_norm divides by page size."),
        "tool": {"name": "docling", "version": getattr(docling, "__version__", "?"),
                 "do_ocr": do_ocr, "do_table_structure": True,
                 "images_scale": images_scale, "pages_dpi": dpi},
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "pages": [
            {"page_no": i, "width_pt": page_geom.get(i, {}).get("w"),
             "height_pt": page_geom.get(i, {}).get("h"),
             "png": page_pngs[i - 1],
             "elements": [e for e in elements if e["page"] == i]}
            for i in range(1, len(page_pngs) + 1)
        ],
        "caption_blocks": [
            {"page": pg,
             "blocks": [{"text": b["text"],
                         "bbox": b["bbox"],
                         "element_ids": [i["element_id"] for i in b["items"]]}
                        for b in blks]}
            for pg, blks in sorted(blocks_by_page.items())
        ],
        "uncaptioned_pictures": uncaptioned,
    }
    with open(os.path.join(pdir, "layout.json"), "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=1, ensure_ascii=False)

    # ---- 9. content.md ----
    md = doc.export_to_markdown()
    with open(os.path.join(pdir, "content.md"), "w", encoding="utf-8") as f:
        f.write(f"<!-- source: {rec['name']} -->\n")
        f.write(f"<!-- source_pdf: {pdf_path} -->\n")
        f.write(f"<!-- pages: {len(page_pngs)} ; extracted_by: docling "
                f"{getattr(docling, '__version__', '?')} -->\n\n")
        f.write(md)

    # ---- 10. figures_meta.json ----
    fmeta = {
        "paper_id": pid,
        "source_pdf": pdf_path,
        "source_sha256": layout["source_sha256"],
        "source_name": rec["name"],
        "n_pages": len(page_pngs),
        "generated_at": layout["generated_at"],
        "tool": layout["tool"],
        "n_figures": len(figures),
        "n_tables": len(table_recs),
        "n_pictures_detected": len(pictures),
        "n_uncaptioned_pictures": len(uncaptioned),
        "figures": figures,
        "tables": table_recs,
    }
    with open(os.path.join(pdir, "figures_meta.json"), "w", encoding="utf-8") as f:
        json.dump(fmeta, f, indent=1, ensure_ascii=False)

    # ---- 11. manifest.json ----
    manifest = {
        "paper_id": pid,
        "source_name": rec["name"],
        "source_pdf": pdf_path,
        "source_sha256": layout["source_sha256"],
        "source_md5": rec["md5"],
        "journal_doi": rec.get("journal_doi"),
        "n_pages": len(page_pngs),
        "n_elements": len(elements),
        "n_figures": len(figures),
        "n_tables": len(table_recs),
        "n_pictures_detected": len(pictures),
        "n_uncaptioned_pictures": len(uncaptioned),
        "n_caption_blocks": sum(len(b) for b in blocks_by_page.values()),
        "tool": layout["tool"],
        "elapsed_s": round(time.time() - t_start, 1),
        "artefacts": {
            "pages_dir": "pages/", "n_page_pngs": len(page_pngs),
            "figures_dir": "figures/", "layout": "layout.json",
            "content": "content.md", "figures_meta": "figures_meta.json"},
        "status": "ok",
        "generated_at": layout["generated_at"],
    }
    with open(os.path.join(pdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="max papers (0 = all kept)")
    ap.add_argument("--papers", nargs="*", default=None, help="explicit paper ids")
    ap.add_argument("--resume", action="store_true", help="skip papers already done")
    ap.add_argument("--dpi", type=int, default=200, help="page render dpi")
    ap.add_argument("--images-scale", type=float, default=2.0)
    ap.add_argument("--ocr", action="store_true", help="enable OCR (slow; digital PDFs need none)")
    ap.add_argument("--out", default=OUT_ROOT)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    inv = build_inventory()
    inv_path = os.path.join(args.out, "pdf_inventory.json")
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=1, ensure_ascii=False)
    print(f"corpus: {inv['n_files_found']} files -> {inv['n_unique_by_md5']} unique "
          f"-> {inv['n_kept']} kept, {inv['n_excluded']} excluded")
    print(f"inventory -> {inv_path}")

    todo = inv["kept"]
    if args.papers:
        todo = [r for r in todo if r["paper_id"] in set(args.papers)]
    if args.limit:
        todo = todo[: args.limit]

    results, failures = [], []
    for i, rec in enumerate(todo, 1):
        pid = rec["paper_id"]
        done = os.path.join(args.out, pid, "manifest.json")
        if args.resume and os.path.exists(done):
            print(f"[{i}/{len(todo)}] SKIP {pid} (already done)")
            try:
                results.append(json.load(open(done, encoding="utf-8")))
            except Exception:                                  # noqa: BLE001
                pass
            continue
        print(f"[{i}/{len(todo)}] {pid} ({rec['n_pages']}pp, "
              f"{rec['size_bytes']/1e6:.1f}MB)", flush=True)
        t0 = time.time()
        try:
            m = extract_paper(rec, args.out, dpi=args.dpi,
                              images_scale=args.images_scale, do_ocr=args.ocr)
            results.append(m)
            print(f"    ok in {m['elapsed_s']}s: {m['n_figures']} figures, "
                  f"{m['n_tables']} tables, {m['n_uncaptioned_pictures']} uncaptioned",
                  flush=True)
        except Exception as e:                                 # noqa: BLE001
            tb = traceback.format_exc()
            print(f"    FAILED in {time.time()-t0:.1f}s: {type(e).__name__}: {e}",
                  flush=True)
            failures.append({"paper_id": pid, "source": rec["path"],
                             "error": f"{type(e).__name__}: {e}",
                             "traceback": tb[-3000:]})
            os.makedirs(os.path.join(args.out, pid), exist_ok=True)
            with open(os.path.join(args.out, pid, "FAILED.json"), "w",
                      encoding="utf-8") as f:
                json.dump(failures[-1], f, indent=1)

    # ---- corpus-level summary ----
    summary = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "inventory": {k: inv[k] for k in
                      ("n_files_found", "n_unique_by_md5", "n_kept", "n_excluded")},
        "attempted": len(todo),
        "succeeded": len(results),
        "failed": len(failures),
        "total_figures": sum(r.get("n_figures", 0) for r in results),
        "total_tables": sum(r.get("n_tables", 0) for r in results),
        "total_pages": sum(r.get("n_pages", 0) for r in results),
        "papers": [{k: r.get(k) for k in
                    ("paper_id", "source_name", "n_pages", "n_figures",
                     "n_tables", "n_uncaptioned_pictures", "elapsed_s")}
                   for r in results],
        "failures": failures,
    }
    with open(os.path.join(args.out, "EXTRACTION_SUMMARY.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(f"\nsucceeded {len(results)}/{len(todo)}; "
          f"{summary['total_figures']} figures, {summary['total_tables']} tables, "
          f"{summary['total_pages']} pages")
    if failures:
        print(f"FAILURES: {[f['paper_id'] for f in failures]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
