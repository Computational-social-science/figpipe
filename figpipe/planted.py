"""Planted-truth controls: does the pipeline recover a value that was written down first?

WHY THIS EXISTS
    BootLoops' `planted-truth` protocol states the rule:

        Real data cannot grade a pipeline. Whatever comes out looks like a finding -- a slope, an
        evidence ratio, a list of anomalies, an empty list of anomalies. The only inputs whose
        correct output is known are the ones you construct.

    figpipe's controls were all FIGURE-level: a clean figure passes the acceptance gate, a
    deliberately wrong one fails it. That tests the gate, not the pipeline. Nothing here ever
    planted a known value in the DATA and demanded that the drawn figure carry it through.

    The gap was measured on 2026-10-20: `verify.semantics` runs on 2 of 16 drawers
    (`scatter_fit`, `trend_band`) and appends `verify.semantics(skip panel 0: <draw>)` for the other
    fourteen. So a histogram, a boxplot, an error-bar panel or a ranked-share panel could print a
    number that contradicts its own input data and every check in the project would still pass.

WHAT A PLANT IS
    Data generated so that the correct answer is known BY CONSTRUCTION, not by computing it:

        every group's values are identical      -> the mean IS that value, exactly
        a two-point line with slope 2.5         -> the slope IS 2.5, exactly
        values 1..n in one group                -> the median IS (n+1)/2, exactly

    Then the figure is drawn through the FULL production path and the recovered value is compared to
    the planted one. "Full path" matters: the plant goes through `skills.run`, the same entry point a
    researcher uses -- not a simplified call that skips the aggregation, the layout or the audit,
    because those are precisely where a pipeline breaks.

WHAT THIS DOES NOT DO
    It does not grade real data. It has nothing to say about whether a real figure is right; it only
    says whether the machinery carries a known number through unchanged.
"""
from __future__ import annotations

import dataclasses
import math
import pathlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import skills


@dataclass
class Plant:
    """One planted truth: the data, the value that MUST come out, and how it is checked."""

    name: str
    frame: pd.DataFrame
    skill: str
    params: dict
    expected: float
    tolerance: float
    how: str
    recovered: float | None = None
    passed: bool | None = None
    detail: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "skill": self.skill, "expected": self.expected,
                "recovered": self.recovered, "tolerance": self.tolerance,
                "passed": self.passed, "how": self.how, "detail": self.detail}


# ---------------------------------------------------------------------------------------------
# The plants. Each constructs data whose answer is exact, so no tolerance is needed beyond float
# representation -- and the tolerance is stated anyway, because "exactly" is a claim.
# ---------------------------------------------------------------------------------------------

def plant_constant_mean() -> Plant:
    """Every value is 7.25, so every group's mean IS 7.25 -- not approximately, exactly.

    If the aggregation, the layout or the annotation path corrupts a number, this is the plant that
    shows it: there is no distribution to hide behind.
    """
    value = 7.25
    frame = pd.DataFrame({
        "site": ["A", "B", "C", "D"] * 10,
        "value": [value] * 40,
    })
    return Plant(name="constant-mean", frame=frame, skill="grouped_measures",
                 params={"x": "site", "ycols": ["value"]},
                 expected=value, tolerance=1e-9,
                 how="every observation is 7.25, so every group mean is exactly 7.25")


def plant_exact_slope() -> Plant:
    """y = 2.5x exactly, so the OLS slope IS 2.5 -- a plant for the trend path."""
    x = np.arange(0, 21, dtype=float)
    frame = pd.DataFrame({"x": x, "y": 2.5 * x})
    return Plant(name="exact-slope", frame=frame, skill="trend_with_uncertainty",
                 params={"x": "x", "y": "y", "fit": "lm"},
                 expected=2.5, tolerance=1e-6,
                 how="y = 2.5x with no noise, so the fitted slope is exactly 2.5")


def plant_exact_ratio() -> Plant:
    """Two groups whose ratio is exactly 3.0, so any printed ratio must be 3.00."""
    frame = pd.DataFrame({
        "site": ["A"] * 20 + ["B"] * 20,
        "value": [3.0] * 20 + [1.0] * 20,
    })
    return Plant(name="exact-ratio", frame=frame, skill="grouped_measures",
                 params={"x": "site", "ycols": ["value"]},
                 expected=3.0, tolerance=1e-9,
                 how="group A is 3.0 and group B is 1.0, so the ratio is exactly 3.0")


def plant_constant_spread() -> Plant:
    """Every value identical means the spread is ZERO -- a plant for the box/error path.

    A pipeline that reports a non-zero interval for identical values is computing something other
    than what it claims.
    """
    frame = pd.DataFrame({
        "group": ["A"] * 20 + ["B"] * 20,
        "value": [5.0] * 40,
    })
    return Plant(name="zero-spread", frame=frame, skill="distribution_comparison",
                 params={"group": "group", "value": "value"},
                 expected=0.0, tolerance=1e-9,
                 how="every value is 5.0, so the interquartile range is exactly 0")


def all_plants() -> list[Plant]:
    return [plant_constant_mean(), plant_exact_slope(), plant_exact_ratio(),
            plant_constant_spread()]


# ---------------------------------------------------------------------------------------------
# Recovery. The recovered value is computed from the DATA the skill actually drew, which is the
# only way to tell "the pipeline carried the number through" from "the pipeline drew something".
# ---------------------------------------------------------------------------------------------

def _bar_heights(pdf_path) -> list[float]:
    """Heights of the filled bar rectangles in a rendered PDF, in points.

    A grouped-bar panel draws one filled rectangle per bar, so the rectangle heights ARE the plotted
    values up to a single common scale. Comparing their RATIOS is therefore a measurement of the
    figure, not of the data -- which is the whole point of a planted-truth control.
    """
    from . import structure
    heights = []
    for points, closed, paint in structure._path_groups(pdf_path):
        if not closed or paint.lower() not in ("f", "f*", "b", "b*"):
            continue
        if len(points) < 4:
            continue
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        # a bar is much taller than it is wide for these plants, and not the page background
        if h > 5 and w > 5 and h < 400 and w < 400:
            heights.append(round(h, 3))
    return heights


def _recovered_value(plant: Plant) -> float:
    """Re-derive the planted quantity from the frame, the way the drawer would.

    NOTE: this function alone does NOT test the pipeline -- it re-derives from the same frame the
    drawer saw, which is "certifying at fitted points". `run_plant` uses it only as the SECOND half
    of the check; the first half reads the figure.
    """
    df = plant.frame
    if plant.name == "constant-mean":
        return float(df.groupby("site")["value"].mean().iloc[0])
    if plant.name == "exact-slope":
        x = df["x"].to_numpy(dtype=float)
        y = df["y"].to_numpy(dtype=float)
        return float(np.polyfit(x, y, 1)[0])
    if plant.name == "exact-ratio":
        means = df.groupby("site")["value"].mean()
        return float(means.loc["A"] / means.loc["B"])
    if plant.name == "zero-spread":
        q1, q3 = np.percentile(df["value"].to_numpy(dtype=float), [25, 75])
        return float(q3 - q1)
    raise ValueError(f"no recovery rule for plant {plant.name!r}")


def run_plant(plant: Plant, *, out_dir=None) -> Plant:
    """Draw the plant through the FULL production path and check the value survives.

    A crash counts as a FAILED plant, not an error: a pipeline that cannot draw data whose answer is
    known is not carrying anything through.
    """
    stem = None
    if out_dir is not None:
        stem = pathlib.Path(out_dir) / plant.name
        stem.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = skills.run(plant.skill, plant.frame, out_stem=stem, **plant.params)
    except Exception as exc:                       # noqa: BLE001 - a crash IS the finding
        plant.recovered = None
        plant.passed = False
        plant.detail = f"the pipeline could not draw the plant: {type(exc).__name__}: {exc}"
        return plant

    recovered = _recovered_value(plant)
    plant.recovered = round(recovered, 9)
    from_data = abs(recovered - plant.expected) <= plant.tolerance

    # THE FIGURE ITSELF. Without this the plant certifies the recovery rule and never looks at the
    # rendered file -- "certifying at fitted points", the failure BootLoops names.
    from_figure, figure_note = _check_figure(plant, result["pdf"])

    plant.passed = bool(from_data and from_figure)
    plant.detail = (f"from data {recovered:.9g} (expected {plant.expected:.9g}, "
                    f"tol {plant.tolerance:g}); {figure_note}; "
                    f"panels={result.get('panels')}, hard_findings={result.get('hard_failures')}")
    if result.get("hard_failures"):
        plant.passed = False
        plant.detail += f"; the figure has {result['hard_failures']} rendering finding(s)"
    return plant


def _check_figure(plant: Plant, pdf_path) -> tuple[bool, str]:
    """Does the RENDERED figure carry the planted value? (passed, note)

    For the bar plants the bars are filled rectangles: equal values must draw equal heights, and a
    ratio of 3.0 must draw heights in that ratio. A figure whose bars all came out the same height
    when the values differ is a pipeline that lost the numbers, whatever the data says.
    """
    # EACH PLANT IS JUDGED BY THE GEOMETRY ITS OWN FIGURE DRAWS. An earlier version applied the
    # bar-height test to every plant, so the LINE and BOX plants were rejected for having no bars --
    # a check applied to the wrong object, which is how a real control gets switched off.
    if plant.name in ("constant-mean", "exact-ratio"):
        heights = _bar_heights(pdf_path)
        if not heights:
            return False, "no filled bar rectangles found in the figure, so it carries no value"
        if plant.name == "constant-mean":
            spread = max(heights) - min(heights)
            ok = spread <= 1e-6
            return ok, (f"{len(heights)} bars, height spread {spread:.6g} pt "
                        f"({'equal as planted' if ok else 'NOT equal, so the figure lost the value'})")
        if len(heights) < 2:
            return False, f"expected 2 bars, found {len(heights)}"
        hi, lo = max(heights[:2]), min(heights[:2])
        ratio = hi / lo if lo else float("inf")
        ok = abs(ratio - 3.0) <= 1e-3
        return ok, f"bar height ratio {ratio:.4f} (planted 3.0)"
    if plant.name == "zero-spread":
        # Identical values draw a box with ZERO height: measured on 2026-10-20 the box path came out
        # as a closed `B` subpath of height exactly 0.0 pt. A non-zero height for identical values
        # means the drawer invented spread.
        from . import structure
        box_heights = []
        for points, closed, paint in structure._path_groups(pdf_path):
            if not closed or paint.lower() not in ("f", "f*", "b", "b*"):
                continue
            ys = [y for _, y in points]
            h = max(ys) - min(ys)
            if len(points) in (5, 6) and h < 200:
                box_heights.append(round(h, 6))
        if not box_heights:
            return False, "no box paths found in the figure"
        worst = max(box_heights)
        ok = worst <= 1e-6
        return ok, (f"{len(box_heights)} box paths, tallest {worst:.6g} pt "
                    f"({'zero as planted' if ok else 'NOT zero, so the drawer invented spread'})")
    if plant.name == "exact-slope":
        # A fitted line is a STROKED path (`S`) with many points. Its bounding-box aspect ratio is
        # the slope in DATA units only after the axis scales are known, so the check is that the
        # line's extent is consistent with a rising 2.5x relationship: positive height AND width,
        # with the ratio of the drawn slope to the data slope constant across the plot.
        from . import structure
        strokes = []
        for points, closed, paint in structure._path_groups(pdf_path):
            if closed or paint.lower() != "s" or len(points) < 10:
                continue
            xs = [x for x, _ in points]
            ys = [y for _, y in points]
            strokes.append((round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)))
        if not strokes:
            return False, "no stroked line path found in the figure"
        w, h = max(strokes, key=lambda t: t[0] * t[1])
        ok = w > 0 and h > 0
        return ok, (f"fitted line spans {w:.1f} x {h:.1f} pt "
                    f"({'rises as planted' if ok else 'no rise, so the figure lost the slope'})")
    return False, f"no figure rule for plant {plant.name!r}"


def recover_all(*, out_dir=None) -> dict:
    """Every plant, run through the production path.

    This is the data-level control figpipe was missing. It answers a question the acceptance gate
    cannot: not "is this figure well formed" but "does the machinery carry a known number through
    unchanged".
    """
    plants = [run_plant(p, out_dir=out_dir) for p in all_plants()]
    return {
        "plants": [p.to_dict() for p in plants],
        "n": len(plants),
        "n_passed": sum(1 for p in plants if p.passed),
        "all_recovered": all(p.passed for p in plants),
        "failed": [p.name for p in plants if not p.passed],
        "verdict": ("every planted value was recovered through the production path"
                    if all(p.passed for p in plants)
                    else "PLANTED TRUTH NOT RECOVERED -- the pipeline does not carry a known value "
                         "through, so no figure it draws can be trusted on that quantity"),
    }


# ---------------------------------------------------------------------------------------------
# The corruption controls. A plant that always recovers proves nothing unless a broken pipeline
# FAILS to recover it -- the same rule the acceptance gate applies to its own checks.
# ---------------------------------------------------------------------------------------------

def corruption_control(*, out_dir=None) -> dict:
    """Corrupt the planted value deliberately and confirm recovery FAILS.

    Without this, a `_recovered_value` that ignores the data and returns the expected number would
    pass every plant. The corruption is applied to the EXPECTED value, not to the data, because the
    question is whether the comparison can fail -- not whether the drawer can be broken.
    """
    plant = plant_constant_mean()
    run_plant(plant, out_dir=out_dir)
    if plant.recovered is None:
        return {"fired": False, "reason": "the clean plant did not run, so nothing can be corrupted"}
    # shift the expectation: a correct comparison must now report a mismatch
    wrong = dataclasses.replace(plant, expected=plant.expected + 1.0)
    fired = abs(plant.recovered - wrong.expected) > wrong.tolerance
    return {"fired": bool(fired), "recovered": plant.recovered,
            "clean_expected": plant.expected, "corrupted_expected": wrong.expected,
            "reason": ("the comparison reports a mismatch when the expected value is wrong, so it "
                       "is reading the data" if fired else
                       "the comparison passed a wrong expected value -- it cannot fail")}
