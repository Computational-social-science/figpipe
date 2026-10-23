"""The collision check has a known blind spot, and it is documented rather than hidden.

WHY THIS EXISTS
    Chasing the "labels close but not overlapping" rubric item found something better: a REAL false
    negative in `overlapping_glyphs`, and a fix for it that was worse than the bug.

THE MEASUREMENT
    Twelve labels on one axis, upright, at five font sizes:

        fontsize=4    0 collisions      <- the labels ARE merged into one span
        fontsize=5   11 collisions
        fontsize=6   11 collisions
        fontsize=7   11 collisions
        fontsize=8   21 collisions

    At 4 pt PyMuPDF emits ONE span for all twelve labels -- `label00label01label02...` -- and the
    check skips pairs inside one span (which is what removes the rotated-label false positives). So
    the WORST crowding is the case it cannot see.

THE FIX THAT FAILED
    Narrowing the filter to "skip only adjacent characters" gave 1 collision at 4 pt -- and 12 FALSE
    POSITIVES on rotated labels, which went from 0 to 12. A rotated label's characters are also
    non-adjacent in the string while legitimately stacked along the diagonal.

    Separating the two cases needs the LINE DIRECTION, and a rule that trades one false negative for
    twelve false positives is worse than the false negative. Reverted.

WHAT IS PINNED HERE
    Both directions, so the next attempt knows what it must not break, and the limit itself so the
    check is not read as complete.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _collisions(tmp_path, fontsize, *, n=12, rotation=0, stem="f"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figpipe import audit

    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    labels = [f"label{i:02d}" for i in range(n)]
    ax.bar(range(n), np.random.default_rng(0).random(n))
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, fontsize=fontsize, rotation=rotation)
    pdf = tmp_path / f"{stem}.pdf"
    fig.savefig(pdf)
    plt.close(fig)
    return len(audit.overlapping_glyphs(pdf))


def test_rotated_labels_produce_NO_false_positives(tmp_path):
    """THE CASE THE SPAN FILTER EXISTS FOR. A rotated label's boxes overlap while its glyphs are
    cleanly separated along the diagonal."""
    for fs in (6, 7):
        n = _collisions(tmp_path, fs, rotation=45, stem=f"r{fs}")
        assert n == 0, f"{n} false positives on rotated labels at {fs} pt"


def test_crowded_upright_labels_ARE_reported(tmp_path):
    """POSITIVE: real crowding at 6 pt and above must be caught."""
    for fs in (6, 7):
        n = _collisions(tmp_path, fs, stem=f"u{fs}")
        assert n > 0, f"crowded labels at {fs} pt produced no collision"


def test_the_merge_limitation_is_DOCUMENTED(tmp_path):
    """THE BLIND SPOT, NAMED. At 4 pt the labels merge into one span and the check reports zero.
    That is a limitation, not a bug, and it must be discoverable from the code."""
    from figpipe import audit

    limits = audit.overlapping_glyphs_limits()
    assert "labels merged into one span" in limits
    assert "4 pt" in limits["labels merged into one span"]
    # and the behaviour the limit describes
    n = _collisions(tmp_path, 4, stem="m4")
    assert n == 0, (
        f"the 4 pt merge now reports {n} collisions; if the check was improved, update the "
        f"documented limit rather than leaving a stale claim")


def test_the_failed_fix_is_recorded(tmp_path):
    """THE NEGATIVE RESULT. Without it the next round re-tries the same narrowing."""
    from figpipe import audit

    limits = audit.overlapping_glyphs_limits()
    key = "separating merge from rotation"
    assert key in limits
    assert "12" in limits[key], (
        "the record does not say how many false positives the failed fix produced")
    assert "LINE DIRECTION" in limits[key].upper()


def test_a_clean_figure_has_no_collisions(tmp_path):
    """NEGATIVE CONTROL: well-spaced labels must not be flagged."""
    n = _collisions(tmp_path, 7, n=4, stem="clean")
    assert n == 0, f"a clean figure produced {n} collisions"
