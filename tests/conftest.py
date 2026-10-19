"""Session-wide test isolation for machine-global state.

WHY THIS FILE EXISTS
    `figpipe/lock.py` is a MACHINE-GLOBAL file: it exists to stop two real measurements from
    overlapping. In a test session that runs several probes across several files, that same
    globality makes tests contend with each other -- and the resulting failures depended on test
    ORDER, which is a defect in the harness rather than in the code.

    This conftest points the lock at a per-session temporary directory, so the suite measures the
    lock's BEHAVIOUR without ever touching the real one. The behaviour tests (refusal, release,
    stale recovery) all still run against a real file, just not the shared one.

    The real lock path is asserted separately by `test_lock.py`, which checks that the production
    entry points acquire it.
"""
from __future__ import annotations

import os
import pathlib
import tempfile

import pytest

_SESSION_LOCK_DIR = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-test-lock-"))
os.environ["FIGPIPE_LOCK_PATH"] = str(_SESSION_LOCK_DIR / ".measurement.lock")


@pytest.fixture(scope="session", autouse=True)
def _isolated_measurement_lock():
    """Guarantee the real lock is never used by the suite."""
    from figpipe import lock
    lock.lock_path()
    assert lock.LOCK_PATH == _SESSION_LOCK_DIR / ".measurement.lock", (
        "the test session is using the REAL measurement lock; a concurrent real run would make "
        "the suite fail for reasons unrelated to the code")
    yield
    try:
        lock.LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        pass
