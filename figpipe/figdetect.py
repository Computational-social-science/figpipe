"""Locate figures by their CAPTIONS, not by merging drawing rectangles.

WHY THE OLD DETECTOR WAS WRONG
    The previous approach collected every drawing and image rectangle on a page, merged
    overlapping ones into vertical "bands", and called each band a figure. The adversarial
    audit found this produced, among 420 bands:

        height_mm max            = 14,437.1 mm   (A4 is 279 mm tall)
        bands taller than 240 mm = 67
        bands with >200 text spans = 10
        bands with 0 text spans  = 181  (43.1 %)

    and, inspecting 18 bands by eye, about half were wrong: a full page of news prose, a
    prompt-template box, a figure with its top and bottom cropped off.

    The root error was conceptual. Merging drawing rectangles does not identify a figure --
    it identifies "ink", and a page of body text is ink. A figure is identified by something
    else entirely: **Nature gives every figure a caption starting "Fig. N |"**. The caption is
    the anchor; the figure is the region above it.

HOW IT WORKS NOW
    1. Find caption markers by text: `Fig. N |` (also `Figure N |`, `Extended Data Fig. N`).
    2. Take the caption block's own bounding box.
    3. The figure region is the largest ink-bearing area between the PREVIOUS caption (or the
       page top) and this caption's top edge.
    4. Record the caption text alongside the region, so a later stage can pair them and read
       the panel descriptions -- which is what "learning layout" actually needs.

WHAT THIS FIXES AND WHAT IT DOES NOT
    Fixes: body-text pages can no longer be mistaken for figures, because they carry no
    caption. Cropping is bounded by the caption position rather than by an arbitrary merge.
    Does NOT fix: figures whose caption is on a different page (rare), and figures in papers
    that use a different caption convention (checked: Nature uses "Fig. N |" consistently).
"""
from __future__ import annotations

import re

import pymupdf

MM_PER_PT = 25.4 / 72.0

#: Nature's caption conventions, most specific first.
CAPTION_PATTERNS = [
    re.compile(r"^Extended\s+Data\s+Fig(?:ure)?\.?\s*(\d+)\s*[|｜]"),
    re.compile(r"^Fig(?:ure)?\.?\s*(\d+)\s*[|｜]"),
    re.compile(r"^Fig(?:ure)?\.?\s*(\d+)\s*\.\s"),   # fallback: "Fig. 1."
]


def _caption_lines(page) -> list[dict]:
    """Caption starts on this page: line text, its bbox, figure number, kind."""
    out = []
    d = page.get_text("dict")
    for blk in d.get("blocks", []):
        for ln in blk.get("lines", []):
            txt = "".join(s.get("text", "") for s in ln.get("spans", [])).strip()
            if not txt or len(txt) > 200:
                continue
            for pat in CAPTION_PATTERNS:
                m = pat.match(txt)
                if m:
                    kind = "extended" if "Extended" in txt else "main"
                    out.append({
                        "num": int(m.group(1)),
                        "kind": kind,
                        "text": txt,
                        "bbox": tuple(ln["bbox"]),
                        "y0": ln["bbox"][1],
                    })
                    break
    return out


#: A vertical gap larger than this separates body text from a figure above it.
#: Measured on real Nature pages: line spacing is ~10-14 pt, so a 20 pt gap is decisive.
FIGURE_GAP_PT = 20.0


def _collect_ink(page, y_top: float, y_limit: float) -> list:
    """Ink rectangles (drawings + images) in the vertical window (y_limit, y_top)."""
    rects = []
    for dr in page.get_drawings():
        r = dr.get("rect")
        if r is None or r.width < 3 or r.height < 3:
            continue
        if r.y0 >= y_limit - 1 and r.y1 <= y_top + 1:
            rects.append(pymupdf.Rect(r))
    for im in page.get_images(full=True):
        try:
            for r in page.get_image_rects(im[0]):
                if r.height > 3 and r.width > 3 and r.y0 >= y_limit - 1 and r.y1 <= y_top + 1:
                    rects.append(pymupdf.Rect(r))
        except Exception:
            continue
    return rects


def _figure_block_above(page, y_top: float, y_limit: float) -> tuple | None:
    """The contiguous ink block immediately above a caption, excluding prose further up.

    WHY A GAP SCAN AND NOT A SIMPLE BBOX
        A plain bounding box over everything above the caption swept in body text: a real
        figure rendered with two columns of prose on top. Nature puts a figure in one
        contiguous block directly above its caption, separated from body copy by a visible
        vertical gap.

        So: walk upward from the caption, merging ink while consecutive pieces are close, and
        STOP at the first gap wider than FIGURE_GAP_PT. Everything above that gap is prose and
        is discarded.

    Returns None when nothing sits directly above the caption.
    """
    rects = _collect_ink(page, y_top, y_limit)
    if not rects:
        return None
    # sort by bottom edge, descending: start at the piece closest to the caption
    rects.sort(key=lambda r: -r.y1)
    block = list(rects[:1])
    cur_top = rects[0].y0
    for r in rects[1:]:
        gap = cur_top - r.y1
        if gap > FIGURE_GAP_PT:
            break                     # prose above; stop here
        block.append(r)
        cur_top = min(cur_top, r.y0)
    x0 = min(r.x0 for r in block); x1 = max(r.x1 for r in block)
    y0 = min(r.y0 for r in block); y1 = max(r.y1 for r in block)

    # INCLUDE PANEL LETTERS AND OTHER TEXT JUST ABOVE THE BLOCK.
    # Panel labels (a, b, c, d) are TEXT, not drawings, so the ink scan never saw them and the
    # crop cut them off -- confirmed by rendering and looking. Extend the top edge to take in
    # any text span whose baseline is within PANEL_MARGIN_PT of the block top, as long as it is
    # still below the caption gap.
    PANEL_MARGIN_PT = 16.0
    try:
        for blk in page.get_text("dict").get("blocks", []):
            for ln in blk.get("lines", []):
                bb = ln.get("bbox")
                if not bb:
                    continue
                txt = "".join(sp.get("text", "") for sp in ln.get("spans", [])).strip()
                if not txt:
                    continue
                # a panel letter is 1-2 chars; also take short labels
                if len(txt) > 24:
                    continue
                if y0 - PANEL_MARGIN_PT <= bb[1] < y0:
                    y0 = min(y0, bb[1])
                    x0 = min(x0, bb[0]); x1 = max(x1, bb[2])
    except Exception:
        pass

    return (x0, y0, x1, y1)


def find_figures(page) -> list[dict]:
    """Figures on one page, anchored by their captions.

    The figure region runs from just below the previous caption (or the page top) to the
    caption's own top edge. Anything without a caption is not reported as a figure.
    """
    caps = _caption_lines(page)
    if not caps:
        return []
    caps.sort(key=lambda c: c["y0"])
    out = []
    prev_bottom = page.rect.y0
    for c in caps:
        region = _figure_block_above(page, c["y0"], prev_bottom)
        if region is not None:
            x0, y0, x1, y1 = region
            w_mm = (x1 - x0) * MM_PER_PT
            h_mm = (y1 - y0) * MM_PER_PT
            if w_mm >= 40 and h_mm >= 15:
                out.append({
                    "figure_number": c["num"],
                    "kind": c["kind"],
                    "caption_text": c["text"],
                    "caption_bbox": [round(v, 1) for v in c["bbox"]],
                    "bbox": [round(v, 1) for v in region],
                    "width_mm": round(w_mm, 1),
                    "height_mm": round(h_mm, 1),
                })
        prev_bottom = c["bbox"][3]
    return out


def extract_paper(pdf_path) -> dict:
    """All caption-anchored figures in one PDF, with page numbers."""
    doc = pymupdf.open(str(pdf_path))
    figures = []
    for pno in range(len(doc)):
        for f in find_figures(doc[pno]):
            figures.append({**f, "page": pno + 1})
    page_rect = doc[0].rect
    info = {
        "file": str(pdf_path).split("\\")[-1],
        "pages": len(doc),
        "page_mm": [round(page_rect.width * MM_PER_PT, 1),
                    round(page_rect.height * MM_PER_PT, 1)],
        "figures": figures,
        "n_figures": len(figures),
    }
    doc.close()
    return info
