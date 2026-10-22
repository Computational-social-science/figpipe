"""The workflow's links must CARRY the signal, not merely run in order.

WHY THIS EXISTS
    Asked: are the workflow's links tightly coupled. The audit found they are not coupled at all in
    the sense that matters:

        * no step consumes another's RETURN VALUE -- each is written into the run record and used
          by nothing
        * the coupling is a shared mutable JSON file, in an order only a COMMENT enforces
        * `mutation_step` reads the pool report and proposes from a five-item hard-coded menu
        * the capability snapshot sees aggregates only, so a cycle can add a real defect, keep the
          same task count, and report ok: true

    These tests pin the three links that were added to close that gap.
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


def test_the_freshness_contract_exists(cron):
    assert hasattr(cron, "_report_is_current"), (
        "nothing checks that the pool report is current before the anchor re-measures against it")


def test_the_freshness_contract_returns_a_reason(cron):
    ok, why = cron._report_is_current()
    assert isinstance(ok, bool)
    assert isinstance(why, str) and why


def test_the_pipeline_USES_the_freshness_contract(cron):
    """A contract that is defined and not used is the defect it was written to fix."""
    import inspect
    src = inspect.getsource(cron._main_locked)
    assert "_report_is_current" in src, (
        "the freshness contract is defined but the pipeline never consults it")


def test_the_snapshot_counts_hard_findings(cron):
    snap = cron.capability_snapshot()
    assert "benchmark_hard_findings" in snap, (
        "the capability snapshot cannot see a hard finding, so a cycle can add a defect and still "
        "report ok: true")
    assert isinstance(snap["benchmark_hard_findings"], int)


def test_more_findings_is_a_REGRESSION(cron):
    """THE DIRECTION THAT MATTERS: introducing a defect must fail the run."""
    prev = {"_code_version": "A", "benchmark_hard_findings": 0}
    cur = {"_code_version": "A", "benchmark_hard_findings": 5}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert [x["field"] for x in verdict["regressions"]] == ["benchmark_hard_findings"]
    assert verdict["ok"] is False


def test_fewer_findings_is_a_GAIN(cron):
    prev = {"_code_version": "A", "benchmark_hard_findings": 5}
    cur = {"_code_version": "A", "benchmark_hard_findings": 0}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert [x["field"] for x in verdict["gains"]] == ["benchmark_hard_findings"]
    assert verdict["ok"] is True


def test_mutation_step_records_finding_derived_proposals(cron):
    import inspect
    src = inspect.getsource(cron.mutation_step)
    assert "finding_proposals" in src, (
        "mutation_step does not record finding-derived proposals, so the five-item menu stays "
        "invisible as the structural limit")
    assert "finding_unproposable" in src, (
        "the findings the loop CANNOT act on must be reported, or the limit is hidden")
