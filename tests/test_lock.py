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
