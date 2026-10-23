"""A total must say what set it is over -- and a path to a deleted file is not provenance.

WHY THIS EXISTS
    Round 82 recorded the rendered PDF path so a finding could be re-inspected. That made things
    worse, and the re-measurement showed it: `artefact_rows: 139` and 139 rows carrying a `pdf`
    path, of which **0 resolved to a file**. The rendered candidates go to a temp directory that is
    deliberately removed (600 files / 60 MB would blow the worktree budget), so the recorded path
    pointed at nothing -- provenance that looks real and is not.

    The fix is not to keep the artefact (it cannot be kept) but to keep the FACT it established:
    whether the figure contained a legend, and whether that legend covered a mark.

THE SECOND DEFECT, FOUND BY THE FIX
    `legend_frames` existed on 6 rows and was absent on 144, while every row claimed the same
    code_version -- because the fingerprint is rendering-only and cannot see a report-schema change.
    Summing absent as 0 produced `legend_frames: 0`, a number about 6 rows sitting beside a report
    about 139.

    That is the "aggregate describes a different set than the one beside it" defect, which this
    project has recorded more times than any other. The total now carries its own membership.
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


def test_a_task_record_does_not_point_at_a_deleted_file(bench):
    """A PATH TO A TEMP FILE IS NOT PROVENANCE. The candidates are removed by design."""
    src = inspect.getsource(bench.run_task)
    assert '"pdf": str(' not in src, (
        "run_task records a path to a rendered candidate, but the temp directory is removed at the "
        "end of every run -- the path resolves to nothing")
    assert "legend_frames" in src, "the FACT the artefact established is not recorded"
    assert "legend_occlusions" in src


def test_the_fact_helpers_exist(bench):
    assert callable(getattr(bench, "_legend_frame_count", None))
    assert callable(getattr(bench, "_legend_occlusion_count", None))


def test_an_unreadable_or_absent_pdf_reports_zero_not_an_error(bench):
    """A missing artefact is a legitimate state, and it must not crash the measurement."""
    assert bench._legend_frame_count(None) == 0
    assert bench._legend_frame_count("") == 0
    assert bench._legend_frame_count("no-such-file.pdf") == 0
    assert bench._legend_occlusion_count(None) == 0
    assert bench._legend_occlusion_count("no-such-file.pdf") == 0


def test_the_total_reports_its_own_membership(bench):
    """THE AGGREGATE DEFECT. `legend_frames: 0` over 6 of 139 rows is not a statement about 139."""
    src = pathlib.Path(bench.__file__).read_text(encoding="utf-8")
    assert "legend_coverage" in src, "the legend totals do not report how many rows they cover"
    assert "n_measured" in src
    assert "n_ok" in src


def test_the_report_on_disk_carries_the_membership(bench):
    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not path.is_file():
        pytest.skip("no pool report")
    report = json.loads(path.read_text(encoding="utf-8"))
    if "legend_coverage" not in report:
        pytest.skip("the report predates the field; the next measurement will carry it")
    cov = report["legend_coverage"]
    assert "n_measured" in cov and "n_ok" in cov
    assert cov["n_measured"] <= cov["n_ok"], (
        f"n_measured ({cov['n_measured']}) exceeds n_ok ({cov['n_ok']})")


def test_the_note_explains_why_rows_are_missing(bench):
    """A reader must be able to tell 'the check found nothing' from 'the check never ran here'."""
    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not path.is_file():
        pytest.skip("no pool report")
    report = json.loads(path.read_text(encoding="utf-8"))
    cov = report.get("legend_coverage") or {}
    if not cov:
        pytest.skip("the report predates the field")
    note = cov.get("note", "")
    assert "n_measured" in note, f"the note does not explain the membership: {note!r}"
