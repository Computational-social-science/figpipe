"""Every defect this pipeline exists to prevent, pinned as a test.

WHY THESE TESTS LOOK LIKE THIS
    Each test corresponds to a real failure that shipped in a figure before this pipeline
    existed. They are written from the failure, not from the implementation, so a future
    refactor cannot quietly reintroduce one.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, layout, style  # noqa: E402


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    """One compliant two-panel figure, reused by the audit tests."""
    tmp = tmp_path_factory.mktemp("figs")
    style.apply()
    fig, w, h = layout.figure(columns=2, height_mm=55)
    gs = layout.gridspec(fig, 1, 2)
    x = np.arange(1, 16)
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(x, 4.1 * np.exp(-x / 4) + 1.6, "o-", color=style.OKABE_ITO["blue"],
            ms=2.5, lw=1)
    ax.set_xlabel("sentence position")
    ax.set_ylabel("mean error rate (%)")
    style.panel_letter(ax, "a")
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(x, np.exp(-x / 5), "o-", color=style.OKABE_ITO["vermillion"], ms=2.5, lw=1)
    ax2.set_yscale("log")
    ax2.set_xlabel("position")
    ax2.set_ylabel("ratio (unitless)")
    style.panel_letter(ax2, "b")
    paths = layout.save(fig, tmp / "demo")
    return pathlib.Path(paths[0]), tmp


# ---------------------------------------------------------------- style

def test_fonttype_is_42_not_3():
    """THE DEFECT THAT LOOKS FINE AND IS REJECTED.

    SciencePlots' `nature` style sets pdf.fonttype=3, which converts text to Type-3 outlines.
    Nature explicitly rejects outlined text. Nothing about the rendered figure looks wrong,
    which is why the defect survives unnoticed.
    """
    style.apply()
    import matplotlib.pyplot as plt
    assert plt.rcParams["pdf.fonttype"] == 42
    assert plt.rcParams["ps.fonttype"] == 42


def test_spines_and_grid_are_off():
    style.apply()
    import matplotlib.pyplot as plt
    assert plt.rcParams["axes.spines.top"] is False
    assert plt.rcParams["axes.spines.right"] is False
    assert plt.rcParams["axes.grid"] is False


def test_font_size_within_band():
    style.apply()
    import matplotlib.pyplot as plt
    assert style.MIN_PT <= plt.rcParams["font.size"] <= style.MAX_PT


def test_preferred_font_is_arial_or_helvetica():
    style.apply()
    import matplotlib.pyplot as plt
    assert plt.rcParams["font.sans-serif"][0] in ("Arial", "Helvetica")


def test_savefig_bbox_is_not_tight():
    """THE THIRD MECHANISM BY WHICH THE WIDTH SILENTLY CHANGED.

    Passing no bbox_inches to savefig is not enough: the style sets savefig.bbox='tight', so
    matplotlib pads the output anyway. A figure created at exactly 183.00 mm was written to a
    185.54 mm page. Pinning the rcParam is what actually holds the size.
    """
    style.apply()
    import matplotlib.pyplot as plt
    assert plt.rcParams["savefig.bbox"] is None


def test_no_latex_required():
    """The plain `science` style sets text.usetex=True; without a TeX install EVERY text call
    fails, so the figure cannot be produced at all."""
    style.apply()
    import matplotlib.pyplot as plt
    assert plt.rcParams["text.usetex"] is False


def test_violations_reports_a_deliberately_broken_style():
    """The checker must actually detect violations, not always return clean."""
    style.apply()
    import matplotlib.pyplot as plt
    plt.rcParams["pdf.fonttype"] = 3
    try:
        problems = style.violations()
        assert any("fonttype" in p for p in problems), (
            "violations() did not notice pdf.fonttype=3")
    finally:
        plt.rcParams["pdf.fonttype"] = 42


# ---------------------------------------------------------------- layout

def test_width_is_exactly_183():
    style.apply()
    fig, w, h = layout.figure(columns=2, height_mm=50)
    assert w == 183.0
    assert abs(fig.get_size_inches()[0] * 25.4 - 183.0) < 1e-6


def test_width_is_exactly_89_for_single_column():
    style.apply()
    fig, w, h = layout.figure(columns=1, height_mm=50)
    assert w == 89.0


def test_invalid_column_count_raises():
    """Size is not a free parameter; a third width must not be expressible."""
    style.apply()
    with pytest.raises(ValueError, match="columns must be 1 or 2"):
        layout.figure(columns=1.5, height_mm=50)


def test_height_over_170_raises():
    """The 170 mm limit leaves room for the legend beneath the figure."""
    style.apply()
    with pytest.raises(ValueError, match="exceeds Nature"):
        layout.figure(columns=2, height_mm=200)


# ---------------------------------------------------------------- audit

def test_audit_passes_a_compliant_figure(demo):
    pdf, _ = demo
    rep = audit.audit(pdf, expect_width_mm=183)
    assert rep["ok"], rep["findings"]
    assert abs(rep["width_mm"] - 183.0) < 0.6


def test_audit_catches_sub_5pt_text(tmp_path):
    """THE DEFECT THAT WAS IN FOUR OF SIX FIGURES AND INVISIBLE BY EYE."""
    style.apply()
    import matplotlib.pyplot as plt
    fig, _, _ = layout.figure(columns=2, height_mm=40)
    ax = fig.add_subplot(111)
    ax.plot([0, 1], [0, 1])
    ax.text(0.5, 0.5, "tiny label", fontsize=4.0)   # below the 5 pt floor
    p = tmp_path / "bad.pdf"
    fig.savefig(p)
    rep = audit.audit(p)
    assert not rep["ok"], "audit passed a figure containing 4 pt text"
    assert any(f["check"] == "font_size" for f in rep["findings"])


def test_audit_catches_log_exponents(tmp_path):
    """10^n EXPONENTS CANNOT MEET THE BAND, and only the rendered file shows it.

    matplotlib draws the exponent at ~0.7x the base size, so even a 7 pt base yields a 4.9 pt
    exponent. Reading the rcParams shows nothing wrong; measuring the PDF does.
    """
    style.apply()
    import matplotlib.pyplot as plt
    fig, _, _ = layout.figure(columns=1, height_mm=40)
    ax = fig.add_subplot(111)
    ax.plot([1, 10, 100, 1000], [1, 10, 100, 1000])
    ax.set_yscale("log")
    # deliberately do NOT call suppress_log_exponents
    p = tmp_path / "logbad.pdf"
    fig.savefig(p)
    rep = audit.audit(p)
    assert not rep["ok"], (
        "audit passed a figure whose log-axis exponents render below 5 pt")
    assert any(f["check"] == "font_size" for f in rep["findings"])


def test_audit_catches_wrong_width(tmp_path):
    style.apply()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(5, 2))     # not a column width
    ax = fig.add_subplot(111)
    ax.plot([0, 1], [0, 1])
    p = tmp_path / "wrong.pdf"
    fig.savefig(p)
    rep = audit.audit(p, expect_width_mm=183)
    assert not rep["ok"]
    assert any(f["check"] == "width" for f in rep["findings"])


def test_suppress_log_exponents_makes_the_log_figure_compliant(tmp_path):
    """The fix must actually work, not merely be available."""
    style.apply()
    import matplotlib.pyplot as plt
    fig, _, _ = layout.figure(columns=1, height_mm=40)
    ax = fig.add_subplot(111)
    ax.plot([1, 10, 100, 1000], [1, 10, 100, 1000])
    ax.set_yscale("log")
    style.suppress_log_exponents(fig)
    p = tmp_path / "logok.pdf"
    fig.savefig(p)
    rep = audit.audit(p)
    assert rep["ok"], rep["findings"]


def test_audit_reports_embedded_font_types(demo):
    pdf, _ = demo
    rep = audit.audit(pdf)
    assert rep.get("fonts"), "no embedded font information reported"
    assert not any("type3" in (f["type"] or "").lower() for f in rep["fonts"]), (
        "Type-3 fonts are present; Nature rejects outlined text")


def test_audit_on_missing_file_is_a_failure_not_a_crash():
    rep = audit.audit(pathlib.Path("does-not-exist.pdf"))
    assert rep["ok"] is False
    assert rep["findings"][0]["check"] == "exists"
