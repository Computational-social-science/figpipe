"""One measurement at a time: a cooperative lock for the heavy entry points.

WHY THIS EXISTS
    On 2026-10-19 a scheduled evolution run and a 150-task benchmark pass shared this machine. The
    suite's timing-sensitive tests failed once under load, the loop recorded a capability
    regression, and the failure was indistinguishable from a real defect. The mitigation written
    down at the time was procedural -- "do not start a pool-wide re-measure while the loop is due"
    -- and a procedural rule that nothing enforces is not a control.

    This module turns it into an enforced one. The heavy entry points (`cron_run`, the benchmark
    harness, the official scoring pass) acquire the same lock; a second heavy run is REFUSED with
    the holder named, rather than silently producing numbers nobody can trust.

DESIGN, DELIBERATELY SIMPLE
    * a lock FILE, not a library lock: the entry points are separate processes started by hand, by
      a scheduler and by each other
    * the file records pid, host, the script and a start time, so a refusal can say who holds it
    * a STALE lock (the holder is gone) is broken automatically, because a crashed run must not
      block the schedule forever
    * it is cooperative: nothing can stop a process that ignores it. What it guarantees is that
      every heavy entry point we own asks first.

WHAT IT IS NOT
    Not a mutex around the whole repository, and not a guarantee against a user editing files
    during a run. It exists to stop two MEASUREMENTS from overlapping, because overlapping
    measurements produce numbers that are neither reproducible nor trustworthy.
"""
from __future__ import annotations

import json
import os
import pathlib
import socket
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "knowledge" / ".measurement.lock"


class MeasurementBusy(RuntimeError):
    """Another heavy measurement holds the lock."""


def _pid_alive(pid: int) -> bool:
    """Is the recorded pid still running?

    WINDOWS IS NOT POSIX HERE. `os.kill(dead_pid, 0)` raises a bare `OSError` with
    WinError 87 ("invalid parameter") rather than `ProcessLookupError`, so the obvious
    implementation treats every dead pid as alive -- and a stale lock then blocks the schedule
    forever. This checks the error CODE on Windows and falls back to signal 0 elsewhere.
    """
    if pid <= 0:
        return False
    if os.name == "nt":
        # `os.kill(pid, 0)` on a dead pid raises WinError 87 here, and on this machine's exFAT
        # volume the exception path itself raised KeyboardInterrupt -- so it is not a safe probe.
        # OpenProcess/GetExitCodeProcess is the documented way to ask "is this pid alive", and it
        # has no signal semantics at all.
        try:
            import ctypes
            from ctypes import wintypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False                     # cannot open -> not running (or not ours)
            try:
                code = wintypes.DWORD()
                if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                    return True                  # cannot tell; err toward "alive"
                return code.value == STILL_ACTIVE
            finally:
                kernel32.CloseHandle(handle)
        except Exception:                        # noqa: BLE001 - never crash a scheduled run
            return True                          # unknown platform state: err toward "alive"
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def _read() -> dict:
    """Read the lock file; a missing or unreadable file means "no lock".

    A transient I/O error must not crash a scheduled run: an unreadable lock is treated as absent,
    and the worst case is that two measurements overlap -- which the caller can see in the record.
    """
    try:
        raw = LOCK_PATH.read_bytes()
    except OSError:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def holder() -> dict | None:
    """The current holder, or None when the lock is free or stale."""
    info = _read()
    if not info:
        return None
    pid = int(info.get("pid", 0) or 0)
    if not _pid_alive(pid):
        return None
    return info


def acquire(name: str, *, wait_s: float = 0.0) -> dict:
    """Take the lock, or raise `MeasurementBusy` naming the holder.

    `wait_s` > 0 polls for that long, which lets a short measurement queue behind a long one
    instead of failing outright. The default is to fail immediately: a scheduled run that silently
    waits an hour is worse than one that reports it could not measure.
    """
    deadline = time.monotonic() + max(0.0, wait_s)
    while True:
        current = holder()
        if current is None:
            break
        if time.monotonic() >= deadline:
            raise MeasurementBusy(
                f"another measurement is running: {current.get('name')} "
                f"(pid {current.get('pid')}, started {current.get('started')}). "
                f"Overlapping measurements produce numbers that are neither reproducible nor "
                f"trustworthy -- wait for it, or delete {LOCK_PATH.name} if the holder is gone.")
        time.sleep(0.5)
    info = {"name": name, "pid": os.getpid(), "host": socket.gethostname(),
            "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def release(name: str) -> None:
    """Drop the lock IF we hold it. Releasing someone else's lock is refused, not ignored."""
    info = _read()
    if not info:
        return
    if info.get("pid") != os.getpid() or info.get("name") != name:
        raise MeasurementBusy(
            f"refusing to release a lock held by {info.get('name')} (pid {info.get('pid')})")
    LOCK_PATH.unlink(missing_ok=True)


class measure:
    """Context manager: `with measure("bench"): ...`."""

    def __init__(self, name: str, *, wait_s: float = 0.0):
        self.name = name
        self.wait_s = wait_s

    def __enter__(self):
        self.info = acquire(self.name, wait_s=self.wait_s)
        return self.info

    def __exit__(self, exc_type, exc, tb):
        release(self.name)
        return False


def break_stale() -> bool:
    """Remove the lock if its holder is gone; returns True if something was removed.

    Reads the file ONCE. An earlier version called `_read()` and then `holder()` (which reads
    again); on this machine's exFAT volume the second open of the same path raised an I/O error
    that surfaced as KeyboardInterrupt. One read, one decision.
    """
    info = _read()
    if not info:
        return False
    if _pid_alive(int(info.get("pid", 0) or 0)):
        return False
    LOCK_PATH.unlink(missing_ok=True)
    return True
