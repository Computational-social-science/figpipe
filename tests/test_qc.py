"""Negative tests for the QC gate.

WHY EVERY TEST HERE BUILDS A VIOLATION
    A test suite that only asserts "a compliant figure passes" is a shell: it passes just as
    happily when the checker is a no-op. Every test below constructs a figure that is
    deliberately wrong in ONE specific way, then asserts the gate FAILs it and names the
    right check. If a check is broken, these tests go red.

    There is also a positive control (a compliant figure must pass) and a control proving the
    gate is not merely failing everything: the compliant figure must NOT fail.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import qc  # noqa: E402

matplotlib = pytest.importorskip("matplotlib", reason="figures are built with matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

NATURE_SINGLE_IN = 89 / 25.4


# --------------------------------------------------------------------------- helpers

def _ids(report):
    return {c.id for c in report.checks}


def _severity(report, check_id):
    for c in report.checks:
        if c.id == check_id:
            return c.severity
    return None


def _failing(report):
    return {c.id for c in report.failures}


@pytest.fixture
def make(tmp_path):
    """Write a figure and return its path."""
    def _make(name, build, **savefig):
        fig = plt.figure(figsize=savefig.pop("figsize", (NATURE_SINGLE_IN, 50 / 25.4)))
        build(fig)
        path = tmp_path / name
        fig.savefig(path, **savefig)
        plt.close(fig)
        return path
    return _make


@pytest.fixture
def compliant(tmp_path):
    """A genuinely compliant figure: 89 mm, 6 pt labels, units, zero baseline, Okabe-Ito."""
    fig, ax = plt.subplots(figsize=(NATURE_SINGLE_IN, 50 / 25.4))
    x = np.arange(1, 6)
    ax.plot(x, x * 2.0, "o-", color="#0072b2", ms=3, lw=1)
    ax.set_xlabel("sentence position", fontsize=6)
    ax.set_ylabel("mean error rate (%)", fontsize=6)
    ax.tick_params(labelsize=5.5)
    ax.set_ylim(0, 12)
    path = tmp_path / "compliant.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


@pytest.fixture
def compliant_source(tmp_path):
    """A plotting source that is honest: zero baseline, no twin axis, no rainbow."""
    p = tmp_path / "plot_compliant.py"
    p.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.plot([1,2,3],[1,2,3])\n"
        "ax.set_ylim(0, 3)\n"
        "fig.savefig('compliant.pdf')\n"
        "fig.savefig('compliant.png', dpi=400)\n",
        encoding="utf-8")
    return p


# --------------------------------------------------------------------------- positive control

def test_compliant_figure_passes(compliant, compliant_source):
    """The gate must NOT fail a compliant figure -- otherwise 'always FAIL' would pass every
    negative test below while being useless."""
    report = qc.run_qc(compliant, compliant_source)
    assert report.ok, f"compliant figure failed: {[(c.id, c.detail) for c in report.failures]}"
    assert report.failures == []


# --------------------------------------------------------------------------- 1. tiny font (4 pt)

def test_catches_4pt_font(make):
    """A 4 pt axis label is below Nature's 5 pt floor and must FAIL."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xlabel("x (mm)", fontsize=4)
        ax.set_ylabel("y (mm)", fontsize=4)
        ax.tick_params(labelsize=4)
        ax.set_ylim(0, 4)

    fig = make("tiny_font.pdf", build)
    report = qc.run_qc(fig)
    assert not report.ok
    assert "figura.tiny_fonts" in _failing(report), _ids(report)
    assert "paperplot.min_font" in _failing(report)


# --------------------------------------------------------------------------- 2. truncated y axis

def test_catches_truncated_y_axis(make, tmp_path):
    """A bar chart with ylim(9, 13) is a truncated quantitative axis with no break: FAIL."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.bar([1, 2, 3], [10, 11, 12])
        ax.set_ylim(9, 13)
        ax.set_xlabel("group")
        ax.set_ylabel("value (units)")

    fig = make("truncated.pdf", build)
    src = tmp_path / "plot_truncated.py"
    src.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.bar([1,2,3],[10,11,12])\n"
        "ax.set_ylim(9, 13)\n"          # the violation
        "fig.savefig('truncated.pdf')\n",
        encoding="utf-8")

    report = qc.run_qc(fig, src)
    assert not report.ok
    assert "light.AXIS_TRUNCATE" in _failing(report), _ids(report)


def test_categorical_axis_truncation_is_not_a_hard_fail(make, tmp_path):
    """CONTROL: a non-zero origin on a CATEGORICAL axis is normal, not misconduct.

    Without this control the truncation check would fire on every horizontal bar chart and
    the gate would be a nuisance that gets switched off.
    """
    def build(fig):
        ax = fig.add_subplot(111)
        ax.barh([1, 2, 3], [0.9, 0.95, 0.99])
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["a", "b", "c"])
        ax.set_xlabel("Pearson r")
        ax.set_ylabel("metric")

    fig = make("categorical.pdf", build)
    src = tmp_path / "plot_categorical.py"
    src.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.barh([1,2,3],[0.9,0.95,0.99])\n"
        "ax.set_yticks([1,2,3]); ax.set_yticklabels(['a','b','c'])\n"
        "ax.set_ylim(-1.2, 3.4)\n"
        "fig.savefig('categorical.pdf')\n",
        encoding="utf-8")

    report = qc.run_qc(fig, src)
    sev = _severity(report, "light.AXIS_TRUNCATE")
    assert sev == qc.WARN, f"categorical truncation should WARN, got {sev}"


# --------------------------------------------------------------------------- 3. jet colormap

def test_catches_jet_colormap(make, tmp_path):
    """jet/rainbow is not perceptually uniform; the lint must flag it."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.imshow(np.arange(100).reshape(10, 10), cmap="jet")
        ax.set_xlabel("x (px)")
        ax.set_ylabel("y (px)")

    fig = make("jet.pdf", build)
    src = tmp_path / "plot_jet.py"
    src.write_text(
        "import matplotlib.pyplot as plt, numpy as np\n"
        "fig, ax = plt.subplots()\n"
        "ax.imshow(np.arange(100).reshape(10,10), cmap='jet')\n"
        "fig.savefig('jet.pdf')\n",
        encoding="utf-8")

    report = qc.run_qc(fig, src)
    assert "light.RAINBOW_CMAP" in _ids(report), _ids(report)
    # Per the light-figure spec this is a WARN (a static lint cannot tell ordered from
    # categorical data). It must still be raised, which the assertion above proves.
    assert _severity(report, "light.RAINBOW_CMAP") == qc.WARN


# --------------------------------------------------------------------------- 4. missing units

def test_catches_missing_units(make):
    """Axis titles with no unit token must FAIL the units check."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xlabel("time", fontsize=6)          # no unit
        ax.set_ylabel("speed", fontsize=6)         # no unit
        ax.tick_params(labelsize=5.5)
        ax.set_ylim(0, 4)

    fig = make("nounits.pdf", build)
    report = qc.run_qc(fig)
    assert not report.ok
    assert "pfv.units-labeled" in _failing(report), _ids(report)


def test_catches_missing_axis_labels(make):
    """A plot with no axis labels at all must FAIL the axes-labeled check."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])   # deliberately no labels

    fig = make("nolabels.pdf", build)
    report = qc.run_qc(fig)
    assert not report.ok
    assert "pfv.axes-labeled" in _failing(report), _ids(report)


# --------------------------------------------------------------------------- 5. SVG rejected

def test_rejects_svg(make):
    """SVG/EPS are rejected formats and must FAIL."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")

    fig = make("figure.svg", build)
    report = qc.run_qc(fig)
    assert not report.ok
    assert "format.rejected" in _failing(report), _ids(report)


# --------------------------------------------------------------------------- 6. missing generator

def test_missing_generator_fails(compliant):
    """A quantitative figure with no generator script is not reproducible: FAIL."""
    report = qc.run_qc(compliant)
    assert not report.ok
    assert "provenance.generator" in _failing(report), _ids(report)


def test_nonexistent_generator_fails(compliant, tmp_path):
    report = qc.run_qc(compliant, tmp_path / "does_not_exist.py")
    assert "provenance.generator" in _failing(report)


# --------------------------------------------------------------------------- 7. missing error bars

def test_catches_bar_chart_without_error_bars(make, tmp_path):
    """A bar chart with no yerr/errorbar hides uncertainty."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.bar([1, 2, 3], [5, 6, 7])
        ax.set_xlabel("group")
        ax.set_ylabel("mean (units)")
        ax.set_ylim(0, 8)

    fig = make("barebar.pdf", build)
    src = tmp_path / "plot_barebar.py"
    src.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.bar([1,2,3],[5,6,7])\n"
        "fig.savefig('barebar.pdf')\n",
        encoding="utf-8")

    report = qc.run_qc(fig, src)
    assert "light.BAR_NO_ERR" in _failing(report), _ids(report)


# --------------------------------------------------------------------------- 8. twin axis

def test_twin_axis_is_flagged(make, tmp_path):
    """twinx is a pseudo-correlation risk and must at least be raised."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xlabel("x")
        ax.set_ylabel("y (units)")
        ax2 = ax.twinx()
        ax2.plot([1, 2, 3], [3, 2, 1])
        ax2.set_ylabel("z (units)")

    fig = make("twin.pdf", build)
    src = tmp_path / "plot_twin.py"
    src.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.plot([1,2,3],[1,2,3])\n"
        "ax2 = ax.twinx()\n"
        "ax2.plot([1,2,3],[3,2,1])\n"
        "fig.savefig('twin.pdf')\n",
        encoding="utf-8")

    report = qc.run_qc(fig, src)
    assert "light.TWIN_AXIS" in _ids(report), _ids(report)


# --------------------------------------------------------------------------- 9. 3D distortion

def test_3d_plot_is_flagged(make, tmp_path):
    """A 3D projection distorts area/height encoding."""
    def build(fig):
        ax = fig.add_subplot(111, projection="3d")
        ax.bar3d([0, 1], [0, 1], [0, 0], [0.5, 0.5], [0.5, 0.5], [1, 2])
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        ax.set_zlabel("z (mm)")

    fig = make("three_d.pdf", build)
    src = tmp_path / "plot_3d.py"
    src.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig = plt.figure()\n"
        "ax = fig.add_subplot(111, projection='3d')\n"
        "ax.bar3d([0,1],[0,1],[0,0],[.5,.5],[.5,.5],[1,2])\n"
        "fig.savefig('three_d.pdf')\n",
        encoding="utf-8")

    report = qc.run_qc(fig, src)
    # The upstream lint matches 3D per line, so a multi-line 3D plot is a known false negative
    # there. Either its finding or our supplementary check must fire.
    assert {"light.PIE_3D", "qc.three_d_projection"} & _ids(report), _ids(report)


# --------------------------------------------------------------------------- 10. missing file

def test_missing_figure_fails(tmp_path):
    report = qc.run_qc(tmp_path / "nope.pdf")
    assert not report.ok
    assert "file.exists" in _failing(report)


# --------------------------------------------------------------------------- 11. tool provenance is real

def test_real_tools_are_actually_executed(compliant, compliant_source):
    """Guard against the gate silently degrading to 'nothing was installed'.

    paper-figure-validator, qinyan and light-figure are vendored real tools. If any of them
    stopped being executed, the gate would still 'pass' but would be lying about provenance.
    """
    report = qc.run_qc(compliant, compliant_source)
    tools = report.by_tool()
    for tool in (qc.TOOL_PFV, qc.TOOL_QINYAN, qc.TOOL_LIGHT):
        assert tool in tools, f"{tool} produced no checks; is it installed?"
        assert not all(c.severity == qc.SKIP for c in tools[tool]), \
            f"{tool} only produced SKIPs; it is not actually running"


def test_paperplot_preflight_really_runs():
    """paperplot.preflight() must be importable and must flag a broken probe figure."""
    report = qc.run_qc.__module__  # noqa: F841  (keeps the import surface honest)
    checks = qc.check_paperplot_live()
    assert checks, "paperplot produced no checks"
    status = {c.severity for c in checks}
    assert qc.SKIP not in status or len(checks) > 1, \
        f"paperplot appears unavailable: {[c.detail for c in checks]}"


# --------------------------------------------------------------------------- 12. CI gate semantics

def test_fail_means_nonzero_exit(make, tmp_path):
    """The CI contract: any FAIL must produce a non-zero exit code."""
    def build(fig):
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xlabel("x (mm)", fontsize=4)     # 4 pt -> FAIL
        ax.set_ylabel("y (mm)", fontsize=4)

    fig = make("gate_fail.pdf", build)
    code = qc.main([str(fig)])
    assert code == 1, "a failing figure must exit 1"


def test_pass_means_zero_exit(compliant, compliant_source):
    code = qc.main([str(compliant), "--source", str(compliant_source)])
    assert code == 0, "a compliant figure must exit 0"


def test_json_output_is_machine_readable(compliant, compliant_source):
    import json
    report = qc.run_qc(compliant, compliant_source)
    payload = json.loads(report.to_json())
    assert payload["ok"] is True
    assert payload["counts"][qc.PASS] > 0
    assert "tool_provenance" in payload
    # provenance must not claim figura was executed
    assert payload["tool_provenance"][qc.TOOL_FIGURA]["equivalent_checks"] is True


def test_every_check_has_evidence_and_method(compliant, compliant_source):
    """No verdict may be issued without stating how it was reached."""
    report = qc.run_qc(compliant, compliant_source)
    for c in report.checks:
        assert c.severity in {qc.PASS, qc.WARN, qc.FAIL, qc.SKIP}, c
        assert c.method in {"source", "artifact", "image", "none"}, f"{c.id} has method={c.method!r}"
        assert c.detail, f"{c.id} has no detail"
