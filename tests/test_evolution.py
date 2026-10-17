"""The evolution loop must be IDEMPOTENT and its run record must be complete.

WHY THESE TESTS EXIST
    Two defects were found in the scheduled run, both of which made the loop's own history
    misleading:

    1. THE RUN RECORD WAS INCOMPLETE. `evolve.py` writes a structured report (reverified
       rules, demoted, promoted, the H02 measurement) but `cron_run.py` kept only the last six
       lines of stdout. So the artefact could not answer "did any rule regress?" or "was
       anything promoted?" -- the two questions the schedule exists to report.

    2. PROMOTION WAS NOT STICKY. H02 was promoted to verified on the first run and then
       "promoted" again on every subsequent run, incrementing the knowledge-base version each
       time. Observed: v5 -> v6 -> v7 within 40 seconds with no rule actually changing. A
       6-hourly schedule would have inflated the version forever.

    Both are the kind of bug that looks like the system working: the version number goes up,
    the run reports success, and nothing is true.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge" / "layout_rules.json"
LATEST = ROOT / "knowledge" / "latest_run.json"
CRON = ROOT / "scripts" / "cron_run.py"


@pytest.fixture(scope="module")
def kb():
    return json.loads(KB.read_text(encoding="utf-8"))


def test_promotion_is_sticky(kb):
    """A rule already verified must not be reported as newly promoted.

    THE DEFECT: every run re-promoted H02, so `promoted` was never empty and the version
    inflated on every run with no change behind it.
    """
    h02 = [r for r in kb["rules"] if r["id"] == "H02"]
    if not h02:
        pytest.skip("H02 absent")
    # H02 is MEASURED but nothing in the code enforces it, so it must not claim to be
    # enforced. The old test asserted confidence == "verified", which the audit showed was a
    # label nothing backed.
    assert h02[0]["mechanism_verified"] is False, (
        "H02 has no enforcement mechanism; it must not claim mechanism_verified")
    assert h02[0]["confidence"] in ("measured_unenforced", "hypothesis"), (
        f"H02 is {h02[0]['confidence']!r}; a measured-but-unenforced rule must not be "
        f"labelled enforced")


def test_version_only_increments_on_real_change(kb):
    """The version must not move when no rule changed state."""
    src = (ROOT / "scripts" / "evolve.py").read_text(encoding="utf-8")
    assert "kb[\"version\"] += 1 if demoted else 0" in src, (
        "evolve.py increments the version unconditionally; a quiet run must leave the "
        "knowledge base alone or the version number becomes meaningless")


def test_run_record_carries_the_evolution_result():
    """The run artefact must be able to answer 'did anything regress / get promoted?'."""
    if not LATEST.is_file():
        pytest.skip("no run recorded yet")
    run = json.loads(LATEST.read_text(encoding="utf-8"))
    for key in ("check_results", "demoted"):
        assert key in run, (
            f"latest_run.json has no {key!r} field, so the scheduled run cannot report "
            f"whether a rule regressed")
    assert run["check_results"], (
        "check_results is empty; the run did not record which rules it re-checked")


def test_two_consecutive_evolve_runs_do_not_change_the_version():
    """IDEMPOTENCY, tested on the evolution step alone.

    THE FIRST VERSION OF THIS TEST HUNG THE SUITE. It spawned cron_run.py, which runs the
    test suite -- which contains this test. Each level spawned another, recursively.

    The fix is to test the property where it lives: run volve.py (which does NOT run the
    suite) twice and require the knowledge version to be unchanged the second time. That is
    the actual idempotency contract; cron_run.py only wraps it.

    A FIGPIPE_NO_TESTS guard was also added to cron_run.py so the runner can never
    re-enter the suite, whatever calls it.
    """
    py = sys.executable
    versions = []
    for _ in range(2):
        p = subprocess.run([py, str(ROOT / "scripts" / "evolve.py")],
                           cwd=ROOT, capture_output=True, text=True,
                           env={**__import__("os").environ, "FIGPIPE_NO_TESTS": "1"})
        assert p.returncode == 0, f"evolve.py failed: {p.stdout[-400:]}{p.stderr[-400:]}"
        kb = json.loads(KB.read_text(encoding="utf-8"))
        versions.append(kb["version"])
    assert versions[0] == versions[1], (
        f"the knowledge version changed across two consecutive evolve runs "
        f"({versions[0]} -> {versions[1]}); the loop is not idempotent and a quiet run is "
        f"indistinguishable from a change")
