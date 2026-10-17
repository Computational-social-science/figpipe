"""The scheduled loop must actually be scheduled, and its history must actually land.

WHY THESE TESTS EXIST
    The 18:00 scheduled run looked healthy -- evolve ok, tests ok, exit 0 -- while two things
    were silently broken:

    1. THE STARTUP LOOP HAD NEVER RUN. A `.ps1` file was placed in the Windows Startup folder,
       but Windows only executes .exe/.bat/.cmd/.lnk/.vbs/.com from there. A .ps1 is silently
       ignored. There was no loop.log and no process; the "durable second schedule" did not
       exist. It looked configured because the file was there.

    2. THE RUN HISTORY WAS NEVER COMMITTED. `git_publish` only committed when the KNOWLEDGE
       BASE changed, but `knowledge/runs/*.json` is the audit trail of what each run found.
       Gating it on knowledge change meant a quiet run's record never landed -- the repository
       permanently lagged one run behind, and after a few weeks would show no evidence the
       loop had ever run.

    Both are the same failure shape: a mechanism that appears present and is inert.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
STARTUP = pathlib.Path(os.path.expandvars(
    r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))


def test_startup_launcher_is_a_format_windows_executes():
    """THE DEFECT: a .ps1 in Startup is silently ignored.

    Windows executes only .exe/.bat/.cmd/.lnk/.vbs/.com from the Startup folder. The first
    attempt wrote figpipe-evolve.ps1 there and it never ran.
    """
    if not STARTUP.is_dir():
        pytest.skip("not a Windows environment with a Startup folder")
    launchers = [p for p in STARTUP.glob("figpipe-evolve.*")]
    assert launchers, (
        "no figpipe Startup launcher found; the durable second schedule does not exist")
    exts = {p.suffix.lower() for p in launchers}
    assert exts & {".vbs", ".bat", ".cmd", ".lnk", ".exe"}, (
        f"Startup launcher(s) {[p.name for p in launchers]} have extensions {exts}, none of "
        f"which Windows executes from the Startup folder. A .ps1 there is silently ignored.")
    assert ".ps1" not in exts or exts & {".vbs", ".bat", ".cmd", ".lnk", ".exe"}, (
        "only a .ps1 is present in Startup; Windows will not run it")


def test_startup_launcher_points_at_a_real_loop_script():
    if not STARTUP.is_dir():
        pytest.skip("no Startup folder")
    vbs = STARTUP / "figpipe-evolve.vbs"
    if not vbs.is_file():
        pytest.skip("no .vbs launcher")
    src = vbs.read_text(encoding="utf-8", errors="replace")
    assert "loop.ps1" in src, (
        "the Startup launcher does not reference loop.ps1, so it starts nothing")
    assert (ROOT / "scripts" / "loop.ps1").is_file(), (
        "loop.ps1 is referenced by the launcher but does not exist")


def test_loop_log_exists_and_is_not_empty():
    """A loop that has run leaves evidence. No log means it never started."""
    log = ROOT / "knowledge" / "loop.log"
    assert log.is_file(), (
        "knowledge/loop.log does not exist, so the durable loop has never executed. The "
        "Startup launcher may be in a format Windows ignores.")
    assert log.stat().st_size > 0, "loop.log is empty; the loop started but produced nothing"


def test_run_history_is_committed_not_just_written():
    """THE SECOND DEFECT: run records were written but never committed.

    `knowledge/runs/` is the audit trail. If it is not committed, the repository shows no
    evidence the loop ran, however many runs have happened.
    """
    runs = sorted((ROOT / "knowledge" / "runs").glob("*.json"))
    if len(runs) < 2:
        pytest.skip("fewer than two runs recorded")
    p = subprocess.run(["git", "ls-files", "knowledge/runs"], cwd=ROOT,
                       capture_output=True, text=True)
    tracked = [ln for ln in p.stdout.splitlines() if ln.strip()]
    assert tracked, (
        "no run record is tracked by git; the audit trail exists only on this disk and "
        "would be lost")
    # The most recent run may legitimately be uncommitted (its own commit is made by the next
    # run). Older ones must be tracked.
    assert len(tracked) >= len(runs) - 1, (
        f"{len(runs)} run records exist but only {len(tracked)} are tracked; the history is "
        f"lagging more than the documented one-run offset")


def test_publish_is_documented_as_describing_the_triggering_run():
    """The publish outcome cannot be inside the commit it describes -- say so explicitly."""
    latest = ROOT / "knowledge" / "latest_run.json"
    if not latest.is_file():
        pytest.skip("no run recorded")
    run = json.loads(latest.read_text(encoding="utf-8"))
    if "published" not in run:
        pytest.skip("published field absent (dry run)")
    assert "publish_note" in run or run.get("published", {}).get("pushed") is not None, (
        "the record does not explain the relationship between the publish outcome and the "
        "commit that carries the record, so a reader cannot tell whether it is current")
