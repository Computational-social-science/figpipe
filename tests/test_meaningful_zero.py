"""The pool's zero on collisions is MEANINGFUL, and this proves it.

WHY THIS EXISTS
    After closing the merged-label false negative, the pool re-measured at `hard findings: 0` across
    139/139 tasks. That looks like a clean result and it needed to be checked, because this project
    has now recorded the vacuous zero several times: a count of zero over a set that contains no
    object for the check.

    The question is not "did the check report zero" but "did the check have something to look at".

WHAT WAS MEASURED
    The pool's own drawers, rendered at the densities the pool uses:

        radial_profile      245 glyphs    0 collisions
        grouped_measures    101 glyphs    0 collisions

    So the figures carry real text -- 245 glyphs is a dense figure -- and the check ran over it and
    found no collision. The zero is a PASS, not an absence of objects.

    Contrast with the legend-occlusion check, where the same pool carries 0 legend frames across
    139 figures: that zero IS vacuous, and `legend_coverage.n_measured` is what says so.

THE DISTINCTION THIS FILE PINS
    A zero needs a MEASURED DENOMINATOR IN THE SAME UNITS AS THE CHECK. For collisions that is the
    glyph count; for legend occlusion it is the legend-frame count. Neither is "the number of tasks".
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _render(skill, df, **kw):
    from figpipe import skills
    import tempfile
    out = pathlib.Path(tempfile.mkdtemp(prefix="dense-"))
    return skills.run(skill, df, out_stem=out / skill, **kw)


def _glyph_count(pdf) -> int:
    import pymupdf
    doc = pymupdf.open(str(pdf))
    page = doc[0]
    n = 0
    for blk in page.get_text("rawdict")["blocks"]:
        for line in blk.get("lines", []):
            for span in line.get("spans", []):
                n += len([c for c in span.get("chars", []) if c.get("c", "").strip()])
    doc.close()
    return n


def test_a_dense_figure_carries_real_text_and_no_collisions():
    """THE MEANINGFUL ZERO. A dense figure (hundreds of glyphs) must pass the collision check."""
    from figpipe import audit

    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "spoke": [f"measurement_name_{i}" for i in range(14)],
        "value": rng.random(14)})
    result = _render("radial_profile", df, theta="spoke", value="value")
    glyphs = _glyph_count(result["pdf"])
    assert glyphs > 100, (
        f"the figure carries only {glyphs} glyphs, so a zero-collision result would be vacuous")
    hits = audit.overlapping_glyphs(result["pdf"])
    assert hits == [], f"a dense figure produced {len(hits)} collisions"


def test_a_grouped_figure_carries_real_text_and_no_collisions():
    """A SECOND DENSITY. Two independent figures make the zero a measurement rather than one draw."""
    from figpipe import audit

    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "model": [f"model_{i}" for i in range(10)],
        "accuracy": rng.random(10), "f1": rng.random(10)})
    result = _render("grouped_measures", df, x="model", ycols=["accuracy", "f1"])
    glyphs = _glyph_count(result["pdf"])
    assert glyphs > 50, f"only {glyphs} glyphs; the zero would be vacuous"
    assert audit.overlapping_glyphs(result["pdf"]) == []


def test_the_pipeline_PREVENTS_collisions_rather_than_detecting_them():
    """THE FINDING THAT REPLACED MY POSITIVE CONTROL.

    I first asserted that 40 long labels on one axis must collide, and it did not: `grouped_measures`
    AGGREGATES with `agg='mean'`, so 40 rows became one bar and one label. Then
    `ranked_composition` with 30 long names drew 117 glyphs and STILL reported zero, because the
    drawer wraps and truncates (`MAX_LABEL_CHARS`).

    So on this pipeline the collision check's zero is not "the check is idle" -- it is "the drawers
    refuse or wrap before drawing". The check exists for figures that do NOT go through the drawers'
    label budget, and the raw-matplotlib tests cover that case.

    This assertion is the honest one: heavy labelling through the pipeline must NOT collide, because
    the protection is upstream.
    """
    from figpipe import audit

    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "name": [f"a_very_long_category_name_{i:02d}" for i in range(30)],
        "value": rng.random(30)})
    result = _render("ranked_composition", df, label="name", value="value")
    glyphs = _glyph_count(result["pdf"])
    assert glyphs > 50, f"only {glyphs} glyphs; the figure is not heavily labelled"
    hits = audit.overlapping_glyphs(result["pdf"])
    assert hits == [], (
        f"the pipeline's own drawer produced {len(hits)} collisions; its label budget is not "
        f"preventing what the check detects")


def test_a_vacuous_zero_needs_a_DIFFERENT_denominator():
    """THE DISTINCTION. For collisions the denominator is glyphs; for legend occlusion it is legend
    frames. Using the task count for either would report a pass where nothing was examined."""
    import json

    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not path.is_file():
        pytest.skip("no pool report")
    report = json.loads(path.read_text(encoding="utf-8"))
    cov = report.get("legend_coverage") or {}
    if not cov:
        pytest.skip("the report predates the field")
    # the legend check's denominator is its own unit, not the task count
    assert "n_measured" in cov
    if report.get("legend_frames") == 0 and cov.get("n_measured"):
        # and the report SAYS the zero is vacuous rather than presenting it as a pass
        assert "legend" in (cov.get("note") or "").lower()
