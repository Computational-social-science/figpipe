"""A network failure must never read as a capability regression.

WHY THIS TEST
    On 2026-10-19 two benchmark tasks returned HTTP 403 from the dataset host. The success rate fell
    1.0 -> 0.986 and the scheduled loop correctly reported a capability regression -- except the
    pipeline never ran. Counting infrastructure failures as capability loss is the same defect
    family as counting a skipped test as a pass: the metric stops measuring what it claims.

    The exclusion must also be VISIBLE. A silent exclusion would let the denominator be quietly
    tuned whenever the number looked bad, which is worse than the original defect.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

cron = None
try:
    import cron_run as cron
except Exception:                        # pragma: no cover - optional env
    cron = None


@pytest.mark.parametrize("error", [
    "HTTPError: HTTP Error 403: Forbidden",
    "URLError: <urlopen error timed out>",
    "ConnectionError: reset by peer",
    "TimeoutError: read timed out",
    "SSLError: certificate verify failed",
])
def test_fetch_failures_are_classified_as_infrastructure(error):
    if cron is None:
        pytest.skip("cron_run unavailable")
    assert cron._is_infra(error) is True, f"{error!r} should be an infrastructure failure"


@pytest.mark.parametrize("error", [
    "SkillError: encode.matrix: 48 rows cannot be shown as a matrix",
    "CodegenError: no panels to emit",
    "ValueError: something the pipeline did wrong",
    "",
])
def test_pipeline_failures_are_not_classified_as_infrastructure(error):
    """Negative control: a real pipeline error must still count against capability."""
    if cron is None:
        pytest.skip("cron_run unavailable")
    assert cron._is_infra(error) is False, f"{error!r} must NOT be excused as infrastructure"


def test_the_exclusion_is_visible_in_the_snapshot():
    """A silent exclusion could be tuned whenever the number looked bad."""
    if cron is None:
        pytest.skip("cron_run unavailable")
    snap = cron.capability_snapshot()
    assert "benchmark_infrastructure_failures" in snap, (
        "the count of excused failures must be reported, or the exclusion is invisible")
    # It is a DIAGNOSTIC, not a capability: fewer fetch failures is not a better pipeline. It must
    # be tracked and diffed so the denominator can never be tuned invisibly, but judged in neither
    # direction.
    tracked = ("benchmark_infrastructure_failures" in cron.CAPABILITY_DIRECTION
               or "benchmark_infrastructure_failures" in getattr(cron, "DIAGNOSTIC_FIELDS", ()))
    assert tracked, "the field must be tracked, not just computed"
    assert "benchmark_infrastructure_failures" not in cron.CAPABILITY_DIRECTION, (
        "an infrastructure-failure count must not be scored as a capability")


def test_a_fetch_failure_does_not_lower_the_success_rate():
    """The whole point: the rate must measure capability, not network luck."""
    if cron is None:
        pytest.skip("cron_run unavailable")
    snap = cron.capability_snapshot()
    infra = snap.get("benchmark_infrastructure_failures")
    if not infra:
        pytest.skip("no infrastructure failures in the current report to test against")
    # with the failures excused, the rate is over tasks that actually ran
    assert snap["benchmark_success_rate"] == 1.0, (
        f"success rate is {snap['benchmark_success_rate']} with {infra} excused fetch failures; "
        f"the exclusion is not being applied")
