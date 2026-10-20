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
                      "n_panels_inferred", "text_chars"}
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
