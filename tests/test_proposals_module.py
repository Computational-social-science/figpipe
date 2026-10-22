"""Candidates must be derivable from findings, not only from a fixed menu.

WHY THIS EXISTS
    Measured over 152 scheduled runs: 4 knowledge changes, 222 ties, 149 runs that selected NOTHING.
    The loop was not failing to find improvements -- it was structurally unable to represent them.
    Its whole search space was five hard-coded budget integers, and `mutation_step()` never read the
    pool report, so it never saw a finding.

    Every real defect this project fixed -- the text collisions, the polar label overflow, the colour
    bar falling off the page, the pivot choosing a row index as its measurement -- was a drawer
    change that no budget integer could express.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import proposals  # noqa: E402


def _report(*checks: str) -> dict:
    return {"tasks": [{"id": "t1", "findings": [{"check": c, "detail": "x"} for c in checks]}]}


def test_a_collision_finding_yields_parameter_candidates():
    """The finding a drawer can act on must produce a candidate."""
    result = proposals.proposals_from_report(_report("text_collision"))
    assert result["n"] >= 1, "a text_collision finding produced no candidate"
    operators = {p["operator"] for p in result["proposals"]}
    assert "layout.split_panels" in operators
    params = {p["parameter"] for p in result["proposals"]}
    assert params & {"max_rows", "max_panels"}


def test_a_code_only_finding_is_reported_as_unproposable():
    """THE HONEST HALF: a drawer change cannot be a scalar, and that must be SAID."""
    result = proposals.proposals_from_report(_report("semantics.mesh_scale"))
    assert result["n"] == 0
    assert result["n_unproposable"] == 1
    why = result["unproposable"][0]["why"]
    assert "drawer change" in why or "not a parameter" in why


def test_an_unknown_finding_is_reported_not_dropped():
    result = proposals.proposals_from_report(_report("something_new"))
    assert result["n_unproposable"] == 1
    assert "no parameter is mapped" in result["unproposable"][0]["why"]


def test_a_clean_report_yields_nothing_and_says_so():
    """A pool with no findings must not invent candidates."""
    result = proposals.proposals_from_report({"tasks": [{"id": "t1", "findings": []}]})
    assert result["n"] == 0
    assert result["n_unproposable"] == 0
    assert "no finding" in result["verdict"]


def test_the_live_pool_report_is_read_without_error():
    """The module must handle the real artefact, whatever it currently contains."""
    import json
    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not path.is_file():
        pytest.skip("no pool report")
    result = proposals.proposals_from_report(json.loads(path.read_text(encoding="utf-8")))
    assert result["n"] >= 0
    assert isinstance(result["unproposable"], list)
    assert result["verdict"]


def test_mutation_step_records_the_finding_proposals():
    """The run record must carry the gap, not only the menu's result."""
    import inspect
    sys.path.insert(0, str(ROOT / "scripts"))
    import cron_run
    src = inspect.getsource(cron_run.mutation_step)
    assert "finding_proposals" in src, (
        "mutation_step does not record finding-derived proposals, so the structural gap stays "
        "invisible in every run record")
    assert "finding_unproposable" in src
