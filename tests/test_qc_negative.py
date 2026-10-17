"""Negative controls: a gate that passes everything is indistinguishable from no gate.

WHY THIS FILE EXISTS, AND WHY IT WAS REWRITTEN
    The adversarial audit constructed figures that each broke exactly ONE rule and found the
    gate passed jet colour maps and truncated axes. Worse, it proved my FIRST version of this
    test was vacuous: it called `run_qc(p)` without a generator, which unavoidably produces
    three unrelated FAILs (missing provenance, missing script, wrong width) -- so
    `assert "FAIL" in severities` passed even if the truncation and colour checks did not
    exist at all. The audit demonstrated this by deleting them.

    This version asserts the FAIL comes from the SPECIFIC check family, and every fixture ships
    a generator that actually describes the figure, so the unrelated FAILs are absent.

EACH FIXTURE BREAKS EXACTLY ONE RULE
    clean       compliant: no violation, must PASS
    jet         a jet colour map, must FAIL from the colour family
    truncated   a quantitative y-axis starting at 99, must FAIL from the honesty family
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

qc = pytest.importorskip("figpipe.qc", reason="qc module absent")

MM = 1 / 25.4
TMP = ROOT / "_qc_negative"

#: Each fixture: how to draw it, and the generator source that describes the same drawing.
FIXTURES = {
    "clean": {
        "draw": lambda ax, x: ax.plot(x, np.sin(x / 4) + 2, color="#0072B2", lw=1.0),
        "labels": ("sentence position (n)", "error rate (%)"),
        "gen": ("import matplotlib.pyplot as plt, numpy as np\n"
                "x = np.arange(1, 21)\n"
                "plt.plot(x, np.sin(x / 4) + 2)\n"),
    },
    "jet": {
        "draw": None,       # handled specially: needs imshow + colorbar
        "gen": ("import matplotlib.pyplot as plt, numpy as np\n"
                "im = plt.imshow(np.random.default_rng(0).random((12, 12)), cmap='jet')\n"
                "plt.colorbar(im)\n"),
    },
    "truncated": {
        "draw": lambda ax, x: ax.plot(x, 100 + x, color="#D55E00", lw=1.0),
        "labels": ("position (n)", "count (unitless)"),
        "ylim": (99.0, 120.0),
        "gen": ("import matplotlib.pyplot as plt, numpy as np\n"
                "x = np.arange(1, 21)\n"
                "y = 100 + np.arange(20)\n"
                "fig, ax = plt.subplots()\n"
                "ax.plot(x, y)\n"
                "ax.set_ylim(99.0, 120.0)\n"
                "ax.set_xlabel('position (n)')\n"
                "ax.set_ylabel('count (unitless)')\n"),
    },
}


def build(kind: str) -> tuple[pathlib.Path, pathlib.Path]:
    """Write the PDF and its matching generator, returning both paths."""
    spec = FIXTURES[kind]
    TMP.mkdir(parents=True, exist_ok=True)
    stem = TMP / kind
    pdf, gen = stem.with_suffix(".pdf"), stem.with_suffix(".py")

    # savefig must not pad: a padded page changes the width and the width gate then fails for
    # a reason unrelated to the rule under test (knowledge-base rule L05).
    plt.rcParams["savefig.bbox"] = None
    plt.rcParams["savefig.pad_inches"] = 0.0

    fig = plt.figure(figsize=(89 * MM, 60 * MM))
    ax = fig.add_subplot(111)
    x = np.arange(1, 21)
    if kind == "jet":
        im = ax.imshow(np.random.default_rng(0).random((12, 12)), cmap="jet")
        fig.colorbar(im, ax=ax)
        ax.set_xlabel("column (unitless)")
        ax.set_ylabel("row (unitless)")
    else:
        spec["draw"](ax, x)
        lo, hi = spec["labels"]
        ax.set_xlabel(lo)
        ax.set_ylabel(hi)
        if "ylim" in spec:
            ax.set_ylim(*spec["ylim"])
    fig.savefig(pdf)
    plt.close(fig)

    gen.write_text(spec["gen"], encoding="utf-8")
    return pdf, gen


def fails_of(report) -> list[str]:
    return [getattr(c, "id", "") for c in getattr(report, "checks", [])
            if getattr(c, "severity", "") == "FAIL"]


def test_clean_figure_passes():
    """Positive control: without it, a gate that fails everything would pass every test."""
    pdf, gen = build("clean")
    rep = qc.run_qc(pdf, source_script=gen)
    fails = fails_of(rep)
    assert not fails, f"a compliant figure was failed by: {fails}"


def test_jet_is_caught():
    """THE AUDIT'S FINDING. The old gate reported PASS with findings=none on exactly this.

    The check is deliberately WARN, not FAIL: a static analysis cannot distinguish ordered data
    (where a rainbow misleads) from categorical data (where it can be defended in the caption).
    Escalating to FAIL would fail legitimate figures. So the assertion is that the COLOUR CHECK
    SPEAKS -- it must produce a non-PASS finding naming the family -- rather than that the gate
    blocks. The audit's complaint was indings=none, and that is what this pins.
    """
    pdf, gen = build("jet")
    rep = qc.run_qc(pdf, source_script=gen)
    findings = [(getattr(c, "id", ""), getattr(c, "severity", ""))
                for c in getattr(rep, "checks", [])
                if getattr(c, "severity", "") in ("WARN", "FAIL")]
    colour = [f for f in findings if "colour" in f[0]]
    assert colour, (
        f"the colour check produced no WARN or FAIL for a jet colour map. "
        f"All findings: {findings}. The audit's complaint was 'findings=none' -- a gate that "
        f"says nothing about a rainbow is the defect.")
    assert any(sev == "WARN" for _, sev in colour), (
        f"jet should be WARN (a static check cannot rule out categorical use), got {colour}")


def test_truncated_axis_is_caught():
    """THE AUDIT'S SECOND FINDING: a truncated quantitative axis passed as WARN."""
    pdf, gen = build("truncated")
    rep = qc.run_qc(pdf, source_script=gen)
    fails = fails_of(rep)
    assert any("honesty" in f for f in fails), (
        f"no FAIL from the honesty family for a truncated quantitative axis. FAIL ids: {fails}")


def test_categorical_axis_truncation_is_only_warned():
    """A barh chart with explicit y ticks legitimately starts above zero.

    Failing it would be a false positive, so this positive control keeps the check honest in
    the other direction.
    """
    TMP.mkdir(parents=True, exist_ok=True)
    stem = TMP / "categorical"
    pdf, gen = stem.with_suffix(".pdf"), stem.with_suffix(".py")
    plt.rcParams["savefig.bbox"] = None
    plt.rcParams["savefig.pad_inches"] = 0.0
    fig = plt.figure(figsize=(89 * MM, 60 * MM))
    ax = fig.add_subplot(111)
    ax.barh([0, 1, 2], [5, 6, 7], color="#0072B2")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["a", "b", "c"])
    ax.set_xlabel("count (unitless)")
    ax.set_ylabel("category (unitless)")
    fig.savefig(pdf)
    plt.close(fig)
    gen.write_text("import matplotlib.pyplot as plt\n"
                   "ax = plt.gca()\n"
                   "ax.barh([0, 1, 2], [5, 6, 7])\n"
                   "ax.set_yticks([0, 1, 2])\n"
                   "ax.set_yticklabels(['a', 'b', 'c'])\n", encoding="utf-8")
    rep = qc.run_qc(pdf, source_script=gen)
    fails = fails_of(rep)
    assert not any("truncation" in f for f in fails), (
        f"a categorical barh axis was failed as truncated: {fails}. That is a false positive.")
