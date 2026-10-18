"""A 2-D field must be drawn on its OWN coordinates, not as an arbitrary matrix.

WHY THIS TEST
    Field 2D was the worst chart type in the benchmark (styled 0.398 vs plain 0.312) because the
    mapper fed a long (x, y, value) table to `matrix_plate`, which drew the first 40 ROWS as if
    they were a grid. The axes then meant "row index", not position and time. The fix is a real
    field drawer whose axes are the measured coordinates; these tests pin that, and pin the refusal
    to invent data where a cell was never measured.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import composite, drawlib, layout, skills  # noqa: E402


def _field(nx=8, ny=6):
    xs = np.repeat(np.arange(nx, dtype=float), ny)
    ys = np.tile(np.arange(ny, dtype=float), nx)
    vals = np.exp(-((xs - nx / 2) ** 2) / 8.0) * (1 + ys / ny)
    return pd.DataFrame({"pos": xs, "time": ys, "conc": vals})


def _render(panels, stem):
    fig = composite.composite(panels, columns=1.0, height_mm=90.0, letters=True)
    return fig, pathlib.Path(layout.save(fig, stem)[0])


def test_the_axes_are_the_measured_coordinates_not_the_row_index(tmp_path):
    df = _field()
    fig, pdf = _render([composite.Panel("field_2d", df,
                                        {"x": "pos", "y": "time", "value": "conc"})],
                       tmp_path / "field")
    ax = fig.axes[0]
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    assert x0 <= 0 and x1 >= df["pos"].max() - 1e-9
    assert y0 <= 0 and y1 >= df["time"].max() - 1e-9
    assert pdf.is_file() and pdf.stat().st_size > 0


def test_the_skill_runs_through_the_global_floor(tmp_path):
    res = skills.run("field_map", _field(), out_stem=tmp_path / "fm",
                     x="pos", y="time", value="conc")
    assert res["hard_failures"] == 0, res["findings"]
    assert res["panels"] == 1


def test_missing_cells_are_not_filled_with_zero(tmp_path):
    df = _field()
    df = df[~((df["pos"] == 2) & (df["time"] == 2))]      # punch a hole
    fig, _ = _render([composite.Panel("field_2d", df,
                                      {"x": "pos", "y": "time", "value": "conc"})],
                     tmp_path / "hole")
    mesh = fig.axes[0].collections[0]
    data = np.ma.getmaskarray(mesh.get_array())
    assert data.any(), "an unmeasured cell must stay masked, not become 0"


def test_a_degenerate_pivot_is_refused():
    df = pd.DataFrame({"x": [0.0, 1.0, 2.0], "y": [0.0, 0.0, 0.0], "v": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="at least 2"):
        composite.Panel("field_2d", df, {"x": "x", "y": "y", "value": "v"})
        drawlib.ax_field_2d(object(), df, x="x", y="y", value="v")


def test_log_colour_needs_positive_values():
    df = _field()
    df.loc[0, "conc"] = 0.0
    with pytest.raises(ValueError, match="strictly positive"):
        _render([composite.Panel("field_2d", df,
                                 {"x": "pos", "y": "time", "value": "conc",
                                  "log_color": True})], "/tmp/neg")
