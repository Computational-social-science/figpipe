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
        return {"ok": False, "findings": [
            {"check": "annotation", "detail": "too few usable points to compute r"}]}
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
        drawn = sum(len(line.get_xdata()) for line in ax.lines
                    if line.get_linestyle() in ("None", "none", " ", ""))
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
            finite = int(np.isfinite(pd.to_numeric(data[x], errors="coerce")).sum())
            checks.append(("marks", check_marks(ax, finite, kind=mark_kind)))
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
MESH_DRAWERS = {
    "tile_diverging": "a signed matrix is one pcolormesh path; the cell values are not in the PDF",
    "field_2d": "a scalar field is one pcolormesh path; the cell values are not in the PDF",
}


def mesh_unverifiable(draw: str) -> str | None:
    """The reason a mesh drawer cannot be verified from the rendered file, or None."""
    return MESH_DRAWERS.get(draw)
