"""The deterministic scorer must fill what it can measure and say so where it cannot.

WHY THESE TESTS
    `figpipe/score.py` adopts the metric DIMENSIONS of a peer benchmark (NaturePanelForge's
    SciFigure2Code) while rejecting its model-judged values. The design promise is: every number
    has evidence, and every dimension that needs an interpretation is reported as NOT MEASURED
    with a reason. A scorer that quietly emits a number for "scientific notation fidelity"
    without measuring it would be the same failure shape as a check that looks present and does
    nothing.
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

score = pytest.importorskip("figpipe.score", reason="score absent")
styleprofile = pytest.importorskip("figpipe.styleprofile")
from figpipe import audit, grammar, layout  # noqa: E402

TREND = pd.DataFrame({
    "Year": range(1990, 2014),
    "mean": [0.10 + 0.008 * i for i in range(24)],
})


def _trend_pdf(tmp_path):
    panel = grammar.panel("trend_with_uncertainty", TREND, x="Year", y="mean",
                          fit="lm", band="fit", reference=0.0,
                          xlabel="Year", ylabel="z-score")
    fig = grammar.plate([panel], columns=2.0, height_mm=90.0)
    paths = layout.save(fig, tmp_path / "trend")
    return pathlib.Path(paths[0])


def test_a_compliant_panel_scores_high_and_carries_evidence(tmp_path):
    pdf = _trend_pdf(tmp_path)
    ref = styleprofile.StyleProfile.from_pdf(pdf)
    s = score.score_panel(pdf, reference_profile=ref,
                          published={"r": 0.88}, computed={"r": 0.884},
                          expected_panels=1,
                          expect_components=["band", "fit_line", "reference"])
    d = s["dimensions"]
    assert d["execution_pass_rate"]["value"] == 1.0
    assert d["clarity_overlap"]["value"] == 2
    assert d["layout_consistency"]["value"] == 2
    assert d["text_label_fidelity"]["value"] == 2
    assert d["component_completeness"]["value"] == 2, d["component_completeness"]
    assert d["data_pattern_fidelity"]["value"] == 2
    assert d["visual_fidelity"]["value"] == pytest.approx(100.0, abs=0.5)
    assert all(dim.get("evidence") for dim in d.values())


def test_a_sub_five_point_panel_fails_execution(tmp_path):
    fig, _, _ = layout.figure(columns=1.0, height_mm=50.0)
    fig.text(0.2, 0.5, "four point text", fontsize=4.0)
    pdf = pathlib.Path(layout.save(fig, tmp_path / "broken")[0])
    s = score.score_panel(pdf)
    assert s["dimensions"]["execution_pass_rate"]["value"] == 0.0
    assert "font_size" in s["dimensions"]["execution_pass_rate"]["evidence"]


def test_unmeasurable_dimensions_are_declared_not_guessed(tmp_path):
    pdf = _trend_pdf(tmp_path)
    s = score.score_panel(pdf)                     # no reference, no statistics, no intents
    assert "visual_fidelity" in s["not_measured"]
    assert "data_pattern_fidelity" in s["not_measured"]
    assert "axis_fidelity" in s["not_measured"]
    assert s["not_measured"]["axis_fidelity"]      # must carry a reason
    assert s["n_not_measured"] >= 5
    assert s["invalidity"]["direct_image_dependency_rate"]["value"] == 0.0


def test_statistics_are_scored_against_the_published_values(tmp_path):
    pdf = _trend_pdf(tmp_path)
    good = score.score_panel(pdf, published={"r": 0.88}, computed={"r": 0.881})
    bad = score.score_panel(pdf, published={"r": 0.88}, computed={"r": 0.60})
    assert good["dimensions"]["data_pattern_fidelity"]["value"] == 2
    assert bad["dimensions"]["data_pattern_fidelity"]["value"] == 0
