"""The merged-label false negative is CLOSED, and the fix is proven by two measurements.

WHY THIS EXISTS
    Round 84 recorded a real false negative: twelve labels merged into ONE span at 4 pt reported ZERO
    collisions, because `overlapping_glyphs` skipped pairs inside one span -- the filter that removes
    rotated-label false positives. The worse the crowding, the more likely the merge, so the check
    reported FEWER collisions as the defect got worse.

    A first fix ("skip only adjacent characters") made it worse: 12 false positives on rotated
    labels. It was reverted.

THE WORKING FIX, and why it is the third attempt
    1. `span_id` filter removed entirely   -> rotated labels false-positive
    2. "skip only adjacent characters"     -> same, 12 false positives
    3. LINE DIRECTION + aggregation key    -> both cases correct

    PyMuPDF reports the line direction: upright labels carry `dir=(1.0, 0.0)`, rotated ones carry
    `dir=(0.707, -0.707)`. A pair inside one span is a real collision only when the line is
    horizontal.

    And the geometry says where the boundary is: measured inside a merged span, the gap between
    consecutive characters WITHIN a label is +0.00 pt, while at a LABEL BOUNDARY it is -1.87 pt.

THE SECOND DEFECT FOUND ON THE WAY
    Even after the pairs were counted, the aggregation key was the span-TEXT pair -- identical for
    every pair inside one span -- so twelve boundaries collapsed into ONE finding. The key now
    carries the character indices.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _labels(tmp_path, fontsize, *, n=12, rotation=0, stem="f"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    labels = [f"label{i:02d}" for i in range(n)]
    ax.bar(range(n), np.random.default_rng(0).random(n))
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, fontsize=fontsize, rotation=rotation)
    pdf = tmp_path / f"{stem}.pdf"
    fig.savefig(pdf)
    plt.close(fig)
    return pdf


def _hits(tmp_path, fontsize, *, rotation=0, stem="f"):
    from figpipe import audit
    return audit.overlapping_glyphs(_labels(tmp_path, fontsize, rotation=rotation, stem=stem))


def test_the_merged_case_is_no_longer_zero(tmp_path):
    """THE FALSE NEGATIVE. Twelve labels at 4 pt merge into one span; the check used to report 0."""
    hits = _hits(tmp_path, 4, stem="m4")
    assert hits, (
        "twelve labels merged into one span at 4 pt produced no finding; the merged-label false "
        "negative is back")
    pairs = sum(h["glyph_pairs"] for h in hits)
    assert pairs > 10, f"only {pairs} glyph pairs reported for twelve overlapping labels"


def test_rotated_labels_still_produce_NO_false_positives(tmp_path):
    """THE CASE THE OLD FILTER PROTECTED. Two earlier fixes broke it; this one must not."""
    for fs in (6, 7):
        hits = _hits(tmp_path, fs, rotation=45, stem=f"r{fs}")
        assert hits == [], f"{len(hits)} false positives on rotated labels at {fs} pt"


def test_more_crowding_means_MORE_findings(tmp_path):
    """THE DIRECTION THAT MATTERS. The old check reported fewer collisions as the defect got worse,
    because worse crowding meant more merging."""
    small = sum(h["glyph_pairs"] for h in _hits(tmp_path, 4, stem="d4"))
    large = sum(h["glyph_pairs"] for h in _hits(tmp_path, 8, stem="d8"))
    assert large > small, (
        f"8 pt reported {large} pairs and 4 pt reported {small}; more crowding must not mean fewer "
        f"findings")


def test_a_merged_run_reports_more_than_one_finding(tmp_path):
    """THE AGGREGATION DEFECT. Keying on the span text collapsed twelve boundaries into one."""
    hits = [h for h in _hits(tmp_path, 4, stem="agg") if h.get("merged_run")]
    assert len(hits) > 1, (
        f"a merged run produced {len(hits)} finding(s); keying on the span text collapses them")


def test_a_clean_figure_has_no_findings(tmp_path):
    """NEGATIVE CONTROL: four well-spaced labels at 7 pt must be clean."""
    from figpipe import audit
    hits = audit.overlapping_glyphs(_labels(tmp_path, 7, n=4, stem="clean"))
    assert hits == [], f"a clean figure produced {len(hits)} findings"


def test_the_closed_limit_is_recorded_as_FIXED_not_open(tmp_path):
    """A limit that was closed must stop being listed as open, and the evidence must be kept."""
    from figpipe import audit

    open_limits = audit.overlapping_glyphs_limits()
    assert "labels merged into one span" not in open_limits, (
        "the merged-label limit is still listed as open, but it was fixed")
    fixed = audit.OVERLAPPING_GLYPHS_FIXED
    assert "labels merged into one span" in fixed
    assert "22 findings" in fixed["labels merged into one span"], (
        "the record does not carry the measurement that proves the fix")


def test_the_failed_attempt_is_still_recorded():
    """Without the negative result the next round re-tries the same narrowing."""
    from figpipe import audit

    fixed = audit.OVERLAPPING_GLYPHS_FIXED
    key = "a fix that was worse than the bug"
    assert key in fixed
    assert "12" in fixed[key]
    assert "dir=(0.707, -0.707)" in fixed[key] or "line direction" in fixed[key].lower()
