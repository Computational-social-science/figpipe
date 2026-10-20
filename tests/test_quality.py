"""Named quality dimensions, scored separately -- and never faked.

WHY THIS EXISTS
    AutoFigure (ResearAI/AutoFigure, ICLR 2026) scores a figure on eleven NAMED dimensions and
    reports each separately, so a user learns what to fix rather than that something is wrong.
    figpipe's audit reported a flat list of findings with no dimensions and no per-dimension score.

    AutoFigure's mechanism is a VLM-as-Judge, which this project measured and rejected:
    `vlm_report.json` recorded 20 fabrications. So the STRUCTURE is adopted and the JUDGE is not.

    The rule this file pins: a dimension that cannot be measured is reported as UNMEASURED with a
    reason. It is never omitted (a reader would believe the figure is good on it) and never faked
    with a heuristic (a wrong number nobody can audit is worse than an honest gap).
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import quality, skills  # noqa: E402


def test_an_empty_findings_list_is_a_pass_not_an_absence():
    """THE BUG: `findings == []` was read as "no check ran".

    An empty list after `verify.collisions` means the check RAN and found nothing -- a PASS. The
    trace records which steps executed, so it is the only honest signal. Without this, a perfect
    figure and an unverified figure look identical.
    """
    findings: list[dict] = []
    ran = ["encode.bars", "layout.plate", "verify.audit", "verify.collisions", "verify.semantics"]
    leg = quality.score_legibility(findings, ran)
    sem = quality.score_semantics(findings, ran)
    assert leg.measured and leg.score == 1.0, leg
    assert sem.measured and sem.score == 1.0, sem
    # and with NO trace, the same empty findings must be unmeasured
    assert not quality.score_legibility(findings, []).measured
    assert not quality.score_semantics(findings, []).measured


def test_a_dimension_that_did_not_run_is_reported_unmeasured():
    findings: list[dict] = []
    rep = quality.report([quality.score_colour(findings, ["verify.audit"])])
    assert rep["dimensions"] == []
    assert rep["unmeasured"] and rep["unmeasured"][0]["name"] == "colour"
    assert "did not run" in rep["unmeasured"][0]["why"]


def test_a_real_collision_lowers_the_legibility_score():
    findings = [{"check": "text_collision", "severity": "hard", "detail": "a over b"}]
    leg = quality.score_legibility(findings, ["verify.collisions"])
    assert leg.measured
    assert leg.score < 1.0
    assert leg.band in ("minor", "needs work", "fails")


def test_the_worst_dimension_is_named_first():
    """Order is the point: a user needs to know what to fix FIRST."""
    dims = [
        quality.DimensionScore("geometry", 1.0),
        quality.DimensionScore("legibility", 0.2),
        quality.DimensionScore("semantics", 0.9),
    ]
    rep = quality.report(dims)
    assert rep["dimensions"][0]["name"] == "legibility"
    assert rep["worst"] == "legibility"
    assert rep["worst_band"] == "fails"


def test_unmeasurable_dimensions_are_listed_with_a_reason():
    """AutoFigure's rubric includes dimensions no deterministic check can decide.

    They must appear as unmeasured WITH the reason, not be silently dropped.
    """
    assert quality.UNMEASURABLE
    for name, why in quality.UNMEASURABLE.items():
        assert why and len(why) > 10, f"{name} has no stated reason"


def test_a_real_skill_result_produces_named_scores():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"site": ["a", "b", "c"] * 10,
                       "m1": rng.random(30), "m2": rng.random(30)})
    res = skills.run("grouped_measures", df, out_stem=None, x="site", ycols=["m1", "m2"])
    rep = quality.for_skill_result(res)
    assert rep["dimensions"], "a clean figure produced no measured dimension"
    for d in rep["dimensions"]:
        assert d["name"] in quality.DIMENSIONS
        assert 0.0 <= d["score"] <= 1.0
        assert d["band"] in ("pass", "minor", "needs work", "fails")
    assert rep["verdict"]


def test_the_report_never_claims_a_dimension_it_did_not_measure():
    """NEGATIVE CONTROL: every entry in `dimensions` must have a real score."""
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"x": range(20), "y": rng.random(20)})
    res = skills.run("trend_with_uncertainty", df, out_stem=None, x="x", y="y", fit="lm")
    rep = quality.for_skill_result(res)
    for d in rep["dimensions"]:
        assert d["score"] is not None
        assert d["band"] != "unmeasured"
    for u in rep["unmeasured"]:
        assert u["why"]
