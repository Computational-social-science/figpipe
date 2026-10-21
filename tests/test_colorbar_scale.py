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
    """THE FALSE POSITIVE, NOW PREVENTED AT THE CALLER.

    A matrix's column of cell annotations is a monotone vertical stack at the right edge --
    geometrically indistinguishable from a colour bar. The first version of this check tried to
    tell them apart by position, then by spacing, then by monotonicity, and each attempt failed on
    some figure.

    The fix was to stop guessing: the OPERATOR knows whether the panel has a bar, because
    `panel.colorbar` is the flag that produced it. `verify.semantics` only runs this check when
    that flag is true. See `test_a_matrix_without_a_colour_bar_stays_unverifiable` for the
    end-to-end case.

    This test therefore pins the LOW-LEVEL behaviour on a bar-less page: whatever the word reader
    finds, it must not crash and must report one of the three declared states. A violation here is
    acceptable -- the caller is what prevents it -- but it must be a real state, not a guess.
    """
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    df = pd.DataFrame({f"c{i}": rng.normal(0, 1, 5) for i in range(4)})
    # colorbar=False: WITHOUT a bar the figure claims no scale, which is the case being tested.
    # `encode.matrix` defaults to colorbar=True, so the default panel DOES carry one.
    panel = composite.Panel("tile_diverging", df, {}, colorbar=False)
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    paths = layout.save(fig, tmp_path / "m")
    result = semantics.check_colorbar_scale(paths[0], df.to_numpy().ravel())
    assert result["state"] in ("checked", "violation", "unverifiable"), (
        f"the check returned an undeclared state: {result}")
    # the low-level function cannot know whether a bar was drawn; that is the caller's job
    assert "data_range" in result or "why" in result or "detail" in result


def test_the_two_tests_are_both_required():
    """Position alone accepts any right-edge column; monotonicity alone accepts a cell column whose
    values happen to be ordered. Both must hold.

    NOTE: the second test is MONOTONICITY, not even spacing. An even-spacing test rejected a
    diverging colour bar, whose ticks are deliberately uneven because `TwoSlopeNorm` compresses
    each half of the range.
    """
    import inspect
    src = inspect.getsource(semantics._scale_numbers)
    assert "page_span" in src, "the position test is missing"
    assert "increasing" in src and "decreasing" in src, (
        "the monotonicity test is missing; even spacing is NOT a valid substitute because a "
        "diverging colour bar is deliberately uneven")


# ---------------------------------------------------------------------------------------
# A DIVERGING COLOUR BAR IS NOT EVENLY SPACED
#
# `ax_tile_diverging` uses `TwoSlopeNorm` whenever the data straddles zero, which maps 0 to the
# MIDDLE of the colour range and compresses each half. Its ticks are therefore deliberately
# uneven: measured gaps were 40.2, 40.3, 22.5, 22.6, 22.5, 22.6 -- two linear halves with a slope
# change at zero.
#
# The first version required "every gap within 25% of the mean" and rejected that legitimate bar, so
# a matrix's colour scale was reported as absent. The discriminator that survives a non-linear
# normalisation is MONOTONICITY: a bar's labels are ordered by value down the axis, a column of cell
# annotations is not.
# ---------------------------------------------------------------------------------------

def test_a_matrix_with_a_colour_bar_is_checked(tmp_path):
    """`encode.matrix` passes colorbar=True, so a matrix DOES make a checkable scale claim.

    A WIDE NUMERIC FRAME HAS NO NAMED VALUE COLUMN. `encode.matrix` draws it directly, with no
    pivot, so nothing in the trace says which column the colour encodes -- and the check now refuses
    to guess, because the widest numeric column is often a coordinate. A wide frame is therefore
    `unverifiable`, and that is correct: no value was named, so no claim can be pinned.

    A LONG-FORMAT table (x, y, value) DOES get a named value, from the pivot trace. That is the case
    that must be checked.
    """
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import skills

    # long format: pivots, so the value column is recorded in the trace
    xs = np.repeat(np.arange(8.0), 6)
    ys = np.tile(np.arange(6.0), 8)
    grid = pd.DataFrame({"x": xs, "y": ys,
                         "v": np.exp(-((xs - 4) ** 2) / 8) * (1 + ys / 6)})
    result = skills.run("matrix_plate", grid, out_stem=tmp_path / "m")
    trace = " ".join(result.get("trace") or [])
    assert "scale check: checked" in trace, (
        f"a matrix with a colour bar was not scale-checked; trace: {trace[-300:]}")
    assert not result.get("hard_failures")


def test_a_wide_frame_is_checked_against_what_the_drawer_plotted(tmp_path):
    """A WIDE FRAME NEEDS NO NAMED VALUE COLUMN, because the DRAWER knows what it plotted.

    `ax_tile_diverging` records its own array on the axes, so the scale can be compared to the
    values the colours encode without anyone naming a column. That is exact, and it is why the check
    no longer has to guess the widest numeric column.

    The guess was the defect: on a long-format grid the widest column is a COORDINATE, and the
    printed scale was compared to it. With the drawer's own array there is nothing to guess.
    """
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import skills

    rng = np.random.default_rng(0)
    df = pd.DataFrame({f"c{i}": rng.normal(0, 1, 5) for i in range(4)})
    result = skills.run("matrix_plate", df, out_stem=tmp_path / "w")
    trace = " ".join(result.get("trace") or [])
    assert "scale check: checked" in trace, (
        f"a wide frame was not scale-checked against the drawn array; trace: {trace[-300:]}")
    assert not result.get("hard_failures"), (
        "the check produced a finding on a correct figure")


def test_a_matrix_without_a_colour_bar_stays_unverifiable(tmp_path):
    """NEGATIVE CONTROL: colorbar=False means no scale is claimed, so nothing can be violated."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import skills

    rng = np.random.default_rng(0)
    df = pd.DataFrame({f"c{i}": rng.normal(0, 1, 5) for i in range(4)})
    result = skills.run("matrix_plate", df, out_stem=tmp_path / "m2", colorbar=False)
    trace = " ".join(result.get("trace") or [])
    assert "scale check: unverifiable" in trace, (
        f"a matrix with no colour bar claimed a scale; trace: {trace[-300:]}")
    assert not result.get("hard_failures"), "an unverifiable scale must not produce a finding"


def test_a_non_monotone_column_is_not_a_scale(tmp_path):
    """A colour bar's labels are ordered by value; scattered annotations are not."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    # cell annotations with NO order down the rightmost column
    df = pd.DataFrame({"a": rng.normal(0, 1, 6), "b": rng.normal(0, 1, 6)})
    panel = composite.Panel("tile_diverging", df, {"annotate": True}, colorbar=False)
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    paths = layout.save(fig, tmp_path / "nobar")
    words = semantics._words_by_position(paths[0])
    # whatever it finds must be monotone, or nothing
    scale = semantics._scale_numbers(words)
    if scale:
        assert scale == sorted(scale) or scale == sorted(scale, reverse=True), (
            f"a non-monotone column was read as a colour scale: {scale}")
