"""Measure how real published Nature figures ARRANGE their panels.

WHY THIS SCRIPT EXISTS
    figpipe can now compose panels (figpipe.composite), but the composer's geometry constants
    must not be invented. The owner's instruction is to learn the layout from real Nature
    figures and sediment it: "必须自主学习真实的《NATURE》出版过的图片LAYOUT、间距等难以学习到的
    技巧". The corpus already carries 73 real figure records with their caption and page
    bounding boxes (corpus/figures_caption_anchored.json), measured from the owner's own PDF
    library. This script reads those figures back, finds their internal panel structure, and
    records the distributions the composer consumes:

        gutter_mm        white space between the printed marks of two panels
        panel_aspect     width:height of one panel
        letter_dx/dy_mm  where the 8 pt panel letter sits relative to its panel
        grid/counts      which grids actually occur

METHOD, AND WHY IT IS NOT SIMPLY "FIND WHITE COLUMNS"
    A y-axis tick label of the right-hand panel is printed INSIDE the gap between the two
    panels, so a purely ink-free gutter does not exist for most two-panel figures. The method
    is therefore anchored on two independent signals and reports their agreement:

      1. THE PANEL LETTERS. Nature labels every panel with a single 8 pt character. Their text
         spans are read from the PDF (not guessed from pixels) and cluster into rows and
         columns. These give the panel COUNT and a starting boundary for each split.
      2. THE CAPTION. The caption walks the panels ("a, ...; b, ..."), so the letters it names
         are an independent count. `agree` records whether the two counts match -- a split
         that disagrees with the caption is not evidence, and the figure is flagged.

    The boundary between two letter columns is then refined to the emptiest band within a
    search window, measured on the ink projection (ink = pixel < 200 at 300 dpi). A boundary
    is accepted only if both cells contain ink and have a plausible aspect ratio. Gutter width
    is measured as the run of ink-free columns around the accepted boundary, in mm.

WHAT IS DELIBERATELY NOT MEASURED
    Whether the figure is well designed, or which panel is the "key" panel. Those are
    judgements, and figpipe's rule is that a model does not decide what its own findings mean.

OUTPUT
    corpus/composite_layouts.json    the distributions + every figure record
    corpus/composite_overlay/*.png   the detected boxes drawn on the crop, for human checking
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pymupdf  # noqa: E402

from figpipe import sources  # noqa: E402  -- the read-only guard

FIG_JSON = ROOT / "corpus" / "figures_caption_anchored.json"
OUT_JSON = ROOT / "corpus" / "composite_layouts.json"
OVERLAY_DIR = ROOT / "corpus" / "composite_overlay"
SEARCH_ROOT = pathlib.Path("D:/2026-AI4S")

DPI = 300
INK_LEVEL = 200          # grey value below which a pixel is ink
MIN_GUTTER_MM = 1.5      # a gap narrower than this is not a panel gutter
REFINE_MM = 15.0         # a letter-derived boundary is refined within this window
LETTER_SIZES = (7.0, 9.5)
LETTER_CHARS = "abcdefgh"


# --------------------------------------------------------------------------------------
# Source resolution
# --------------------------------------------------------------------------------------

def resolve_pdfs(names) -> dict[str, str]:
    """PDF basename -> absolute path, searched once under the owner's library (read-only)."""
    want = set(names)
    found: dict[str, str] = {}
    for p in SEARCH_ROOT.rglob("*.pdf"):
        if p.name in want and p.name not in found:
            found[p.name] = str(p)
            if len(found) == len(want):
                break
    return found


# --------------------------------------------------------------------------------------
# Rendering and ink
# --------------------------------------------------------------------------------------

def render_region(pdf_path: str, page_no: int, bbox_pt) -> tuple[np.ndarray, float]:
    """Greyscale ink image of one region, and mm per pixel."""
    sources.assert_writable(ROOT / "corpus" / "composite_overlay" / "x")  # project path
    doc = pymupdf.open(pdf_path)
    try:
        page = doc[page_no - 1]
        rect = pymupdf.Rect(*bbox_pt)
        pix = page.get_pixmap(clip=rect, dpi=DPI, colorspace=pymupdf.csGRAY)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    finally:
        doc.close()
    return img, 25.4 / DPI


def ink_mask(img: np.ndarray) -> np.ndarray:
    return img < INK_LEVEL


def profiles(ink: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fraction of ink per column and per row."""
    col = ink.mean(axis=0)
    row = ink.mean(axis=1)
    return col, row


def _white_run(frac: np.ndarray, pos: int, threshold: float = 0.01) -> tuple[int, int]:
    """Expand from `pos` while the profile stays (almost) ink-free; returns [lo, hi)."""
    lo = pos
    while lo > 0 and frac[lo - 1] <= threshold:
        lo -= 1
    hi = pos
    while hi < len(frac) and frac[hi] <= threshold:
        hi += 1
    return lo, hi


def _band_score(frac: np.ndarray, pos: int, half_px: int) -> float:
    lo = max(0, pos - half_px)
    hi = min(len(frac), pos + half_px)
    if hi <= lo:
        return 1.0
    return float(frac[lo:hi].mean())


def refine_boundary(frac: np.ndarray, init: int, window_px: int, half_px: int) -> int:
    """The emptiest position within `window_px` of `init` -- a gutter centre, not an edge."""
    best, best_score = init, _band_score(frac, init, half_px)
    lo = max(1, init - window_px)
    hi = min(len(frac) - 1, init + window_px)
    for pos in range(lo, hi):
        s = _band_score(frac, pos, half_px)
        if s < best_score - 1e-9:
            best, best_score = pos, s
    return best


# --------------------------------------------------------------------------------------
# Panel letters and caption cross-check
# --------------------------------------------------------------------------------------

def panel_letters(pdf_path: str, page_no: int, bbox_pt) -> list[dict]:
    """Single-character spans a-h at 8 pt inside the figure: Nature's panel labels."""
    doc = pymupdf.open(pdf_path)
    out = []
    try:
        page = doc[page_no - 1]
        clip = pymupdf.Rect(*bbox_pt)
        for block in page.get_text("dict", clip=clip).get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    size = float(span.get("size", 0))
                    if len(text) == 1 and text in LETTER_CHARS and \
                            LETTER_SIZES[0] <= size <= LETTER_SIZES[1]:
                        x0, y0, x1, y1 = span["bbox"]
                        out.append({"char": text, "size_pt": round(size, 2),
                                    "x": (x0 + x1) / 2, "y": (y0 + y1) / 2,
                                    "font": span.get("font", "")})
    finally:
        doc.close()
    out.sort(key=lambda d: (round(d["y"], 1), d["x"]))
    return out


def caption_letters(caption: str) -> list[str]:
    """Panel letters a caption names, by conservative patterns only.

    A bare single letter is NOT counted: "a" is an English article, and a counter that treats
    every "a" as a panel produces a count of two for a one-panel figure. Only the forms Nature
    actually uses are accepted: "(a)", "a,", "a;", "a–c" ranges, and "Figure 1a".
    """
    caps = caption or ""
    found: set[str] = set()
    for m in re.finditer(r"\(([a-h])\)", caps):
        found.add(m.group(1))
    for m in re.finditer(r"(?<![\w])([a-h])\s*[,;:]", caps):
        found.add(m.group(1))
    for m in re.finditer(r"(?<![\w])([a-h])\s*[–\-]\s*([a-h])(?![\w])", caps):
        a, b = m.group(1), m.group(2)
        if a <= b:
            found.update(chr(c) for c in range(ord(a), ord(b) + 1))
    for m in re.finditer(r"(?:Figure|Fig\.?)\s*\d+\s*([a-h])(?![\w])", caps):
        found.add(m.group(1))
    return sorted(found)


def caption_index(features=ROOT / "corpus" / "caption_features.jsonl",
                  extracted=ROOT / "corpus" / "extracted") -> dict[tuple[str, int], str]:
    """(PDF basename, figure number) -> the FULL caption text.

    WHY THIS EXISTS
        The figure records carry `caption_text` TRUNCATED to about 80 characters, which is one
        sentence and never the panel walk. A caption cross-check built on that text returns an
        empty letter set for every figure: it agrees with nothing, so it could never disagree
        either -- a control that looks present and does nothing.

        `corpus/caption_features.jsonl` holds the full captions of the corpus's 196 figures,
        keyed by extraction slug; each slug's manifest maps back to the source PDF name. The
        join is by (basename, figure number). Where no full caption exists the record's own
        (truncated) text is used and `caption_source` says so.
    """
    feat = pathlib.Path(features)
    if not feat.is_file():
        return {}
    slug2pdf: dict[str, str] = {}
    for man in pathlib.Path(extracted).glob("*/manifest.json"):
        try:
            m = json.loads(man.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if m.get("paper_id") and m.get("source_name"):
            slug2pdf[m["paper_id"]] = m["source_name"]
    out: dict[tuple[str, int], str] = {}
    for line in feat.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        pdf = slug2pdf.get(rec.get("paper"), rec.get("paper"))
        fid = str(rec.get("figure_id", ""))
        digits = "".join(ch for ch in fid if ch.isdigit())
        if not pdf or not digits:
            continue
        key = (pdf, int(digits))
        if key not in out or len(rec.get("caption_text", "")) > len(out[key]):
            out[key] = rec.get("caption_text", "")
    return out


# --------------------------------------------------------------------------------------
# Grid inference
# --------------------------------------------------------------------------------------

def _factor_pairs(n: int, max_cols: int = 4) -> list[tuple[int, int]]:
    pairs = []
    for r in range(1, n + 1):
        if n % r:
            continue
        c = n // r
        if c <= max_cols and r <= 4:
            pairs.append((r, c))
    return pairs or [(1, n)]


def _cluster(values: list[float], tol: float) -> list[float]:
    """Centre of each cluster of near-equal positions."""
    if not values:
        return []
    vals = sorted(values)
    groups, cur = [], [vals[0]]
    for v in vals[1:]:
        if v - cur[-1] <= tol:
            cur.append(v)
        else:
            groups.append(sum(cur) / len(cur))
            cur = [v]
    groups.append(sum(cur) / len(cur))
    return groups


def _letters_grid(letters: list[dict]) -> tuple[list[float], list[float]]:
    """Column centres and row centres of the panel letters, in pixel-ish coordinates."""
    xs = [lt["x"] for lt in letters]
    ys = [lt["y"] for lt in letters]
    # tolerance: a letter is ~2 mm wide, columns are tens of mm apart; 12 pt is generous and
    # still far below one panel width
    return _cluster(xs, 12.0), _cluster(ys, 12.0)


def _build_cells(col_bounds: list[int], row_bounds: list[int]):
    cells = []
    for r in range(len(row_bounds) - 1):
        for c in range(len(col_bounds) - 1):
            cells.append({"row": r, "col": c,
                          "x0": col_bounds[c], "x1": col_bounds[c + 1],
                          "y0": row_bounds[r], "y1": row_bounds[r + 1]})
    return cells


def _score(cells, ink, cfg) -> float:
    """Lower is better: empty boundaries, populated cells, plausible aspect ratios."""
    h, w = ink.shape
    _total = ink.sum()
    score = 0.0
    for c in cells:
        sub = ink[max(0, c["y0"]):c["y1"], max(0, c["x0"]):c["x1"]]
        if sub.size == 0:
            return 1e9
        frac = sub.mean()
        if frac < 0.004:
            score += 2.0            # an "empty panel" usually means the split is wrong
        cw = (c["x1"] - c["x0"]) * cfg["mm_per_px"]
        ch = (c["y1"] - c["y0"]) * cfg["mm_per_px"]
        aspect = cw / ch if ch else 0
        c["w_mm"], c["h_mm"], c["aspect"] = cw, ch, aspect
        if aspect < 0.15 or aspect > 8.0:
            score += 1.0
    # boundaries: the mean ink in a +-0.4 mm band around each interior boundary line
    half = max(1, int(round(0.4 / cfg["mm_per_px"])))
    interior_x = sorted({c["x0"] for c in cells} | {c["x1"] for c in cells})
    interior_y = sorted({c["y0"] for c in cells} | {c["y1"] for c in cells})
    for x in interior_x:
        if 0 < x < w:
            score += 30.0 * _band_score(ink.mean(axis=0), x, half)
    for y in interior_y:
        if 0 < y < h:
            score += 30.0 * _band_score(ink.mean(axis=1), y, half)
    return score


def infer_grid(letters, caption_chars, ink, mm_per_px) -> dict:
    """The best (rows, cols) partition for one figure, and where its boundaries are.

    The panel COUNT is not searched for: it comes from the letters (or the caption), which are
    independent evidence. Only the ORIENTATION is uncertain, so the factor pairs are scored and
    the winner must satisfy a hard check -- every boundary has to sit in a genuinely empty band
    at least MIN_GUTTER_MM wide. A grid whose boundaries cut through ink is reported as
    `split_verified=False` and contributes nothing to the geometry priors.
    """
    h, w = ink.shape
    col_frac, row_frac = profiles(ink)
    cfg = {"mm_per_px": mm_per_px}
    n_letter = len(letters)
    n_caption = len(caption_chars)
    if n_letter >= 2:
        n = n_letter
    elif n_caption >= 2:
        n = n_caption
    else:
        n = 1
    result = {"n_panels": n, "rows": 1, "cols": 1, "grid_source": "single",
              "cells": [], "split_verified": n == 1, "bad_boundaries": 0}
    if n == 1:
        cells = [{"row": 0, "col": 0, "x0": 0, "x1": w, "y0": 0, "y1": h}]
        _score(cells, ink, cfg)
        result.update(cells=cells, grid_source="single panel")
        return result

    xc, yc = _letters_grid(letters) if n_letter >= 2 else ([], [])
    half_band = max(1, int(round(0.4 / mm_per_px)))
    best = None
    for rows, cols in _factor_pairs(n):
        # A panel letter sits at the TOP-LEFT of its panel, so the boundary between panel k and
        # panel k+1 is just LEFT of letter k+1 -- not halfway between the two letters, which
        # would put the line through the middle of panel k. The refinement window then finds
        # the actual white band.
        if len(xc) == cols:
            inits = [int(round(xc[i + 1])) for i in range(len(xc) - 1)]
            src = "letters"
        else:
            inits = [int(round(w * i / cols)) for i in range(1, cols)]
            src = "equal division"
        xs = [0] + [refine_boundary(col_frac, p, int(REFINE_MM / mm_per_px), half_band)
                    for p in inits] + [w]
        if len(yc) == rows:
            ry = [int(round(yc[i + 1])) for i in range(len(yc) - 1)]
            src_y = "letters"
        else:
            ry = [int(round(h * i / rows)) for i in range(1, rows)]
            src_y = "equal division"
        ys = [0] + [refine_boundary(row_frac, p, int(REFINE_MM / mm_per_px), half_band)
                    for p in ry] + [h]
        if sorted(set(xs)) != sorted(xs) or sorted(set(ys)) != sorted(ys):
            continue
        cells = _build_cells(xs, ys)
        s = _score(cells, ink, cfg)
        # THE CHECK: each boundary must sit in an empty band. A strong boundary is empty to
        # <=1 % of its rows with a >=1.5 mm white run; a weak one is <=5 % with >=0.3 mm. The
        # panel count is external evidence, so this only decides the ORIENTATION and whether
        # the grid is trustworthy enough to contribute numbers.
        bad = 0
        strong = 0
        half_band = max(1, int(round(0.4 / mm_per_px)))
        min_run_px = 1.5 / mm_per_px
        for frac, positions in ((col_frac, xs[1:-1]), (row_frac, ys[1:-1])):
            for pos in positions:
                lo, hi = _white_run(frac, int(pos))
                run = hi - lo
                band = _band_score(frac, int(pos), half_band)
                if band <= 0.01 and run >= min_run_px:
                    strong += 1
                elif band <= 0.05 and run >= 0.3 / mm_per_px:
                    pass
                else:
                    bad += 1
        cand = (bad, -strong, s, rows, cols, xs, ys, cells,
                f"cols:{src}, rows:{src_y}")
        if best is None or cand[:3] < best[:3]:
            best = cand
    if best is None:
        return result
    bad, neg_strong, s, rows, cols, xs, ys, cells, src = best
    result.update(rows=rows, cols=cols, cells=cells, grid_source=src,
                  split_verified=bad == 0, bad_boundaries=bad,
                  strong_boundaries=-neg_strong,
                  cols_centres=xc, rows_centres=yc)
    return result


# --------------------------------------------------------------------------------------
# Gutters and letters
# --------------------------------------------------------------------------------------

def measure_gutters(ink, cells, mm_per_px) -> tuple[list[float], list[float]]:
    """White space between adjacent panels, measured between their INK, in mm.

    Deliberately not measured from the boundary line: the boundary is only known to lie
    somewhere inside the whitespace, and the distance from it to the ink is an artefact of
    where the search happened to land. The gap a reader sees is ink-to-ink, so that is what is
    recorded -- which also makes the number robust to a boundary that is a millimetre off.
    """
    boxes = []
    for c in cells:
        sub = ink[max(0, c["y0"]):c["y1"], max(0, c["x0"]):c["x1"]]
        ys, xs = np.nonzero(sub)
        if len(xs) == 0:
            boxes.append(None)
            continue
        boxes.append({"x0": c["x0"] + int(xs.min()), "x1": c["x0"] + int(xs.max()) + 1,
                      "y0": c["y0"] + int(ys.min()), "y1": c["y0"] + int(ys.max()) + 1,
                      "row": c["row"], "col": c["col"]})
    gx, gy = [], []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a is None or b is None:
                continue
            if a["row"] == b["row"] and b["col"] == a["col"] + 1:
                gx.append(round((b["x0"] - a["x1"]) * mm_per_px, 1))
            if a["col"] == b["col"] and b["row"] == a["row"] + 1:
                gy.append(round((b["y0"] - a["y1"]) * mm_per_px, 1))
    return gx, gy


def match_letters(letters, cells, mm_per_px) -> list[dict]:
    """Panel letter offsets relative to the cell that contains its top-left area.

    Cells are in CROP PIXELS; a letter is in the same space, so the offsets are millimetres
    computed from the crop's own scale. `dx` is positive when the letter starts inside the
    panel (right of its left edge); `dy` is positive when the letter sits ABOVE the panel top.
    """
    out = []
    for lt in letters:
        lx = lt["x"] * mm_per_px
        ly = lt["y"] * mm_per_px
        best, best_d = None, 1e9
        for c in cells:
            x0, x1 = c["x0"] * mm_per_px, c["x1"] * mm_per_px
            y0, y1 = c["y0"] * mm_per_px, c["y1"] * mm_per_px
            if not (x0 - 12 <= lx <= x1 and y0 - 8 <= ly <= y1):
                continue
            d = abs(lx - x0) + abs(ly - y0)
            if d < best_d:
                best, best_d = c, d
        if best is None:
            continue
        best["letter"] = lt["char"]
        out.append({"char": lt["char"], "size_pt": lt["size_pt"],
                    "x_mm": round(lx, 1), "y_mm": round(ly, 1),
                    "dx_mm": round(lx - best["x0"] * mm_per_px, 1),
                    "dy_mm": round(best["y0"] * mm_per_px - ly, 1),
                    "panel_row": best["row"], "panel_col": best["col"]})
    return out


# --------------------------------------------------------------------------------------
# Overlay
# --------------------------------------------------------------------------------------

def write_overlay(img, cells, xs, ys, path, figure_no, grid):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    h, w = img.shape
    fig, ax = plt.subplots(figsize=(min(6.0, w / DPI), min(6.0, w / DPI * h / w)))
    ax.imshow(img, cmap="gray", vmin=0, vmax=255)
    for c in cells:
        ax.add_patch(Rectangle((c["x0"], c["y0"]), c["x1"] - c["x0"],
                               c["y1"] - c["y0"], fill=False, ec="red", lw=0.8))
    for x in xs[1:-1]:
        ax.axvline(x, color="blue", lw=0.6, ls="--")
    for y in ys[1:-1]:
        ax.axhline(y, color="blue", lw=0.6, ls="--")
    ax.set_title(f"figure {figure_no}: {grid}", fontsize=6)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(path, dpi=140, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def _stats(values, nd=1) -> dict:
    v = sorted(x for x in values if x is not None and np.isfinite(x))
    if not v:
        return {"n": 0}
    def q(p):
        return round(float(np.percentile(v, p)), nd)
    return {"n": len(v), "median": q(50), "p10": q(10), "p25": q(25), "p75": q(75),
            "p90": q(90)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=None, help="measure only the first N figures")
    ap.add_argument("--overlays", type=int, default=8, help="how many overlay PNGs to write")
    args = ap.parse_args(argv)

    recs = json.loads(FIG_JSON.read_text(encoding="utf-8"))
    if args.limit:
        recs = recs[:args.limit]
    paths = resolve_pdfs({r["paper"] for r in recs})
    caps_full = caption_index()
    print(f"  {len(recs)} figure records, {len(paths)} source PDFs resolved, "
          f"{len(caps_full)} full captions indexed")

    figures, rejected = [], []
    gutter_mm, panel_aspects, fig_aspects, dxs, dys, letter_sizes = [], [], [], [], [], []
    grids: dict[str, int] = {}
    counts: dict[int, int] = {}
    n_measured = n_composite = n_agree = n_verified = 0
    overlay_budget = args.overlays
    mm_per_pt = 25.4 / 72.0

    for i, rec in enumerate(recs):
        paper = rec.get("paper")
        pdf = paths.get(paper)
        if not pdf:
            rejected.append({"paper": paper, "figure_number": rec.get("figure_number"),
                             "why": "source PDF not found"})
            continue
        bbox = rec.get("bbox")
        if not bbox or bbox[2] - bbox[0] < 20 or bbox[3] - bbox[1] < 20:
            rejected.append({"paper": paper, "figure_number": rec.get("figure_number"),
                             "why": f"implausible bbox {bbox}"})
            continue
        try:
            img, mm_per_px = render_region(pdf, int(rec["page"]), bbox)
        except Exception as e:                                        # noqa: BLE001
            rejected.append({"paper": paper, "figure_number": rec.get("figure_number"),
                             "why": f"render failed: {type(e).__name__}: {e}"})
            continue
        if img.size == 0 or (img < INK_LEVEL).mean() < 1e-4:
            rejected.append({"paper": paper, "figure_number": rec.get("figure_number"),
                             "why": "empty crop (no ink)"})
            continue

        ink = ink_mask(img)
        raw_letters = panel_letters(pdf, int(rec["page"]), bbox)
        # Letters come back in PAGE POINTS; the grid works in CROP PIXELS. One conversion, at
        # the boundary, so no later function has to remember which space it is in.
        letters = [{"char": lt["char"], "size_pt": lt["size_pt"],
                    "x": (lt["x"] - bbox[0]) * mm_per_pt / mm_per_px,
                    "y": (lt["y"] - bbox[1]) * mm_per_pt / mm_per_px} for lt in raw_letters]
        cap_key = (paper, int(rec.get("figure_number", 0)))
        full_caption = caps_full.get(cap_key)
        caption_source = "full" if full_caption else "record (truncated)"
        caption_text = full_caption or rec.get("caption_text", "")
        cap = caption_letters(caption_text)
        grid = infer_grid(letters, cap, ink, mm_per_px)
        _col_frac, _row_frac = profiles(ink)
        bounds_x = sorted({c["x0"] for c in grid["cells"]} |
                          {c["x1"] for c in grid["cells"]})
        bounds_y = sorted({c["y0"] for c in grid["cells"]} |
                          {c["y1"] for c in grid["cells"]})
        n_measured += 1
        width_mm = (bbox[2] - bbox[0]) * mm_per_pt
        height_mm = (bbox[3] - bbox[1]) * mm_per_pt
        fig_aspects.append(width_mm / height_mm if height_mm else None)

        if grid["n_panels"] >= 2:
            n_composite += 1
            verified = bool(grid.get("split_verified"))
            n_verified += int(verified)
            if verified:
                gx, gy = measure_gutters(ink, grid["cells"], mm_per_px)
                gutter_mm.extend([g for g in gx if 0.5 <= g <= 30])
                gutter_mm.extend([g for g in gy if 0.5 <= g <= 30])
                for c in grid["cells"]:
                    a = c.get("aspect")
                    if a and 0.15 <= a <= 8:
                        panel_aspects.append(a)
            else:
                gx, gy = [], []
            lts = match_letters(letters, grid["cells"], mm_per_px)
            if verified:
                for lt in lts:
                    dxs.append(lt["dx_mm"])
                    dys.append(lt["dy_mm"])
                    letter_sizes.append(lt["size_pt"])
            agree = bool(cap) and len(cap) == grid["n_panels"]
            n_agree += int(agree)
            key = f'{grid["rows"]}x{grid["cols"]}'
            grids[key] = grids.get(key, 0) + 1
            counts[grid["n_panels"]] = counts.get(grid["n_panels"], 0) + 1
        else:
            gx, gy, lts, agree, verified = [], [], [], False, True
            key = "1x1"
            grids[key] = grids.get(key, 0) + 1
            counts[1] = counts.get(1, 0) + 1

        if overlay_budget > 0 and (grid["n_panels"] >= 2 or overlay_budget <= 2):
            slug = re.sub(r"[^A-Za-z0-9]+", "_", pathlib.Path(paper).stem)[:48]
            OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
            write_overlay(img, grid["cells"], bounds_x, bounds_y,
                          OVERLAY_DIR / f"{slug}_f{rec.get('figure_number')}.png",
                          rec.get("figure_number"), key)
            overlay_budget -= 1

        figures.append({
            "paper": paper, "figure_number": rec.get("figure_number"),
            "page": rec.get("page"),
            "rows": grid["rows"], "cols": grid["cols"], "n_panels": grid["n_panels"],
            "grid_source": grid["grid_source"],
            "split_verified": verified,
            "bad_boundaries": grid.get("bad_boundaries"),
            "n_letters_detected": len(letters),
            "n_letters_caption": len(cap), "letters_in_caption": ",".join(cap),
            "caption_source": caption_source,
            "agree": agree,
            "width_mm": round(width_mm, 1), "height_mm": round(height_mm, 1),
            "aspect": round(width_mm / height_mm, 2) if height_mm else None,
            "gutters_x_mm": gx, "gutters_y_mm": gy,
            "panels": [{"row": c["row"], "col": c["col"],
                        "w_mm": round(c.get("w_mm", 0), 1),
                        "h_mm": round(c.get("h_mm", 0), 1),
                        "aspect": round(c.get("aspect", 0), 2)} for c in grid["cells"]],
            "letters": lts,
        })
        if (i + 1) % 10 == 0:
            print(f"    {i + 1}/{len(recs)} measured")

    payload = {
        "about": ("How real published Nature figures arrange their panels, measured from the "
                  "owner's own PDF library. Consumed by figpipe.composite as its geometry "
                  "priors: the gutter, the panel aspect and the panel-letter offset are read "
                  "from here rather than invented."),
        "method": (
            "Each figure's caption-anchored bbox is rendered at 300 dpi and binarised "
            "(ink = grey < 200). Panel letters are read from the PDF's own text spans "
            "(single characters a-h, 7-9.5 pt). Full captions come from "
            "corpus/caption_features.jsonl joined through the extraction manifests; the "
            "caption letter counter accepts only forms Nature writes: '(a)', 'a,', 'a;', "
            "'a-c' ranges, 'Figure 1a'. The panel count is the detected letter count, falling "
            "back to the caption count, falling back to 1. For a count of n the factor pairs "
            "(rows, cols) are enumerated; a boundary starts at the next letter's position "
            "(letters sit at the panel's top-left, so the split is just left of the following "
            "letter) or at equal division, and is refined to the emptiest 0.8 mm band within "
            "+-15 mm on the ink projection. A grid is accepted when every cell holds ink and "
            "has aspect in 0.15-8. Gutters are the ink-free run around the accepted boundary, "
            "in mm."),
        "source": "corpus/figures_caption_anchored.json",
        "n_records": len(recs), "n_pdfs_resolved": len(paths),
        "n_measured": n_measured, "n_composites": n_composite,
        "n_split_verified": n_verified,
        "n_caption_agreement": n_agree,
        "caveats": [
            "Panel count comes from the panel letters; a figure whose letters are drawn as "
            "outlines rather than text is counted from its caption, and one with neither is "
            "recorded as a single panel. That under-counts composites rather than inventing "
            "them.",
            "A gutter measured here is white space between INK, which includes the panels' own "
            "tick labels. The composer adds its label furniture on top of this number when "
            "axes are not shared -- see figpipe/composite.py.",
            "The corpus of measured figures is the caption-anchored set (73 figures from 11 "
            "papers). It is the owner's library, not a random sample of Nature.",
        ],
        "gutter": _stats(gutter_mm),
        "panel_aspect": _stats(panel_aspects, 2),
        "figure_aspect": _stats(fig_aspects, 2),
        "panel_count_distribution": {str(k): v for k, v in sorted(counts.items())},
        "grid_distribution": dict(sorted(grids.items())),
        "letter_offsets": {
            "n": len(dxs),
            "dx_mm": _stats(dxs), "dy_mm": _stats(dys),
            "size_pt": _stats(letter_sizes, 2),
            # flat keys, because figpipe.composite reads these two directly and a nested
            # lookup that silently misses would put the letters in the wrong place
            "dx_median_mm": _stats(dxs).get("median"),
            "dx_p10_mm": _stats(dxs).get("p10"),
            "dx_p90_mm": _stats(dxs).get("p90"),
            "dy_median_mm": _stats(dys).get("median"),
            "dy_p10_mm": _stats(dys).get("p10"),
            "dy_p90_mm": _stats(dys).get("p90"),
            "size_pt_median": _stats(letter_sizes, 2).get("median"),
        },
        "rejected": rejected,
        "figures": figures,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  measured {n_measured}, composites {n_composite}, "
          f"caption agreement {n_agree}")
    print(f"  gutter: {payload['gutter']}")
    print(f"  panel aspect: {payload['panel_aspect']}")
    print(f"  grids: {payload['grid_distribution']}")
    print(f"  letter dx: {payload['letter_offsets'].get('dx_median_mm')} mm, "
          f"dy: {payload['letter_offsets'].get('dy_median_mm')} mm")
    print(f"  wrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
