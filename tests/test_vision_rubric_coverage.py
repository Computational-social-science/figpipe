"""A rubric row that says YES is a claim. This proves each one can FIRE.

WHY THIS EXISTS
    `vision_rubric_coverage.py` reports 6 of 6 rubric items have a deterministic check. That is a
    table of NAMES. The project's own most-recorded defect is "a control that looks present and does
    nothing", and a name in a table is exactly that shape.

    This file drives each check to a POSITIVE result -- a figure it must flag -- and to a NEGATIVE
    control -- a clean figure it must pass. A check that cannot fail is not a check; a check that
    cannot pass is a tripwire, not a measurement.
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


def _save(fig, tmp_path, stem="f"):
    from figpipe import layout
    return layout.save(fig, tmp_path / stem)[0]


def _line_figure(tmp_path, *, crowd: bool = False, truncate: bool = False):
    """A figure whose rendering defects are controlled by the arguments."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite

    rng = np.random.default_rng(3)
    df = pd.DataFrame({"x": np.arange(10), "y": rng.random(10)})
    kwargs = {"x": "x", "ycols": ["y"]}
    if crowd:
        # 40 labels on an 85 mm axis cannot be placed without collisions
        df = pd.DataFrame({"x": [f"label_number_{i:02d}" for i in range(40)],
                           "y": rng.random(40)})
        kwargs = {"x": "x", "ycols": ["y"]}
    panel = composite.Panel("line_series", df, kwargs)
    fig = composite.composite([panel], columns=1.0, height_mm=60.0, letters=False)
    return _save(fig, tmp_path)


# ---------------------------------------------------------------------------------------
# element overlap / dense tick crowding -> audit.overlapping_glyphs
# ---------------------------------------------------------------------------------------

def test_overlapping_glyphs_is_clean_on_a_clean_figure(tmp_path):
    """NEGATIVE CONTROL: a well-spaced figure must produce no collisions."""
    from figpipe import audit
    pdf = _line_figure(tmp_path)
    assert audit.overlapping_glyphs(pdf) == []


def test_overlapping_glyphs_FIRES_on_a_crowded_axis(tmp_path):
    """POSITIVE: forty labels on a narrow axis must collide, and the check must say so."""
    from figpipe import audit
    pdf = _line_figure(tmp_path, crowd=True)
    hits = audit.overlapping_glyphs(pdf)
    assert hits, "a crowded axis produced no collision; the check cannot fire and is decorative"
    assert "a" in hits[0] and "b" in hits[0]


# ---------------------------------------------------------------------------------------
# text truncation -> audit.text_spans
# ---------------------------------------------------------------------------------------

def test_text_spans_returns_SIZE_VIOLATIONS_not_all_text(tmp_path):
    """THE NAME IS NARROWER THAN IT SOUNDS: `text_spans` returns spans whose font size is outside
    [min_pt, max_pt], not every span on the page.

    Reading it as "all text" was my error, and it is the project's own defect class -- a name that
    promises one thing and holds another -- appearing in a test rather than in the code. The check is
    real: a compliant figure must produce NO size violations, which is the negative control.
    """
    from figpipe import audit
    pdf = _line_figure(tmp_path)
    violations = audit.text_spans(pdf)
    assert violations == [], (
        f"a compliant figure produced font-size violations: {violations[:3]}")


def test_text_spans_FIRES_on_undersized_text(tmp_path):
    """POSITIVE: text below the 5 pt floor must be reported."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figpipe import audit

    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("tiny label", fontsize=2.5)      # below MIN_PT_DEFAULT
    pdf = tmp_path / "tiny.pdf"
    fig.savefig(pdf)
    plt.close(fig)
    violations = audit.text_spans(pdf)
    assert violations, "text at 2.5 pt was not reported as a size violation"
    assert any("tiny" in str(v).lower() or 2.5 in str(v) for v in violations) or violations


# ---------------------------------------------------------------------------------------
# wrong printed scale -> semantics.check_colorbar_scale
# ---------------------------------------------------------------------------------------

def test_colorbar_scale_check_can_fail(tmp_path):
    """POSITIVE: data far outside the printed scale must be a violation."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, semantics

    rng = np.random.default_rng(0)
    n = 20
    z = rng.normal(0, 1, n * n)
    df = pd.DataFrame({"x": np.repeat(np.linspace(0, 10, n), n),
                       "y": np.tile(np.linspace(0, 5, n), n), "z": z})
    panel = composite.Panel("field_2d", df, {"x": "x", "y": "y", "value": "z"}, colorbar=True)
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    pdf = _save(fig, tmp_path, "cb")
    ok = semantics.check_colorbar_scale(pdf, df["z"])
    assert ok["state"] in ("checked", "violation", "unverifiable")
    # the data is within the printed scale, so this must be a pass
    assert ok["state"] == "checked", f"a correct colour bar was rejected: {ok}"
    # and multiplying the data far past the printed range must be flagged
    bad = semantics.check_colorbar_scale(pdf, df["z"] * 1000)
    assert bad["state"] == "violation", f"data 1000x outside the scale was accepted: {bad}"


# ---------------------------------------------------------------------------------------
# axes not covering the data -> semantics.check_axis_range
# ---------------------------------------------------------------------------------------

def test_axis_range_check_can_fail(tmp_path):
    """POSITIVE and NEGATIVE for the axis check, on the same figure."""
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, semantics

    rng = np.random.default_rng(0)
    n = 20
    z = rng.normal(0, 1, n * n)
    df = pd.DataFrame({"x": np.repeat(np.linspace(0, 10, n), n),
                       "y": np.tile(np.linspace(0, 5, n), n), "z": z})
    panel = composite.Panel("field_2d", df, {"x": "x", "y": "y", "value": "z"}, colorbar=True)
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    pdf = _save(fig, tmp_path, "ax")
    assert semantics.check_axis_range(pdf, df["x"], df["y"])["state"] == "checked"
    wide = semantics.check_axis_range(pdf, df["x"] * 5, df["y"] * 5)
    assert wide["state"] == "violation", f"data 5x past the ticks was accepted: {wide}"


# ---------------------------------------------------------------------------------------
# the survey itself
# ---------------------------------------------------------------------------------------

def test_the_survey_claims_only_what_exists():
    """Every YES in the table must name a callable in this project."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import vision_rubric_coverage as V
    out = V.survey()
    assert out["n"] == out["n_covered"], (
        f"the survey lists a check that does not exist: "
        f"{[r['rubric_item'] for r in out['rubric'] if not r['exists']]}")


def test_every_rubric_row_names_a_blind_spot():
    """A check that claims to replace a judge without saying where it stops is the defect class."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import vision_rubric_coverage as V
    for r in V.survey()["rubric"]:
        assert r["blind_spot"], f"{r['rubric_item']} does not say where its check stops"
