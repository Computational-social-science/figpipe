"""A legend that covers a data mark -- the blind spot the rubric table named.

WHY THIS EXISTS
    Round 80 mapped six vision-channel rubric items to deterministic checks and named each check's
    BLIND SPOT. The one for `legend occlusion` was:

        a legend covering a LINE without covering text is not detected

    because `overlapping_text` compares text to text. This file covers the check that closes it.

THE HARD PART WAS THE MEASUREMENT, NOT THE IDEA
    The first version summed each path's bounding-box overlap with the legend frame and reported
    "covered over 400% of its area" -- a ratio that cannot exceed 1 exceeded 4.

    The second version took a union over boxes and reported 100% for every legend inside the axes,
    because a data line drawn by `ax.plot` is ONE path whose BOUNDING BOX spans the whole axes:

        type=s  rect=(34.6, 22.3, 186.8, 123.1)  items=19

    A box cannot say where a line is. The working version walks the path ITEMS -- the actual
    segments -- and samples them against grid cells.

MEASURED, with the two cases that matter:
    legend in an empty corner, flat line elsewhere    2.1% covered
    legend centred over two crossing lines           15.5% covered

    A seven-fold separation, and the number cannot exceed 1.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _pdf(tmp_path, fn, stem="f"):
    """Render with a PINNED style.

    THE FAILURE WAS ORDER-DEPENDENT: this file passed alone and failed inside the suite, which means
    global state. Other tests install figpipe's rcParams and change matplotlib's globals, and a
    legend drawn under a different style has a different frame -- so the measured coverage moved.

    `plt.rcdefaults()` before the figure makes the measurement independent of whatever ran first.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    fn(ax)
    path = tmp_path / f"{stem}.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def _empty_corner(ax):
    x = np.arange(20)
    ax.plot(x, np.full(20, 5.0), label="a")
    ax.legend(loc="upper left")


def _over_crossing(ax):
    x = np.arange(20)
    ax.plot(x, x, label="a")
    ax.plot(x, 20 - x, label="b")
    ax.legend(loc="center")


def _no_legend(ax):
    x = np.arange(20)
    ax.plot(x, x)


def test_the_check_reports_that_it_is_implemented():
    """A check that cannot decide must SAY so, not return an empty list that reads as 'no problem'."""
    from figpipe import audit
    assert audit.legend_occlusion_supported() is True


def test_no_legend_means_no_occlusion(tmp_path):
    """NEGATIVE CONTROL: a figure with no legend has nothing to occlude."""
    from figpipe import audit
    assert audit.legend_occlusion(_pdf(tmp_path, _no_legend)) == []


def test_a_legend_over_lines_is_flagged(tmp_path):
    """POSITIVE: a legend centred on two crossing lines hides them."""
    from figpipe import audit
    hits = audit.legend_occlusion(_pdf(tmp_path, _over_crossing))
    assert hits, "a legend over crossing lines was not reported"
    assert hits[0]["covered_ratio"] > 0.02


def test_a_legend_in_an_empty_corner_is_NOT_flagged(tmp_path):
    """THE DISCRIMINATION. This is what a bounding-box test could not do: every legend inside the
    axes reported 100%, so the check could not tell a corner from a crossing."""
    from figpipe import audit
    hits = audit.legend_occlusion(_pdf(tmp_path, _empty_corner))
    assert not hits, f"a legend in an empty corner was flagged as occluding: {hits}"


def test_the_ratio_cannot_exceed_one(tmp_path):
    """The first version reported 400%. A ratio that cannot exceed 1 exceeding 4 is a tautology, not
    a measurement."""
    from figpipe import audit
    for fn in (_empty_corner, _over_crossing):
        for hit in audit.legend_occlusion(_pdf(tmp_path, fn)):
            assert 0.0 <= hit["covered_ratio"] <= 1.0, (
                f"covered_ratio={hit['covered_ratio']} is not a ratio")


def test_crossing_lines_cover_more_than_a_corner_legend(tmp_path):
    """THE SEPARATION IS THE MEASUREMENT. Two cases that a coin flip could not distinguish."""
    from figpipe import audit
    corner = audit.legend_occlusion(_pdf(tmp_path, _empty_corner, "a"))
    crossing = audit.legend_occlusion(_pdf(tmp_path, _over_crossing, "b"))
    c = crossing[0]["covered_ratio"] if crossing else 0.0
    k = corner[0]["covered_ratio"] if corner else 0.0
    assert c > k * 3, (
        f"a legend over crossing lines ({c}) is not clearly worse than one in a corner ({k})")


def test_segments_are_read_from_path_items_not_boxes(tmp_path):
    """The helper that made this possible: a line is ONE path with many segments."""
    import pymupdf
    from figpipe import audit
    doc = pymupdf.open(str(_pdf(tmp_path, _over_crossing)))
    segs = audit._segments(doc[0])
    doc.close()
    assert len(segs) > 10, f"only {len(segs)} segments found; the line was read as a box"
    for (x0, y0), (x1, y1) in segs[:5]:
        assert isinstance(x0, float) and isinstance(y0, float)
