"""The acceptance gate, borrowed from BootLoops: what "done" means for a figure.

WHY THIS EXISTS
    BootLoops (E:\\2026-AI4S\\bootloops) states the standard a computed result must meet:

        A result is done when it has survived a check that could have failed, run by a route that
        could not have known the answer. It is never done merely because the computation that
        produced it finished.

    Its failure-mode list reads like this project's own bug history:

        "the gate that cannot fail"        -- the anchor that accepted a partial membership
        "the unconditional success line"   -- RESULT: compliant printed after a skipped audit
        "certifying at fitted points"      -- the pool score that copied reference_code
        "threshold drift"                  -- KNOWN_CORRECTIONS widened until 93.53 passed
        "adjectives in place of counts"    -- "compliant" with no dimension scores

    figpipe had each as a separate lesson. BootLoops states them as one standard with a procedure
    that produces evidence rather than an adjective. `figpipe/gate.py` is that procedure, executable.

THE LOAD-BEARING TEST IN THIS FILE IS THE NEGATIVE CONTROL. A gate that has never failed anything
certifies nothing: every clause of it might be broken and you would see only passes.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import gate, skills  # noqa: E402


@pytest.fixture()
def clean_result(tmp_path):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"site": ["n", "s", "e", "w"] * 10,
                       "year": list(range(2015, 2025)) * 4,
                       "value": rng.random(40)})
    return skills.run("grouped_measures", df, out_stem=tmp_path / "clean",
                      x="site", ycols=["value"], columns=2.0)


# ---------------------------------------------------------------------------------------
# THE CONTROLS -- the reason any other pass in this file means something
# ---------------------------------------------------------------------------------------

def test_the_gate_can_fire(tmp_path):
    """BOTH controls must fire, or every pass the gate reports is vacuous."""
    v = gate.validate(tmp_path)
    assert v["positive"]["fired"] is True, (
        f"a clean figure did not pass the gate, so the gate is broken: {v['positive']}")
    assert v["negative"]["fired"] is True, (
        f"a deliberately wrong figure PASSED the gate, so the gate cannot fire: {v['negative']}")
    assert v["gate_can_fire"] is True
    assert "can fire" in v["verdict"]


def test_the_negative_control_fails_at_the_check_that_should_catch_it(tmp_path):
    """A gate that fires for the wrong reason is as broken as one that does not fire."""
    neg = gate.negative_control(tmp_path)
    assert neg["verdict"] == gate.OPEN
    assert "column_width" in neg["failed_checks"], (
        f"the wrong-width figure failed, but not at column_width: {neg['failed_checks']}")


def test_the_positive_control_reaches_closed(tmp_path):
    """CLOSED must be REACHABLE. A verdict nobody can attain is as meaningless as one always given."""
    pos = gate.positive_control(tmp_path)
    assert pos["verdict"] == gate.CLOSED, (
        f"a clean figure could not reach CLOSED: "
        f"{[c['name'] for c in pos['gate']['checks'] if not c['passed']]}")


# ---------------------------------------------------------------------------------------
# The gate's own logic
# ---------------------------------------------------------------------------------------

def test_an_empty_gate_cannot_pass():
    """NEGATIVE CONTROL for the verdict: no checks run means nothing was established."""
    g = gate.Gate(name="empty")
    assert g.close() == gate.OPEN
    assert any("empty" in n for n in g.notes)


def test_one_failed_check_opens_the_gate(tmp_path):
    g = gate.Gate(name="one-fail")
    g.add("a", 1, "1", True)
    g.add("b", 2, "1", False)
    assert g.close() == gate.OPEN
    assert [c.name for c in g.checks if not c.passed] == ["b"]


def test_a_clean_figure_closes_the_gate(clean_result):
    g = gate.run_gate(clean_result["pdf"], result=clean_result)
    assert g.verdict == gate.CLOSED, (
        f"failed: {[c.to_dict() for c in g.checks if not c.passed]}")


def test_the_verdict_is_computed_not_set(clean_result):
    """The verdict must come from the measured checks, never be assigned by the caller."""
    g = gate.run_gate(clean_result["pdf"], result=clean_result)
    before = g.verdict
    # flipping a check must flip the verdict on re-close
    g.checks[0].passed = False
    assert g.close() == gate.OPEN
    assert before == gate.CLOSED


def test_every_check_records_a_measured_value_not_an_adjective(clean_result):
    """"Adjectives in place of counts" is a named failure mode; every check must carry a number."""
    g = gate.run_gate(clean_result["pdf"], result=clean_result)
    for c in g.checks:
        assert c.measured is not None, f"{c.name} has no measured value"
        assert c.required, f"{c.name} does not say what it had to be"


def test_a_multipanel_figure_must_letter_its_panels(tmp_path):
    """A multi-panel figure with unlabelled panels is not submittable, whatever else it does."""
    df = pd.DataFrame({"g": ["a", "b", "c", "d"] * 10, "v": list(range(40))})
    res = skills.run("faceted_distribution", df, out_stem=tmp_path / "f",
                     value="v", by="g", of="hist", columns=2.0)
    g = gate.run_gate(res["pdf"], result=res)
    names = {c.name for c in g.checks}
    assert "panel_labels" in names, (
        "a 4-panel figure produced no panel_labels check")
    label_check = next(c for c in g.checks if c.name == "panel_labels")
    assert label_check.passed is True


def test_the_pipeline_controls_recover_every_plant(tmp_path):
    """The gate answers "is this figure well formed"; the plants answer "is the right number in it".

    A figure can be perfectly formed around a wrong number, so both controls are needed.
    """
    c = gate.pipeline_controls(tmp_path)
    assert c["all_recovered"] is True, (
        f"these plants were not recovered: {c['failed']}")
    assert c["n"] == c["n_passed"] >= 4
    assert "recovered" in c["verdict"]


def test_the_gate_and_the_plants_are_different_claims(tmp_path):
    """NEGATIVE CONTROL: neither control may substitute for the other.

    The gate is a statement about the FILE; the plants are a statement about the MACHINERY. A test
    that treated them as one would hide whichever broke.
    """
    v = gate.validate(tmp_path / "gate")
    c = gate.pipeline_controls(tmp_path / "plants")
    assert "gate_can_fire" in v
    assert "all_recovered" in c
    assert set(v) != set(c), "the two controls returned the same shape, so they are not distinct"
