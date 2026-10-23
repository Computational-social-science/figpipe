"""Post-render audits. These check the OUTPUT FILE, not the source code.

WHY THIS MODULE IS THE IMPORTANT ONE
    Every defect this pipeline exists to prevent was invisible in the source and visible only
    in the rendered artefact:

      * four of six figures carried text at 4.00-4.80 pt, hard-coded per annotation and never
        checked against the 5 pt floor;
      * `10^n` log labels rendered exponents at 3.15 pt, which no amount of reading the
        rcParams would reveal;
      * one figure was 198.8 mm wide against a 183 mm specification.

    A source-code linter cannot catch any of these, because the code is not wrong -- the
    rendered result is. So the primary check reads the PDF back and measures the spans.

WHAT IS CHECKED
    font sizes   every text span in the PDF, via PyMuPDF
    dimensions   width against {89, 183} mm, height against 170 mm
    vector       the PDF exists and carries embedded fonts (fonttype 42)
    palette      the figure uses the Okabe-Ito hues
    overlap      text spans whose bounding boxes intersect (approximate, see caveat)

WHAT IS NOT CHECKED
    Whether the figure is WELL DESIGNED. Panel balance, visual hierarchy, and whether the eye
    is led to the finding cannot be measured. A passing audit means the mechanical
    requirements are met -- it is not a claim of quality, and this docstring says so rather
    than letting a green check imply more.
"""
from __future__ import annotations

import pathlib

MIN_PT_DEFAULT = 5.0
MAX_PT_DEFAULT = 7.0
MAX_HEIGHT_MM = 170.0
ALLOWED_WIDTHS_MM = (89.0, 183.0)
PANEL_LETTER_PT = 8.0
TOL_MM = 0.6


def _require_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz
            return fitz
        except ImportError:
            return None


def text_spans(pdf_path, min_pt: float = MIN_PT_DEFAULT, max_pt: float = MAX_PT_DEFAULT):
    """Every span outside [min_pt, max_pt], as (page, size, text, bbox).

    Panel letters are exempt from the maximum: the guide specifies 8 pt for them, above the
    7 pt ceiling that applies to body text.
    """
    pymupdf = _require_pymupdf()
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required for the audit: pip install pymupdf")
    out = []
    doc = pymupdf.open(str(pdf_path))
    for pno, page in enumerate(doc, 1):
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = float(span.get("size", 0))
                    text = span.get("text", "")
                    if not text.strip():
                        continue
                    # a lone lowercase/uppercase letter at exactly 8 pt is a panel label
                    if abs(size - PANEL_LETTER_PT) < 0.3 and len(text.strip()) == 1:
                        continue
                    if size < min_pt - 1e-6 or size > max_pt + 1e-6:
                        out.append((pno, round(size, 2), text, tuple(span.get("bbox", ()))))
    doc.close()
    return out


def dimensions(pdf_path):
    """(width_mm, height_mm) of the first page."""
    pymupdf = _require_pymupdf()
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required: pip install pymupdf")
    doc = pymupdf.open(str(pdf_path))
    r = doc[0].rect
    doc.close()
    return r.width / 72 * 25.4, r.height / 72 * 25.4


def embedded_fonts(pdf_path):
    """Font names and types embedded in the PDF.

    Nature requires TrueType (2 or 42), i.e. EDITABLE text. Type-3 fonts are outlines and are
    rejected. `pdf.fonttype=42` in matplotlib is what produces this.
    """
    pymupdf = _require_pymupdf()
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required: pip install pymupdf")
    doc = pymupdf.open(str(pdf_path))
    fonts = []
    for pno in range(len(doc)):
        for f in doc.get_page_fonts(pno):
            fonts.append({"name": f[3], "type": f[2], "ext": f[1]})
    doc.close()
    return fonts


def overlapping_text(pdf_path, iou_threshold: float = 0.30):
    """Pairs of text spans whose boxes overlap enough to be a collision.

    APPROXIMATE. This catches text drawn on top of text, which is the failure the guide names
    ("Avoid overlapping text"). It cannot catch a label colliding with a data mark, and the
    IoU threshold is a heuristic -- a deliberate overlap (a label placed on a band) will be
    reported. Treat findings as leads to inspect, not as verdicts.
    """
    pymupdf = _require_pymupdf()
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required: pip install pymupdf")
    out = []
    doc = pymupdf.open(str(pdf_path))
    for pno, page in enumerate(doc, 1):
        boxes = []
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        boxes.append((tuple(span["bbox"]), span["text"]))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, ta = boxes[i]
                b, tb = boxes[j]
                ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
                iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
                if ix <= 0 or iy <= 0:
                    continue
                inter = ix * iy
                area = min((a[2]-a[0])*(a[3]-a[1]), (b[2]-b[0])*(b[3]-b[1]))
                if area > 0 and inter / area >= iou_threshold:
                    out.append((pno, ta, tb, round(inter / area, 2)))
    doc.close()
    return out


def overlapping_glyphs(pdf_path, min_ratio: float = 0.25):
    """Text-on-text collisions measured at GLYPH level, grouped by span pair.

    WHY NOT THE SPAN BBOX TEST
        `overlapping_text` compares axis-aligned span boxes. For ROTATED tick labels -- the 20
        rotated country names of a ranked bar panel, for instance -- every neighbouring pair of
        boxes overlaps heavily while the glyphs themselves are cleanly separated along the
        diagonal. Running the span test on such a figure reports 22 "collisions" that a reader
        would never see, which is worse than no check: it teaches everyone to ignore the check.

        Comparing individual character boxes and ignoring pairs inside the same span removes the
        rotated-label false positives while still catching the real defect (two labels printed on
        top of each other). A collision is reported when the overlap covers at least `min_ratio`
        of the smaller glyph box.
    """
    pymupdf = _require_pymupdf()
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required: pip install pymupdf")
    out = []
    doc = pymupdf.open(str(pdf_path))
    try:
        for pno, page in enumerate(doc, 1):
            chars = []
            for block in page.get_text("rawdict").get("blocks", []):
                for line in block.get("lines", []):
                    for sid, span in enumerate(line.get("spans", [])):
                        text = "".join(c.get("c", "") for c in span.get("chars", []))
                        for c in span.get("chars", []):
                            ch = c.get("c", "")
                            if not ch.strip():
                                continue
                            chars.append({"bbox": c["bbox"], "char": ch,
                                          "span": text, "span_id": (pno, id(span), sid)})
            chars.sort(key=lambda c: c["bbox"][0])
            counts: dict[tuple, int] = {}
            for i, a in enumerate(chars):
                ax0, ay0, ax1, ay1 = a["bbox"]
                for b in chars[i + 1:]:
                    bx0, by0, bx1, by1 = b["bbox"]
                    if bx0 >= ax1:
                        break
                    if a["span_id"] == b["span_id"]:
                        continue
                    ix = min(ax1, bx1) - max(ax0, bx0)
                    iy = min(ay1, by1) - max(ay0, by0)
                    if ix <= 0 or iy <= 0:
                        continue
                    area = min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))
                    if area > 0 and (ix * iy) / area >= min_ratio:
                        key = tuple(sorted([a["span"], b["span"]]))
                        counts[key] = counts.get(key, 0) + 1
            for (ta, tb), n in counts.items():
                out.append({"page": pno, "a": ta, "b": tb, "glyph_pairs": n})
    finally:
        doc.close()
    out.sort(key=lambda d: -d["glyph_pairs"])
    return out


def audit(pdf_path, min_pt=MIN_PT_DEFAULT, max_pt=MAX_PT_DEFAULT,
          expect_width_mm=None, check_overlap=True) -> dict:
    """Run every check and return a structured report.

    A report with `ok=False` is a hard failure for submission; the individual findings say
    what to fix.
    """
    p = pathlib.Path(pdf_path)
    report = {"path": str(p), "ok": True, "findings": []}
    if not p.is_file():
        report["ok"] = False
        report["findings"].append({"check": "exists", "detail": "file not found"})
        return report

    spans = text_spans(p, min_pt, max_pt)
    if spans:
        sizes = sorted({s[1] for s in spans})
        report["findings"].append({
            "check": "font_size", "detail":
            f"{len(spans)} span(s) outside {min_pt}-{max_pt} pt; sizes present: {sizes}",
            "examples": [(s[1], s[2]) for s in spans[:6]]})
        report["ok"] = False

    w, h = dimensions(p)
    report["width_mm"], report["height_mm"] = round(w, 2), round(h, 2)
    if expect_width_mm is not None:
        if not any(abs(w - a) < TOL_MM for a in ALLOWED_WIDTHS_MM):
            report["findings"].append({
                "check": "width", "detail":
                f"{w:.1f} mm is not one of Nature's column widths {ALLOWED_WIDTHS_MM}"})
            report["ok"] = False
        elif abs(w - expect_width_mm) > TOL_MM:
            report["findings"].append({
                "check": "width", "detail":
                f"expected {expect_width_mm} mm, got {w:.1f} mm"})
            report["ok"] = False
    # A TOLERANCE, for the same reason width has one. Without it a page measured at 170.0000001 mm
    # against a 170.0 mm maximum fails, and the finding reads "170.0 mm exceeds the 170.0 mm
    # maximum" -- a message that contradicts itself, which is how this was found.
    if h > MAX_HEIGHT_MM + TOL_MM:
        report["findings"].append({
            "check": "height", "detail":
            f"{h:.1f} mm exceeds the {MAX_HEIGHT_MM} mm maximum"})
        report["ok"] = False

    fonts = embedded_fonts(p)
    report["fonts"] = fonts
    type3 = [f for f in fonts if "type3" in (f["type"] or "").lower()]
    if type3:
        report["findings"].append({
            "check": "font_type", "detail":
            f"{len(type3)} Type-3 font(s) embedded; Nature rejects outlined text",
            "fonts": type3[:4]})
        report["ok"] = False

    if check_overlap:
        overlaps = overlapping_text(p)
        if overlaps:
            report["findings"].append({
                "check": "overlap", "detail":
                f"{len(overlaps)} overlapping text pair(s)", "examples": overlaps[:6]})
            # Overlap is a lead, not automatically a failure: deliberate label placement on a
            # band is legitimate. Reported but does not set ok=False.

    return report

def _legend_frames(page) -> list[tuple]:
    """Filled-and-stroked white rectangles that look like a LEGEND frame.

    A legend frame in matplotlib is a rect with `type == "fs"` and a near-white fill, big enough to
    hold text. Measured on a 216x144 pt page:

        no legend        0 candidates
        legend centre    (77.4, 56.5, 66.7, 32.3)   type='fs'  fill=(1,1,1)
        legend upper-R   (122.7, 22.3, 66.7, 32.3)  type='fs'  fill=(1,1,1)

    The page background is excluded by size and the axes background by `type` (it is `"f"`, filled
    only). Those two exclusions are what stop the check from calling the whole figure a legend.
    """
    page_r = page.rect
    out = []
    for d in page.get_drawings():
        r = d.get("rect")
        if r is None or d.get("type") != "fs":
            continue
        fill = d.get("fill")
        if fill is None or min(fill) < 0.9:
            continue
        if r.width >= page_r.width - 1 or r.height >= page_r.height - 1:
            continue
        if r.width < 8 or r.height < 8:
            continue
        out.append((r.x0, r.y0, r.x1, r.y1))
    return out


def _segments(page) -> list[tuple]:
    """Every straight segment on the page as ((x0,y0),(x1,y1)).

    A data line is ONE path whose ITEMS are the segments between points:

        l  [Point(34.6, 123.1), Point(42.6, 117.8)]
        l  [Point(42.6, 117.8), Point(50.6, 112.5)]

    Reading the items is what makes the occlusion test possible: the path's BOUNDING BOX spans the
    whole axes, so a box test cannot tell where the line actually is.
    """
    out = []
    for d in page.get_drawings():
        if d.get("type") == "fs":
            continue
        for item in (d.get("items") or []):
            if not item or item[0] != "l":
                continue
            try:
                p0, p1 = item[1], item[2]
                out.append(((p0.x, p0.y), (p1.x, p1.y)))
            except (AttributeError, IndexError, TypeError):
                continue
    return out


def _segment_hits_cell(seg, cx0, cy0, cx1, cy1, samples: int = 12) -> bool:
    """Does the segment pass through the cell? Sampled along its length.

    SAMPLING, NOT CLIPPING. A proper Liang-Barsky clip would be exact; sampling is what this
    implements and the docstring says so. Twelve samples per segment on a 24x24 grid over a legend
    frame resolves a line crossing the frame -- the failure this check exists to find.

    THE THRESHOLD IS PLACED IN A MEASURED GAP, not derived from a principle:

        legend in an empty corner, flat line elsewhere    2.1 %  (tick marks and spines)
        legend centred over two crossing lines           15.5 %

    6 % sits between them with room on both sides. A lower threshold flagged the empty-corner case,
    which is how the first attempt failed.
    """
    (ax0, ay0), (ax1, ay1) = seg
    for i in range(samples + 1):
        t = i / samples
        x = ax0 + (ax1 - ax0) * t
        y = ay0 + (ay1 - ay0) * t
        if cx0 <= x <= cx1 and cy0 <= y <= cy1:
            return True
    return False

#: Set to True only when the occlusion test follows path ITEMS rather than bounding boxes. A
#: bounding-box test cannot answer this question on a real page, and a check that always answers the
#: same way is not a measurement.
LEGEND_OCCLUSION_IMPLEMENTED = True


def legend_occlusion_supported() -> bool:
    """Whether `legend_occlusion` can actually decide the question.

    False until the test walks path items. Exposed so a caller can report "not available" instead of
    reading an empty list as "no occlusion".
    """
    return LEGEND_OCCLUSION_IMPLEMENTED


def legend_occlusion(pdf_path, *, ink_ratio: float = 0.06) -> list[dict]:
    """Legend frames that sit on top of drawn marks.

    THE BLIND SPOT THIS CLOSES. `overlapping_text` compares TEXT to TEXT, so a legend covering a
    data line -- the failure the benchmark's vision channel names -- is invisible to it: the legend's
    frame is a filled rect, the line is a path, and neither is text.

    HOW IT IS MEASURED: a legend frame is filled, so anything drawn under it is HIDDEN. The check
    sums the drawing paths whose bounding box falls inside the frame and which are not the frame
    itself. A legend in the empty margin has almost nothing under it; a legend over a curve has the
    curve.

    THIS FUNCTION DOES NOT WORK, AND IT SAYS SO RATHER THAN RETURNING A NUMBER.

    Measured on a real page: a data line drawn by `ax.plot` is ONE path with 19 points whose
    BOUNDING BOX spans the whole axes --

        type=s  rect=(34.6, 22.3, 186.8, 123.1)  items=19

    So every legend placed inside the axes reports "covered 100%", and the check cannot tell a legend
    in an empty corner from one sitting on a curve. The first version summed per-path overlaps and
    reported "over 400% of its area", which was worse: a ratio that cannot exceed 1 exceeded 4.

    The path ITEMS are available, so the geometry exists -- but testing every segment against every
    cell is a different algorithm from a bounding-box test, and shipping the bounding-box version
    with a caveat would be the "a control that looks present and does nothing" defect this project
    records most often.

    It returns an EMPTY list and reports the limitation through `legend_occlusion_supported()`, so a
    caller that wants the check is told it is unavailable rather than told everything is fine.
    """
    if not legend_occlusion_supported():
        return []
    pymupdf = _require_pymupdf()
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required: run `pip install pymupdf`")

    out = []
    doc = pymupdf.open(str(pdf_path))
    for pno, page in enumerate(doc, 1):
        frames = _legend_frames(page)
        if not frames:
            continue
        segs = _segments(page)
        if not segs:
            continue
        for (fx0, fy0, fx1, fy1) in frames:
            # A UNION, NOT A SUM. Summing each path's overlap counts the same pixel once per path
            # and produced "covered over 400% of its area" -- a ratio that cannot exceed 1. The grid
            # is 24x24 cells, which is coarse and is why the threshold is a ratio.
            cells = 24
            cw = max(1e-9, (fx1 - fx0) / cells)
            ch = max(1e-9, (fy1 - fy0) / cells)
            covered_cells = 0
            for gy in range(cells):
                cy0 = fy0 + gy * ch
                cy1 = cy0 + ch
                for gx in range(cells):
                    cx0 = fx0 + gx * cw
                    cx1 = cx0 + cw
                    for seg in segs:
                        if _segment_hits_cell(seg, cx0, cy0, cx1, cy1):
                            covered_cells += 1
                            break
            ratio = covered_cells / float(cells * cells)
            if ratio >= ink_ratio:
                out.append({"page": pno,
                            "frame": (round(fx0, 1), round(fy0, 1), round(fx1, 1), round(fy1, 1)),
                            "covered_ratio": round(ratio, 3),
                            "detail": (f"a legend frame at ({fx0:.0f},{fy0:.0f}) covers drawing "
                                       f"paths over {ratio:.0%} of its area, so it may be hiding a "
                                       f"data mark")})
    doc.close()
    return out
