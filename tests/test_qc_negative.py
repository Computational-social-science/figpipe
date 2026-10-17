"""Negative control: does the QC gate actually FAIL on violations?

WHY THIS TEST IS THE ONLY ONE THAT MATTERS
    The adversarial audit constructed figures that each broke exactly one rule and found the
    gate passed jet colour maps and truncated axes. A gate that passes everything is
    indistinguishable from no gate at all -- and its PASS output is worse than silence,
    because it implies a check happened.

    So: build figures that are compliant except for ONE violation, and require the gate to
    fail each one. A test that only checks "compliant figures pass" cannot distinguish a real
    gate from a stub.
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


def _base(ax, values):
    ax.plot(values, color="#0072B2", lw=1.0)
    ax.set_xlabel("sentence position (n)")
    ax.set_ylabel("error rate (%)")


def make(kind: str, path: pathlib.Path) -> pathlib.Path:
    fig = plt.figure(figsize=(89 * MM, 60 * MM))
    ax = fig.add_subplot(111)
    x = np.arange(1, 21)
    if kind == "clean":
        _base(ax, np.sin(x / 4) + 2)
    elif kind == "jet":
        # a jet/rainbow colour map -- explicitly rejected by the paper workflow
        im = ax.imshow(np.random.default_rng(0).random((12, 12)), cmap="jet")
        fig.colorbar(im, ax=ax)
        ax.set_xlabel("column (unitless)")
        ax.set_ylabel("row (unitless)")
    elif kind == "truncated":
        y = 100 + np.arange(20)
        ax.plot(x, y, color="#D55E00", lw=1.0)
        ax.set_ylim(y.min() - 1, y.max() + 1)      # non-zero baseline, unmarked
        ax.set_xlabel("position (n)")
        ax.set_ylabel("count (unitless)")
    elif kind == "no_unit":
        ax.plot(x, x, color="#009E73", lw=1.0)
        ax.set_xlabel("position")                  # no unit in parentheses
        ax.set_ylabel("count")
    else:
        raise ValueError(kind)
    path.parent.mkdir(parents=True, exist_ok=True)
    # NOT bbox_inches='tight': that shrinks the page and the width gate correctly rejects the
    # result (this is knowledge-base rule L05, found the same way). Pin the rcParam too.
    plt.rcParams["savefig.bbox"] = None
    plt.rcParams["savefig.pad_inches"] = 0.0
    fig.savefig(path)
    plt.close(fig)
    return path


def _severities(report) -> list[str]:
    return [getattr(c, "severity", "") for c in getattr(report, "checks", [])]


def test_clean_figure_passes():
    """A genuinely compliant figure must pass.

    The first version of this test failed, and the gate was RIGHT: the figure had no
    generating script, which the workflow requires. So the fixture now writes one -- a
    "compliant" figure without a generator is not compliant.
    """
    stem = TMP / "clean"
    p = make("clean", stem.with_suffix(".pdf"))
    gen = stem.with_suffix(".py")
    gen.write_text(
        "import matplotlib.pyplot as plt, numpy as np\n"
        "x = np.arange(1, 21)\n"
        "fig, ax = plt.subplots(figsize=(89/25.4, 60/25.4))\n"
        "ax.plot(x, np.sin(x/4) + 2, color='#0072B2')\n"
        "ax.set_xlabel('sentence position (n)')\n"
        "ax.set_ylabel('error rate (%)')\n"
        "fig.savefig('clean.pdf')\n",
        encoding="utf-8")
    rep = qc.run_qc(p, source_script=gen)
    sev = _severities(rep)
    fails = [(getattr(c,'id',''), getattr(c,'detail','')[:60])
             for c in getattr(rep,'checks',[]) if getattr(c,'severity','')=='FAIL']
    assert "FAIL" not in sev, f"a compliant figure was failed: {fails}"


@pytest.mark.parametrize("kind,why", [
    ("jet", "jet/rainbow colour map"),
    ("truncated", "truncated y-axis"),
])
def test_violation_is_caught(kind, why):
    """THE AUDIT'S FINDING, AS A TEST.

    The audit constructed exactly these and the old gate passed them with findings=none.
    """
    p = make(kind, TMP / f"{kind}.pdf")
    rep = qc.run_qc(p)
    sev = _severities(rep)
    assert "FAIL" in sev, (
        f"the gate did not fail a figure with a {why}. Severities: {sev}. "
        f"Checks: {[(getattr(c,'id',''), getattr(c,'severity','')) for c in getattr(rep,'checks',[])]}")
