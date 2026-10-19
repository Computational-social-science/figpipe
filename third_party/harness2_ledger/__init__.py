"""Vendored budget accounting from harness2 -- see NOTICE.md in this directory.

WHY THIS PACKAGE EXISTS
    figpipe's mutation loop must be able to REFUSE to exceed a rollout budget. Writing that
    accounting from scratch would be a second implementation of a solved problem, and the
    project's standing rule is that a control reimplemented by its consumer is a control nobody
    audited. harness2 (google-research/harness2, Apache 2.0) already ships a pure-stdlib ledger
    that counts rollouts and stages, so it is vendored here.

WHAT IS VENDORED
    `ledger.py`, byte-identical to upstream (see NOTICE.md for the commit sha and the sha256).
    It is NOT edited. This `__init__.py` is written by figpipe and re-exports the public names,
    so callers never import a third-party module path directly.

    The budget ENFORCEMENT (refusing before an over-budget rollout is executed) is figpipe's
    addition and lives in `figpipe/mutation.py`; the upstream ledger is a recorder plus an
    identity check, not an admission controller. Stating the split matters: a reader who
    assumes the vendored file refuses overspend would be wrong.
"""
from .ledger import (  # noqa: F401
    BudgetError,
    Entry,
    Ledger,
    expected_rollouts,
    expected_sessions,
)

__all__ = ["BudgetError", "Entry", "Ledger", "expected_rollouts", "expected_sessions"]
