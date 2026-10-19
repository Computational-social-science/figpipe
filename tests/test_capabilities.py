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
    prev = {"benchmark_success_rate": 0.95, "skills": 12,
            "benchmark_anchor_distance": 0.28, "tests": 229}
    cur = {"benchmark_success_rate": 0.80, "skills": 12,
           "benchmark_anchor_distance": 0.31, "tests": 229}
    out = cron.capability_delta(prev, cur)
    verdict = out["verdict"]
    assert verdict["ok"] is False
    fields = {r["field"] for r in verdict["regressions"]}
    assert fields == {"benchmark_success_rate", "benchmark_anchor_distance"}
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
    pipeline had changed; the SET had. The anchor is now a FROZEN list of task ids, so growth
    cannot move it.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    ids = bench.anchor_ids([])           # reads the frozen file
    if len(ids) < 5:
        import pytest
        pytest.skip("anchor file not initialised")
    base = [{"id": i, "status": "ok", "distance": 0.30} for i in ids]
    grown = base + [{"id": f"zz{i:03d}", "status": "ok", "distance": 0.90} for i in range(40)]
    assert bench._anchor_distance(base) == bench._anchor_distance(grown) == 0.3
    worse = [dict(t, distance=0.40) for t in base]
    assert bench._anchor_distance(worse) == 0.4
    assert bench._anchor_distance(base[:3]) is None


def test_the_anchor_ids_are_frozen_not_recomputed():
    """"First N sorted ids" is NOT stable: newly measured tasks that sort earlier enter the set
    and move the anchor with no capability change (observed 0.297 -> 0.329 on a coverage-only run).

    The ids are persisted in knowledge/benchmark_anchor.json and reused forever.
    """
    import sys, json
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    ids = json.loads((ROOT / "knowledge" / "benchmark_anchor.json").read_text(encoding="utf-8"))["ids"]
    # a report containing the anchor plus a NEW id that sorts first must not change the anchor
    tasks = [{"id": i, "status": "ok", "distance": 0.30} for i in ids]
    tasks.append({"id": "AAA-newly-measured", "status": "ok", "distance": 0.90})
    assert bench.anchor_ids(tasks) == ids
    assert bench._anchor_distance(tasks) == 0.3


def test_the_shipped_distance_is_judged_on_a_frozen_subset():
    """The selection step is a capability, and its metric must be both judged and stable.

    The FULL-SET shipped mean moves whenever a task is added (0.257 -> 0.258 on a coverage-only
    run, a false regression). The judged field is therefore the frozen-subset version, exactly as
    for the always-styled anchor.
    """
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    # the JUDGED field is the single-instrument view; the all-rows value mixes fingerprints and is
    # recorded but never judged (see test_a_metric_mixing_instruments_is_not_comparable)
    assert cron.CAPABILITY_DIRECTION.get("benchmark_shipped_anchor_single") == -1
    assert "benchmark_shipped_anchor_distance" not in cron.CAPABILITY_DIRECTION
    assert "benchmark_shipped_distance" not in cron.CAPABILITY_DIRECTION
    snap = cron.capability_snapshot()
    assert "benchmark_shipped_anchor_single" in snap
    better = cron.capability_delta({"benchmark_shipped_anchor_single": 0.278},
                                   {"benchmark_shipped_anchor_single": 0.259})
    assert better["verdict"]["ok"] is True
    worse = cron.capability_delta({"benchmark_shipped_anchor_single": 0.259},
                                  {"benchmark_shipped_anchor_single": 0.300})
    assert worse["verdict"]["ok"] is False


def test_the_shipped_anchor_is_frozen_and_ignores_new_tasks():
    import sys, json
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    ids = bench.shipped_anchor_ids([])
    if len(ids) < 5:
        import pytest
        pytest.skip("shipped anchor not initialised")
    base = [{"id": i, "status": "ok", "distance": 0.4, "selected_distance": 0.30} for i in ids]
    grown = base + [{"id": f"zz{i}", "status": "ok", "distance": 0.9,
                     "selected_distance": 0.90} for i in range(30)]
    assert bench._shipped_anchor_distance(base) == bench._shipped_anchor_distance(grown) == 0.3


def test_the_benchmark_slice_walks_forward_instead_of_re_measuring():
    """Coverage must advance: re-measuring covered tasks looks busy and grows nothing."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    covered = bench.covered_offsets()
    assert isinstance(covered, set)
    # coverage is defined by the REPORT, so it must survive pruning the cache entirely
    seen = bench.measured_ids()
    assert isinstance(seen, set)
    nxt = bench.next_uncovered_offset(6)
    assert 0 <= nxt < bench.POOL
    window = set(range(nxt, min(nxt + 6, bench.POOL)))
    if seen and covered:
        assert not window.issubset(covered) or nxt == 0


def test_stale_rows_are_detectable_not_guessed():
    """Rows rendered before a fix must be identifiable as stale.

    Field 2D and Heatmap both looked like operator failures because their rows predated the
    canvas-width fix. Each row now records the fingerprint of the rendering code, so staleness is a
    queryable fact instead of a suspicion.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    assert len(bench.CODE_VERSION) == 12
    # the fingerprint must cover RENDERING code only: including the harness invalidated every row
    # on every edit and turned the signal into noise
    src = (ROOT / "scripts" / "bench_plottwin.py").read_text(encoding="utf-8")
    fp_block = src[src.index("def _code_version"):src.index("CODE_VERSION = _code_version()")]
    assert "bench_plottwin.py" not in fp_block.split("for rel in")[1].split("):")[0]
    fresh = [{"id": "a", "status": "ok", "code_version": bench.CODE_VERSION}]
    old = [{"id": "b", "status": "ok", "code_version": "deadbeef1234"}]
    missing = [{"id": "c", "status": "ok"}]                 # predates the field
    unsupported = [{"id": "d", "status": "unsupported"}]
    assert bench.stale_tasks(fresh) == []
    assert bench.stale_tasks(old) == ["b"]
    assert bench.stale_tasks(unsupported) == []
    assert bench.stale_tasks(fresh + old) == ["b"]
    # UNKNOWN IS NOT STALE. A row without a recorded version may well have been rendered by the
    # current code; reporting it as stale made 117 of 141 rows permanently "stale".
    f = bench.freshness(fresh + old + missing + unsupported)
    assert f["n_fresh"] == 1 and f["n_stale"] == 1 and f["n_unknown"] == 1
    assert bench.stale_tasks(missing) == []


def test_every_judged_field_is_actually_measured():
    """A field in CAPABILITY_DIRECTION that the snapshot never returns is never judged.

    This is the recurring "control that looks present and does nothing" defect. It happened again:
    benchmark_official_code_score was added to the direction table but not to the snapshot, so the
    loop could never have noticed a change in it.
    """
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    snap = cron.capability_snapshot()
    missing = [k for k in cron.CAPABILITY_DIRECTION if k not in snap]
    assert not missing, (
        f"these fields are judged but the snapshot never emits them: {missing}")


def test_the_official_score_is_recorded_and_judged():
    """The benchmark's own channel is the closest thing to an external measure we have."""
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    snap = cron.capability_snapshot()
    assert "benchmark_official_code_score" in snap
    assert cron.CAPABILITY_DIRECTION["benchmark_official_code_score"] == +1
    better = cron.capability_delta({"benchmark_official_code_score": 88.0},
                                   {"benchmark_official_code_score": 92.68})
    assert better["verdict"]["gains"][0]["field"] == "benchmark_official_code_score"
    # a drop on this field is a DOCUMENTED CORRECTION (the measurement became honest), so it is
    # reported as a correction with its reason rather than as a capability loss
    worse = cron.capability_delta({"benchmark_official_code_score": 92.68},
                                  {"benchmark_official_code_score": 80.0})
    assert worse["verdict"]["ok"] is True
    assert worse["verdict"]["corrections"][0]["field"] == "benchmark_official_code_score"


def test_the_capability_uses_the_honest_official_pass_not_the_harness_aggregate():
    """One concept, one number.

    The harness computes its own official mean over whichever tasks happen to carry reference_code
    in the current cache (it read 93.53), while the dedicated pass measures the whole pool with
    image-inferred style (70.59). The capability must read the honest pass, or the loop tracks a
    number that drifts with cache contents.
    """
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    import json
    path = ROOT / "corpus" / "e2e" / "official_scores.json"
    if not path.is_file():
        import pytest
        pytest.skip("official pass absent")
    summary = json.loads(path.read_text(encoding="utf-8")).get("summary", {})
    if summary.get("style_source") != "image":
        import pytest
        pytest.skip("official pass is not the image-inferred one")
    snap = cron.capability_snapshot()
    assert snap["benchmark_official_code_score"] == summary["mean_score"]


def test_a_documented_correction_is_not_a_regression():
    """The official score fell 93.53 -> 70.59 because the measurement became honest.

    That is a correction, not a capability loss. It must be reported as a correction WITH its
    reason, while a genuine regression on the same field still fails the run.
    """
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    out = cron.capability_delta({"benchmark_official_code_score": 93.53},
                                {"benchmark_official_code_score": 70.59})
    verdict = out["verdict"]
    assert verdict["ok"] is True
    assert verdict["regressions"] == []
    assert verdict["corrections"][0]["field"] == "benchmark_official_code_score"
    assert "honest" in verdict["corrections"][0]["why"]
    # a field WITHOUT a documented correction still fails
    bad = cron.capability_delta({"benchmark_success_rate": 0.95},
                                {"benchmark_success_rate": 0.80})
    assert bad["verdict"]["ok"] is False


def test_a_metric_mixing_instruments_is_not_comparable():
    """A frozen task set is not enough -- the rows inside it must come from ONE instrument.

    The shipped anchor moved 0.252 -> 0.243 when only 3 of its 20 tasks had been re-measured after
    a styleprofile fix. The mean moved because the INSTRUMENT changed, not the capability. The
    single-instrument view must report non-comparable rather than a small-sample number.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        pytest.skip("benchmark harness unavailable")
    import json
    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not path.is_file():
        pytest.skip("report absent")
    tasks = json.loads(path.read_text(encoding="utf-8"))["tasks"]
    info = bench._shipped_anchor_single_instrument(tasks)
    for key in ("mean", "partial_mean", "n_same_instrument", "n_other_instrument",
                "comparable", "note"):
        assert key in info
    if not info["comparable"]:
        assert info["mean"] is None, (
            "a non-comparable metric must be None, not a small-sample number that reads as a gain")
        assert "not comparable" in info["note"]
    if cron is not None:
        assert "benchmark_shipped_anchor_single" in cron.CAPABILITY_DIRECTION
        # the mixed all-rows value must never be judged
        assert "benchmark_shipped_anchor_distance" not in cron.CAPABILITY_DIRECTION


def test_the_anchor_can_be_restored_to_one_instrument():
    """A non-comparable anchor must be fixable, not merely reported.

    `--ids` re-measures exactly the frozen anchor tasks. Without it the only options were scanning
    whole chart types (more work, no guarantee of covering the anchor) or accepting a permanent
    "—". The coverage index maps id -> offset, and it must survive cache pruning.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        pytest.skip("benchmark harness unavailable")
    cov = bench._read_coverage()
    if not cov:
        pytest.skip("coverage index empty in this checkout")
    assert all(isinstance(k, int) for k in list(cov)[:5])
    assert all(isinstance(v, str) for v in list(cov.values())[:5])
    # every anchor id must be locatable, or the targeted refresh cannot work
    import json
    anchor = json.loads((ROOT / "knowledge" / "benchmark_shipped_anchor.json")
                        .read_text(encoding="utf-8"))["ids"]
    by_id = {task_id: off for off, task_id in cov.items()}
    missing = [a for a in anchor if a not in by_id]
    assert not missing, f"anchor tasks not locatable: {missing[:3]}"


def test_refresh_anchor_is_a_no_op_when_already_comparable():
    """The loop must not re-measure 20 tasks every six hours for nothing."""
    if cron is None:
        import pytest
        pytest.skip("cron_run unavailable")
    import json
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        pytest.skip("report absent")
    single = (json.loads(report.read_text(encoding="utf-8"))
              .get("benchmark_shipped_anchor_single") or {})
    if not single.get("comparable"):
        pytest.skip("anchor currently non-comparable; nothing to assert")
    out = cron.refresh_anchor()
    assert out["ran"] is False
    assert "already comparable" in out["reason"]
