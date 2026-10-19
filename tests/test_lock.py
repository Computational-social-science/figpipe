"""Two measurements must not overlap, and the lock must never block the schedule.

WHY THIS TEST
    On 2026-10-19 a scheduled run and a 150-task benchmark pass shared this machine; timing-sensitive
    tests failed under load and the loop recorded a capability regression indistinguishable from a
    real defect. The mitigation written down was procedural -- "do not start a re-measure while the
    loop is due" -- and a procedural rule nothing enforces is not a control.

    `figpipe/lock.py` is the enforcement. These tests pin both halves: it must REFUSE a second
    measurement, and it must never block forever because of a crashed holder.

    The Windows liveness probe earned its own test: `os.kill(dead_pid, 0)` raises WinError 87 there
    (not ProcessLookupError), so the obvious implementation treats every dead pid as alive and a
    stale lock blocks the schedule forever. On this machine's exFAT volume the exception path itself
    raised KeyboardInterrupt, so the probe uses OpenProcess/GetExitCodeProcess instead.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

lock = pytest.importorskip("figpipe.lock", reason="lock module absent")


@pytest.fixture(autouse=True)
def _clean_lock():
    lock.LOCK_PATH.unlink(missing_ok=True)
    yield
    lock.LOCK_PATH.unlink(missing_ok=True)


def test_a_second_measurement_is_refused():
    with lock.measure("first"):
        assert lock.holder()["name"] == "first"
        with pytest.raises(lock.MeasurementBusy, match="another measurement is running"):
            with lock.measure("second"):
                pass
    assert lock.holder() is None


def test_a_released_lock_is_free():
    lock.acquire("a")
    lock.release("a")
    assert lock.holder() is None


def test_releasing_someone_elses_lock_is_refused():
    lock.LOCK_PATH.write_text(json.dumps({"name": "other", "pid": os.getpid()}), encoding="utf-8")
    with pytest.raises(lock.MeasurementBusy, match="refusing to release"):
        lock.release("mine")


def test_a_dead_pid_is_not_alive():
    assert lock._pid_alive(999999) is False
    assert lock._pid_alive(0) is False


def test_our_own_pid_is_alive():
    assert lock._pid_alive(os.getpid()) is True


def test_a_stale_lock_is_broken_rather_than_blocking_forever():
    lock.LOCK_PATH.write_text(json.dumps({"name": "ghost", "pid": 999999,
                                          "started": "yesterday"}), encoding="utf-8")
    assert lock.holder() is None, "a dead holder must not count as holding the lock"
    assert lock.break_stale() is True
    assert lock.holder() is None
    # and a live lock must NOT be broken
    lock.acquire("live")
    assert lock.break_stale() is False
    assert lock.holder()["name"] == "live"


def test_an_unreadable_lock_file_means_no_lock():
    """A corrupt file must not crash a scheduled run."""
    lock.LOCK_PATH.write_text("{not json", encoding="utf-8")
    assert lock.holder() is None
    assert lock.break_stale() is False


def test_the_heavy_entry_points_acquire_the_lock():
    """A lock nothing uses is not a control.

    The three entry points that take minutes and touch shared state must ask first: the scheduled
    loop, the benchmark harness and the official scoring pass.
    """
    for rel, marker in (("scripts/cron_run.py", "lock.acquire"),
                        ("scripts/bench_plottwin.py", "lock.acquire"),
                        ("scripts/score_official.py", "lock.acquire")):
        path = ROOT / rel
        if not path.is_file():
            pytest.skip(f"{rel} absent")
        text = path.read_text(encoding="utf-8")
        assert marker in text, f"{rel} does not acquire the measurement lock"
        assert "lock.release" in text, f"{rel} never releases the lock"


def test_children_of_the_loop_do_not_re_lock():
    """cron_run launches the benchmark as a subprocess and already holds the lock.

    A child that tries to take it again would deadlock against its own parent.
    """
    path = ROOT / "scripts" / "cron_run.py"
    if not path.is_file():
        pytest.skip("cron_run absent")
    text = path.read_text(encoding="utf-8")
    assert "--no-lock" in text, "the loop must tell its children not to re-lock"


def test_the_report_cannot_be_shrunk_silently():
    """A small diagnostic run once destroyed 106 accumulated benchmark rows.

    The harness wrote its report unconditionally, so any run without --merge REPLACED the pool.
    A `--limit 2` lock test did exactly that, and a scheduled run then committed the damage. The
    report is the deliverable and the accumulated measurement history; shrinking it must be
    deliberate, not a side effect.
    """
    import subprocess
    import sys
    script = ROOT / "scripts" / "bench_plottwin.py"
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not (script.is_file() and report.is_file()):
        pytest.skip("harness or report absent")
    import json
    before = len(json.loads(report.read_text(encoding="utf-8")).get("tasks") or [])
    if before < 10:
        pytest.skip("report too small to test shrinkage")
    cp = subprocess.run([sys.executable, str(script), "--limit", "1", "--offset", "0",
                         "--no-lock"], cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert cp.returncode != 0, "a 1-task run replaced a large report without complaint"
    assert "refusing to shrink" in (cp.stdout + cp.stderr), cp.stdout[-500:] + cp.stderr[-500:]
    after = len(json.loads(report.read_text(encoding="utf-8")).get("tasks") or [])
    assert after == before, f"the report changed anyway: {before} -> {after}"
