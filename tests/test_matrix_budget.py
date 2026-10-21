"""The matrix row budget must apply to the PIVOTED shape, not only the raw table.

WHY THIS EXISTS
    `op_encode_matrix` consults `max_rows` only in the branch where NO 2-D reading exists. When a
    pivot SUCCEEDS it took the pivot whatever shape it produced.

    Measured on the pool: 14 `matrix_plate` tasks were reported `unverifiable`. Investigating why
    found 40-row matrices drawn on a 90 mm panel -- 2.25 mm per row. The drawer then hides BOTH the
    tick labels and the annotations (its own density rule, `readable = rows <= 12 and cols <= 12`),
    so the rendered file carries no recoverable cell values and no rendered-file check can exist.

    The `unverifiable` label was therefore CORRECT, and the reason in MESH_DRAWERS ("the cell values
    are not in the PDF") is accurate. The defect is one level up: the pipeline DREW a figure nobody
    can read instead of refusing.

WHAT THE FIX DOES
    The budget now applies to the pivoted shape. A pivot landing past it raises SkillError naming
    the size and the fix -- the same shape as every other refusal in this operator.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import skills  # noqa: E402


@pytest.fixture(scope="module")
def tmp_stem(tmp_path_factory):
    return str(tmp_path_factory.mktemp("mx") / "m")


def test_a_pivot_past_the_budget_is_refused(tmp_stem):
    """THE BUG: a successful pivot bypassed the budget entirely."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "rowkey": np.repeat(np.arange(40), 8),
        "colkey": np.tile(np.arange(8), 40),
        "value": rng.normal(0, 1, 320),
    })
    with pytest.raises(skills.SkillError) as exc:
        skills.run("matrix_plate", df, out_stem=tmp_stem)
    msg = str(exc.value)
    assert "budget" in msg, f"the refusal does not name the budget: {msg}"
    assert "field_map" in msg or "aggregate" in msg, (
        f"the refusal does not name a fix: {msg}")


def test_a_pivot_inside_the_budget_still_renders(tmp_stem):
    """NEGATIVE CONTROL: the fix must not refuse readable matrices."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "rowkey": np.repeat(np.arange(6), 5),
        "colkey": np.tile(np.arange(5), 6),
        "value": rng.normal(0, 1, 30),
    })
    result = skills.run("matrix_plate", df, out_stem=tmp_stem + "_ok")
    assert result is not None
    trace = " ".join(result.get("trace") or [])
    assert "encode.matrix" in trace


def test_the_budget_constant_is_used_not_a_literal():
    """The budget must remain a parameter so the mutation loop can probe it."""
    assert hasattr(skills, "MAX_MATRIX_ROWS")
    assert isinstance(skills.MAX_MATRIX_ROWS, int)


# ---------------------------------------------------------------------------------------
# THE UNVERIFIABLE REASON MUST CARRY ITS MEASUREMENT
#
# "the cell values are not in the PDF" states the conclusion and hides the cause. A reader cannot
# tell whether it is a FORMAT limit or a bug, nor at what size it stops being true.
#
# The measurement: a 40-row matrix on a 90 mm panel gives 2.25 mm per row, and a 5.5 pt label needs
# about 2 mm, so the drawer's density rule hides both ticks and annotations above 12 per axis.
# ---------------------------------------------------------------------------------------

def test_the_mesh_reason_names_the_row_limit():
    from figpipe import semantics
    assert semantics.MESH_LABEL_ROW_LIMIT == 12, (
        "the row limit moved; the density rule in drawlib.ax_tile_diverging uses its own "
        "MAX_AXIS_LABELS and the two must agree")
    for draw, reason in semantics.MESH_DRAWERS.items():
        assert str(semantics.MESH_LABEL_ROW_LIMIT) in reason, (
            f"{draw}'s reason does not name the row limit it depends on: {reason}")


def test_the_mesh_reason_carries_a_measurement():
    """A reason with numbers can be checked; one without numbers is an assertion."""
    from figpipe import semantics
    reason = semantics.MESH_DRAWERS["tile_diverging"]
    assert "mm" in reason, f"the reason carries no measurement: {reason}"
    assert "colour" in reason, (
        f"the reason does not say what the values become instead of text: {reason}")


def test_the_two_limits_agree():
    """The drawer's MAX_AXIS_LABELS and the semantics row limit describe the same boundary."""
    import inspect
    from figpipe import drawlib, semantics
    src = inspect.getsource(drawlib.ax_tile_diverging)
    assert "MAX_AXIS_LABELS" in src
    # extract the literal and compare
    import re
    m = re.search(r"MAX_AXIS_LABELS\s*=\s*(\d+)", src)
    assert m, "the drawer no longer declares MAX_AXIS_LABELS"
    assert int(m.group(1)) == semantics.MESH_LABEL_ROW_LIMIT, (
        f"the drawer hides labels above {m.group(1)} rows but semantics says "
        f"{semantics.MESH_LABEL_ROW_LIMIT}; the unverifiable reason would be wrong")
