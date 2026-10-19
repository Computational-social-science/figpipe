"""A matrix axis must not carry more labels than it can show.

WHY THIS TEST
    Measured on the real PlotTwin-Bench pool: 13 of 14 `matrix_plate` tasks had hard text
    collisions at the CURRENT row budget, summing 995 findings with a worst case of 405 on one
    figure. The collisions were raw floats like

        '0.7015383331293864' over '0.7128659440184021'

    `ax_tile_diverging` set a tick label for EVERY row and column and annotated EVERY cell, with no
    budget on either. A 40-row matrix drew 40 tick labels plus up to 200 cell annotations on a
    90 mm panel. `MAX_MATRIX_ROWS` was never the lever -- even 40 rows cannot be labelled at 5.5 pt.

    The mutation loop had selected "raise the budget to 41" on a six-task fixture containing a clean
    41-row matrix. Applying that would have made all 14 tasks worse. This test pins the actual fix.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import grammar  # noqa: E402

MAX_LABELS = 12


def _matrix(n_rows: int, n_cols: int = 6, string_index: bool = True):
    df = pd.DataFrame(np.random.default_rng(0).random((n_rows, n_cols)),
                      index=[f"row{i}" for i in range(n_rows)] if string_index else None)
    fig = grammar.plate([grammar.panel("signed_matrix", df, colorbar=True, cbar_label="")],
                        columns=1.0, height_mm=90.0)
    return fig.axes[0]


@pytest.mark.parametrize("n", [4, 8, 12])
def test_a_small_matrix_keeps_its_labels(n):
    """Negative control: the budget must not hide labels that FIT."""
    ax = _matrix(n)
    drawn = [t for t in ax.get_yticklabels() if t.get_text()]
    assert len(drawn) == n, f"a {n}-row matrix should show {n} labels, showed {len(drawn)}"


@pytest.mark.parametrize("n", [20, 40, 60])
def test_a_tall_matrix_hides_its_labels(n):
    """The defect: 40 rows produced 40 labels and up to 405 collisions."""
    ax = _matrix(n)
    drawn = [t for t in ax.get_yticklabels() if t.get_text()]
    assert drawn == [], f"a {n}-row matrix drew {len(drawn)} labels; it cannot carry them"


def test_a_tall_matrix_does_not_annotate_every_cell():
    """Cell annotations are the other half: raw floats at 5.5 pt collide too."""
    ax = _matrix(40, 10)
    texts = [t for t in ax.texts if t.get_text()]
    assert len(texts) == 0, f"a 400-cell matrix wrote {len(texts)} annotations into the panel"


def test_the_benchmark_matrix_tasks_are_clean_after_the_fix():
    """The measured outcome: hard findings on matrix tasks fell 995 -> 98 on the real pool."""
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        pytest.skip("report absent")
    import json
    data = json.loads(report.read_text(encoding="utf-8"))
    mat = [t for t in data.get("tasks", []) if t.get("skill") == "matrix_plate"]
    if not mat:
        pytest.skip("no matrix tasks measured")
    total = sum((t.get("hard_failures") or 0) for t in mat)
    worst = max((t.get("hard_failures") or 0) for t in mat)
    assert total < 400, f"matrix tasks still carry {total} hard findings (was 995 before the fix)"
    assert worst < 200, f"the worst matrix task still has {worst} hard findings (was 405)"


def test_the_mutation_fixture_resembles_production():
    """A fixture that does not look like production selects the wrong edit, confidently.

    The first mutation space selected `matrix-max-rows-41` because its matrices used an INTEGER
    index -- and the drawer hides ticks for numeric indices, so the label path that produces the
    real collisions was never exercised. Its "unpivotable" tables were refused before reaching the
    drawer at all. The space now contains a real-shaped matrix (40x10, string index).
    """
    sys.path.insert(0, str(ROOT))
    from figpipe import mutation
    space = mutation.default_space()
    ids = [t.id for t in space.tasks]
    assert any("real" in i for i in ids), (
        f"the mutation space has no production-shaped matrix task: {ids}")
    real = next(t for t in space.tasks if "real" in t.id)
    df = real.frame()
    assert len(df) == 40 and df.shape[1] >= 8, (
        f"the real-shaped task is {df.shape}, not the benchmark's 40x10")
    # and it must carry a STRING index, which is what makes the axis over-full
    assert not isinstance(df.index[0], (int, float)), (
        "the real-shaped matrix must have a string index; a numeric one hides the ticks")
