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


def test_the_scheduled_run_releases_the_lock_around_the_test_suite():
    """THE DEFECT: the measurement lock was held across the TEST SUITE.

    One test in the suite spawns a subprocess that must ACQUIRE the same lock, and it waits 240 s.
    The lock is held for the whole scheduled run -- a benchmark slice alone is ~30 minutes -- so the
    test waited, timed out, and the run reported "tests: FAILED" while nothing was broken. Observed
    2026-10-20 07:52, and it took a manual investigation to see it was contention rather than a
    regression.

    A test suite is not a measurement: it renders small fixtures and never touches the pool. Holding
    the measurement lock over it protects nothing and creates a self-deadlock.
    """
    import inspect
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import cron_run
    src = inspect.getsource(cron_run._main_locked)
    assert "lock.release" in src, (
        "the scheduled run never releases the lock inside _main_locked, so the suite runs under it")
    assert "released_for_tests" in src, (
        "the release-around-the-suite block is gone; the suite would deadlock against itself")
    # and the release must come BEFORE run_tests, not after
    i_release = src.find("lock.release")
    i_tests = src.find("run_tests()")
    assert 0 < i_release < i_tests, (
        "the lock is released AFTER the suite starts, which does not help")


def test_a_failed_reacquire_does_not_publish():
    """If another measurement starts while the suite runs, the commit must be skipped.

    Losing one commit is recoverable; publishing during someone else's measurement is not.
    """
    import inspect
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import cron_run
    src = inspect.getsource(cron_run._main_locked)
    assert "MeasurementBusy" in src, (
        "the re-acquire is not guarded; a busy lock would raise and lose the run record")
    assert "not publishing" in src or "not pushed" in src, (
        "the refusal to publish is not reported")


def test_the_scheduled_run_only_releases_a_lock_it_still_holds():
    """THE BUG: `finally: lock.release("cron_run")` assumed we still held the lock.

    `_main_locked` deliberately releases it around the test suite (round 32) and may fail to
    re-acquire when another measurement starts. In that case the lock belongs to someone else and
    releasing it raises `MeasurementBusy` -- FROM INSIDE A `finally`, which turns a clean
    "not pushed" exit into a traceback and loses the exit code.

    Observed 2026-10-20 13:56 in knowledge/loop.log:
        not pushed: another measurement started while the suite ran
        Traceback ... lock.release("cron_run")
        MeasurementBusy: refusing to release a lock held by bench_plottwin
    """
    import inspect
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import cron_run
    src = inspect.getsource(cron_run.main)
    assert "lock.holder()" in src, (
        "the finally block releases the lock without checking ownership; a lock taken by another "
        "measurement would raise inside the finally")
    assert 'holder.get("name") == "cron_run"' in src or "holder.get('name') == 'cron_run'" in src, (
        "the ownership check does not compare the holder name")


def test_releasing_a_lock_we_do_not_hold_raises():
    """NEGATIVE CONTROL: the behaviour the fix protects against must actually exist."""
    import sys
    sys.path.insert(0, str(ROOT))
    from figpipe import lock
    lock.break_stale()
    token = lock.acquire("someone-else")
    try:
        with pytest.raises(lock.MeasurementBusy):
            lock.release("cron_run")
    finally:
        lock.release("someone-else")
