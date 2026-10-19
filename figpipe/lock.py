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
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
_DEFAULT_LOCK_PATH = ROOT / "knowledge" / ".measurement.lock"


def _resolve_lock_path() -> pathlib.Path:
    """Where the measurement lock lives.

    `FIGPIPE_LOCK_PATH` overrides it. Tests set this so a suite that runs several probes cannot
    contend with itself, a real measurement, or a crashed run's leftover -- contention produced
    failures that depended on test ORDER, which is a defect in the test harness, not the code.
    """
    override = os.environ.get("FIGPIPE_LOCK_PATH")
    return pathlib.Path(override) if override else _DEFAULT_LOCK_PATH


#: Kept as a module attribute for callers that read it, but always re-resolved through
#: `lock_path()` so an override takes effect.
LOCK_PATH = _DEFAULT_LOCK_PATH


def lock_path() -> pathlib.Path:
    """The current lock file, honouring `FIGPIPE_LOCK_PATH`."""
    global LOCK_PATH
    LOCK_PATH = _resolve_lock_path()
    return LOCK_PATH


#: A lock older than this is stale whatever its pid says. PID reuse is common on Windows, so
#: "the pid is alive" cannot prove the WRITER is alive. Long enough for any real measurement.
STALE_AFTER_S = 6 * 3600


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
    lock_path()
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
    lock_path()
    """The current holder, or None when the lock is free or provably stale.

    A pid alone cannot prove the WRITER is alive: Windows recycles pids, so a crashed run's entry
    can name a process that now exists but never wrote this file. Age is the tiebreaker -- no
    measurement on this project runs for six hours.
    """
    info = _read()
    if not info:
        return None
    pid = int(info.get("pid", 0) or 0)
    if not _pid_alive(pid):
        return None
    started_ts = float(info.get("started_ts") or 0.0)
    if started_ts and (time.time() - started_ts) > STALE_AFTER_S:
        return None                     # too old to be a real measurement
    return info


def acquire(name: str, *, wait_s: float = 0.0) -> dict:
    lock_path()
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
            "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "started_ts": time.time(),
            #: a unique token, so release() can prove it owns THIS file rather than inferring
            #: ownership from a pid that Windows may have recycled
            "token": uuid.uuid4().hex}
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    # REMOVE FIRST, THEN WRITE. A stale file whose holder is dead makes holder() return None, so
    # this loop proceeds -- but the stale FILE is still there. Writing over it worked, yet any read
    # between the two saw the old holder. Unlinking first makes "no lock" and "my lock" the only
    # states.
    LOCK_PATH.unlink(missing_ok=True)
    LOCK_PATH.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def release(name: str, *, token: str | None = None) -> None:
    lock_path()
    """Drop the lock IF we hold it.

    With `token`, ownership is proven by the token we wrote, so a stale or recycled file can never
    block cleanup. Without it, the older pid-based inference is used (kept for callers that acquired
    outside the context manager).
    """
    info = _read()
    if token is not None:
        on_disk = info.get("token")
        if on_disk is None or on_disk == token:
            # Either the file is unreadable/absent (so it cannot be another holder's live lock) or
            # it carries our token. Both cases: clear it. Returning early on an unreadable file is
            # what left a stale lock on disk and wedged every later measurement.
            LOCK_PATH.unlink(missing_ok=True)
            return
        # a DIFFERENT token: someone else owns it now; leave it alone
        return
    if not info:
        return
    if info.get("pid") == os.getpid() and info.get("name") == name:
        LOCK_PATH.unlink(missing_ok=True)
        return
    # PID REUSE: a dead process's pid can be reassigned, so "pid is alive" does not mean "the
    # process that wrote this file is alive". An entry that has been on disk far longer than any
    # plausible measurement is stale whatever its pid says.
    started_ts = float(info.get("started_ts") or 0.0)
    if started_ts and (time.time() - started_ts) > STALE_AFTER_S:
        LOCK_PATH.unlink(missing_ok=True)
        return
    if not _pid_alive(int(info.get("pid", 0) or 0)):
        # a dead holder's leftover file is not a lock; clearing it is safe and unblocks the schedule
        LOCK_PATH.unlink(missing_ok=True)
        return
    raise MeasurementBusy(
        f"refusing to release a lock held by {info.get('name')} (pid {info.get('pid')})")


class measure:
    """Context manager: `with measure("bench"): ...`."""

    def __init__(self, name: str, *, wait_s: float = 0.0):
        self.name = name
        self.wait_s = wait_s

    def __enter__(self):
        self.info = acquire(self.name, wait_s=self.wait_s)
        return self.info

    def __exit__(self, exc_type, exc, tb):
        # RELEASE BY TOKEN, NOT BY RE-READING THE FILE.
        #
        # Re-reading was wrong three ways, and each way wedged the machine:
        #   * a stale file from a crashed run made `release()` refuse, MASKING the body's error
        #   * a pid-recycled file made it refuse forever
        #   * a concurrent process rewriting the file between our write and our read made it refuse
        # The context manager already knows the token it wrote; comparing that to the file is the
        # only check needed, and it cannot be fooled by staleness.
        try:
            release(self.name, token=self.info.get("token"))
        except (MeasurementBusy, OSError):
            if exc_type is None:
                raise
        return False


def break_stale() -> bool:
    lock_path()
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
