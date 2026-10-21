"""The update rule must be a function of history -- and the measurement says that was not enough.

WHY THIS EXISTS
    Measured 2026-10-21: figpipe's loop had run 130 cycles, made 4 knowledge changes, and selected
    NOTHING in 127 of them. `mutation._verdict` had `min_margin = 0.1` as a literal.

    VisionHOPE's thesis is that a system whose update rule is a constant cannot adapt. That is the
    part figpipe can take -- not the backbone, not the CUDA kernels, not the gradients.

    BUT THE HONEST RESULT IS NEGATIVE: the adaptive margin computes to 0.060 against the constant
    0.100, and replaying the 180 recorded decisions selects **5 either way**. The margin was never
    the binding constraint. The verdict distribution is tie 134 / rejected 41 / selected 5, because
    the candidate space is five budget adjustments that usually change nothing.

    These tests pin BOTH the mechanism and the negative result, so a future round cannot claim the
    adaptive rule fixed the loop.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import adaptiverule as A  # noqa: E402


@pytest.fixture(scope="module")
def history():
    runs = []
    for f in sorted((ROOT / "knowledge" / "runs").glob("*.json")):
        try:
            runs.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    if not runs:
        pytest.skip("no run records")
    return A.history_from_runs(runs), runs


# ---------------------------------------------------------------------------------------
# The mechanism
# ---------------------------------------------------------------------------------------

def test_the_margin_is_computed_from_history_not_hard_coded(history):
    h, _ = history
    res = A.margin_from(h)
    assert res["margin"] != A.MARGIN_DEFAULT or res["resolution"] is not None, (
        "the margin fell back to the default even though history was available")
    assert res["separability"] is not None
    assert res["retention"] is not None
    assert 0.0 < res["retention"] <= 1.0


def test_the_margin_is_bounded(history):
    """A margin below the noise floor selects noise; above the ceiling the loop stops moving."""
    h, _ = history
    res = A.margin_from(h)
    assert A.MARGIN_FLOOR <= res["margin"] <= A.MARGIN_CEIL


def test_zero_deltas_do_not_drag_the_margin_to_the_floor(history):
    """THE BUG IN THE FIRST VERSION: the median of |delta| was 0 because 74% are exactly zero.

    The zeros mean "this candidate changed nothing", not "there is no difference to measure". Using
    the median of NON-ZERO deltas is the right statistic, and this test pins it.
    """
    h, _ = history
    res = A.margin_from(h)
    assert res["zero_share"] > 0.5, "the fixture is not exercising the zero-delta case"
    assert res["separability"] > 0.0, (
        "separability collapsed to zero, which means the zeros were included in the median")
    assert res["margin"] > A.MARGIN_FLOOR, (
        "the margin sits on the floor; the zero deltas dragged it down")


def test_the_rule_never_reads_the_candidate():
    """A rule that reads the thing it judges is the 'gate designed after the answer' failure.

    Check the CODE, not the comments: the docstring explains the failure mode and therefore
    contains the word.
    """
    import inspect
    src = inspect.getsource(A.margin_from)
    code = "\n".join(ln for ln in src.splitlines()
                     if ln.strip() and not ln.lstrip().startswith("#"))
    # strip the docstring
    import ast
    tree = ast.parse(src.lstrip())
    fn = tree.body[0]
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant):
        fn.body = fn.body[1:]
    body = ast.unparse(fn)
    for forbidden in ("candidate", "Cand"):
        assert forbidden not in body, (
            f"margin_from reads {forbidden!r} in its BODY; the rule must depend only on PAST "
            f"outcomes")


# ---------------------------------------------------------------------------------------
# The negative result
# ---------------------------------------------------------------------------------------

def test_the_adaptive_margin_does_not_change_what_gets_selected(history):
    """THE HONEST RESULT: 5 selections either way. The margin was never the constraint."""
    h, runs = history
    margin = A.margin_from(h)["margin"]
    const = would = total = 0
    for r in runs:
        for d in ((r.get("mutation") or {}).get("decisions") or []):
            delta = d.get("delta")
            if not isinstance(delta, (int, float)):
                continue
            total += 1
            const += delta >= 0.10
            would += delta >= margin
    assert total >= 100, f"only {total} decisions to replay; the fixture is too small"
    assert would == const, (
        f"the adaptive margin selects {would} against the constant's {const}. If this ever "
        f"diverges, the negative result in the docstring needs revisiting -- which would be good "
        f"news, but it must be checked rather than assumed")


def test_the_tie_rate_is_the_real_bottleneck(history):
    """74% ties: the candidates usually change nothing, so no threshold can separate them."""
    _, runs = history
    verdicts = {}
    for r in runs:
        for d in ((r.get("mutation") or {}).get("decisions") or []):
            verdicts[d.get("verdict")] = verdicts.get(d.get("verdict"), 0) + 1
    assert verdicts.get("tie", 0) > verdicts.get("selected", 0) * 5, (
        f"the tie rate is no longer dominant: {verdicts}. The docstring's diagnosis needs revising")
