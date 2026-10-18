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


def test_a_capability_loss_is_a_regression_not_a_footnote():
    """The loop must FAIL when a judged capability field gets worse.

    WHY: recording "benchmark_ok: 23" after a previous "26" is not a control. The verdict has
    to name the loss and main() has to exit non-zero, otherwise a run that lost capability
    reports success.
    """
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    prev = {"benchmark_ok": 26, "benchmark_tasks": 30, "skills": 12,
            "benchmark_anchor_distance": 0.28, "tests": 229}
    cur = {"benchmark_ok": 23, "benchmark_tasks": 30, "skills": 12,
           "benchmark_anchor_distance": 0.31, "tests": 229}
    out = cron.capability_delta(prev, cur)
    verdict = out["verdict"]
    assert verdict["ok"] is False
    fields = {r["field"] for r in verdict["regressions"]}
    assert fields == {"benchmark_ok", "benchmark_anchor_distance"}
    assert out["changed"] is True


def test_an_improvement_is_recorded_as_a_gain():
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    out = cron.capability_delta({"skills": 12, "operators": 16},
                                {"skills": 13, "operators": 16})
    assert out["verdict"]["ok"] is True
    assert [g["field"] for g in out["verdict"]["gains"]] == ["skills"]


def test_a_lower_distance_counts_as_improvement():
    """Lower style distance is better; the direction table must not treat it as a loss."""
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    out = cron.capability_delta({"benchmark_anchor_distance": 0.31},
                                {"benchmark_anchor_distance": 0.28})
    assert out["verdict"]["ok"] is True
    assert [g["field"] for g in out["verdict"]["gains"]] == ["benchmark_anchor_distance"]


def test_the_raw_benchmark_mean_is_not_judged():
    """A growing task set moves the mean; that is a property of the measurement, not of the
    capability, so it must never produce a regression."""
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    out = cron.capability_delta({"benchmark_mean_distance": 0.278},
                                {"benchmark_mean_distance": 0.302})
    assert out["verdict"]["ok"] is True
    assert out["verdict"]["regressions"] == []


def test_unjudged_fields_never_count_as_gains_or_regressions():
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    out = cron.capability_delta({"mystery": 1}, {"mystery": 0})
    assert out["changed"] is True
    assert out["verdict"]["ok"] is True
    assert out["verdict"]["gains"] == [] and out["verdict"]["regressions"] == []


def test_a_scheduled_commit_may_not_delete_evidence():
    """A scheduled run deleted the whole seed package once and called it "no knowledge change".

    The publisher stages with `git add -A`, so a missing file becomes an intended deletion.
    `deletion_problems()` must refuse that, and it must NOT block ordinary modifications.
    """
    import subprocess
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    repo = ROOT
    # a real staged deletion inside a protected prefix
    target = repo / "templates" / "transfer" / "style_transfer_best.png"
    if not target.is_file():
        import pytest
        pytest.skip("protected fixture missing")
    subprocess.run(["git", "rm", "--cached", "-q", "--force",
                    str(target.relative_to(repo))], cwd=repo, check=False)
    try:
        blocked = cron.deletion_problems()
        assert any(p.endswith("style_transfer_best.png") for p in blocked), blocked
    finally:
        subprocess.run(["git", "reset", "-q", "--",
                        str(target.relative_to(repo))], cwd=repo, check=False)
    assert cron.deletion_problems() == []


def test_the_anchor_metric_is_stable_when_the_task_set_grows():
    """A growing benchmark must not look like a capability regression.

    On 2026-10-19 the loop reported one: 0.278 over 30 tasks -> 0.302 over 66. Nothing about the
    pipeline had changed; the SET had. The judged metric is now the mean over a fixed, sorted
    subset (ANCHOR_N), which only moves when those tasks' results move.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    small = [{"id": f"t{i:02d}", "status": "ok", "distance": 0.30} for i in range(20)]
    grown = small + [{"id": f"u{i:02d}", "status": "ok", "distance": 0.90} for i in range(40)]
    assert bench._anchor_distance(small) == bench._anchor_distance(grown) == 0.3
    worse = [dict(t, distance=0.40) for t in small]
    assert bench._anchor_distance(worse) == 0.4
    assert bench._anchor_distance(small[:3]) is None
