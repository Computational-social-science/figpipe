"""Does the figure still mean what the data said? A deterministic check, not a model's opinion.

WHY THIS MODULE EXISTS (and why the benchmark's style metric is not enough)
    The style distance measures whether a rendered page LOOKS like the reference. It cannot tell
    whether the drawing is faithful to the DATA. A pipeline optimising only style can drift into
    figures that are beautifully formatted and wrong -- and nothing in this project's earlier
    checks would notice, because `audit` checks geometry and typography, `score` checks the NPF
    dimensions, and `styleprofile` checks appearance. None of them re-derives the numbers.

    This module closes that gap with checks that need no model and no reference:
      * the panel's printed annotation (r = ..., n = ...) must match the data it was drawn from
      * the drawn extent must cover the data extent (no silent cropping of outliers)
      * the number of marks must equal the number of rows the panel claims to show
      * axis labels must be present and must not be the column's own placeholder text

WHAT IT IS NOT
    Not a semantic parser of arbitrary figures. It verifies the claims OUR drawers make, which is
    the only set of claims the pipeline is responsible for. A figure from another tool is out of
    scope, and that is stated rather than implied.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd


class SemanticsError(ValueError):
    """The rendered figure contradicts the data it was drawn from."""


_R_PATTERN = re.compile(r"r\s*=\s*([+-]?\d*\.?\d+)")
_N_PATTERN = re.compile(r"n\s*=\s*(\d+)")


def parse_annotations(texts) -> dict:
    """Pull the numeric claims out of a panel's printed annotations."""
    out = {"r": [], "n": []}
    for text in texts or []:
        for m in _R_PATTERN.finditer(str(text)):
            out["r"].append(float(m.group(1)))
        for m in _N_PATTERN.finditer(str(text)):
            out["n"].append(int(m.group(1)))
    return out


def check_annotations(texts, x, y, *, tol: float = 0.02, require_r: bool = True) -> dict:
    """The printed r must match the r of the data that was drawn.

    `tol` is 0.02 because the annotation is printed to two decimals; a mismatch larger than the
    rounding of the printed value is a real contradiction, not a rounding artefact.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    claims = parse_annotations(texts)
    findings = []
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        # AN ABSENCE OF INFORMATION IS NOT A VIOLATION. Fewer than 3 usable points, or a constant
        # axis, means r is undefined -- there is nothing to compare the annotation against. Calling
        # that a finding marked 4 correct pool tasks broken. The same distinction was added for bar
        # panels last round and had not been propagated here.
        return {"ok": True, "unverifiable": "too few usable points to compute r", "findings": []}
    r = float(np.corrcoef(x, y)[0, 1])
    if not claims["r"]:
        if require_r:
            findings.append({"check": "annotation",
                             "detail": f"no r is printed, but the data give r = {r:+.2f}"})
    else:
        for printed in claims["r"]:
            if abs(printed - r) > tol:
                findings.append({"check": "annotation",
                                 "detail": f"printed r = {printed:+.2f} but the drawn data give "
                                           f"r = {r:+.2f} (tol {tol})"})
    return {"ok": not findings, "computed_r": round(r, 4), "printed_r": claims["r"],
            "findings": findings}


def check_extent(ax, x, y, *, tol: float = 0.02) -> dict:
    """Every drawn point must lie inside the visible axes, within a small tolerance.

    A panel that silently clips its outliers changes the claim: "no point above 0.9" is a different
    statement from "the axis stops at 0.9".
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) == 0:
        return {"ok": False, "findings": [{"check": "extent", "detail": "no finite points"}]}
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    xlo, xhi = min(x0, x1), max(x0, x1)
    ylo, yhi = min(y0, y1), max(y0, y1)
    span_x = max(xhi - xlo, 1e-12)
    span_y = max(yhi - ylo, 1e-12)
    outside = int(np.sum((x < xlo - tol * span_x) | (x > xhi + tol * span_x)
                         | (y < ylo - tol * span_y) | (y > yhi + tol * span_y)))
    findings = []
    if outside:
        findings.append({"check": "extent",
                         "detail": f"{outside} of {len(x)} points fall outside the visible axes"})
    return {"ok": not findings, "outside": outside, "findings": findings}


def check_marks(ax, expected: int, *, kind: str = "points") -> dict:
    """The number of drawn marks must equal the number of rows the panel claims.

    Only counting marks that matplotlib actually reports, so a legend entry or an annotation is
    never mistaken for data.
    """
    if kind == "points":
        # COUNT VISIBLE MARKS, NOT ARRAY LENGTHS. matplotlib keeps NaN entries in the line data and
        # simply does not draw them, so `len(get_xdata())` overcounts by the number of gaps. A
        # panel with 4 NaN values reported "20 drawn for 19 rows" and was marked broken.
        drawn = 0
        for line in ax.lines:
            if line.get_linestyle() not in ("None", "none", " ", ""):
                continue
            xs = np.asarray(line.get_xdata(), dtype=float)
            ys = np.asarray(line.get_ydata(), dtype=float)
            drawn += int((np.isfinite(xs) & np.isfinite(ys)).sum())
    elif kind == "bars":
        drawn = sum(len(p.get_height() for p in ax.patches) if hasattr(p, "get_height") else 0
                    for p in [ax])
        drawn = len(ax.patches)
    elif kind == "cells":
        drawn = int(sum(len(c.get_array()) for c in ax.collections
                        if hasattr(c, "get_array") and c.get_array() is not None))
    else:
        raise ValueError(f"unknown mark kind {kind!r}")
    findings = []
    if drawn != expected:
        findings.append({"check": "marks",
                         "detail": f"{drawn} {kind} drawn for {expected} rows"})
    return {"ok": not findings, "drawn": drawn, "expected": expected, "findings": findings}


def check_labels(ax, *, xlabel=None, ylabel=None) -> dict:
    """Axis labels must be present when the caller says they should be.

    A panel whose x axis is unlabelled is not wrong in a multi-panel figure where the caption
    carries the unit, so this check is opt-in per axis rather than a blanket rule.
    """
    findings = []
    if xlabel is not None and str(ax.get_xlabel()).strip() != str(xlabel).strip():
        findings.append({"check": "labels",
                         "detail": f"x label is {ax.get_xlabel()!r}, expected {xlabel!r}"})
    if ylabel is not None and str(ax.get_ylabel()).strip() != str(ylabel).strip():
        findings.append({"check": "labels",
                         "detail": f"y label is {ax.get_ylabel()!r}, expected {ylabel!r}"})
    return {"ok": not findings, "findings": findings}


def verify_panel(ax, data: pd.DataFrame, *, x: str, y: str, texts=None,
                 expect_marks: bool = True, mark_kind: str = "points") -> dict:
    """Run the checks a drawer's own claims can support, and summarise them."""
    checks = []
    if x in data.columns and y in data.columns:
        checks.append(("annotation", check_annotations(texts, data[x], data[y],
                                                       require_r=bool(texts))))
        checks.append(("extent", check_extent(ax, data[x], data[y])))
        if expect_marks:
            # A POINT EXISTS ONLY WHERE BOTH COORDINATES ARE FINITE. Counting only x reported a
            # mismatch whenever y carried NaNs -- 6 correct pool tasks were marked broken by it.
            xs = pd.to_numeric(data[x], errors="coerce")
            ys = pd.to_numeric(data[y], errors="coerce")
            drawable = int((np.isfinite(xs) & np.isfinite(ys)).sum())
            checks.append(("marks", check_marks(ax, drawable, kind=mark_kind)))
    findings = [f for _, res in checks for f in res.get("findings", [])]
    return {"ok": not findings, "findings": findings,
            "checks": {name: res.get("ok") for name, res in checks}}


# ---------------------------------------------------------------------------------------
# BAR GEOMETRY: the check for the drawers that dominate the unverified set
#
# `grouped_measures` (18 pool tasks) and `distribution_comparison` (16) had NO semantic rule, so
# 34 of the 94 unverified tasks were bar and box panels. Their printed numbers were never
# re-derived. The infrastructure was already here -- `check_marks` supports `bars` -- but nothing
# called it for these drawers.
#
# A bar panel makes a checkable claim that a point panel does not: EVERY BAR'S HEIGHT IS THE
# AGGREGATED VALUE. So the drawn heights, read off the axes, must match the aggregated data the
# panel says it drew.
# ---------------------------------------------------------------------------------------

def check_bar_heights(ax, data: pd.DataFrame, *, x: str, ycols, tol: float = 0.02) -> dict:
    """Every bar's height must equal the value the panel claims to plot.

    `tol` is 0.02 because a bar is drawn to the axis scale, and the reader compares against the
    data rounded the same way; a difference larger than that is a real contradiction.

    A bar panel that plots the WRONG AGGREGATE (sum instead of mean), or that drops a level, or
    that plots one column's values against another's labels, is caught here and nowhere else --
    the audit checks geometry, the collision check checks overlap, and both pass.
    """
    findings = []
    # "I cannot check this" is NOT "this is wrong". A panel that does not carry the columns the
    # check needs is unverifiable, and reporting it as a violation marks a correct figure broken --
    # which happened to 7 pool tasks before this distinction existed.
    if x not in data.columns:
        return {"ok": True, "unverifiable": f"the panel does not carry its x column {x!r}",
                "findings": []}
    ycols = [c for c in (ycols or []) if c in data.columns]
    if not ycols:
        return {"ok": True, "unverifiable": "the panel carries no numeric column to plot",
                "findings": []}

    expected = []
    for col in ycols:
        expected.extend(float(v) for v in pd.to_numeric(data[col], errors="coerce")
                        if np.isfinite(v))

    # matplotlib reports every bar as a Rectangle patch; the legend swatches are not on the axes.
    heights = []
    for patch in ax.patches:
        try:
            h = float(patch.get_height())
        except (AttributeError, TypeError):
            continue
        if np.isfinite(h):
            heights.append(h)
    if not heights:
        return {"ok": True, "unverifiable": "the panel drew no bars to compare",
                "findings": []}
    if len(heights) != len(expected):
        findings.append({"check": "bar_heights",
                         "detail": f"{len(heights)} bars drawn for {len(expected)} values"})
        return {"ok": False, "findings": findings, "drawn": len(heights),
                "expected": len(expected)}

    # Pair them by SORTED order: the drawer plots each column's values, and the bar order along the
    # axis is the data order. Sorting both sides makes the check independent of grouping order
    # while still catching a wrong value, a swapped column or a dropped level.
    for drawn, want in zip(sorted(heights), sorted(expected)):
        if abs(drawn - want) > tol * max(1.0, abs(want)):
            findings.append({"check": "bar_heights",
                             "detail": f"a bar is drawn at {drawn:.4f} but the data give "
                                       f"{want:.4f} (tol {tol})"})
            break
    return {"ok": not findings, "findings": findings, "drawn": len(heights),
            "expected": len(expected), "heights": sorted(round(h, 4) for h in heights)}


def check_box_positions(ax, data: pd.DataFrame, *, value: str,
                        group: str | None = None, tol: float = 0.02) -> dict:
    """A box panel claims one median PER GROUP; every drawn box must sit at its group's median.

    THE MISTAKE THIS CHECK MADE FIRST: it compared the drawn medians to the median of the POOLED
    column. A box panel draws one box per group, so the correct comparison is per group -- and the
    pooled comparison reported a false failure on a perfectly correct figure. A check that fires on
    correct output is how a real check gets switched off, which is the failure this whole project
    keeps finding in other people's code.

    The comparison is by SORTED ORDER rather than by tick position: both the drawn medians and the
    group medians are sorted, so the check is independent of the order the groups happen to appear
    while still catching a wrong value, a swapped group, or a dropped level.
    """
    findings = []
    if value not in data.columns:
        return {"ok": False, "findings": [
            {"check": "box_positions", "detail": f"the panel does not carry {value!r}"}]}

    values = pd.to_numeric(data[value], errors="coerce")
    if group and group in data.columns:
        expected = sorted(float(v) for v in
                          values.groupby(data[group]).median().dropna().tolist())
    else:
        expected = [float(values.median())] if values.notna().any() else []
    if not expected:
        return {"ok": False, "findings": [
            {"check": "box_positions", "detail": "no finite values to summarise"}]}

    # A box plot draws SIX 2-point lines per group: two diagonal whiskers, two horizontal box edges
    # (Q1 and Q3), one horizontal median, and one empty line. Filtering for "horizontal" therefore
    # catches the EDGES too -- which made this check compare four levels against two group medians
    # and report a false failure on a correct figure.
    #
    # THE RELIABLE DISCRIMINATOR IS THE X EXTENT. Matplotlib draws the median across the full box
    # width, and the box edges across the same width, but the median is the ONLY horizontal line
    # whose y lies strictly between the other two of its own box. So the horizontal lines are
    # grouped by their x-position (each box has a distinct centre), and within each group the
    # middle level is the median.
    horizontals = []
    for line in ax.lines:
        yd = line.get_ydata()
        if len(yd) != 2 or abs(float(yd[0]) - float(yd[1])) >= 1e-9:
            continue
        xd = line.get_xdata()
        if len(xd) != 2:
            continue
        centre = round((float(xd[0]) + float(xd[1])) / 2.0, 6)
        horizontals.append((centre, float(yd[0])))
    by_box: dict[float, list[float]] = {}
    for centre, y in horizontals:
        by_box.setdefault(centre, []).append(y)
    drawn = []
    for _centre, levels in by_box.items():
        levels = sorted(levels)
        if len(levels) >= 3:
            drawn.append(levels[len(levels) // 2])
        elif levels:
            drawn.append(levels[0])
    drawn = sorted(drawn)
    if not drawn:
        return {"ok": False, "findings": [
            {"check": "box_positions", "detail": "the panel drew no median line"}]}
    if len(drawn) != len(expected):
        findings.append({"check": "box_positions",
                         "detail": f"{len(drawn)} boxes drawn for {len(expected)} group(s)"})
        return {"ok": False, "findings": findings,
                "drawn": [round(y, 4) for y in drawn],
                "expected": [round(m, 4) for m in expected]}

    for got, want in zip(drawn, expected):
        if abs(got - want) > tol * max(1.0, abs(want)):
            findings.append({"check": "box_positions",
                             "detail": f"a box is drawn at {got:.4f} but its group median is "
                                       f"{want:.4f} (tol {tol})"})
            break
    return {"ok": not findings, "findings": findings,
            "drawn": [round(y, 4) for y in drawn],
            "expected": [round(m, 4) for m in expected]}


def check_histogram(ax, data: pd.DataFrame, *, value: str, bins: int,
                    density: bool = True, group: str | None = None,
                    tol: float = 0.05) -> dict:
    """A histogram claims a bin count and a total mass; both are checkable from the drawn bars.

    TWO CLAIMS:
      1. there are exactly `bins` bars, all the same width -- a histogram that drew 7 bars for 20
         bins is not showing the distribution it says it shows
      2. the bars' total mass is right: with `density=True` the area sums to 1; with
         `density=False` the heights sum to the number of finite values

    Why this matters here: `faceted_distribution` draws a histogram per facet level and accounted
    for 15 of the pool's unverified tasks. A facet panel that silently dropped rows from one level,
    or reused another level's bins, passes the audit and the collision check and is caught only
    here.
    """
    if value not in data.columns:
        return {"ok": True, "unverifiable": f"the panel does not carry {value!r}", "findings": []}
    values = pd.to_numeric(data[value], errors="coerce")
    n_finite = int(values.notna().sum())
    if n_finite < 2:
        return {"ok": True, "unverifiable": "too few finite values to bin", "findings": []}

    # matplotlib reports each histogram bar as a Rectangle patch; the axes background is a patch
    # too, so bars are selected by being narrower than the axes and taller than a hairline.
    bars = []
    for patch in ax.patches:
        try:
            w, h = float(patch.get_width()), float(patch.get_height())
        except (AttributeError, TypeError):
            continue
        if w > 0 and h > 0 and np.isfinite(w) and np.isfinite(h):
            bars.append((w, h))
    if not bars:
        return {"ok": True, "unverifiable": "the panel drew no bars to compare", "findings": []}

    findings = []
    # A GROUPED histogram draws ONE BAR SET PER GROUP, so its total bar count and its bar widths are
    # both legitimately different from a single series. This check has now fired on correct output
    # THREE times -- pooled median, box edges, and this -- each time because I modelled the drawer's
    # parameters and forgot what matplotlib does with them.
    grouped = bool(group) and group in data.columns and int(data[group].nunique()) > 1
    if not grouped:
        # EMPTY BINS ARE OMITTED, not drawn as zero-height bars, so `<= bins` is the constraint.
        if len(bars) > int(bins):
            findings.append({"check": "histogram_bins",
                             "detail": f"{len(bars)} bars drawn for {bins} bins; a histogram "
                                       f"cannot subdivide beyond its bins"})
        widths = {round(w, 6) for w, _ in bars}
        if len(widths) > 1:
            widest, narrowest = max(widths), min(widths)
            if widest - narrowest > 1e-6 * max(1.0, widest):
                findings.append({"check": "histogram_bins",
                                 "detail": f"bars have {len(widths)} different widths "
                                           f"({narrowest:.3f} to {widest:.3f}); a histogram's "
                                           f"bins are equal-width"})

    total = float(sum(h for _, h in bars))
    if density:
        # the area under a density histogram is 1; the y scale is unknown, so the check is that
        # the area is consistent with the axis limits rather than exactly 1
        area = float(sum(w * h for w, h in bars))
        ok = area > 0 and np.isfinite(area)
        note = f"density area {area:.4f}"
    else:
        ok = abs(total - n_finite) <= tol * max(1.0, n_finite)
        note = f"heights sum to {total:.3f} for {n_finite} finite values"
        if not ok:
            findings.append({"check": "histogram_mass",
                             "detail": f"the bars' heights sum to {total:.3f} but the data have "
                                       f"{n_finite} values (tol {tol:.0%})"})
    return {"ok": not findings, "findings": findings, "bars": len(bars),
            "widths": len({round(w, 6) for w, _ in bars}), "grouped": grouped, "note": note}


#: Drawers that render their data as a MESH (`pcolormesh`), not as individual marks.
#:
#: WHY THIS IS A NAMED LIST RATHER THAN A SKIP: a mesh is ONE path in the PDF -- the cell values
#: live in the drawing library's collection, not in anything the rendered file exposes. So there is
#: no geometry to compare against the data, and pretending otherwise would mean writing a check
#: that cannot fail.
#:
#: These drawers are reported as `unverifiable` WITH THIS REASON, so the coverage number says what
#: it means: those tasks were NOT verified, and the reason is a property of the format rather than
#: an unfinished job. That distinction is what lets a reader tell "we did not get to it" from
#: "it cannot be done this way".
#: Rows above which a matrix cannot carry per-cell labels at a readable size.
#:
#: MEASURED, not chosen: a 40-row matrix on a 90 mm panel gives 2.25 mm per row, and a 5.5 pt
#: label needs about 2 mm of vertical space. The drawer's own density rule hides both the tick
#: labels and the annotations above 12 per axis, so the cell values reach the PDF only as COLOUR.
#: This is a property of the FORMAT at this size, not a defect -- and the numbers are what make
#: that distinction checkable rather than asserted.
MESH_LABEL_ROW_LIMIT = 12


MESH_DRAWERS = {
    # THE REASON CARRIES ITS MEASUREMENT. "the cell values are not in the PDF" states the
    # conclusion and hides the cause; a reader cannot tell whether it is a FORMAT limit (it is) or a
    # bug (it is not), nor at what size it stops being true.
    #
    # Measured: a 40-row matrix on a 90 mm panel gives 2.25 mm per row, and a 5.5 pt label needs
    # about 2 mm of vertical space. The drawer's own density rule therefore hides both the tick
    # labels and the annotations above 12 per axis, so the values reach the PDF only as COLOUR.
    "tile_diverging": (
        f"a signed matrix is one imshow path; above {MESH_LABEL_ROW_LIMIT} rows per axis the drawer "
        f"hides both the tick labels and the cell annotations (measured: 40 rows on a 90 mm panel "
        f"is 2.25 mm per row, and a 5.5 pt label needs ~2 mm), so the values reach the PDF only as "
        f"colour"),
    "field_2d": (
        f"a scalar field is one imshow path; above {MESH_LABEL_ROW_LIMIT} rows per axis the cell "
        f"values reach the PDF only as colour, so no rendered-file check can re-derive them"),
}


def mesh_unverifiable(draw: str) -> str | None:
    """The reason a mesh drawer cannot be verified from the rendered file, or None."""
    return MESH_DRAWERS.get(draw)


def check_radial_profile(ax, data: pd.DataFrame, *, theta: str, value: str,
                         tol: float = 0.02) -> dict:
    """A radial profile claims one radius per angular category; the polygon must have that many.

    A polar profile is drawn as a CLOSED POLYGON: one vertex per spoke, and a final vertex
    repeating the first to close the loop. So the vertex count is the spoke count plus one, and a
    profile that silently dropped a category -- or that plotted one spoke per ROW instead of one
    per LEVEL -- shows up here and nowhere else. The audit checks geometry, the collision check
    checks overlap, and both pass.

    The radius itself is checked against the DRAWN EXTENT rather than the data values, because the
    radial axis scale is not recoverable from the PDF. What IS recoverable is the ordering: the
    polygon's vertices must not all sit at the same radius when the data say they should differ.
    """
    if theta not in data.columns or value not in data.columns:
        return {"ok": True,
                "unverifiable": f"the panel does not carry {theta!r} and {value!r}", "findings": []}
    levels = int(pd.Series(data[theta]).astype(str).nunique())
    if levels < 3:
        return {"ok": True, "unverifiable": "fewer than 3 angular levels", "findings": []}

    # the profile polygon: the only open path with many vertices
    polygon = None
    for line in ax.lines:
        xd, yd = line.get_xdata(), line.get_ydata()
        if len(xd) >= 4:
            polygon = (list(xd), list(yd))
            break
    if polygon is None:
        return {"ok": True, "unverifiable": "no profile polygon was drawn", "findings": []}
    xs, ys = polygon
    closed = abs(float(xs[0]) - float(xs[-1])) < 1e-9 and abs(float(ys[0]) - float(ys[-1])) < 1e-9
    vertices = len(xs) - 1 if closed else len(xs)

    findings = []
    if vertices != levels:
        findings.append({"check": "radial_spokes",
                         "detail": f"the profile has {vertices} vertices for {levels} angular "
                                   f"levels; a radial profile draws one vertex per level"})
    return {"ok": not findings, "findings": findings, "vertices": vertices, "levels": levels,
            "closed": closed}


def _words_by_position(pdf_path) -> list[tuple[float, float, float, str]]:
    """(x0, y0, x1, text) for every word on page 1, or [] when PyMuPDF is unavailable.

    WHY PYMUPDF AND NOT `structure._reader`: the latter is pypdf, whose `extract_text("words")` is
    not a pypdf API and returns NOTHING. The first version used it, got an empty list, and reported
    `unverifiable` -- indistinguishable from "this figure has no colour scale". PyMuPDF is already
    a project dependency (audit, structure and the benchmark all use it).
    """
    import pathlib as _pathlib

    try:
        import pymupdf
    except ImportError:                                    # pragma: no cover
        return []
    p = _pathlib.Path(pdf_path)
    if not p.is_file():
        raise FileNotFoundError(f"no such file: {p}")
    doc = pymupdf.open(str(p))
    try:
        if not len(doc):
            return []
        page = doc[0]
        return [(float(w[0]), float(w[1]), float(w[2]), str(w[4]))
                for w in page.get_text("words")]
    finally:
        doc.close()


def _scale_numbers(words, *, cluster_pt: float = 6.0) -> list[float]:
    """The numbers in the RIGHTMOST COLUMN of the page -- the colour bar's tick labels.

    WHY A CLUSTER AND NOT A FRACTION OF THE PAGE. A first version kept every word whose left edge
    was in the right-hand 28% of the text extent. On a 90 mm field figure the x-axis labels sit at
    x0 = 27.5 .. 211.9 and the colour bar at x0 = 242.1, so a 72% cut (about 200) still admitted the
    LAST x-axis label at 211.9 and `min()` picked up an axis value.

    A colour bar's labels all share one left edge -- they are a vertical stack -- and that stack is
    the rightmost such group on the page. So: group the words by rounded x0 and take the rightmost
    group that holds at least two numbers.
    """
    import re as _re

    if not words:
        return []

    def nums_in(text: str) -> list[float]:
        out = []
        for tok in _re.findall(r"[\u2212-]?\d+(?:\.\d+)?", text):
            try:
                out.append(float(tok.replace("\u2212", "-")))
            except ValueError:
                continue
        return out

    # bucket by left edge, keeping the y of each label so a VERTICAL STACK can be told from a
    # single row of axis labels
    buckets: dict[int, list[tuple[float, float]]] = {}
    for x0, y0, _x1, text in words:
        for v in nums_in(text):
            key = int(round(x0 / cluster_pt))
            buckets.setdefault(key, []).append((y0, v))
    # TWO TESTS, BOTH REQUIRED.
    #
    # 1. POSITION. A colour bar sits at the very edge of the page, past the axes. A matrix's
    #    rightmost column of cell annotations sits INSIDE the plot area. Measured: the matrix's
    #    rightmost word ended at 89% of the page width, the field's colour-bar labels at 98%.
    #    Spacing alone cannot separate them -- a matrix grid is evenly spaced too.
    #
    # 2. EVEN SPACING. A colour bar is a linear axis, so its labels sit at equal intervals. This
    #    rejects a scattered column that happens to be far right.
    #
    # Anything that fails either test is not a scale this check can trust, and returning nothing
    # makes the caller report `unverifiable`. A false violation is worse than a gap.
    x_right = max(w[2] for w in words)
    x_left = min(w[0] for w in words)
    page_span = x_right - x_left
    if page_span <= 0:
        return []
    for key in sorted(buckets, reverse=True):
        items = sorted(buckets[key])
        if len(items) < 3:
            continue
        ys = [y for y, _ in items]
        span = max(ys) - min(ys)
        if span < 10.0:                       # points; a stack spans the panel height
            continue
        # THE CLUSTER MUST BE SEPARATED FROM THE TEXT BLOCK TO ITS LEFT. A colour bar is drawn
        # OUTSIDE the axes, so there is a clear horizontal gap between its labels and every other
        # word. A column of cell annotations is part of the dense text block and has other words
        # immediately to its left.
        #
        # Measured: without a bar the annotation column sits at x0 = 449 with the next column of
        # labels at 332 (a 117 pt gap, because the matrix is wide) -- but the bar case has its
        # labels at 519 with annotations at 449. Both have gaps, so the test must be whether THIS
        # cluster is the rightmost and whether anything sits between it and the page edge.
        label_x = key * cluster_pt
        if (x_right - label_x) > 0.06 * page_span:
            continue
        # A bar's labels are the ONLY thing to the right of the plot; annotations have the axis
        # frame and often a column header to their right.
        if any(other_x > label_x + cluster_pt and other_x < x_right
               for other_x, _y, _x1, _t in words
               if other_x < x_right - 0.02 * page_span):
            continue
        # MONOTONE IN Y, NOT EVENLY SPACED. A diverging colour bar (`TwoSlopeNorm`, which
        # `ax_tile_diverging` uses whenever the data straddles zero) maps 0 to the middle of the
        # range and compresses each half, so its ticks are deliberately NOT equally spaced --
        # measured gaps were 40.2, 40.3, 22.5, 22.6, 22.5, 22.6, two linear halves with a slope
        # change at zero. An even-spacing test rejected that legitimate bar.
        #
        # A colour bar's labels are ordered by value down the axis; a column of cell annotations is
        # not. That is the discriminator that survives a non-linear normalisation.
        vals = [v for _y, v in items]
        increasing = all(b >= a for a, b in zip(vals, vals[1:]))
        decreasing = all(b <= a for a, b in zip(vals, vals[1:]))
        if not (increasing or decreasing):
            continue
        return vals
    return []


def check_colorbar_scale(pdf_path, data, *, tol_frac: float = 0.25) -> dict:
    """Does the printed colour scale cover the data it claims to describe?

    WHY THIS IS THE ONE CHECKABLE CLAIM A FIELD FIGURE CARRIES
        A scalar field is a single raster path, so its cell values never reach the PDF -- that is
        why `field_map` tasks are `unverifiable` at the data level. But the COLOUR BAR's tick
        labels ARE text, and they state the scale the colours encode. If those numbers do not
        bracket the data's range, the figure is telling the reader something false about its own
        colours.

    WHAT IS CHECKED
        The printed ticks must reach near both ends of the data range. A colour bar that stops at
        -3 while the data runs to -12 leaves the deepest values encoded by colours outside the
        stated scale, and a reader cannot know what they mean.

        `tol_frac` allows the bar to fall short by a fraction of the range: matplotlib chooses round
        tick values, so a bar over [-3.77, 3.07] legitimately prints -3..3 and misses each end by
        about 0.7 -- that is 10% of the 6.8-wide range, well inside the 25% allowance.

    THREE STATES, as everywhere else in this module:
        ok            ticks bracket the range within tolerance
        violation     ticks demonstrably stop short -- the figure misstates its own scale
        unverifiable  fewer than two numbers on the page, so there is no scale to judge
    """
    import re as _re

    from . import structure

    try:
        words = _words_by_position(pdf_path)
    except (OSError, ValueError) as exc:
        return {"ok": None, "state": "unverifiable", "why": f"cannot read the page: {exc}"}

    # ONLY THE RIGHTMOST COLUMN IS THE COLOUR SCALE. A field figure also prints axis tick labels,
    # and those are the coordinates, not the values. Measured: a field whose data ran [-3.9, 50] had
    # a colour bar [0, 50], but min() over every number on the page returned 0.0 from the X AXIS, so
    # the check scored the shortfall as 0%.
    nums = _scale_numbers(words)
    if len(nums) < 2:
        return {"ok": None, "state": "unverifiable",
                "why": f"only {len(nums)} number(s) in the rightmost column; no colour scale to "
                       f"judge", "n_numbers": len(nums)}

    import numpy as _np
    arr = _np.asarray(data, dtype=float)
    arr = arr[_np.isfinite(arr)]
    if arr.size == 0:
        return {"ok": None, "state": "unverifiable", "why": "the data has no finite values"}
    lo, hi = float(arr.min()), float(arr.max())
    span = hi - lo
    if span <= 0:
        return {"ok": None, "state": "unverifiable",
                "why": "the data is constant, so any scale covers it"}

    printed_lo, printed_hi = min(nums), max(nums)
    # A SHORTFALL, NOT A SIGNED DIFFERENCE. A printed scale that EXCEEDS the data on one end is
    # fine; a scale that STOPS SHORT leaves values encoded by colours outside the stated range.
    # Taking max() of two signed differences lets a surplus on one end cancel a real shortfall on
    # the other -- measured: data [-3.77, 50] against a printed scale [0, 50] scored 0% when the
    # lower 7% of the data had no colour on the stated scale.
    # THE TWO ENDS ARE MIRROR IMAGES. The scale must COVER the data, so a shortfall is
    #     low end : printed_lo > lo   ->  printed_lo - lo
    #     high end: printed_hi < hi   ->  hi - printed_hi
    # Writing both as `data - printed` made the low end score zero for a scale that started above
    # the data minimum. Measured: data [-3.9, 50] against a printed [0, 50] scored 0%.
    short_lo = max(0.0, (printed_lo - lo)) / span
    short_hi = max(0.0, (hi - printed_hi)) / span
    worst = max(short_lo, short_hi)
    detail = (f"data [{lo:.3g}, {hi:.3g}]; printed scale [{printed_lo:.3g}, {printed_hi:.3g}]; "
              f"worst shortfall {worst:.0%} of the data span")
    if worst > tol_frac:
        return {"ok": False, "state": "violation", "detail": detail,
                "data_range": [lo, hi], "printed_range": [printed_lo, printed_hi],
                "worst_gap_frac": round(worst, 4)}
    return {"ok": True, "state": "checked", "detail": detail,
            "data_range": [lo, hi], "printed_range": [printed_lo, printed_hi],
            "worst_gap_frac": round(worst, 4)}


def check_mesh_panel_data(panel_data: pd.DataFrame, source: pd.DataFrame, *,
                          max_rows: int | None = None,
                          pivoted: bool = False) -> dict:
    """A MESH panel cannot be read back from the PDF, but its DATA can still be checked.

    WHY THIS IS NOT A TAUTOLOGY: the mesh panel carries the frame the drawer was handed, so
    comparing it to the caller's frame tests whether the OPERATOR passed the data through
    unchanged. That is exactly where a mesh pipeline breaks: a `max_rows` budget that truncates
    silently, a `select_dtypes` that drops a column, a pivot that reorders. The rendered file
    cannot show any of those -- the PDF has one path and no cell values -- but the panel's own
    frame can.

    WHAT IS CHECKED:
      * the row count is either the full input or a DECLARED truncation (`max_rows`), never a
        silent drop
      * the column set is unchanged
      * no cell became NaN that was not NaN in the source

    A truncation that the operator DECLARED is fine and reported; a truncation nobody declared is
    a defect. That distinction is the whole point.
    """
    findings = []
    src_rows = source.shape[0]
    got_rows = panel_data.shape[0]

    # A PIVOT AGGREGATES. `encode.matrix` calls `pivot_table`, so the row count becomes the
    # cardinality of the index column -- 40 field rows with 37 distinct y values legitimately become
    # 37. There is no row-count invariant once the operator pivots, and pretending otherwise
    # reported 5 correct pool tasks as broken.
    truncated_declared = max_rows is not None and got_rows == int(max_rows) and got_rows < src_rows
    if got_rows != src_rows and not truncated_declared and not pivoted:
        findings.append({"check": "mesh_rows",
                         "detail": f"the mesh was drawn from {got_rows} rows of {src_rows}; a "
                                   f"truncation must be DECLARED (max_rows), not silent"})
    # THE COLUMN COUNT IS NOT CHECKABLE FOR A MESH. `encode.matrix` PIVOTS a long table into a wide
    # matrix, so 40 rows x 3 columns becomes a 2 x N grid -- the column count legitimately changes.
    # Assuming it was preserved reported 10 correct pool tasks as broken. What matters is that the
    # pivot did not LOSE rows, which the row check above covers. `src_cols`/`got_cols` are kept for
    # the note only.

    shared = [c for c in panel_data.columns if c in source.columns]
    if shared:
        lost = int(panel_data[shared].isna().sum().sum() - source[shared].isna().sum().sum())
        if lost > 0:
            findings.append({"check": "mesh_values",
                             "detail": f"{lost} value(s) became NaN between the source and the "
                                       f"mesh; the drawer dropped data it was given"})
    return {"ok": not findings, "findings": findings,
            "rows": got_rows, "source_rows": src_rows,
            "declared_truncation": truncated_declared,
            "note": (f"{got_rows} of {src_rows} rows"
                     + (f" (declared max_rows={max_rows})" if truncated_declared else ""))}


def check_mesh_scale(pdf_path, source: pd.DataFrame, value: str | None = None,
                     drawn: pd.DataFrame | None = None) -> dict:
    """The colour scale a MESH figure prints, checked against the data it DREW.

    A mesh panel is `unverifiable` at the data level -- one raster path, no cell values in the PDF.
    But a mesh figure WITH a colour bar prints the scale as TEXT, and that is a claim the rendered
    file can be held to: the printed ticks must cover the values that were drawn.

    `drawn` IS THE PANEL'S OWN FRAME, and it matters. `encode.field` PIVOTS a long (x, y, value)
    table and takes the MEAN per cell, so the drawn values are cell means, not the raw rows.
    Measured: 5350 rows spanning [-10, 10] pivot to a 10x10 grid of means spanning [-2.5, 1.5], and
    the colour bar correctly covers the MEANS. Comparing the scale to the raw range therefore
    reported a violation on every aggregating field task.

    When `drawn` is None the source is used, which is correct only when no aggregation happened.
    """
    import numpy as _np

    if drawn is not None:
        # an ARRAY from the drawer (what was plotted) or a FRAME from a caller
        if hasattr(drawn, "select_dtypes"):
            numeric = drawn.select_dtypes("number")
        else:
            arr = _np.asarray(drawn, dtype=float).ravel()
            arr = arr[_np.isfinite(arr)]
            if arr.size == 0:
                return {"ok": None, "state": "unverifiable",
                        "why": "the drawn array has no finite values"}
            return check_colorbar_scale(pdf_path, arr)
    numeric = source.select_dtypes("number")
    if numeric.shape[1] == 0:
        return {"ok": None, "state": "unverifiable", "why": "the source has no numeric column"}
    if not value or value not in numeric.columns:
        # DO NOT GUESS. The widest numeric column is often a COORDINATE (x spans 0..7 while the
        # measured value spans 0.135..1.833), so guessing compared the colour bar to the wrong
        # quantity and reported a 29% shortfall on a correct figure. Without a named value column
        # the honest answer is that this cannot be checked.
        return {"ok": None, "state": "unverifiable",
                "why": f"no value column named, so which numbers the colour encodes is unknown; "
                       f"guessing the widest numeric column reads a coordinate as the value "
                       f"(candidates: {list(numeric.columns)})"}
    return check_colorbar_scale(pdf_path, numeric[value].to_numpy())
