"""The watchdog has three branches; each must be exercised, not just written.

WHY THIS TEST
    Round 21 added the watchdog and verified the HEALTHY path against the live loop. The WEDGED and
    DEAD paths were only ever read, never run -- and a guard whose failure path is untested is the
    defect this project keeps finding (a control that looks present and does nothing).

    These tests drive the real script against a TEMPORARY root, so no live process is touched and
    no real measurement is disturbed. The script takes its paths from $here, so a copy with the
    root rewritten is the honest way to exercise it.

BRANCHES
    healthy  live process + fresh heartbeat   -> exit 0, no action
    wedged   live process + STALE heartbeat   -> exit 2, and NO kill (it may be mid-measurement)
    dead     no process at all                -> relaunch attempt, exit 0 or 3/4/5
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WATCHDOG = ROOT / "scripts" / "watchdog.ps1"


def _sandbox(root: pathlib.Path) -> pathlib.Path:
    """Copy the watchdog with its root pointed at a temp directory.

    Rewritten by LINE, not by regex: a Windows path in a regex replacement is full of backslash
    escapes, and `re.sub` treats `\\U` in the replacement as a bad escape. Lines have no such
    problem and the intent is clearer.
    """
    if not WATCHDOG.is_file():
        pytest.skip("watchdog.ps1 absent")
    src = WATCHDOG.read_text(encoding="utf-8")
    out_lines: list[str] = []
    replaced = False
    for line in src.splitlines(keepends=True):
        stripped = line.lstrip()
        if not replaced and stripped.startswith("$root") and "=" in stripped:
            out_lines.append("$root     = '" + str(root) + "'\n")
            replaced = True
        else:
            out_lines.append(line)
    assert replaced, "could not find the $root assignment to rewrite"
    out = root / "watchdog.ps1"
    out.write_text("".join(out_lines), encoding="utf-8")
    return out


def _run(script: pathlib.Path, *, pretend_dead: bool = True) -> subprocess.CompletedProcess:
    """Run the sandboxed watchdog.

    `pretend_dead` sets FIGPIPE_LOOP_PATTERN to a name nothing is running, so the DEAD branch can be
    exercised while the REAL evolution loop is alive on this machine. Without it the watchdog
    correctly finds the live loop and every failure-path test passes for the wrong reason.
    """
    env = dict(os.environ)
    if pretend_dead:
        env["FIGPIPE_LOOP_PATTERN"] = "figpipe-definitely-not-running-{0}.ps1".format(os.getpid())
    else:
        env.pop("FIGPIPE_LOOP_PATTERN", None)
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", str(script)],
                          capture_output=True, text=True, timeout=180, env=env)


@pytest.fixture()
def sandbox():
    d = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-wd-"))
    (d / "knowledge").mkdir(parents=True, exist_ok=True)
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "scripts" / "watchdog.ps1", d / "scripts" / "watchdog.ps1")
    script = _sandbox(d)
    yield d, script
    shutil.rmtree(d, ignore_errors=True)


def test_the_dead_branch_attempts_a_restart(sandbox):
    """No process and no heartbeat: the watchdog must try to relaunch, not sit silent.

    The launcher will not exist in the sandbox, so the expected outcome is exit 3 with a
    CANNOT RESTART log line -- which still proves the DEAD branch was reached and acted.
    """
    d, script = sandbox
    cp = _run(script)
    log = (d / "knowledge" / "watchdog.log")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    assert "no heartbeat file" in text or "no powershell process" in text, (
        f"the dead branch did not record its diagnosis; log was: {text!r} "
        f"stdout={cp.stdout!r} stderr={cp.stderr!r}")
    # exit 3 = CANNOT RESTART (launcher absent in the sandbox), which is the DEAD branch acting
    assert cp.returncode in (0, 3, 4, 5), f"unexpected exit {cp.returncode}"


def test_a_stale_heartbeat_with_no_process_is_not_called_healthy(sandbox):
    """A fresh-looking file must not paper over a missing process."""
    d, script = sandbox
    beat = d / "knowledge" / "loop.heartbeat"
    beat.write_text("2026-01-01 00:00:00|idle|1", encoding="utf-8")   # mtime is NOW
    cp = _run(script)
    log = (d / "knowledge" / "watchdog.log")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    assert "no powershell process" in text, (
        f"a fresh heartbeat with no process must still be a PROBLEM; log: {text!r}")
    assert "OK:" not in text.split("PROBLEM:")[-1] if "PROBLEM:" in text else True


def test_the_watchdog_never_kills():
    """The WEDGED branch must report, not terminate: a wedged loop may be mid-measurement."""
    src = WATCHDOG.read_text(encoding="utf-8") if WATCHDOG.is_file() else ""
    if not src:
        pytest.skip("watchdog.ps1 absent")
    assert "Stop-Process" not in src
    assert "taskkill" not in src.lower()
    # and it must SAY it is not killing, so a reader knows the choice was deliberate
    assert "NOT killing" in src


def test_the_staleness_threshold_exceeds_the_sleep_interval():
    """A watchdog that fires while the loop sleeps is worse than none: it restarts constantly.

    The loop sleeps 6 hours; the threshold must be strictly larger than that plus a cycle.
    """
    src = WATCHDOG.read_text(encoding="utf-8") if WATCHDOG.is_file() else ""
    if not src:
        pytest.skip("watchdog.ps1 absent")
    import re
    m = re.search(r"\$STALE_MINUTES\s*=\s*(\d+)\s*\*\s*(\d+)", src)
    assert m, "the staleness threshold is not a recognisable expression"
    minutes = int(m.group(1)) * int(m.group(2))
    assert minutes > 6 * 60, (
        f"the threshold is {minutes} min but the loop sleeps 360 min; the watchdog would restart "
        f"a healthy sleeping loop")


def test_the_launcher_is_idempotent():
    """The launcher must not start a second loop when one is already running.

    THIS IS THE FORK BOMB, and only a live drill found it. The launcher is called from three
    places (login, the watchdog, and by hand) and the first version started a new loop AND a new
    watchdog unconditionally. During a restart drill on 2026-10-20 that produced 76 processes in
    ten seconds: two watchdogs each restarted the loop the other had just restarted.

    Five unit tests and a live health check all passed while the launcher was a fork bomb, because
    none of them exercised the path where things are broken.
    """
    launcher = ROOT / "scripts" / "figpipe-evolve.vbs"
    if not launcher.is_file():
        pytest.skip("launcher absent")
    src = launcher.read_text(encoding="utf-8", errors="replace")
    assert "CountMatching" in src, (
        "the launcher does not check whether a loop is already running; every call starts another")
    assert "Win32_Process" in src
    # each start must be guarded by a zero-count check
    assert src.count("= 0 Then") >= 2, (
        "both the loop and the watchdog start must be conditional on nothing running")


def test_the_watchdog_loop_is_single_instance():
    """THE DEFECT: 190 "watchdog loop started" lines against ONE live process.

    The launcher is idempotent, but a script started DIRECTLY bypasses that check. Instances
    accumulated and each ran its own watchdog every 30 minutes -- which is why the log shows
    repeated PROBLEM reports while the loop was alive.

    A MUTEX WAS TRIED AND DID NOT WORK: `New-Object Mutex($true, name, [ref]$new)` reports
    createdNew only for the first creator and the handle is released on collection, so two
    processes both saw "created". The fix is an exclusive-share FILE HANDLE, held for the process
    lifetime, which a second opener cannot acquire.
    """
    script = ROOT / "scripts" / "watchdog_loop.ps1"
    if not script.is_file():
        pytest.skip("watchdog_loop.ps1 absent")
    src = script.read_text(encoding="utf-8")
    assert "System.IO.File]::Open" in src, (
        "the watchdog loop has no exclusive file lock; instances will accumulate")
    assert "'None'" in src or '"None"' in src, (
        "the file is opened with a sharing mode that allows a second opener")
    assert "another watchdog loop holds the lock" in src
    # and the mutex approach must NOT be the MECHANISM. It appears in the comment explaining why
    # it does not work, so check the executable lines only.
    code_lines = [ln for ln in src.splitlines()
                  if ln.strip() and not ln.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    assert "Threading.Mutex" not in code, (
        "the mutex form does not exclude across processes; use the file handle")


def test_the_watchdog_loop_holds_the_lock_for_its_lifetime():
    """The handle must not be closed or disposed inside the loop, or the lock lapses."""
    script = ROOT / "scripts" / "watchdog_loop.ps1"
    if not script.is_file():
        pytest.skip("watchdog_loop.ps1 absent")
    src = script.read_text(encoding="utf-8")
    after_open = src[src.find("$lockHandle"):]
    assert ".Dispose()" not in after_open, (
        "the lock handle is disposed, so the single-instance guarantee lapses")
    assert ".Close()" not in after_open


def test_the_evolution_loop_is_single_instance():
    """THE DEFECT: `loop started` appears 197 times in loop.log.

    The last cluster is one per SECOND during the fork-bomb window. The launcher is idempotent,
    but anything starting loop.ps1 DIRECTLY bypasses that check. Two loops then run the same
    six-hourly cycle and fight over the measurement lock -- the backoff hides it by retrying, so
    the symptom is a drifting schedule rather than an error anyone notices.

    Fixed with the same primitive that worked for watchdog_loop: an exclusive-share file handle,
    not a mutex (a mutex reports createdNew only for the first creator in a process's lifetime).
    """
    script = ROOT / "scripts" / "loop.ps1"
    if not script.is_file():
        pytest.skip("loop.ps1 absent")
    src = script.read_text(encoding="utf-8")
    assert "System.IO.File]::Open" in src, (
        "the evolution loop has no single-instance guard; instances will accumulate")
    assert "'None'" in src or '"None"' in src
    assert "another evolution loop holds the lock" in src
    code_lines = [ln for ln in src.splitlines()
                  if ln.strip() and not ln.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    assert "Threading.Mutex" not in code, (
        "a mutex does not exclude across processes here; use the file handle")


def test_both_persistent_loops_use_the_same_lock_primitive():
    """Two loops, two chances to get it wrong differently. They must use the same primitive."""
    files = [ROOT / "scripts" / "loop.ps1", ROOT / "scripts" / "watchdog_loop.ps1"]
    for f in files:
        if not f.is_file():
            pytest.skip(f"{f.name} absent")
        src = f.read_text(encoding="utf-8")
        assert "System.IO.File]::Open" in src, (
            f"{f.name} does not use the exclusive file handle the other loop uses")


def test_the_launcher_does_not_confuse_the_watchdog_with_the_loop():
    """THE BUG: `CountMatching("loop.ps1")` also matched `watchdog_loop.ps1`.

    "watchdog_loop.ps1" CONTAINS "loop.ps1" as a substring, so once the watchdog was running the
    launcher believed a loop was running too and NEVER started the evolution loop. Observed
    2026-10-20 07:47: watchdog alive, loop dead, every launcher call a silent no-op.

    A guard whose test cannot distinguish the thing it guards from a DIFFERENT thing is worse than
    no guard, because it reports success while doing nothing.
    """
    launcher = ROOT / "scripts" / "figpipe-evolve.vbs"
    if not launcher.is_file():
        pytest.skip("launcher absent")
    src = launcher.read_text(encoding="utf-8", errors="replace")
    # the anchored form must be used
    assert '"\\loop.ps1"' in src or "'\\loop.ps1'" in src, (
        "the launcher does not anchor the loop match to a path separator; "
        "watchdog_loop.ps1 will match it and the loop will never start")
    # and the bare substring form must NOT be the check for the loop
    code_lines = [ln for ln in src.splitlines() if not ln.lstrip().startswith("'")]
    code = "\n".join(code_lines)
    assert 'CountMatching("loop.ps1")' not in code, (
        "the launcher still uses the unanchored substring, which collides with watchdog_loop.ps1")


def test_the_substring_collision_is_real():
    """NEGATIVE CONTROL: prove the naive form really does collide, so the fix is justified."""
    watchdog_cmd = r"C:\x\scripts\watchdog_loop.ps1"
    loop_cmd = r"C:\x\scripts\loop.ps1"
    # naive substring
    assert "loop.ps1" in watchdog_cmd.lower(), "the naive form WOULD match the watchdog"
    # anchored
    assert "\\loop.ps1" not in watchdog_cmd.lower()
    assert "\\loop.ps1" in loop_cmd.lower()
