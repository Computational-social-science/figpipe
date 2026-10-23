r"""A skip is an environment fact, not a capability loss.

WHY THIS EXISTS
    On 2026-10-24 the scheduled run exited 1 and reported:

        capability_regressions: [{'field': 'tests', 'before': 854, 'after': 853}]

    The suite had not shrunk. It went `854 passed, 2 skipped` -> `853 passed, 3 skipped`: 856 tests
    collected both times, one of them started skipping because a precondition was unavailable.

THE MECHANISM
    The field was parsed as `re.search(r"(\d+) passed", tail)` -- PASSED ONLY. So any test that moves
    from passing to skipping reads as a test that disappeared, and the capability delta calls it a
    regression.

WHY THAT IS A DEFECT AND NOT A NUANCE
    A count that moves when the ENVIRONMENT changes is not a capability. Reporting it as one teaches
    the reader to distrust the field -- and this project has already spent rounds on exactly that
    shape (a zero that was the instrument's, a distance read as a score).

THE FIX
    `tests` is the collected total: passed + skipped. The passed count is recorded separately as
    `tests_passed`, so a genuine failure is still legible from the record.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def cron():
    import cron_run
    return cron_run


def _total(tail: str) -> int | None:
    """The parsing rule, extracted so it can be tested without running the suite."""
    passed = re.search(r"(\d+) passed", tail or "")
    skipped = re.search(r"(\d+) skipped", tail or "")
    if not passed:
        return None
    return int(passed.group(1)) + (int(skipped.group(1)) if skipped else 0)


def test_a_skip_does_not_look_like_a_lost_test():
    """THE EXACT CASE. Same collected total, different split."""
    a = _total("854 passed, 2 skipped, 1 warning in 359.01s")
    b = _total("853 passed, 3 skipped, 1 warning in 357.77s")
    assert a == b == 856, f"a skip changed the total: {a} vs {b}"


def test_a_real_failure_still_changes_the_total():
    """THE OTHER DIRECTION. If a test is genuinely removed, the total must fall."""
    a = _total("856 passed, 0 skipped in 100s")
    b = _total("855 passed, 0 skipped in 100s")
    assert b < a, "removing a test did not change the total"


def test_no_skips_parses_cleanly():
    assert _total("10 passed in 1s") == 10


def test_an_unparseable_tail_returns_none():
    assert _total("") is None
    assert _total("no tests ran") is None


def test_the_snapshot_records_the_passed_count_separately(cron):
    """A GENUINE FAILURE MUST STILL BE LEGIBLE. The total alone cannot distinguish 'one more skip'
    from 'one fewer test', so the passed count is kept."""
    src = pathlib.Path(cron.__file__).read_text(encoding="utf-8")
    assert "tests_passed" in src, (
        "the run record does not carry the passed count, so a real failure cannot be told from a skip")
    assert r"(\d+) skipped" in src or "(\\d+) skipped" in src, (
        "the skipped count is not parsed, so the total cannot include it")


def test_the_capability_direction_still_judges_tests(cron):
    """The field is still a capability signal -- it is the COUNT that was wrong, not the intent."""
    assert "tests" in cron.CAPABILITY_DIRECTION
    assert cron.CAPABILITY_DIRECTION["tests"] == +1
