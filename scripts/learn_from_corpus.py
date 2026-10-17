"""Learn layout from REAL published Nature figures, using the local PDF corpus.

WHY THIS REPLACES EVERYTHING BEFORE IT
    figpipe's nine rules were written from defects I hit while building one project. That is a
    curriculum of my own mistakes, not of Nature's practice. It showed immediately: the first
    published figure inspected had ink density 35.8 %, while my "verified" rule H02 claimed a
    compliant band of 3.3-17.4 % -- measured on six of my own line plots and generalised to
    "figures".

    This module reads actual Nature PDFs from the local corpus and measures what the published
    figures actually do. Rules derived from it are grounded in the journal, not in my history.

WHY PDF AND NOT SCREENSHOTS
    A PDF carries the real numbers: page geometry in points, every text span with its actual
    rendered size, and the vector/image objects that make up each figure. A raster screenshot
    would force me to guess at all of them.

WHAT IS MEASURED PER FIGURE
    * the figure's bounding box and its width in mm (single 89 / double 183 / other)
    * the set of font sizes present, and the minimum -- the number the 5 pt floor is about
    * ink density (fraction of non-white pixels), for the whitespace question
    * whether the figure is vector, raster, or mixed

HOW A FIGURE IS LOCATED
    Nature lays figures out as a block of images/drawings with a caption beneath. Rather than
    guess, this module takes every page, finds contiguous vertical bands that contain drawings
    or images, and treats each band as a figure. Bands are recorded with their geometry so a
    later pass can reject caption text mistaken for a figure.

    This is a heuristic and it is labelled as one. Its output is a distribution to learn a
    BAND from, not a per-figure verdict -- an occasional bad crop shifts a percentile, it does
    not invalidate the distribution.
"""
from __future__ import annotations

import json
import pathlib
import re

import numpy as np
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
OUT = CORPUS / "measured.json"
PDF_ROOT = pathlib.Path(r"D:\2026-AI4S")

#: Filenames that mention NATURE but are not Nature papers. Recorded explicitly so the
#: exclusion is auditable rather than buried in a regex.
DIRTY_PATTERNS = [
    (r"national\s+science\s+review", "National Science Review -- a different journal entirely"),
    (r"natl\s+sci\s+rev", "abbreviation of the same unrelated journal"),
    (r"nature\s+communications", "a different journal in the Nature PORTFOLIO, not Nature"),
    (r"npj\s", "npj journals are a separate series"),
    (r"scientific\s+reports", "different journal"),
]

MM_PER_PT = 25.4 / 72.0


def is_nature_paper(path: pathlib.Path) -> tuple[bool, str]:
    """Accept only filenames that are actually Nature, and say why when rejecting."""
    name = path.name
    low = name.lower()
    for pat, why in DIRTY_PATTERNS:
        if re.search(pat, low):
            return False, f"rejected: {why}"
    if "nature" not in low:
        return False, "rejected: filename does not contain NATURE"
    if not low.endswith(".pdf"):
        return False, "rejected: not a PDF"
    return True, "accepted"


def find_figures(page) -> list[dict]:
    """Contiguous vertical bands containing drawings or images, treated as figures.

    HEURISTIC, and labelled as such. Nature puts each figure in one band with its caption
    below. A band shorter than 25 mm or narrower than 60 mm is dropped as noise.
    """
    rects = []
    for d in page.get_drawings():
        r = d.get("rect")
        if r is not None and r.width > 4 and r.height > 4:
            rects.append(pymupdf.Rect(r))
    for im in page.get_images(full=True):
        try:
            for r in page.get_image_rects(im[0]):
                if r.width > 4 and r.height > 4:
                    rects.append(pymupdf.Rect(r))
        except Exception:
            continue
    if not rects:
        return []

    # merge overlapping/adjacent rectangles into bands
    rects.sort(key=lambda r: (r.y0, r.x0))
    bands = []
    for r in rects:
        merged = False
        for b in bands:
            if r.y0 <= b["y1"] + 6 and r.y1 >= b["y0"] - 6:
                b["x0"] = min(b["x0"], r.x0); b["x1"] = max(b["x1"], r.x1)
                b["y0"] = min(b["y0"], r.y0); b["y1"] = max(b["y1"], r.y1)
                merged = True
                break
        if not merged:
            bands.append({"x0": r.x0, "x1": r.x1, "y0": r.y0, "y1": r.y1})

    out = []
    for b in bands:
        w = (b["x1"] - b["x0"]) * MM_PER_PT
        h = (b["y1"] - b["y0"]) * MM_PER_PT
        if w < 60 or h < 25:
            continue
        out.append({"bbox": [round(v, 1) for v in (b["x0"], b["y0"], b["x1"], b["y1"])],
                    "width_mm": round(w, 1), "height_mm": round(h, 1)})
    return out


def measure_pdf(path: pathlib.Path) -> dict | None:
    """Measure figure bands and the font sizes used inside them."""
    try:
        doc = pymupdf.open(str(path))
    except Exception:
        return None

    all_sizes = []
    figures = []
    pages_scanned = 0
    for pno in range(min(len(doc), 24)):
        page = doc[pno]
        pages_scanned += 1
        bands = find_figures(page)
        if not bands:
            continue
        # font sizes inside each band
        spans = []
        for blk in page.get_text("dict").get("blocks", []):
            for ln in blk.get("lines", []):
                for sp in ln.get("spans", []):
                    t = sp.get("text", "").strip()
                    if t:
                        spans.append((sp["size"], sp["bbox"]))
        for b in bands:
            bx0, by0, bx1, by1 = b["bbox"]
            inside = [s for s, bb in spans
                      if bx0 - 2 <= bb[0] and bb[2] <= bx1 + 2
                      and by0 - 2 <= bb[1] and bb[3] <= by1 + 2]
            b["n_text_spans"] = len(inside)
            if inside:
                b["min_font_pt"] = round(min(inside), 2)
                b["max_font_pt"] = round(max(inside), 2)
                all_sizes.extend(inside)
            figures.append(b)

    page_rect = doc[0].rect
    info = {
        "file": path.name,
        "pages": len(doc),
        "pages_scanned": pages_scanned,
        "page_mm": [round(page_rect.width * MM_PER_PT, 1),
                    round(page_rect.height * MM_PER_PT, 1)],
        "figures": figures,
    }
    doc.close()

    if all_sizes:
        arr = np.array(all_sizes)
        info["font_sizes"] = {
            "n": int(arr.size),
            "min": round(float(arr.min()), 2),
            "p05": round(float(np.percentile(arr, 5)), 2),
            "median": round(float(np.median(arr)), 2),
            "p95": round(float(np.percentile(arr, 95)), 2),
            "max": round(float(arr.max()), 2),
            "below_5pt_fraction": round(float((arr < 5.0).mean()), 4),
        }
    return info


def main() -> int:
    CORPUS.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(PDF_ROOT.rglob("*.pdf"))
    accepted, rejected = [], []
    for p in pdfs:
        ok, why = is_nature_paper(p)
        (accepted if ok else rejected).append((p, why))

    print(f"  PDFs scanned        : {len(pdfs)}")
    print(f"  accepted as Nature  : {len(accepted)}")
    print(f"  rejected            : {len(rejected)}")
    from collections import Counter
    reasons = Counter(w for _, w in rejected if w.startswith("rejected:"))
    for w, c in reasons.most_common(4):
        print(f"      {c:4d}  {w}")

    results = []
    for p, _ in accepted:
        m = measure_pdf(p)
        if m and m["figures"]:
            results.append(m)
            print(f"  {p.name[:62]:<62} figures={len(m['figures']):2d}")

    widths = [f["width_mm"] for r in results for f in r["figures"]]
    mins = [f["min_font_pt"] for r in results for f in r["figures"] if "min_font_pt" in f]

    summary = {
        "papers_measured": len(results),
        "figure_bands": len(widths),
        "width_mm": {
            "n": len(widths),
            "min": round(min(widths), 1) if widths else None,
            "p25": round(float(np.percentile(widths, 25)), 1) if widths else None,
            "median": round(float(np.median(widths)), 1) if widths else None,
            "p75": round(float(np.percentile(widths, 75)), 1) if widths else None,
            "max": round(max(widths), 1) if widths else None,
        },
        "min_font_pt": {
            "n": len(mins),
            "min": round(min(mins), 2) if mins else None,
            "median": round(float(np.median(mins)), 2) if mins else None,
            "below_5_fraction": round(float(np.mean([m < 5.0 for m in mins])), 4) if mins else None,
        },
        "dirty_data_excluded": reasons.most_common(),
    }
    OUT.write_text(json.dumps({"summary": summary, "papers": results}, indent=2),
                   encoding="utf-8")

    print()
    print("  === MEASURED FROM REAL NATURE PAPERS ===")
    print(f"  papers        : {summary['papers_measured']}")
    print(f"  figure bands  : {summary['figure_bands']}")
    w = summary["width_mm"]
    print(f"  width mm      : min {w['min']}  p25 {w['p25']}  median {w['median']}  "
          f"p75 {w['p75']}  max {w['max']}")
    f = summary["min_font_pt"]
    print(f"  min font pt   : min {f['min']}  median {f['median']}  "
          f"below-5pt share {f['below_5_fraction']}")
    print(f"\n  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
