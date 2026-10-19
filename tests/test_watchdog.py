"""The unattended loop must be checked by something other than a log nobody reads.

WHY THIS TEST
    The evolution loop is the only unattended component in this project, and until now nothing
    verified it was alive. loop.log shows the evidence: 13 markers over three days, one gap of
    10.8 hours against a 6-hour schedule, and on 2026-10-20 the loop took exit=3 at 01:54 (the
    measurement lock refused because a manual run held it) and then slept the full six hours.

    Every other defect this project found had a guard. This one had a log line.

    These tests pin the three properties that make the guard real:
      1. a heartbeat exists and is written by the loop
      2. a transient lock refusal RETRIES instead of sleeping six hours
      3. the watchdog does NOT kill a live process (it may be mid-measurement)
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOOP = ROOT / "scripts" / "loop.ps1"
WATCHDOG = ROOT / "scripts" / "watchdog.ps1"


def test_the_loop_writes_a_heartbeat():
    """A watchdog needs a cheap liveness signal; parsing a growing log is not one."""
    if not LOOP.is_file():
        pytest.skip("loop.ps1 absent")
    src = LOOP.read_text(encoding="utf-8")
    assert "loop.heartbeat" in src, "the loop does not write a heartbeat"
    assert "Write-Heartbeat" in src


def test_a_transient_lock_refusal_retries_instead_of_sleeping_six_hours():
    """exit=3 means ANOTHER RUN HELD THE LOCK. That is a scheduling accident, not a cycle.

    Observed 2026-10-20: a manual run at 01:52 made the loop take exit=3 at 01:54, and the old
    script then slept until 07:54 -- one manual run starved the schedule for a quarter of a day.
    """
    if not LOOP.is_file():
        pytest.skip("loop.ps1 absent")
    src = LOOP.read_text(encoding="utf-8")
    assert "$EXIT_BUSY" in src, "the loop does not distinguish a busy lock from a completed cycle"
    assert "RETRY_SLEEP_S" in src, "there is no short backoff for a transient refusal"
    # the retry must be bounded, or a stuck lock spins forever
    assert "RETRY_MAX" in src
    # and the full sleep must come AFTER the retry loop, not inside it
    retry_block = src[src.find("if ($code -eq $EXIT_BUSY)"):]
    assert "continue" in retry_block, "the busy branch does not retry"
    assert "6 * 3600" in src[retry_block.find("continue"):], (
        "the six-hour sleep is not after the retry loop")


def test_the_watchdog_does_not_kill_a_live_loop():
    """A wedged loop may be mid-measurement; killing it abandons a half-written report.

    That is the exact defect class this project spent rounds fixing (a routine operation removing
    evidence as a side effect). The watchdog must report, not kill.
    """
    if not WATCHDOG.is_file():
        pytest.skip("watchdog.ps1 absent")
    src = WATCHDOG.read_text(encoding="utf-8")
    assert "Stop-Process" not in src, (
        "the watchdog kills processes; it must report a wedged loop and let a human decide")
    assert "WEDGED" in src, "the watchdog does not distinguish a wedged loop from a dead one"


def test_the_watchdog_checks_both_heartbeat_and_process():
    """Either alone is wrong: a touched-but-stale file, or a live-but-wedged process."""
    if not WATCHDOG.is_file():
        pytest.skip("watchdog.ps1 absent")
    src = WATCHDOG.read_text(encoding="utf-8")
    assert "loop.heartbeat" in src
    assert "Get-LoopProcesses" in src or r"loop\.ps1" in src
    assert "STALE_MINUTES" in src


def test_the_watchdog_has_been_run_and_reports():
    """It must produce a log line, or it is another component nobody can see working."""
    log = ROOT / "knowledge" / "watchdog.log"
    if not log.is_file():
        pytest.skip("watchdog has not run yet")
    text = log.read_text(encoding="utf-8", errors="replace")
    assert ("OK:" in text or "PROBLEM:" in text), "the watchdog ran but recorded no verdict"
