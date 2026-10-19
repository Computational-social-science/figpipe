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
