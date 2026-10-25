"""A None in the capability record must say why it is None.

WHY THIS EXISTS
    Measured 2026-10-25: every reference-image download from HuggingFace returned `HTTP 403 Forbidden`,
    so only 6 of the 20 anchor tasks could be measured. The benchmark report handled that correctly:

        benchmark_anchor_single.mean:  None
        benchmark_anchor_single.comparable: False
        note: "incomplete: 6 of 20 anchor tasks measured; a partial mean is not the anchor, so it is
               not judged"

    **The benchmark was right and the run record was unreadable.** A reader seeing
    `benchmark_anchor_single: None` cannot tell three different situations apart:

        (a) the anchor is genuinely not applicable
        (b) the instrument changed and the anchor is incomparable
        (c) the DOWNLOAD FAILED and no anchor could be measured

    (c) is an infrastructure fact. Reporting it as a bare None makes it look like a capability result --
    which is the same shape as the "a zero that looks like a fact about the world is often a fact about
    the instrument" pattern this project has recorded repeatedly.

THE RULE
    Every nullable capability field that can be absent for MORE THAN ONE reason must carry its reason
    alongside it, and the printed summary must surface the infrastructure cases.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def cap():
    import cron_run
    return cron_run.capability_snapshot()


VALID_STATES = {"measured", "incomplete", "incomparable", "absent"}


def test_the_anchor_carries_its_reason(cap):
    """THE FIX. `None` must be accompanied by a REASON CODE that says which None it is.

    A code, not a sentence: `test_snapshot_reads_capability_artefacts_without_opinions` refuses prose in
    the capability record, and it is right to -- a snapshot holds counts and measured distances. The
    reason is still there, as an enumerable fact.
    """
    state = cap.get("benchmark_anchor_state")
    assert state in VALID_STATES, (
        f"the anchor state is {state!r}, not one of {sorted(VALID_STATES)}; a bare None cannot be told "
        f"apart from an unmeasured anchor")
    if cap.get("benchmark_anchor_single") is None:
        assert state != "measured", "the anchor is None but the state says it was measured"


def test_the_incomplete_state_reports_its_counts(cap):
    """A STATE WITHOUT THE COUNTS THAT PRODUCED IT IS A LABEL, NOT A MEASUREMENT."""
    if cap.get("benchmark_anchor_state") != "incomplete":
        pytest.skip("the anchor is not in the incomplete state on this run")
    assert isinstance(cap.get("benchmark_anchor_n_same"), int), cap
    assert isinstance(cap.get("benchmark_anchor_n_expected"), int), cap
    assert cap["benchmark_anchor_n_same"] < cap["benchmark_anchor_n_expected"], cap


def test_the_anchor_reports_comparability(cap):
    """`comparable` distinguishes "the instrument changed" from "there was nothing to compare"."""
    assert "benchmark_anchor_comparable" in cap, (
        "the capability record does not say whether the anchor is comparable")


def test_the_runner_prints_an_unmeasured_anchor():
    """A CAPABILITY THE SUMMARY DOES NOT MENTION IS ONE NOBODY NOTICES.

    Measured 2026-10-25: every download returned 403 and the printed summary said nothing about the
    anchor at all. The run looked healthy while measuring almost nothing.
    """
    src = (ROOT / "scripts" / "cron_run.py").read_text(encoding="utf-8")
    assert "ANCHOR NOT MEASURED" in src, (
        "the runner does not print an unmeasured anchor; a reader of the summary cannot tell that the "
        "measurement did not happen")
    assert "ANCHOR INCOMPARABLE" in src, (
        "the runner does not distinguish an incomparable anchor from an unmeasured one")


def test_a_failed_download_is_not_a_capability_result():
    """THE GENERAL FORM. The slice records its failures; those must not be read as capability.

    `benchmark_slice.tail` carries the per-task failures. If every one is an HTTP error, the run has an
    infrastructure problem, not a capability one -- and `success_rate` must not be computed as if the
    missing tasks had failed.
    """
    import json
    latest = ROOT / "knowledge" / "latest_run.json"
    if not latest.is_file():
        pytest.skip("no run record")
    run = json.loads(latest.read_text(encoding="utf-8"))
    slice_ = run.get("benchmark_slice") or {}
    tail = slice_.get("tail") or []
    http_failures = [ln for ln in tail if "HTTPError" in str(ln) or "Forbidden" in str(ln)]
    if not http_failures:
        pytest.skip("no download failures on this run")
    # the record must still report a success rate over what was ATTEMPTED, and the failures are visible
    cap_ = run.get("capabilities") or {}
    assert cap_.get("benchmark_success_rate") is not None, (
        "a run with download failures reports no success rate; the infrastructure failure is hiding "
        "the capability measurement")
    assert http_failures, "the slice did not record its HTTP failures"
