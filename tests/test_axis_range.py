"""A raster figure's AXES are the second claim it makes that a reader can check.

WHY THIS EXISTS
    A field or a mesh is one raster path, so its cell values never reach the PDF. Round 58 built a
    check for the colour scale, which is one claim that does reach it. The AXIS TICK LABELS are the
    other: they are text, and they state which coordinates the raster spans.

    If the x ticks stop at 8 while the data runs to 10, the rightmost fifth of the figure sits
    outside the stated coordinates and a reader cannot tell where those cells are.

HOW THE AXES ARE FOUND
    By POSITION, not by a caller flag: x labels sit in a row along the bottom of the page, y labels
    in a column along the left. That is where a Cartesian plot puts them and `composite` does not
    rotate axes. A cluster that is neither is not treated as an axis -- which is why the colour bar
    (a right-hand column) is never mistaken for one.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf", reason="PyMuPDF is needed to read the rendered page")

from figpipe import semantics  # noqa: E402


@pytest.fixture(scope="module")
def field_figure(tmp_path_factory):
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    n = 20
    z = rng.normal(0, 1, n * n)
    df = pd.DataFrame({"x": np.repeat(np.linspace(0, 10, n), n),
                       "y": np.tile(np.linspace(0, 5, n), n), "z": z})
    panel = composite.Panel("field_2d", df, {"x": "x", "y": "y", "value": "z"}, colorbar=True)
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    out = tmp_path_factory.mktemp("ax")
    paths = layout.save(fig, out / "f")
    return paths[0], df


def test_a_correct_figure_passes(field_figure):
    pdf, df = field_figure
    result = semantics.check_axis_range(pdf, df["x"], df["y"])
    assert result["state"] == "checked", f"a correct figure was rejected: {result}"


def test_the_check_reports_both_axes(field_figure):
    pdf, df = field_figure
    result = semantics.check_axis_range(pdf, df["x"], df["y"])
    assert "x" in result["axes"] and "y" in result["axes"]
    assert result["axes"]["x"]["state"] == "checked"
    assert result["axes"]["y"]["state"] == "checked"


def test_a_coordinate_range_wider_than_the_ticks_is_a_VIOLATION(field_figure):
    """THE DEFECT THIS CATCHES: data outside the stated coordinates."""
    pdf, df = field_figure
    result = semantics.check_axis_range(pdf, df["x"] * 5, df["y"] * 5)
    assert result["state"] == "violation", (
        f"coordinates five times wider than the printed ticks were accepted: {result}")
    assert result["axes"]["x"]["shortfall"] > 0.25


def test_ticks_wider_than_the_data_are_FINE(field_figure):
    """NEGATIVE CONTROL: a tick range that EXCEEDS the data is normal -- matplotlib pads axes."""
    pdf, df = field_figure
    result = semantics.check_axis_range(pdf, df["x"] / 2, df["y"] / 2)
    assert result["state"] == "checked", (
        f"a padded axis was reported as a violation: {result}")


def test_the_colour_bar_is_not_mistaken_for_an_axis(field_figure):
    """The colour bar is a RIGHT-hand column; neither axis is. If it were read as the y axis the
    check would compare the data range to the colour values."""
    pdf, df = field_figure
    result = semantics.check_axis_range(pdf, df["x"], df["y"])
    # the y axis must be the coordinate range [0, 5], not the colour scale [-3.77, 3.07]
    assert result["axes"]["y"]["state"] in ("checked", "unverifiable")


def test_verify_semantics_runs_the_axis_check():
    """The check must be part of the normal run, not a library function nobody calls."""
    import inspect
    from figpipe import skills
    src = inspect.getsource(skills.op_verify_semantics)
    assert "check_axis_range" in src, (
        "verify.semantics does not run the axis check, so no figure is held to its axes")


def test_negative_and_positive_labels_are_both_read(tmp_path):
    """AXIS LABELS ARE RIGHT-ALIGNED, so a minus sign shifts a label's LEFT edge.

    Measured on a y axis over [-9, 9]: '7.5'/'2.5'/'0.0' printed at x0=27.5 and '-2.5'/'-5.0'/'-7.5'
    at x0=24.5. A window anchored on the leftmost word captured ONLY the negative half, and the axis
    looked like it spanned [-7.5, -2.5] when it spanned [-7.5, 7.5] -- ten pool tasks were flagged
    for a defect that did not exist.
    """
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    n = 20
    z = rng.normal(0, 1, n * n)
    df = pd.DataFrame({"x": np.repeat(np.linspace(-9, 9, n), n),
                       "y": np.tile(np.linspace(-9, 9, n), n), "z": z})
    panel = composite.Panel("field_2d", df, {"x": "x", "y": "y", "value": "z"}, colorbar=True)
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    paths = layout.save(fig, tmp_path / "f")
    result = semantics.check_axis_range(paths[0], df["x"], df["y"])
    assert result["state"] == "checked", (
        f"a symmetric axis was reported as not covering its data: {result.get('detail')}")
    for axis in ("x", "y"):
        ticks = result["axes"][axis]
        assert ticks["state"] == "checked"
        assert ticks["shortfall"] < 0.25
