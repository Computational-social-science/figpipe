"""`not_exercised` must reach the report, and must be able to be non-zero.

WHY THIS EXISTS
    Round 87 made every check report a denominator and a three-way state. This round carries that
    into the pool report, because a mechanism that lives only in a trace nobody reads is not a
    mechanism.

THE DEFECT THIS AVOIDS
    The first version counted `not_exercised` by scanning each task's `trace` -- but the task record
    does not carry a trace, so the count would ALWAYS have been zero. A check that looks present and
    reads nothing is this project's most-recorded defect, and it was one field away from shipping.

    The count now comes from the render, where the trace exists, and is stored as
    `checks_not_exercised` on the task record.
"""
from __future__ import annotations

import inspect
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def bench():
    import bench_plottwin
    return bench_plottwin


def test_the_task_record_carries_the_count(bench):
    """THE FIELD. Without it the aggregate has nothing to sum."""
    src = inspect.getsource(bench.run_task)
    assert '"checks_not_exercised"' in src, (
        "run_task does not record how many checks had nothing to examine")


def test_the_count_comes_from_the_render_not_from_an_absent_field(bench):
    """THE DEFECT THE FIRST VERSION HAD. Counting from `t["trace"]` reads a field the record does not
    carry, so the answer is always zero -- a control that looks present and does nothing."""
    src = inspect.getsource(bench._not_exercised_count)
    assert "trace" in src
    # and the aggregate must NOT scan t["trace"]
    whole = pathlib.Path(bench.__file__).read_text(encoding="utf-8")
    assert 'for line in (t.get("trace") or [])' not in whole, (
        "the aggregate still scans a task's trace, which the record does not carry")


def test_the_helper_counts_not_exercised_lines(bench):
    """THE COUNTING RULE, on a trace built by hand."""
    trace = [
        "verify.audit.examined: font_size 0/14 text spans=pass; font_type 0/2 embedded fonts=pass",
        "verify.collisions.examined: 0 finding(s) over 0 glyphs=not_exercised",
    ]
    assert bench._not_exercised_count(trace) == 1
    assert bench._not_exercised_count([]) == 0
    assert bench._not_exercised_count(None) == 0
    assert bench._not_exercised_count(
        ["x: a 0/0 u=not_exercised; b 0/0 u=not_exercised"]) == 2


def test_the_report_carries_the_aggregate(bench):
    """THE REPORT. A count that never reaches the deliverable is not reported."""
    src = pathlib.Path(bench.__file__).read_text(encoding="utf-8")
    assert 'report["checks_examined"]' in src
    assert "not_exercised" in src


def test_a_real_figure_reports_zero_not_exercised():
    """MEANINGFUL ZERO. This project's figures carry axis labels, so no check should be idle."""
    from figpipe import skills
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": np.arange(12), "a": rng.random(12), "b": rng.random(12)})
    result = skills.run("dual_measure", df, out_stem=ROOT / "examples" / "output" / "_ne",
                        x="x", y1="a", y2="b")
    lines = [t for t in (result.get("trace") or []) if "examined:" in t]
    assert lines, "the render carries no examined lines, so the count would be vacuous"
    n = sum(str(line).count("=not_exercised") for line in lines)
    assert n == 0, f"a labelled figure reported {n} checks with nothing to examine"


def test_a_page_with_no_text_reports_nonzero():
    """THE OTHER DIRECTION. If the count can only ever be zero, it is not a measurement."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import tempfile
    from figpipe import audit

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ne-"))
    fig, ax = plt.subplots(figsize=(2.0, 2.0))
    ax.plot([0, 1], [0, 1])
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    pdf = tmp / "nt.pdf"
    fig.savefig(pdf)
    plt.close(fig)
    report = audit.audit(pdf)
    n = report["examined"]["n_not_exercised"]
    assert n > 0, "a page with no text reported zero not_exercised; the state cannot be reached"
