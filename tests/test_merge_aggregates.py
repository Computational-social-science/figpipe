"""A merged report must be internally consistent: every aggregate over the WHOLE set.

WHY THIS TEST
    The merge recomputed `n_ok`, `by_type`, the means and the anchors over the merged task list --
    but left `failures`, `unsupported_types` and `semantic_violations` as computed over the SLICE.
    A 6-task scheduled slice therefore rewrote the report's failure list to the slice's failures,
    erasing 11 deliberate unsupported tasks from the record and dropping semantic_violations 8 -> 0.

    A partial recompute is worse than none: the report LOOKS internally consistent and is not. This
    is the same defect family as the mixed-instrument anchors -- an aggregate that describes a
    different set than the one it sits next to.
"""
from __future__ import annotations

import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "corpus" / "e2e" / "plottwin_report.json"


def _load() -> dict:
    if not REPORT.is_file():
        pytest.skip("report absent")
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_the_failure_list_matches_the_task_list():
    """Every non-ok task appears in `failures`, and nothing else does."""
    data = _load()
    tasks = data.get("tasks") or []
    if not tasks:
        pytest.skip("no tasks")
    expected = {t["id"] for t in tasks if t.get("status") != "ok"}
    recorded = {f["id"] for f in (data.get("failures") or [])}
    assert recorded == expected, (
        f"failures {sorted(recorded)[:3]}... does not match the non-ok tasks "
        f"{sorted(expected)[:3]}...; a merge recomputed one and not the other")


def test_unsupported_types_matches_the_unsupported_tasks():
    data = _load()
    tasks = data.get("tasks") or []
    uns = [t for t in tasks if t.get("status") == "unsupported"]
    recorded = data.get("unsupported_types") or {}
    assert set(recorded) == {t.get("chart") for t in uns}, (
        "unsupported_types does not describe the unsupported tasks in the report")


def test_the_counts_add_up():
    """n_ok + n_unsupported + n_error must equal n_tasks, or a number describes another set."""
    data = _load()
    tasks = data.get("tasks") or []
    if not tasks:
        pytest.skip("no tasks")
    n_ok = sum(1 for t in tasks if t.get("status") == "ok")
    n_uns = sum(1 for t in tasks if t.get("status") == "unsupported")
    n_err = len(tasks) - n_ok - n_uns
    assert data.get("n_tasks") == len(tasks)
    assert data.get("n_ok") == n_ok
    assert data.get("n_unsupported") == n_uns
    assert data.get("n_error") == n_err


def test_semantic_violations_counts_the_whole_report():
    data = _load()
    tasks = data.get("tasks") or []
    if not tasks:
        pytest.skip("no tasks")
    expected = sum(1 for t in tasks
                   if t.get("status") == "ok" and t.get("semantic_findings"))
    assert data.get("semantic_violations") == expected, (
        f"semantic_violations is {data.get('semantic_violations')} but the tasks carry {expected}; "
        f"a merge recomputed one and not the other")


def test_the_merge_recomputes_every_aggregate():
    """Structural check: the merge block must assign each aggregate, not inherit it."""
    src = (ROOT / "scripts" / "bench_plottwin.py").read_text(encoding="utf-8")
    i = src.find("if args.merge and OUT.is_file():")
    assert i > 0, "the merge block is gone"
    block = src[i:i + 4000]
    for key in ("failures", "unsupported_types", "semantic_violations",
                "n_ok", "n_unsupported", "n_error", "by_type"):
        assert f'report["{key}"]' in block, (
            f"the merge does not recompute {key!r}; a slice would overwrite it with the slice's value")
