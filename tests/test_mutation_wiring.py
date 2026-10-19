"""A capability that is not wired in is not a capability of the system.

WHY THIS TEST
    `figpipe/mutation.py` passed 30 tests, was described in the report as a deliverable, and was
    never imported by anything. AST-level verification found ZERO imports and ZERO call sites. It
    was a capability of the test suite, not of the pipeline -- and the distinction is the whole
    point of this project.

    The same round found the consequence: 91 scheduled runs produced 4 knowledge changes and 0 rule
    changes, because the loop could re-verify and record but never PROPOSE, PROBE or SELECT.

    These tests pin the wiring, so the orphan cannot come back.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_the_mutation_module_is_imported_by_real_code():
    """AST-level: an import inside a docstring or a string does not count."""
    importers = []
    for p in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "figpipe").glob("*.py")):
        if p.name == "mutation.py":
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if "mutation" in (node.module or ""):
                    importers.append(p.name)
                elif any("mutation" in (a.name or "") for a in node.names):
                    importers.append(p.name)
            elif isinstance(node, ast.Import):
                if any("mutation" in a.name for a in node.names):
                    importers.append(p.name)
    assert importers, (
        "figpipe/mutation.py is an ORPHAN: no module imports it. A capability that is not wired "
        "in is not a capability of the system.")
    assert "mutate.py" in importers or "mutation.py" in importers, importers


def test_the_cron_loop_runs_the_mutation_step():
    """The evolution loop must PROPOSE, PROBE and SELECT, or it is only a self-checker."""
    src = (ROOT / "scripts" / "cron_run.py").read_text(encoding="utf-8")
    assert "mutation_step" in src, "the loop does not run a mutation step"
    assert "mutate.py" in src, "the loop does not invoke the mutation entry point"
    # and it must be recorded, so a run can say what it selected
    assert '"mutation"' in src, "the mutation result is not recorded in the run"


def test_the_mutation_entry_point_exists_and_reports():
    script = ROOT / "scripts" / "mutate.py"
    if not script.is_file():
        pytest.skip("mutate.py absent")
    report = ROOT / "knowledge" / "mutation_report.json"
    if not report.is_file():
        pytest.skip("no mutation report yet")
    data = json.loads(report.read_text(encoding="utf-8"))
    for key in ("proposed", "tasks", "selected", "rejected", "ties"):
        assert key in data, f"the mutation report omits {key!r}"
    # a selection must NEVER be silently applied: applying an edit measured on six tasks is the
    # "a fix is a change, a change needs the same evidence" defect
    assert data.get("applied") is False, (
        "the mutation report claims an edit was applied; a six-task selection is a finding, "
        "not a change")
    assert data.get("why_not_applied"), "the report must say why it did not apply the selection"


def test_the_loop_does_not_commit_when_nothing_changed():
    """49 of 80 commits once said "no knowledge change"; that hides the ones that mattered."""
    src = (ROOT / "scripts" / "cron_run.py").read_text(encoding="utf-8")
    assert "no knowledge change: the run record stays uncommitted" in src, (
        "the loop still commits a run that changed nothing")
    # a FAILED run is evidence and must still be committed
    assert "run_ok" in src, "a failed run must still be preserved"
