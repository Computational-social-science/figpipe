"""Semantic checks for BAR and BOX panels -- 34 of the 94 previously unverified tasks.

WHY THIS TEST
    `verify.semantics` ran on 2 of 16 drawers (`scatter_fit`, `trend_band`). The pool measured
    94 of 139 tasks (68%) as `skipped`: their printed numbers were never re-derived, so a pass on
    them was a statement about geometry, not about correctness.

    The two biggest contributors were `grouped_measures` (18 tasks) and `distribution_comparison`
    (16). Both make a claim a point panel does not: EVERY BAR'S HEIGHT IS THE AGGREGATED VALUE, and
    EVERY BOX SITS AT ITS GROUP'S MEDIAN. Both are checkable from the drawn axes.

TWO BUGS IN THE CHECKS THEMSELVES, both caught by running them on correct figures:

  1. The box check compared drawn medians to the median of the POOLED column. A box panel draws one
     box per GROUP, so it reported a false failure on a correct figure -- and a check that fires on
     correct output is how a real check gets switched off.

  2. Filtering for "horizontal 2-point lines" caught the box EDGES (Q1 and Q3) as well as the
     median, so 4 levels were compared against 2 group medians. The reliable discriminator is the
     line's x-centre: each box has a distinct centre, and within a box the MIDDLE level is the
     median.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import semantics, skills  # noqa: E402


@pytest.fixture()
def bar_axes():
    fig, ax = plt.subplots()
    ax.bar(["A", "B", "C"], [10.0, 20.0, 30.0])
    yield ax
    plt.close(fig)


@pytest.fixture()
def box_axes():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"g": ["A"] * 20 + ["B"] * 20,
                       "v": list(rng.random(20)) + list(rng.random(20) + 2)})
    fig, ax = plt.subplots()
    ax.boxplot([df[df.g == "A"]["v"], df[df.g == "B"]["v"]])
    yield ax, df
    plt.close(fig)


# ---------------------------------------------------------------------------------------
# BAR HEIGHTS
# ---------------------------------------------------------------------------------------

def test_a_correct_bar_panel_passes(bar_axes):
    data = pd.DataFrame({"x": ["A", "B", "C"], "v": [10.0, 20.0, 30.0]})
    assert semantics.check_bar_heights(bar_axes, data, x="x", ycols=["v"])["ok"] is True


def test_a_wrong_bar_value_is_caught(bar_axes):
    """NEGATIVE CONTROL: a check that cannot fail certifies nothing."""
    data = pd.DataFrame({"x": ["A", "B", "C"], "v": [10.0, 99.0, 30.0]})
    res = semantics.check_bar_heights(bar_axes, data, x="x", ycols=["v"])
    assert res["ok"] is False
    assert res["findings"]


def test_a_dropped_bar_is_caught(bar_axes):
    """A panel that silently drops a level changes what the figure claims."""
    data = pd.DataFrame({"x": ["A", "B"], "v": [10.0, 20.0]})
    res = semantics.check_bar_heights(bar_axes, data, x="x", ycols=["v"])
    assert res["ok"] is False
    assert "bars drawn" in res["findings"][0]["detail"]


def test_a_wrong_aggregate_is_caught(bar_axes):
    """sum instead of mean is the classic wrong-aggregate mistake."""
    data = pd.DataFrame({"x": ["A", "B", "C"], "v": [100.0, 200.0, 300.0]})
    assert semantics.check_bar_heights(bar_axes, data, x="x", ycols=["v"])["ok"] is False


# ---------------------------------------------------------------------------------------
# BOX MEDIANS
# ---------------------------------------------------------------------------------------

def test_a_correct_box_panel_passes(box_axes):
    """THE BUG: this used to FAIL on a correct figure, because the pooled median was used."""
    ax, df = box_axes
    res = semantics.check_box_positions(ax, df, value="v", group="g")
    assert res["ok"] is True, res["findings"]
    assert len(res["drawn"]) == 2


def test_a_shifted_group_median_is_caught(box_axes):
    ax, df = box_axes
    bad = df.copy()
    bad.loc[bad.g == "A", "v"] += 5.0
    res = semantics.check_box_positions(ax, bad, value="v", group="g")
    assert res["ok"] is False
    assert "median" in res["findings"][0]["detail"]


def test_the_box_check_uses_per_group_medians_not_the_pooled_one(box_axes):
    """Structural: the pooled median is a different number, so using it would fail here."""
    ax, df = box_axes
    pooled = float(df["v"].median())
    per_group = [float(x) for x in df.groupby("g")["v"].median()]
    assert pooled not in per_group, "the fixture does not distinguish pooled from per-group"


# ---------------------------------------------------------------------------------------
# THE DRAWERS ARE NOW CHECKED, NOT SKIPPED
# ---------------------------------------------------------------------------------------

def test_grouped_measures_is_now_semantically_checked():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"site": ["A", "B", "C", "D"] * 10,
                       "m1": rng.random(40), "m2": rng.random(40)})
    res = skills.run("grouped_measures", df, out_stem=None, x="site", ycols=["m1", "m2"])
    skips = [t for t in res["trace"] if "semantics(skip" in t]
    assert not skips, f"grouped_bars is still skipped: {skips}"
    assert res["hard_failures"] == 0, res["findings"]


def test_distribution_comparison_is_now_semantically_checked():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"g": ["A"] * 20 + ["B"] * 20,
                       "v": list(rng.random(20)) + list(rng.random(20) + 2)})
    res = skills.run("distribution_comparison", df, out_stem=None, group="g", value="v")
    skips = [t for t in res["trace"] if "semantics(skip" in t]
    assert not skips, f"boxplot is still skipped: {skips}"
    assert res["hard_failures"] == 0, res["findings"]


def test_a_panel_without_the_columns_is_UNVERIFIABLE_not_wrong(bar_axes):
    """THE BUG: "I cannot check this" was reported as "this figure is WRONG".

    A `composite_groups` sub-panel does not always carry `ycols`, and the first version of
    `check_bar_heights` returned a hard finding for that -- marking 7 correct pool tasks broken.
    Reporting a defect where there is only an absence of information is the worst confusion a
    verification layer can make, because it teaches the operator to ignore the check.
    """
    data = pd.DataFrame({"x": ["A", "B", "C"], "v": [10.0, 20.0, 30.0]})
    res = semantics.check_bar_heights(bar_axes, data, x="x", ycols=[])
    assert res["ok"] is True, "an unverifiable panel must not be reported as a violation"
    assert res.get("unverifiable"), "the reason must be stated"
    assert not res["findings"]

    res2 = semantics.check_bar_heights(bar_axes, data, x="missing", ycols=["v"])
    assert res2["ok"] is True
    assert res2.get("unverifiable")


def test_a_wrong_value_is_still_a_violation(bar_axes):
    """NEGATIVE CONTROL: the unverifiable state must not swallow real violations."""
    data = pd.DataFrame({"x": ["A", "B", "C"], "v": [10.0, 99.0, 30.0]})
    res = semantics.check_bar_heights(bar_axes, data, x="x", ycols=["v"])
    assert res["ok"] is False
    assert res["findings"]
    assert "unverifiable" not in res
