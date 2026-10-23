"""A dropped socket is not a capability regression.

WHY THIS EXISTS
    On 2026-10-23 the scheduled run exited 1 and reported:

        benchmark_success_rate: 1.0 -> 0.993     (judged as a REGRESSION)

    The cause was ONE task whose fetch failed with `ConnectionResetError`. The task never ran; the
    remote host closed the connection. The pipeline's own docstring says such a task "never exercised
    the pipeline" and must not count as capability loss -- and it did.

THE MECHANISM OF THE BUG
    `_is_infra` matched the ERROR TYPE NAME as a substring against a fixed tuple:

        ("HTTPError", "URLError", "ConnectionError", "TimeoutError", "SSLError")

    `ConnectionResetError` IS a `ConnectionError`, but the string "ConnectionResetError" does not
    contain the substring "ConnectionError". So the classifier returned False and the arithmetic ran:

        n_tasks=150  n_ok=138  n_unsupported=11  infra=0
        attempted = 150 - 11 - 0 = 139
        success_rate = 138/139 = 0.993

WHY THE FIX IS A LONGER LIST AND NOT `isinstance`
    Only the error STRING survives into the report; the exception object is gone by the time the
    snapshot is taken. So the honest fix is to enumerate the subtypes that actually occur -- and to
    say in the docstring that the list is a proxy for a type check, not the type check itself.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def cron():
    import cron_run
    return cron_run


def test_a_connection_reset_is_infrastructure(cron):
    """THE EXACT CASE THAT CAUSED THE FALSE REGRESSION."""
    assert cron._is_infra(
        "ConnectionResetError: [WinError 10054] remote host forcibly closed an existing connection")


def test_the_connection_subtypes_are_all_covered(cron):
    """`ConnectionResetError` was the one that fired, but its siblings have the same meaning."""
    for name in ("ConnectionResetError", "ConnectionAbortedError", "ConnectionRefusedError",
                 "ConnectionError"):
        assert cron._is_infra(f"{name}: something"), f"{name} is not classified as infrastructure"


def test_a_skill_refusal_is_NOT_infrastructure(cron):
    """THE OTHER DIRECTION. A refusal is a capability result and must be judged as one."""
    assert not cron._is_infra(
        "SkillError: encode.polar: 'panel_group' reduces to 2 distinct angle(s)")


def test_a_genuine_error_is_NOT_infrastructure(cron):
    """A crash in the pipeline is a capability failure, not a network problem."""
    assert not cron._is_infra("ValueError: unexpected data shape")
    assert not cron._is_infra("KeyError: 'missing_column'")


def test_an_empty_error_is_not_infrastructure(cron):
    assert not cron._is_infra(None)
    assert not cron._is_infra("")


def test_the_name_list_covers_the_subtypes_not_only_the_bases(cron):
    """THE DEFECT STATED AS A PROPERTY: every name in the tuple must be checked for whether its
    SUBTYPES also appear. A base-only list is what missed ConnectionResetError."""
    names = cron.INFRA_ERROR_NAMES
    assert "ConnectionResetError" in names, (
        "the list covers the base ConnectionError but not the subtype that actually occurred")
    assert len(set(names)) == len(names), "the list has duplicates"
