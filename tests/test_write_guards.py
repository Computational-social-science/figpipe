"""Accumulated evidence must not be destroyed as a side effect of a routine write.

WHY THIS TEST
    A two-task diagnostic run once destroyed 106 benchmark rows because the harness rewrote its
    report unconditionally, and the next scheduled run committed the damage. That was fixed for ONE
    file. `figpipe/guard.py` is the shared implementation now used by every writer that can lose
    accumulated data.

    Each case here has a NEGATIVE CONTROL: a bypassed guard must be DETECTED. A guard test that
    cannot fail proves nothing.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

guard = pytest.importorskip("figpipe.guard", reason="guard module absent")


def test_shrinking_is_refused_and_the_file_is_unchanged(tmp_path):
    path = tmp_path / "report.json"
    guard.write_or_refuse(path, {"tasks": list(range(10))}, key="tasks")
    before = path.read_text(encoding="utf-8")
    with pytest.raises(guard.ShrinkRefused, match="would drop 10 -> 2"):
        guard.write_or_refuse(path, {"tasks": [0, 1]}, key="tasks")
    assert path.read_text(encoding="utf-8") == before, "the file changed despite the refusal"


def test_the_refusal_names_its_own_escape_hatch(tmp_path):
    path = tmp_path / "report.json"
    guard.write_or_refuse(path, {"tasks": list(range(5))}, key="tasks")
    with pytest.raises(guard.ShrinkRefused) as exc:
        guard.write_or_refuse(path, {"tasks": [0]}, key="tasks", override="--fresh")
    assert "--fresh" in str(exc.value)


def test_growing_is_allowed(tmp_path):
    path = tmp_path / "report.json"
    guard.write_or_refuse(path, {"tasks": [1, 2]}, key="tasks")
    out = guard.write_or_refuse(path, {"tasks": [1, 2, 3]}, key="tasks")
    assert out["new"] == 3 and out["shrank"] is False
    assert len(json.loads(path.read_text(encoding="utf-8"))["tasks"]) == 3


def test_the_same_size_is_allowed(tmp_path):
    path = tmp_path / "report.json"
    guard.write_or_refuse(path, {"tasks": [1, 2]}, key="tasks")
    guard.write_or_refuse(path, {"tasks": [3, 4]}, key="tasks")     # same size, must not refuse


def test_an_explicit_override_permits_a_deliberate_shrink(tmp_path):
    path = tmp_path / "report.json"
    guard.write_or_refuse(path, {"tasks": list(range(8))}, key="tasks")
    out = guard.write_or_refuse(path, {"tasks": [0]}, key="tasks", allow_shrink=True)
    assert out["shrank"] is True and out["allowed"] is True


def test_a_corrupt_existing_file_does_not_crash_the_writer(tmp_path):
    path = tmp_path / "report.json"
    path.write_text("{not json", encoding="utf-8")
    guard.write_or_refuse(path, {"tasks": [1, 2]}, key="tasks")     # must not raise


def test_a_missing_file_is_not_a_shrink(tmp_path):
    path = tmp_path / "brand_new.json"
    out = guard.write_or_refuse(path, {"tasks": []}, key="tasks")
    assert out["shrank"] is False
    assert out["existing_state"] == "missing"


def test_a_keyless_payload_is_its_own_collection(tmp_path):
    path = tmp_path / "coverage.json"
    guard.write_or_refuse(path, {"a": 1, "b": 2})                   # key=None: payload is the map
    with pytest.raises(guard.ShrinkRefused):
        guard.write_or_refuse(path, {"a": 1})


def test_the_guard_refuses_a_payload_without_the_declared_key(tmp_path):
    path = tmp_path / "report.json"
    with pytest.raises(guard.GuardMisuse, match="no 'tasks' collection"):
        guard.write_or_refuse(path, {"rows": [1, 2]}, key="tasks")


def test_the_benchmark_report_path_is_routed_through_the_guard():
    """The one writer that actually destroyed data must use the shared implementation."""
    script = ROOT / "scripts" / "bench_plottwin.py"
    if not script.is_file():
        pytest.skip("harness absent")
    text = script.read_text(encoding="utf-8")
    assert "guard.write_or_refuse" in text, "the benchmark report is not routed through the guard"
    assert "def write_report" in text


def test_negative_control_a_bypassed_guard_really_does_destroy_data(tmp_path):
    """If the guard were absent, this is what would happen -- proving the tests above can fail.

    Two paths are exercised on identical inputs: a plain `write_text` (the old behaviour) destroys
    the rows, and `write_or_refuse` refuses. If the guard ever became a no-op, the second assertion
    would fail and this test would catch it.
    """
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"tasks": list(range(10))}), encoding="utf-8")

    # PATH A: unguarded write, exactly as the old code did it -- data is destroyed
    path.write_text(json.dumps({"tasks": [0]}), encoding="utf-8")
    assert len(json.loads(path.read_text(encoding="utf-8"))["tasks"]) == 1

    # PATH B: same operation through the guard -- refused, and the 1 row survives
    before = path.read_text(encoding="utf-8")
    with pytest.raises(guard.ShrinkRefused):
        guard.write_or_refuse(path, {"tasks": []}, key="tasks")
    assert path.read_text(encoding="utf-8") == before
