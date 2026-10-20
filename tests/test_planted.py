"""Planted-truth controls: does the pipeline recover a value written down first?

WHY THIS EXISTS
    figpipe's controls were all FIGURE-level: the acceptance gate passes a clean figure and fails a
    wrong one. That tests the GATE, not the pipeline. Nothing planted a known value in the DATA and
    demanded that the drawn figure carry it through.

    BootLoops' `planted-truth` protocol states why that matters:

        Real data cannot grade a pipeline. Whatever comes out looks like a finding -- a slope, an
        evidence ratio, a list of anomalies, an empty list of anomalies. The only inputs whose
        correct output is known are the ones you construct.

THE TRAP THIS FILE GUARDS AGAINST
    My first version re-derived the planted number FROM THE FRAME and compared it to itself. That is
    BootLoops' named failure mode "certifying at fitted points": agreement at points the derivation
    already reproduces measures nothing. The plants now ALSO read the value back from the RENDERED
    PDF -- bar heights, line extent, box height -- so the check is on the figure.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import planted  # noqa: E402

pytest.importorskip("pypdf", reason="pypdf not installed")


@pytest.fixture(scope="module")
def recovery(tmp_path_factory):
    return planted.recover_all(out_dir=tmp_path_factory.mktemp("planted"))


def test_every_planted_value_is_recovered(recovery):
    """A pipeline that cannot carry a KNOWN value through cannot be trusted on an unknown one."""
    assert recovery["all_recovered"] is True, (
        f"these plants failed: {recovery['failed']}\n"
        + "\n".join(f"  {p['name']}: {p['detail']}" for p in recovery["plants"]
                    if not p["passed"]))


def test_the_recovery_reads_the_figure_not_only_the_data(recovery):
    """THE TRAP: re-deriving from the frame certifies the recovery rule, not the pipeline.

    Every plant's detail must mention what the FIGURE showed -- a bar spread, a line extent, a box
    height -- not only the number recomputed from the frame.
    """
    figure_words = ("bars", "bar height ratio", "line spans", "box paths")
    for p in recovery["plants"]:
        assert any(w in p["detail"] for w in figure_words), (
            f"{p['name']} was certified without reading the figure: {p['detail']}")


def test_a_constant_plant_draws_equal_bars(tmp_path):
    """Every observation is 7.25, so every bar must be the same height -- to 1e-6 pt."""
    plant = planted.run_plant(planted.plant_constant_mean(), out_dir=tmp_path)
    assert plant.passed, plant.detail
    assert "height spread 0" in plant.detail or "spread 0 pt" in plant.detail, plant.detail


def test_an_exact_ratio_plant_draws_that_ratio(tmp_path):
    """Groups of 3.0 and 1.0 must draw bars whose heights are in a 3:1 ratio."""
    plant = planted.run_plant(planted.plant_exact_ratio(), out_dir=tmp_path)
    assert plant.passed, plant.detail
    assert "3.0000" in plant.detail, plant.detail


def test_a_zero_spread_plant_draws_a_zero_height_box(tmp_path):
    """Identical values draw a box of height exactly 0; a non-zero height means invented spread."""
    plant = planted.run_plant(planted.plant_constant_spread(), out_dir=tmp_path)
    assert plant.passed, plant.detail
    assert "zero as planted" in plant.detail, plant.detail


def test_the_comparison_can_fail(tmp_path):
    """NEGATIVE CONTROL: a wrong expected value must be reported as a mismatch.

    Without this, a comparison that ignores its inputs and returns `expected == recovered` would
    pass every plant in this file.
    """
    c = planted.corruption_control(out_dir=tmp_path)
    assert c["fired"] is True, c["reason"]
    assert "reading the data" in c["reason"]


def test_each_plant_is_judged_by_its_own_geometry(recovery):
    """THE BUG: the bar-height test ran before the per-plant dispatch, so the LINE and BOX plants
    were rejected for having no bars -- a check applied to the wrong object."""
    by_name = {p["name"]: p for p in recovery["plants"]}
    assert "bars" in by_name["constant-mean"]["detail"]
    assert "line spans" in by_name["exact-slope"]["detail"]
    assert "box paths" in by_name["zero-spread"]["detail"]
