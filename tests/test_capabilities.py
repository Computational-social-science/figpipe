"""The scheduled run must measure capability, not only self-consistency.

WHY THIS TEST
    The review found that 27 scheduled runs changed knowledge only 4 times and could not show
    whether the project had gained any capability. `capability_snapshot()` reads capability
    artefacts (skills, benchmark results, reproduction statistics) and `capability_delta()` makes
    the change explicit, so a run can say "nothing changed" or name what changed.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

cron = None
try:
    import cron_run as cron
except Exception:                        # pragma: no cover - optional env
    cron = None


def test_snapshot_reads_capability_artefacts_without_opinions():
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    snap = cron.capability_snapshot()
    for key in ("skills", "operators", "benchmark_tasks", "benchmark_ok",
                "benchmark_mean_distance", "statistics_reproduced", "knowledge_version",
                "tests"):
        assert key in snap
    assert isinstance(snap["skills"], int) and snap["skills"] >= 0
    assert isinstance(snap["operators"], int) and snap["operators"] >= 0
    assert isinstance(snap["benchmark_tasks"], int)
    # a capability snapshot must not contain prose judgements
    for value in snap.values():
        assert not isinstance(value, str) or key == "knowledge_version"


def test_delta_names_what_changed_and_reports_no_change():
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    base = {"skills": 12, "operators": 16, "tests": 225}
    assert cron.capability_delta(base, dict(base))["changed"] is False
    nxt = dict(base, skills=13, tests=230)
    d = cron.capability_delta(base, nxt)
    assert d["changed"] is True
    assert d["delta"]["skills"] == {"before": 12, "after": 13}
    assert d["delta"]["tests"] == {"before": 225, "after": 230}
    assert "operators" not in d["delta"]
