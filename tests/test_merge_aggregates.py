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
    # FIND THE BLOCK BY INDENTATION, NOT BY A CHARACTER COUNT. A fixed window reported a
    # real-looking failure when a comment pushed one assignment 29 characters past the edge --
    # a test that breaks when unrelated text changes is measuring the text, not the code.
    lines = src[i:].splitlines()
    block_lines = [lines[0]]
    base_indent = len(lines[0]) - len(lines[0].lstrip())
    for line in lines[1:]:
        if line.strip() and (len(line) - len(line.lstrip())) <= base_indent:
            break
        block_lines.append(line)
    block = "\n".join(block_lines)
    assert len(block) > 500, f"the merge block looks empty: {len(block)} chars"
    for key in ("failures", "unsupported_types", "semantic_violations",
                "n_ok", "n_unsupported", "n_error", "by_type"):
        assert f'report["{key}"]' in block, (
            f"the merge does not recompute {key!r}; a slice would overwrite it with the slice's value")


def test_the_task_list_is_order_stable():
    """A merge must not reorder the array, or every slice rewrites the whole file.

    `old_tasks - seen + new` appended freshly measured tasks to the END, so a 6-task slice moved
    six entries and produced a 150-row diff with ZERO content change. That is noise in a history
    whose whole value is that a diff means something.
    """
    data = _load()
    ids = [t["id"] for t in (data.get("tasks") or [])]
    if not ids:
        pytest.skip("no tasks")
    assert ids == sorted(ids), (
        "the task list is not sorted by id; a slice will produce a large diff with no content "
        "change")


def test_a_slice_does_not_move_tasks():
    """Structural: the merge must sort, so re-measured rows stay in place."""
    src = (ROOT / "scripts" / "bench_plottwin.py").read_text(encoding="utf-8")
    i = src.find("merged = [t for t in old_tasks")
    assert i > 0, "the merge block is gone"
    window = src[i:i + 400]
    assert ".sort(" in window, (
        "the merge does not sort the merged list; re-measured tasks will move to the end and "
        "rewrite the whole array")
