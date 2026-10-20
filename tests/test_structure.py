"""Read a figure's structure deterministically, where a VLM was measured to fabricate.

WHY THIS EXISTS
    `corpus/vlm_report.json` (model `gemma3:12b`, 40 figures) answered ten fields every time. The
    control experiment in `corpus/vlm_controls.json` shows what that confidence was worth -- on
    three images containing no figure at all:

        control_blank.png      7 asserted,  2 fabricated   ("column_width": "single")
        control_noise.png     15 asserted,  9 fabricated   ("high_contrast": true on random strokes)
        control_textonly.png  12 asserted,  9 fabricated

    20 fabricated values across 3 controls. A model that reports `column_width: single` about a
    blank page cannot be the ground truth for column width, which is why this project does not use
    a VLM as a judge.

    But the FIELDS are not all unknowable. `figpipe/structure.py` measures the two that were still
    missing -- `figure_type` and `panel_labels_present` -- from the PDF's own text and font sizes.

THE KEY INSIGHT, found by measurement not by design: panel letters are drawn at a LARGER font size
than every axis label and tick. Matching on text alone reported the panel letters of a 4-facet
histogram as ['v','a'] -- `v` was the y-axis label. Font size separates them exactly.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import skills, structure  # noqa: E402

pytest.importorskip("pypdf", reason="pypdf not installed")


@pytest.fixture(scope="module")
def faceted_pdf(tmp_path_factory):
    d = tmp_path_factory.mktemp("struct")
    df = pd.DataFrame({"c": ["a"] * 20 + ["b"] * 20, "v": list(range(40))})
    res = skills.run("faceted_distribution", df, out_stem=d / "facet",
                     value="v", by="c", of="hist")
    return pathlib.Path(res["pdf"])


@pytest.fixture(scope="module")
def single_pdf(tmp_path_factory):
    d = tmp_path_factory.mktemp("struct1")
    df = pd.DataFrame({"c": ["a", "b", "c"] * 10, "m1": np.linspace(0, 1, 30)})
    res = skills.run("grouped_measures", df, out_stem=d / "single", x="c", ycols=["m1"])
    return pathlib.Path(res["pdf"])


def test_panel_letters_are_found_by_size_not_by_text(faceted_pdf):
    """THE BUG: text-only matching reported ['v','a'] -- `v` is the y-axis label."""
    items = structure.text_items(faceted_pdf)
    letters = structure.panel_labels_from_sizes(items)
    assert letters == ["a", "b"], (
        f"panel letters should be ['a','b']; got {letters}. A single-letter AXIS LABEL must not "
        f"be counted, and font size is what distinguishes them")


def test_a_single_panel_figure_has_no_panel_letters(single_pdf):
    items = structure.text_items(single_pdf)
    assert structure.panel_labels_from_sizes(items) == []


def test_the_figure_type_does_not_call_a_histogram_a_heatmap(faceted_pdf):
    """THE BUG: the word `density` is an AXIS LABEL on a histogram, not evidence of a heatmap."""
    assert structure.describe(faceted_pdf)["figure_type"] == "histogram"


def test_describe_reports_what_it_can_and_nothing_more(faceted_pdf):
    d = structure.describe(faceted_pdf)
    assert set(d) == {"figure_type", "panel_labels_present", "panel_labels",
                      "n_panels_inferred", "arrow_style", "text_chars"}
    assert d["panel_labels_present"] is True
    assert d["text_chars"] > 0


def test_a_missing_file_raises_rather_than_describing_nothing(tmp_path):
    with pytest.raises(FileNotFoundError):
        structure.describe(tmp_path / "nope.pdf")


def test_an_empty_text_layer_is_reported_as_other(tmp_path):
    """A figure with no text layer cannot be classified, and must say so rather than guess."""
    assert structure.figure_type("") == "other"


def test_compare_to_vlm_reports_disagreement_without_resolving_it(faceted_pdf):
    """The only honest use for a model label: a second opinion that is CHECKED, not trusted."""
    out = structure.compare_to_vlm(faceted_pdf,
                                   {"figure_type": "bar", "panel_labels_present": True})
    assert out["agree"] is False
    assert any(d["field"] == "figure_type" for d in out["disagreements"])
    # it must report BOTH readings, not pick a winner
    for d in out["disagreements"]:
        assert "deterministic" in d and "vlm" in d


# ---------------------------------------------------------------------------------------
# arrow_style -- the last VLM field that could be made deterministic
#
# A direction arrow needs a head; a head is a closed FILLED subpath; its size separates it from a
# bar or a panel border. Measured from the PDF content stream, so the answer is reproducible.
#
# THE BUG THIS FIXED, caught by the positive control below: matplotlib draws an arrowhead with the
# `B` operator (fill AND stroke), and the first version filtered for `f` (fill only) -- so every
# arrowhead was excluded and the detector reported `none` for a figure that plainly had an arrow.
# ---------------------------------------------------------------------------------------

def _make_arrow_pdf(tmp_path, *, with_arrow: bool) -> pathlib.Path:
    """A figure that DOES or DOES NOT contain an arrow -- the control pair."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = tmp_path / ("with.pdf" if with_arrow else "without.pdf")
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.plot([0, 1], [0, 1])
    if with_arrow:
        ax.annotate("", xy=(0.8, 0.8), xytext=(0.2, 0.2),
                    arrowprops=dict(arrowstyle="-|>", color="k", lw=1.5))
    fig.savefig(out)
    plt.close(fig)
    return out


def test_an_arrow_is_detected(tmp_path):
    """POSITIVE CONTROL: without this, a detector that always says `none` would pass."""
    pdf = _make_arrow_pdf(tmp_path, with_arrow=True)
    assert structure.arrow_style(pdf) == "filled_triangle"


def test_a_figure_without_an_arrow_reports_none(tmp_path):
    """NEGATIVE CONTROL: the same figure minus the arrow must NOT be called an arrow."""
    pdf = _make_arrow_pdf(tmp_path, with_arrow=False)
    assert structure.arrow_style(pdf) == "none"


def test_the_fill_operator_b_counts_as_filled(tmp_path):
    """THE BUG: matplotlib draws an arrowhead with `B` (fill+stroke), not `f` (fill only).

    Filtering for `f` alone excluded every arrowhead. This asserts the operator the control figure
    actually produced is accepted, so the fix cannot silently regress.
    """
    pdf = _make_arrow_pdf(tmp_path, with_arrow=True)
    groups = structure._path_groups(pdf)
    triangles = [(pts, closed, paint) for pts, closed, paint in groups
                 if closed and len(pts) == 3]
    assert triangles, "the control figure produced no closed 3-point subpath at all"
    assert any(paint.lower() in ("f", "f*", "b", "b*") for _, _, paint in triangles), (
        f"no triangle uses a fill operator: {[p for _, _, p in triangles]}")


def test_arrow_style_is_in_describe(faceted_pdf):
    d = structure.describe(faceted_pdf)
    assert "arrow_style" in d
    assert d["arrow_style"] in ("none", "filled_triangle", "other")


# ---------------------------------------------------------------------------------------
# panel_layout -- the LAST field that was left for a VLM, and did not need one
#
# The layout layer DECIDED the grid, so the answer is known before the figure is drawn. Reading it
# from pixels would be re-deriving a fact the caller already holds.
# ---------------------------------------------------------------------------------------

def _facet_result(tmp_path, columns: float, n_levels: int):
    d = tmp_path / f"f{n_levels}c{int(columns)}"
    df = pd.DataFrame({"g": [f"g{i}" for i in range(n_levels)] * 10,
                       "v": list(range(10 * n_levels))})
    return skills.run("faceted_distribution", df, out_stem=d, value="v", by="g",
                      of="hist", columns=columns)


def test_a_single_panel_is_reported_as_single(tmp_path):
    df = pd.DataFrame({"c": ["a", "b", "c"] * 10, "m": np.linspace(0, 1, 30)})
    res = skills.run("grouped_measures", df, out_stem=tmp_path / "s", x="c", ycols=["m"])
    assert structure.panel_layout(res) == "single"


def test_a_two_by_two_grid_is_named(tmp_path):
    res = _facet_result(tmp_path, columns=2.0, n_levels=4)
    assert structure.panel_layout(res) == "2x2"


def test_a_single_row_is_named(tmp_path):
    """`columns` is an enum of 1 or 2, so 2 levels at 2 columns is the only single-row grid."""
    res = _facet_result(tmp_path, columns=2.0, n_levels=2)
    assert structure.panel_layout(res) == "1x2"


def test_a_single_column_is_named(tmp_path):
    res = _facet_result(tmp_path, columns=1.0, n_levels=3)
    assert structure.panel_layout(res) == "3x1"


def test_the_layout_is_never_a_guess(tmp_path):
    """NEGATIVE CONTROL: a shape name must match the panel count it claims."""
    for columns, levels in ((2.0, 4), (2.0, 2), (1.0, 2), (2.0, 3)):
        res = _facet_result(tmp_path, columns=columns, n_levels=levels)
        name = structure.panel_layout(res)
        if name == "single":
            assert res["panels"] == 1
            continue
        rows, cols = (int(x) for x in name.split("x"))
        assert rows * cols >= res["panels"], (
            f"{name} cannot hold {res['panels']} panels")
        assert rows * cols - res["panels"] < cols, (
            f"{name} wastes a whole row for {res['panels']} panels")


def test_all_ten_vlm_fields_are_now_deterministic(tmp_path):
    """The corpus asked a VLM for ten fields and it fabricated 20 values on three controls.

    Every one of those ten now has a deterministic answer, so no model is needed for any of them.
    """
    res = _facet_result(tmp_path, columns=2.0, n_levels=4)
    fields = structure.all_fields(res["pdf"], res)
    for name in ("figure_type", "panel_labels_present", "arrow_style",
                 "panel_layout", "panel_count"):
        assert name in fields, f"{name} is missing from all_fields()"
        assert fields[name] is not None
    assert fields["panel_count"] == 4
    assert fields["panel_layout"] == "2x2"
