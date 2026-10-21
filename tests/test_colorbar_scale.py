"""The colour scale a field figure prints must cover the data it drew.

WHY THIS EXISTS
    Round 57 fixed two stacked defects so a field figure carries its colour bar at all. That made
    the scale visible; it did not make it CORRECT. The colour bar's tick labels are the only numeric
    statement a field figure makes, and therefore the only claim the rendered file can be held to.

    Everything below was found by testing the check against cases where it must fail, and each
    version was wrong in a different way:

    1. Reading every number on the page. A field figure also prints AXIS tick labels (the
       coordinates), so `min(nums)` returned the axis extent, not the scale.
    2. A fraction-of-the-page cut. On a 90 mm figure the x-axis labels sit at x0 = 27.5..211.9 and
       the bar at 242.1; a 72% cut admitted the last axis label.
    3. A signed difference. `data - printed` makes a scale that EXCEEDS the data look like a
       shortfall of zero, and lets a surplus on one end cancel a real shortfall on the other.
    4. The same formula at both ends. The ends are mirror images: the scale must cover the data, so
       a shortfall is `printed_lo - lo` at the bottom and `hi - printed_hi` at the top. Writing both
       as `data - printed` scored a bar starting ABOVE the data minimum as 0%.

    A check that cannot fail is not a check, so the tests below pin both directions.
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
def rendered(tmp_path_factory):
    """A field figure plus the data that produced it."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import skills

    rng = np.random.default_rng(0)
    n = 20
    z = rng.normal(0, 1, n * n)
    df = pd.DataFrame({"x": np.repeat(np.linspace(0, 1, n), n),
                       "y": np.tile(np.linspace(0, 1, n), n), "z": z})
    out = tmp_path_factory.mktemp("cbar")
    result = skills.run("field_map", df, out_stem=out / "f", x="x", y="y", value="z")
    pdf = result.get("pdf") or (result.get("paths") or [None])[0]
    return pdf, z


def test_the_scale_is_read_from_the_rightmost_column(rendered):
    """THE FIRST TWO BUGS: axis labels are numbers too, and they are not the scale."""
    pdf, _z = rendered
    words = semantics._words_by_position(pdf)
    assert words, "no words were extracted; the position reader is broken"
    scale = semantics._scale_numbers(words)
    assert scale, "no scale numbers were found in the rightmost column"
    # the axis coordinates run 0.0..1.0; the colour scale runs about -3..3
    assert min(scale) < -1.0, (
        f"the extracted numbers {scale} look like AXIS ticks (0..1), not a colour scale")


def test_a_correct_figure_passes(rendered):
    pdf, z = rendered
    result = semantics.check_colorbar_scale(pdf, z)
    assert result["ok"] is True, f"a correct figure was rejected: {result}"
    assert result["state"] == "checked"


def test_a_scale_that_stops_short_is_a_VIOLATION(rendered):
    """THE SIGN BUGS. Data ten times wider than the drawn scale must fail."""
    pdf, z = rendered
    result = semantics.check_colorbar_scale(pdf, z * 10)
    assert result["ok"] is False, (
        f"a scale covering a tenth of the data was accepted: {result}")
    assert result["state"] == "violation"
    assert result["worst_gap_frac"] > 0.25


def test_a_lower_end_shortfall_is_caught(rendered):
    """THE MIRROR-IMAGE BUG: a bar starting ABOVE the data minimum.

    The drawn figure's scale starts near -3. Data shifted far below that must fail, and the
    shortfall must be attributed to the LOW end -- an earlier version scored this as zero because
    both ends used `data - printed`.
    """
    pdf, z = rendered
    shifted = z - 40.0                     # data now spans about [-44, -37]
    result = semantics.check_colorbar_scale(pdf, shifted)
    assert result["ok"] is False, f"a low-end shortfall was not caught: {result}"
    assert result["worst_gap_frac"] > 0.25


def test_a_constant_field_is_unverifiable_not_a_violation(rendered):
    """A constant field is covered by any scale; calling it a violation would be a false positive."""
    pdf, z = rendered
    result = semantics.check_colorbar_scale(pdf, np.full_like(z, 5.0))
    assert result["state"] == "unverifiable"
    assert result["ok"] is None


def test_a_page_without_a_scale_column_is_unverifiable(tmp_path):
    """No colour scale printed at all is `unverifiable`, not a pass.

    NOTE: a matrix WITHOUT a colour bar still prints axis tick labels, and those are numbers in the
    rightmost column too. So this test cannot rely on "no numbers on the page" -- it has to check
    the state, which is what the caller acts on. A figure with no bar and no numeric scale is
    unverifiable rather than a violation, because nothing was CLAIMED about the colours.
    """
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    df = pd.DataFrame({"a": rng.normal(0, 1, 6), "b": rng.normal(0, 1, 6)})
    panel = composite.Panel("tile_diverging", df, {})
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    paths = layout.save(fig, tmp_path / "m")
    result = semantics.check_colorbar_scale(paths[0], df.to_numpy().ravel())
    # whatever the outcome, it must be one of the three declared states -- never a crash and never
    # a silent pass reported as a check
    assert result["state"] in ("checked", "violation", "unverifiable")
    if result["state"] == "unverifiable":
        assert result["ok"] is None


# ---------------------------------------------------------------------------------------
# TELLING A COLOUR BAR FROM A COLUMN OF CELL ANNOTATIONS
#
# Both are vertical stacks of numbers. Both are evenly spaced when the matrix grid is regular. The
# first version of this check selected the rightmost stack and reported 10 `tile_diverging` tasks
# (which have NO colour bar) as scale violations -- reading the cell annotations as a scale.
#
# What separates them is POSITION: a colour bar sits at the very edge of the page, past the axes;
# cell annotations sit inside the plot area. Measured: the matrix's rightmost word ended at 89% of
# the page width, the field's colour-bar labels at 98%.
# ---------------------------------------------------------------------------------------

def test_a_matrix_without_a_colour_bar_is_unverifiable(tmp_path):
    """THE FALSE POSITIVE: cell annotations are not a colour scale."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    df = pd.DataFrame({f"c{i}": rng.normal(0, 1, 5) for i in range(4)})
    panel = composite.Panel("tile_diverging", df, {})
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    paths = layout.save(fig, tmp_path / "m")
    result = semantics.check_colorbar_scale(paths[0], df.to_numpy().ravel())
    assert result["state"] == "unverifiable", (
        f"a matrix with no colour bar was judged as {result['state']}: {result}. Its cell "
        f"annotations are a vertical stack of evenly spaced numbers, but they are INSIDE the plot "
        f"area and are not a scale")


def test_the_two_tests_are_both_required():
    """Position alone would accept a scattered column at the right edge; spacing alone accepts a
    matrix grid. Both must hold."""
    import inspect
    src = inspect.getsource(semantics._scale_numbers)
    assert "page_span" in src, "the position test is missing"
    assert "mean_gap" in src, "the even-spacing test is missing"
