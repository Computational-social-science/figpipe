"""The scheduled run must keep its own artefacts current.

WHY THIS EXISTS
    Two failures on the first real run of the claim re-derivation, both found by the guards added in
    rounds 112-115 rather than by reading the code:

    1. `claim_rederivation()` returned `exit 3`. `validate_style_metric.py` acquires
       `lock.acquire("style_validation")` and refuses when it is busy -- and `cron_run` is HOLDING the
       measurement lock when it calls the child. The child was right to refuse; the caller was wrong to
       ask it to take a lock it already had. Fixed with `--no-lock`, the same pattern as
       `mutation.probe(lock_held=True)`.

    2. `benchmark_slice()` rewrote the benchmark JSON every run and NOTHING rebuilt
       `reports/figpipe_report.html`, so the page was stale by construction. The freshness guard caught
       it on its first scheduled run.

THE RULE THIS FILE DEFENDS
    A run that measures must leave every artefact it publishes consistent with what it measured. A step
    that silently cannot run is worse than a step that fails loudly, which is why both are now PRINTED.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def cron():
    import cron_run
    return cron_run


def test_claim_rederivation_succeeds_while_the_parent_holds_the_lock(cron):
    """THE LOCK DEFECT. `cron_run` owns the lock; the child must be told, not refused."""
    result = cron.claim_rederivation()
    assert result.get("ran") is True, (
        f"claim_rederivation failed: {result.get('reason')}. If this says 'exit 3', the child is "
        f"trying to acquire a lock the parent already holds")
    assert isinstance(result.get("accuracy"), (int, float)), result


def test_the_child_is_told_the_lock_is_held(cron):
    """THE MECHANISM. Passing `--no-lock` is the whole fix; assert it rather than inferring it."""
    import inspect
    src = inspect.getsource(cron.claim_rederivation)
    assert "--no-lock" in src, (
        "claim_rederivation does not pass --no-lock; the child will refuse with exit 3 whenever the "
        "scheduled run holds the measurement lock")


def test_the_runner_rebuilds_the_report(cron):
    """THE STALENESS DEFECT. The slice rewrites the JSON; the page must follow."""
    import inspect
    src = inspect.getsource(cron)
    assert "def build_report(" in src, "cron_run has no build_report step"
    assert "report_run = build_report()" in src, (
        "cron_run defines build_report but never calls it; the page stays stale by construction")


def test_a_failed_step_is_printed_not_just_recorded(cron):
    """A FIELD NOBODY READS IS HOW THE MUTATION LOOP STAYED DEAD FOR FOUR RUNS."""
    src = (ROOT / "scripts" / "cron_run.py").read_text(encoding="utf-8")
    for message in ("CLAIM DRIFTED", "CLAIM NOT RE-DERIVED", "REPORT NOT REBUILT",
                    "MUTATION DID NOT RUN"):
        assert message in src, f"cron_run does not print {message!r}; a failure would be silent"


def test_the_report_is_current_after_a_rebuild(cron):
    """THE END STATE. After the runner's own step, the freshness contract holds."""
    if not (ROOT / "reports" / "figpipe_report.html").is_file():
        pytest.skip("no report")
    result = cron.build_report()
    assert result.get("ran") is True, result.get("reason")
    report = ROOT / "reports" / "figpipe_report.html"
    data = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if data.is_file():
        age = data.stat().st_mtime - report.stat().st_mtime
        assert age < 60, f"the report is still {age:.0f} s older than its data after a rebuild"
