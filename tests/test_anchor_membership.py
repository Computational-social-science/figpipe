"""A partial anchor is not the anchor.

WHY THIS TEST
    At 2026-10-19T16:25 two anchor tasks had errored on a transient HTTP 403, so 18 of 20 rows were
    present and the shipped-anchor mean came out 0.289. The loop read that as an IMPROVEMENT over
    0.296 -- and then read the restoration as a REGRESSION. An anchor whose membership changes with
    network luck is not a frozen task set, which is the entire reason anchors exist.

    The rule: an anchor mean is judged only when EVERY anchor task is present AND on the current
    instrument. A partial mean may be reported, but never judged.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

bench = None
try:
    import bench_plottwin as bench
except Exception:                        # pragma: no cover - optional env
    bench = None


def _anchor_tasks(kind: str) -> tuple[list[str], list[dict]]:
    name = ("benchmark_shipped_anchor.json" if kind == "shipped" else "benchmark_anchor.json")
    ids = json.loads((ROOT / "knowledge" / name).read_text(encoding="utf-8"))["ids"]
    return ids, ids


def _fake(ids: list[str], *, drop: int = 0, stale: int = 0) -> list[dict]:
    """A task list where the first `drop` anchor rows are missing and the next `stale` are old."""
    tasks = []
    for i, tid in enumerate(ids):
        if i < drop:
            continue                       # absent entirely (a fetch failure)
        tasks.append({"id": tid, "status": "ok",
                      "distance": 0.2, "selected_distance": 0.2,
                      "code_version": (bench.CODE_VERSION if i >= drop + stale else "old")})
    return tasks


@pytest.mark.parametrize("kind", ["shipped", "styled"])
def test_a_complete_anchor_is_comparable(kind):
    if bench is None:
        pytest.skip("bench_plottwin unavailable")
    ids, _ = _anchor_tasks(kind)
    fn = (bench._shipped_anchor_single_instrument if kind == "shipped"
          else bench._anchor_single_instrument)
    out = fn(_fake(ids))
    assert out["comparable"] is True, out
    assert out["mean"] is not None
    assert out["n_same_instrument"] == len(ids)


@pytest.mark.parametrize("kind", ["shipped", "styled"])
def test_a_partial_anchor_is_not_judged(kind):
    """The defect: 18 of 20 rows produced a mean that moved with network luck."""
    if bench is None:
        pytest.skip("bench_plottwin unavailable")
    ids, _ = _anchor_tasks(kind)
    fn = (bench._shipped_anchor_single_instrument if kind == "shipped"
          else bench._anchor_single_instrument)
    out = fn(_fake(ids, drop=2))
    assert out["comparable"] is False, "a partial anchor must never be judged"
    assert out["mean"] is None, "a partial anchor must not report a judgeable mean"
    assert out["n_same_instrument"] == len(ids) - 2
    assert "incomplete" in out["note"]


@pytest.mark.parametrize("kind", ["shipped", "styled"])
def test_a_mixed_instrument_anchor_is_not_judged(kind):
    if bench is None:
        pytest.skip("bench_plottwin unavailable")
    ids, _ = _anchor_tasks(kind)
    fn = (bench._shipped_anchor_single_instrument if kind == "shipped"
          else bench._anchor_single_instrument)
    out = fn(_fake(ids, stale=3))
    assert out["comparable"] is False
    assert out["mean"] is None
    assert out["n_other_instrument"] == 3


def test_the_live_report_anchor_is_complete_or_unjudged():
    """Whatever the current state, a judged mean implies full membership."""
    if bench is None:
        pytest.skip("bench_plottwin unavailable")
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        pytest.skip("report absent")
    data = json.loads(report.read_text(encoding="utf-8"))
    for key in ("benchmark_anchor_single", "benchmark_shipped_anchor_single"):
        info = data.get(key) or {}
        if info.get("mean") is not None:
            assert info.get("n_same_instrument") == info.get("n_expected"), (
                f"{key} reports a judged mean {info.get('mean')} with only "
                f"{info.get('n_same_instrument')} of {info.get('n_expected')} tasks present")
