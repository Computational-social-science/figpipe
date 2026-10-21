"""The validation figure must be able to EXPRESS the dimensions it is used to test.

WHY THIS TEST
    Round 48 found that the validation draws a single-series trend panel: one colour, one axis. Two
    of the six style dimensions cannot appear in it, and their tie rates gave it away -- `letters`
    tied 28/30 and `palette` 8/30. A dimension the figure cannot express ties on almost every pair,
    and a tie is a limit of the EXPERIMENT, not a weakness of the metric.

    This file pins BOTH directions:
      * the single-series panel really cannot express them (so the diagnosis is not folklore)
      * the multi-series multi-panel figure really can (so the fix is real)

    If only the second were tested, a figure that showed colour for an unrelated reason would pass.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pytest.importorskip("pymupdf", reason="PyMuPDF is needed to re-profile a rendered PDF")


@pytest.fixture(scope="module")
def checker():
    import check_panel_expressibility as c
    return c


def test_the_single_series_panel_cannot_express_the_palette(checker, tmp_path):
    """THE LIMITATION the round-48 diagnosis rests on."""
    got = checker.single_series(tmp_path)
    assert got["palette_present"] <= 1, (
        f"the single-series panel carried {got['palette_present']} of "
        f"{got['palette_expected']} palette colours; the panel CAN express a palette, so the "
        f"diagnosis would be wrong")


def test_the_single_series_panel_cannot_express_panel_letters(checker, tmp_path):
    got = checker.single_series(tmp_path)
    assert got["panel_letters"] < 2, (
        f"the single-series panel drew {got['panel_letters']} panel letters")


def test_the_multi_panel_EXPRESSES_the_palette(checker, tmp_path):
    """THE FIX: three series, three colours, all present in the rendered file."""
    got = checker.multi_series(tmp_path)
    assert got["palette_present"] >= 2, (
        f"the multi-series figure carried only {got['palette_present']} of "
        f"{got['palette_expected']} palette colours")


def test_the_multi_panel_EXPRESSES_panel_letters(checker, tmp_path):
    got = checker.multi_series(tmp_path)
    assert got["panel_letters"] >= 2, (
        f"the multi-panel figure drew {got['panel_letters']} panel letters")


def test_the_checker_passes_end_to_end(checker):
    assert checker.main() == 0


def test_the_validator_now_has_a_multi_panel():
    """The validator must be able to build the figure those dimensions need."""
    import inspect
    import validate_style_metric as v
    src = inspect.getsource(v)
    assert "_multi_panel" in src, (
        "the validator has no multi-series panel, so palette and letters remain untestable")
