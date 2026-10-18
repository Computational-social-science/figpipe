"""The figure must still MEAN what the data said -- style distance cannot check that.

WHY THESE TESTS
    Every other check in this project inspects appearance or geometry: audit (width, type size,
    fonts), styleprofile (palette, sizes, aspect), score (NPF dimensions). None of them re-derives
    the numbers. A pipeline that optimises style can therefore ship a beautifully formatted figure
    that prints "r = +0.80" over data whose r is -0.20 and nothing would notice.

    `figpipe/semantics.py` closes that gap with deterministic checks. These tests use NEGATIVE
    controls deliberately: a check that cannot fail is not a check.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

sem = pytest.importorskip("figpipe.semantics", reason="semantics module absent")
from figpipe import grammar, layout  # noqa: E402

RNG = np.random.default_rng(0)


def test_a_true_annotation_passes_and_a_false_one_fails():
    x = np.arange(20.0)
    y = 0.1 + 0.02 * x
    good = sem.check_annotations(["r = +1.00"], x, y)
    assert good["ok"] is True
    bad = sem.check_annotations(["r = -0.80"], x, y)
    assert bad["ok"] is False
    assert "printed r" in bad["findings"][0]["detail"]


def test_a_missing_annotation_is_reported_when_it_is_required():
    x = np.arange(10.0)
    y = np.arange(10.0)
    assert sem.check_annotations([], x, y, require_r=True)["ok"] is False
    assert sem.check_annotations([], x, y, require_r=False)["ok"] is True


def test_a_rounded_annotation_is_not_a_contradiction():
    x = np.arange(30.0)
    y = np.sin(x / 5.0)
    r = float(np.corrcoef(x, y)[0, 1])
    printed = f"r = {r:+.2f}"
    assert sem.check_annotations([printed], x, y)["ok"] is True


def test_clipping_a_point_outside_the_axes_is_caught():
    df = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0], "y": [0.1, 0.2, 0.3, 9.0]})
    panel = grammar.panel("trend_with_uncertainty", df, x="x", y="y", fit=None)
    fig = grammar.plate([panel], columns=1.0, height_mm=60.0)
    ax = fig.axes[0]
    ax.set_ylim(0, 1)                      # silently clip the outlier
    res = sem.check_extent(ax, df["x"], df["y"])
    assert res["ok"] is False
    assert res["outside"] == 1


def test_the_rendered_trend_panel_passes_its_own_semantic_check(tmp_path):
    df = pd.DataFrame({"x": np.arange(24.0), "y": 0.1 + 0.02 * np.arange(24.0)})
    panel = grammar.panel("trend_with_uncertainty", df, x="x", y="y", fit="lm")
    fig = grammar.plate([panel], columns=2.0, height_mm=70.0)
    ax = fig.axes[0]
    texts = [t.get_text() for t in ax.texts]
    res = sem.verify_panel(ax, df, x="x", y="y", texts=texts,
                           mark_kind="points")
    assert res["ok"], res["findings"]
    assert res["checks"]["extent"] is True


def test_a_wrong_axis_label_is_caught():
    df = pd.DataFrame({"x": np.arange(6.0), "y": np.arange(6.0)})
    panel = grammar.panel("trend_with_uncertainty", df, x="x", y="y", fit=None,
                          xlabel="year", ylabel="rate")
    fig = grammar.plate([panel], columns=1.0, height_mm=60.0)
    ax = fig.axes[0]
    assert sem.check_labels(ax, xlabel="year", ylabel="rate")["ok"] is True
    assert sem.check_labels(ax, xlabel="month")["ok"] is False
