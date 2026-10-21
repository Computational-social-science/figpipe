"""`POOL = 150` was a claim; the coverage index is a record. Check them against each other.

WHY THIS EXISTS
    Round 52 found that the invariant's second clause -- COMPLETE MEMBERSHIP -- was never enforced:
    `n_tasks` was `len(merged)`, whatever was fetched, and nothing compared it to the declared pool
    size. The fix added `complete_membership`.

    But that fix rested on `POOL = 150`, a literal in the source. So `complete_membership` was
    computed against a number nobody re-derived -- the same shape as a control that looks present
    and does nothing.

    The authority already existed on disk: `_record_coverage` writes offset -> task id for every
    task ever fetched, and the coverage backfill walks that index. `pool_facts()` compares the
    declaration against the record.

WHAT A DISAGREEMENT WOULD MEAN
    `indexed != declared`  -> the upstream dataset changed shape, and every rate in the report is
                              computed against a stale denominator
    `not contiguous`       -> the index has a gap, so it is INCOMPLETE, not evidence the pool is
                              smaller. The two readings are opposite and must not be confused.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def bench():
    return pytest.importorskip("bench_plottwin")


def test_the_declared_pool_agrees_with_the_coverage_index(bench):
    """THE CHECK. A mismatch means the upstream dataset changed shape."""
    facts = bench.pool_facts()
    assert facts["consistent"], (
        f"the declared pool ({facts['declared']}) disagrees with the coverage index "
        f"({facts['indexed']} offsets, {facts['ids_indexed']} ids, contiguous={facts['contiguous']}). "
        f"Every rate in the report is computed against a stale denominator until this is resolved.")


def test_the_coverage_index_is_contiguous(bench):
    """A gap means the INDEX is incomplete -- the opposite of the pool being smaller."""
    facts = bench.pool_facts()
    assert facts["contiguous"], (
        "the coverage index has a gap, so it does not describe a complete pool; re-run the backfill "
        "rather than concluding the pool shrank")


def test_the_report_carries_the_pool_facts(bench):
    """A disagreement must be visible in the artefact, not only discoverable by running code."""
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        pytest.skip("no benchmark report")
    b = json.loads(report.read_text(encoding="utf-8"))
    assert "pool_facts" in b, (
        "the report does not carry the pool facts, so a reader cannot tell whether the declared "
        "pool still agrees with reality")
    facts = b["pool_facts"]
    assert facts["consistent"], f"the report's own pool facts disagree: {facts}"
    assert b["complete_membership"] == (b["n_tasks"] == facts["indexed"] and facts["consistent"]), (
        "complete_membership contradicts the pool facts")


def test_a_disagreement_is_detected(bench, monkeypatch):
    """A CHECK THAT CANNOT FAIL IS NOT A CHECK.

    Simulate the upstream growing: an extra offset appears in the index that the declaration does
    not know about. `pool_facts` must report it, and `consistent` must go False.
    """
    real = bench._read_coverage()
    grown = dict(real)
    grown[max(real) + 1] = "a-task-that-did-not-exist-when-POOL-was-written"
    monkeypatch.setattr(bench, "_read_coverage", lambda: grown)
    facts = bench.pool_facts()
    assert facts["indexed"] == len(real) + 1
    assert not facts["consistent"], (
        "an extra task in the coverage index was not noticed; the membership check would silently "
        "keep using the old denominator")


def test_a_missing_MIDDLE_offset_is_reported_as_a_gap(bench, monkeypatch):
    """A gap in the middle means the INDEX is incomplete -- the opposite of a smaller pool."""
    real = bench._read_coverage()
    victim = sorted(real)[len(real) // 2]
    gapped = {k: v for k, v in real.items() if k != victim}
    monkeypatch.setattr(bench, "_read_coverage", lambda: gapped)
    facts = bench.pool_facts()
    assert facts["contiguous"] is False, (
        f"a missing middle offset ({victim}) was not reported as a gap")
    assert victim in facts["gaps"]
    assert not facts["consistent"]


def test_a_missing_LAST_offset_is_reported_as_a_short_tail(bench, monkeypatch):
    """THE BUG THIS TEST FOUND IN ITS OWN DETECTOR.

    Dropping the highest offset leaves an index of 0..148, which is perfectly CONTIGUOUS. An earlier
    version tested only contiguity, so losing the last task read as "the pool is 149" -- an absence
    of information reported as a smaller pool. A gap and a short tail are different failures.
    """
    real = bench._read_coverage()
    dropped = {k: v for k, v in real.items() if k != max(real)}
    monkeypatch.setattr(bench, "_read_coverage", lambda: dropped)
    facts = bench.pool_facts()
    assert facts["indexed"] == len(real) - 1
    assert facts["contiguous"] is True, "dropping the tail should still be contiguous"
    assert facts["short_tail"] is True, (
        "losing the last task was not reported as a short tail; it would read as a smaller pool")
    assert facts["highest_offset"] == max(real) - 1
    assert not facts["consistent"]


def test_the_snapshot_records_pool_consistency():
    """Every run record must say whether the pool still agrees, not leave it to be discovered."""
    import cron_run
    snap = cron_run.capability_snapshot()
    assert "benchmark_pool_consistent" in snap, (
        "the capability snapshot does not record whether the declared pool still agrees with the "
        "coverage index")
    assert snap["benchmark_pool_consistent"] is True
