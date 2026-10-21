"""A capability field must not be compared across a change to its measurement instrument.

WHY THIS EXISTS
    The scheduled run of 2026-10-21T20:26 exited 1 with:

        capability_regressions: [{'field': 'benchmark_anchor_single',
                                  'before': 0.355, 'after': 0.357}]

    A "regression" of +0.002 in a style DISTANCE (lower is better), reported as a capability LOSS
    and failing the run. Investigating it: **0 of the 20 anchor tasks had changed distance.** The
    anchor moved because the INSTRUMENT had changed -- a label-wrapping fix altered the rendered
    text, the style profile reads text, and the mean moved.

    That is the exact violation this project's own invariant forbids:

        a judged metric must be a function of a fixed task set, complete membership of that set,
        and a SINGLE INSTRUMENT VERSION

    `capability_snapshot()` did not record which instrument produced it, so `capability_delta`
    could not tell the two cases apart.

WHAT THE FIX MUST NOT DO
    It must not stop comparing entirely. A real regression on the SAME instrument is still a
    regression and must still fail the run. The tests below pin both directions.
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


def test_the_snapshot_records_its_instrument(cron):
    """Without this field the comparison cannot know whether the quantities are comparable."""
    snap = cron.capability_snapshot()
    assert "_code_version" in snap, (
        "the capability snapshot does not record which instrument produced it, so a later "
        "comparison cannot tell a capability change from an instrument change")


def test_a_regression_across_an_instrument_change_is_not_judged(cron):
    """THE BUG: 0.355 -> 0.357 reported as a capability loss when the instrument had changed."""
    prev = {"_code_version": "OLD", "benchmark_anchor_single": 0.355, "tests": 648}
    cur = {"_code_version": "NEW", "benchmark_anchor_single": 0.357, "tests": 650}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert verdict["instrument_changed"] is True
    assert not verdict["regressions"], (
        f"an instrument change was judged as a capability regression: {verdict['regressions']}")
    assert any(x["field"] == "benchmark_anchor_single" for x in verdict["not_compared"]), (
        "the field was silently dropped rather than reported as not-comparable")
    assert verdict["ok"] is True


def test_a_real_regression_on_the_same_instrument_IS_judged(cron):
    """NEGATIVE CONTROL: the fix must not stop comparing altogether."""
    prev = {"_code_version": "SAME", "benchmark_anchor_single": 0.355, "tests": 648}
    cur = {"_code_version": "SAME", "benchmark_anchor_single": 0.357, "tests": 650}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert verdict["instrument_changed"] is False
    assert [x["field"] for x in verdict["regressions"]] == ["benchmark_anchor_single"]
    assert verdict["ok"] is False, "a real regression on the same instrument must still fail"


def test_an_improvement_on_the_same_instrument_is_a_gain(cron):
    """The direction check must still work: a style distance going DOWN is an improvement.

    Only `benchmark_anchor_single` is asserted to be a gain here; other fields move too, and the
    test is about the anchor's direction, not about the exact set.
    """
    prev = {"_code_version": "SAME", "benchmark_anchor_single": 0.360}
    cur = {"_code_version": "SAME", "benchmark_anchor_single": 0.350}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert "benchmark_anchor_single" in [x["field"] for x in verdict["gains"]], (
        f"a style distance going DOWN was not recorded as a gain: {verdict['gains']}")
    assert not verdict["regressions"]
    assert verdict["ok"] is True


def test_a_non_instrument_field_is_still_judged_across_an_instrument_change(cron):
    """`tests` is not produced by a measurement instrument, so it stays comparable."""
    prev = {"_code_version": "OLD", "tests": 650}
    cur = {"_code_version": "NEW", "tests": 640}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert [x["field"] for x in verdict["regressions"]] == ["tests"], (
        "a test-count drop was excused by an instrument change; only instrument-dependent fields "
        "should be exempt")


def test_an_unprovable_instrument_match_is_NOT_compared(cron):
    """THE UNSAFE DEFAULT: a snapshot with no `_code_version` was compared anyway.

    Replaying the actual failing comparison: the older run record has no `_code_version` at all, so
    "no evidence of a change" was read as "no change" and the +0.002 anchor move was reported as a
    capability regression. Absence of proof that the instruments match is a reason NOT to compare --
    the same rule as treating a missing measurement as not-passed rather than passed.
    """
    prev = {"benchmark_anchor_single": 0.355}                       # no version at all
    cur = {"_code_version": "NEW", "benchmark_anchor_single": 0.357}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert verdict["instrument_changed"] is True, (
        "an unprovable instrument match was treated as a match")
    assert not verdict["regressions"]
    assert verdict["ok"] is True


def test_a_missing_version_on_EITHER_SIDE_blocks_the_comparison(cron):
    """ASYMMETRY IS EVIDENCE: if one side records an instrument and the other does not, the
    recording layer changed between them, so the values are not comparable.

    The case that actually failed is exactly this one: the old scheduled run predates the field, so
    its snapshot has no `_code_version` while the new one does.
    """
    for prev, cur in (
        ({"benchmark_anchor_single": 0.355}, {"_code_version": "N", "benchmark_anchor_single": 0.357}),
        ({"_code_version": "N", "benchmark_anchor_single": 0.355}, {"benchmark_anchor_single": 0.357}),
    ):
        verdict = cron.capability_delta(prev, cur)["verdict"]
        assert verdict["instrument_changed"] is True, (
            f"a one-sided instrument record was treated as a match: {prev} vs {cur}")
        assert not verdict["regressions"]


def test_neither_side_recording_an_instrument_is_a_plain_comparison(cron):
    """NO INSTRUMENT INFORMATION AT ALL is not evidence of a change.

    A caller passing two plain dicts -- a unit test, a hand check -- has not recorded instruments.
    Treating that as a change makes capability_delta unusable outside the scheduled loop, and it
    broke six existing tests when an earlier version did exactly that. The tests were right.
    """
    prev = {"benchmark_anchor_single": 0.355}
    cur = {"benchmark_anchor_single": 0.357}
    verdict = cron.capability_delta(prev, cur)["verdict"]
    assert verdict["instrument_changed"] is False
    assert [x["field"] for x in verdict["regressions"]] == ["benchmark_anchor_single"], (
        "with no instrument information the comparison must proceed normally")
