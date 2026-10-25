"""The scheduled loop must re-derive the claim, not merely re-measure capability.

WHY THIS EXISTS
    CLAIM.md opens with "Everything below is measured by scripts in this repository and can be re-run".
    Round 114 proved that was aspirational: the style-metric discrimination accuracy had drifted from
    0.933 (28/30) to 0.900 (27/30) across five commits, and nothing noticed for two days -- because the
    loop measures CAPABILITY and never re-derived the CLAIM.

    A claim that re-derives to a different number is worse than one that cannot be re-derived, because
    the re-derivation LOOKS like verification.

WHAT THIS FILE PINS
    1. `cron_run.claim_rederivation()` runs the script CLAIM.md cites and reports what it measured.
    2. It reports `agrees` correctly in BOTH directions -- a stale number is detected, a true one passes.
    3. The run record carries `claim_rederivation` and `claim_ok`.
    4. The step does NOT edit CLAIM.md: a loop that rewrites its own claim can make any claim true.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CLAIM = ROOT / "CLAIM.md"


@pytest.fixture(scope="module")
def cron():
    import cron_run
    return cron_run


def test_the_step_runs_and_reports(cron):
    """THE FIX. The script CLAIM.md cites is executed and its number reported."""
    result = cron.claim_rederivation()
    assert result.get("ran") is True, result
    assert isinstance(result.get("accuracy"), (int, float)), result
    assert result.get("n_pairs"), result
    assert result.get("ci95"), result


def test_it_agrees_when_the_document_is_current(cron):
    """THE HAPPY PATH. A document that states the measured number must pass."""
    result = cron.claim_rederivation()
    if not result.get("ran"):
        pytest.skip(f"cannot re-derive: {result.get('reason')}")
    assert result.get("agrees") is True, (
        f"CLAIM.md states {result.get('claim_states')} but the measurement is {result.get('accuracy')}")


def test_it_detects_a_stale_number(cron):
    """THE NEGATIVE CONTROL. A guard that cannot fail is not a guard."""
    import re
    saved = CLAIM.read_text(encoding="utf-8")
    current = cron.claim_rederivation()
    if not current.get("ran"):
        pytest.skip("cannot re-derive")
    stated = current["claim_states"]
    wrong = 0.933 if abs(stated - 0.933) > 1e-6 else 0.900
    try:
        broken = re.sub(r"([Dd]iscrimination accuracy[^0-9]{0,24})0\.\d{3}",
                        rf"\g<1>{wrong:.3f}", saved, count=1)
        if broken == saved:
            pytest.skip("could not construct the drift case in this version of CLAIM.md")
        CLAIM.write_text(broken, encoding="utf-8")
        result = cron.claim_rederivation()
        assert result.get("agrees") is False, (
            f"the step did not detect a claim stating {wrong} when the measurement is "
            f"{current['accuracy']}; the check is a no-op")
    finally:
        CLAIM.write_text(saved, encoding="utf-8")


def test_the_step_does_not_edit_the_claim(cron):
    """A LOOP THAT REWRITES ITS OWN CLAIM CAN MAKE ANY CLAIM TRUE."""
    before = CLAIM.read_text(encoding="utf-8")
    cron.claim_rederivation()
    after = CLAIM.read_text(encoding="utf-8")
    assert before == after, "claim_rederivation() modified CLAIM.md; the check must only report"


def test_the_run_record_carries_the_rederivation(cron):
    """A MEASUREMENT NOBODY READS IS HOW THE MUTATION LOOP STAYED DEAD FOR FOUR RUNS."""
    src = (ROOT / "scripts" / "cron_run.py").read_text(encoding="utf-8")
    assert '"claim_rederivation"' in src, "the run record does not carry the re-derivation"
    assert '"claim_ok"' in src, "the run record has no boolean a reader can filter on"
    assert "CLAIM DRIFTED" in src, (
        "the runner does not PRINT a drift; opening the JSON must not be required to notice")
