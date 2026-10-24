"""The scheduling guard must detect the runner by evidence it cannot fake.

WHY THIS EXISTS
    `test_run_history_is_committed_not_just_written` allows one extra uncommitted run record when the
    suite is executing inside `cron_run` -- the runner writes the record, runs the suite, then
    commits, so the in-flight record is legitimately untracked for as long as the suite takes.

    My first `_inside_cron()` searched the PARENT PROCESS'S COMMAND LINE for "cron_run". Measured: it
    returned True from a plain PowerShell whose command line contained that string because I had
    typed it. So the test allowed the extra record ALWAYS, from anywhere.

    That is the defect class this project records most often -- **a control that looks present and
    does nothing** -- and it was introduced by the fix for a different instance of the same class.

THE RULE
    The evidence must be something only the runner produces. `cron_run` holds
    `knowledge/.measurement.lock` under the name `"cron_run"` for the whole run. A command line that
    merely MENTIONS the runner cannot forge it, and the name is the discriminator: a `bench` lock is
    not the runner.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

LOCK = ROOT / "knowledge" / ".measurement.lock"


@pytest.fixture()
def helper():
    import test_scheduling
    return test_scheduling._inside_cron


@pytest.fixture()
def restore_lock():
    """Put the lock file back exactly as it was, whatever the test does to it."""
    saved = LOCK.read_bytes() if LOCK.is_file() else None
    yield
    if saved is None:
        LOCK.unlink(missing_ok=True)
    else:
        LOCK.write_bytes(saved)


def _write_lock(name: str) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps({"name": name, "pid": 1, "host": "t",
                                "started": "x", "started_ts": 0, "token": "t"}), encoding="utf-8")


def test_no_lock_means_not_inside_the_runner(helper, restore_lock):
    """THE COMMON CASE. A developer running pytest by hand is not the scheduled runner."""
    LOCK.unlink(missing_ok=True)
    assert helper() is False


def test_a_cron_run_lock_means_inside_the_runner(helper, restore_lock):
    """THE POSITIVE CASE. Without this the offset would never apply and the test would fail in cron."""
    _write_lock("cron_run")
    assert helper() is True


def test_a_different_lock_name_is_not_the_runner(helper, restore_lock):
    """THE DISCRIMINATOR. Any measurement holds the lock; only the runner's name counts."""
    _write_lock("bench")
    assert helper() is False


def test_a_corrupt_lock_is_not_the_runner(helper, restore_lock):
    """A half-written lock must not be read as "the runner is here"."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text("{not json", encoding="utf-8")
    assert helper() is False


def test_the_detection_does_not_read_a_command_line():
    """THE DEFECT ITSELF. A command line can contain the word 'cron_run' by accident -- measured, a
    shell whose command mentioned it made the old version return True from outside the runner."""
    import inspect
    import test_scheduling
    src = inspect.getsource(test_scheduling._inside_cron)
    assert "CommandLine" not in src, (
        "the detection reads a process command line again; a shell that mentions the runner would "
        "defeat it")
    assert "measurement.lock" in src, "the detection does not use the lock file"
