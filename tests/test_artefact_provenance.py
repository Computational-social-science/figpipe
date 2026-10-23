"""A finding must have an artefact behind it, and the report must say how many do.

WHY THIS EXISTS
    Wiring `legend_occlusion` into `verify.audit` and re-measuring the pool gave `hard findings: 0`.
    That looked like a clean result. It was not checkable: `run_task` recorded the COUNT of hard
    failures and DISCARDED the rendered PDF, so no finding in the report could be re-inspected by
    anyone who did not watch it happen.

    Worse, the zero could have been vacuous -- if no pool figure contains a legend, "0 findings" says
    nothing about whether the check works.

    This is the project's own recurring defect: a number nobody can re-derive. The fix is to record
    the artefact path, and to report HOW MANY rows carry one so an absent field cannot read as clean.
"""
from __future__ import annotations

import inspect
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def bench():
    import bench_plottwin
    return bench_plottwin


def test_a_task_record_carries_the_rendered_pdf(bench):
    """THE ARTEFACT: a count with no path behind it cannot be checked."""
    src = inspect.getsource(bench.run_task)
    assert '"pdf"' in src, (
        "run_task does not record where the rendered figure went, so every finding in the report is "
        "unreproducible from the report")
    assert '"png"' in src


def test_the_report_counts_rows_that_carry_an_artefact(bench):
    """THE HONEST HALF: the fingerprint is rendering-only, so old rows legitimately lack the field.
    The count is what stops an absent field from reading as a clean result."""
    src = pathlib.Path(bench.__file__).read_text(encoding="utf-8")
    assert 'report["artefact_rows"]' in src, (
        "the report does not say how many rows carry a rendered artefact, so a reader cannot tell "
        "'no findings' from 'no artefact to check'")


def test_the_fingerprint_ignores_the_report_schema(bench):
    """THE DESIGN DECISION, PINNED. Including the harness in CODE_VERSION made every edit to the
    report invalidate all rows -- 120 of 132 'stale' after a one-line change. The fingerprint is
    deliberately rendering-only, which is also why adding a report field does not invalidate rows."""
    src = inspect.getsource(bench._code_version)
    assert "figpipe/drawlib.py" in src
    assert "bench_plottwin" not in src, (
        "the fingerprint includes the harness, so every report edit marks every row stale")


def test_legend_occlusion_is_wired_into_the_run():
    """A check that exists and is never called is the defect this project records most often."""
    sys.path.insert(0, str(ROOT))
    from figpipe import skills
    src = inspect.getsource(skills.op_verify_audit)
    assert "legend_occlusion" in src, (
        "verify.audit does not run the legend occlusion check, so no figure is held to it")
