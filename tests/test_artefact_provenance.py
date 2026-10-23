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


def test_the_report_counts_rows_that_carry_the_FACT(bench):
    """THE HONEST HALF, REVISED.

    This test first pinned `artefact_rows`, which counted rows carrying a `pdf` PATH. That field was
    removed because every path pointed at a temp file deleted at the end of the run: 139 rows
    "carried an artefact" and 0 resolved. The replacement counts rows carrying the FACT the artefact
    established, which is what actually makes a zero checkable.
    """
    src = pathlib.Path(bench.__file__).read_text(encoding="utf-8")
    assert "legend_coverage" in src, (
        "the report does not say how many rows carry the legend measurement, so a reader cannot "
        "tell 'no findings' from 'no artefact to check'")
    assert 'report["artefact_rows"]' not in src, (
        "the report still records artefact_rows, a count of paths that resolve to deleted temp files")


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
