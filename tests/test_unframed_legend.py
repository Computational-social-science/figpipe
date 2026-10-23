"""A legend without a frame is still a legend, and the project draws them that way on purpose.

WHY THIS EXISTS
    The pool reported `legend_frames: 0` across 139 figures and I concluded the pool has no legends.
    That conclusion was wrong: the detector only found FILLED-AND-STROKED rects, and this project's
    own default is `frameon=False` --

        ax.legend(frameon=False, ncol=..., loc=legend_loc, ...)

    with the comment "an inside legend is the most common way a faithful reproduction starts to look
    assembled rather than drawn". So the detector was blind to every legend the pipeline draws, and
    the "vacuous zero" was partly MY INSTRUMENT's zero.

MEASURED
    trend_with_uncertainty WITH a series column:
        labels 'alpha', 'beta', 'gamma' on the page at y=24.1
        framed-only detector: 0 frames
        fixed detector:       1 frame (433.9, 24.1, 509.1, 30.8)
    trend_with_uncertainty WITHOUT a series column: 0 frames   (correct -- no legend is drawn)

    And three ordinary figures whose tick labels form a tight row: 0 frames, so the new text-based
    rule does not mistake axis labels for a legend.

WHAT THE RULE IS
    Two sources, unioned: a filled white rect (a framed legend), and a run of at least two short
    labels sharing a baseline and TIGHTLY spaced (an unframed legend). A single axis label is a row
    of one and is excluded.
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
    import tempfile
    from figpipe import skills
    out = pathlib.Path(tempfile.mkdtemp(prefix="leg-"))
    return skills.run(skill, df, out_stem=out / skill, **kw)


def _frames(pdf):
    import pymupdf
    from figpipe import audit
    doc = pymupdf.open(str(pdf))
    n = sum(len(audit._legend_frames(page)) for page in doc)
    doc.close()
    return n


def test_an_unframed_legend_is_found():
    """THE DEFECT. `frameon=False` is this project's default, so the framed-only detector found
    nothing and the pool's zero was partly an instrument artefact."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "x": np.tile(np.arange(10), 3),
        "y": rng.random(30),
        "series": np.repeat(["alpha", "beta", "gamma"], 10)})
    result = _render("trend_with_uncertainty", df, x="x", y="y", series="series")
    assert _frames(result["pdf"]) >= 1, (
        "an unframed legend was not detected; the pool's zero may be the instrument's, not the data's")


def test_a_figure_without_a_series_has_no_legend():
    """NEGATIVE CONTROL: no series column means the drawer draws no legend, and none must be found."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": np.arange(10), "y": rng.random(10)})
    result = _render("trend_with_uncertainty", df, x="x", y="y")
    assert _frames(result["pdf"]) == 0


def test_tick_labels_are_not_mistaken_for_a_legend():
    """THE FALSE POSITIVE THE NEW RULE COULD INTRODUCE. Axis labels also form a row of short texts;
    they must not be read as a legend."""
    rng = np.random.default_rng(0)
    cases = [
        ("dual_measure", pd.DataFrame({"x": np.arange(12), "a": rng.random(12),
                                       "b": rng.random(12)}),
         dict(x="x", y1="a", y2="b")),
        ("ranked_composition", pd.DataFrame({"name": [f"c{i}" for i in range(10)],
                                             "v": rng.random(10)}),
         dict(label="name", value="v")),
    ]
    for name, df, kw in cases:
        result = _render(name, df, **kw)
        assert _frames(result["pdf"]) == 0, (
            f"{name}: a row of axis labels was read as a legend")


def test_the_legend_frame_is_where_the_labels_are():
    """THE BOX MUST CONTAIN THE LEGEND, not be an arbitrary rect."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "x": np.tile(np.arange(10), 3),
        "y": rng.random(30),
        "series": np.repeat(["alpha", "beta", "gamma"], 10)})
    result = _render("trend_with_uncertainty", df, x="x", y="y", series="series")
    import pymupdf
    from figpipe import audit
    doc = pymupdf.open(str(result["pdf"]))
    page = doc[0]
    frames = audit._legend_frames(page)
    label_boxes = []
    for block in page.get_text("dict").get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("text", "").strip() in ("alpha", "beta", "gamma"):
                    label_boxes.append(span["bbox"])
    doc.close()
    assert frames and label_boxes
    fx0, fy0, fx1, fy1 = frames[0]
    for bx0, by0, bx1, by1 in label_boxes:
        assert fx0 <= bx0 and bx1 <= fx1, "a legend label lies outside the detected frame"
        assert fy0 <= by0 and by1 <= fy1, "a legend label lies outside the detected frame"
