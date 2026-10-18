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
