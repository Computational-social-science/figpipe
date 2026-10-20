"""The report must say WHERE THE PROJECT IS, not only what exists.

WHY THIS TEST
    A reader said: "the report does not seem to be updated in time, I cannot tell how far the
    project has got." The file WAS current -- it was regenerated minutes earlier. The problem was
    that it answered a different question: an inventory of deliverables says what EXISTS, not what
    is DONE, what is BROKEN, or what the next move is.

    `_status_board()` puts four lines before everything else, all read from artefacts:
        Done                capabilities with a verified number behind them
        Biggest known gap   the largest KNOWN gap, stated as a number
        Unverified rules    rules that have no machine check
        Next step           the single next move, with its acceptance criterion
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def report_src():
    return (ROOT / "reports" / "figpipe_report.html")


def test_the_report_opens_with_a_status_board(report_src):
    if not report_src.is_file():
        pytest.skip("report not built")
    html = report_src.read_text(encoding="utf-8")
    assert 'class="status"' in html, "the report has no status board"
    # and it must come BEFORE the KPI grid and the deliverables, or a reader meets inventory first
    i_status = html.find('class="status"')
    i_kpis = html.find('class="kpis"')
    i_deliv = html.find("Research deliverables")
    assert i_status < i_kpis, "the status board is not before the KPIs"
    assert i_status < i_deliv, "the status board is not before the deliverables"


def test_the_status_board_names_the_biggest_gap_as_a_number(report_src):
    """"Biggest known gap" must carry a count, not an adjective."""
    if not report_src.is_file():
        pytest.skip("report not built")
    html = report_src.read_text(encoding="utf-8")
    i = html.find("Biggest known gap")
    assert i > 0, "the report does not name its biggest known gap"
    window = html[i:i + 700]
    assert "tasks" in window and "%" in window, (
        f"the gap is not stated as a number: {window[:300]}")


def test_the_status_board_states_a_next_step_with_an_acceptance_criterion(report_src):
    if not report_src.is_file():
        pytest.skip("report not built")
    html = report_src.read_text(encoding="utf-8")
    i = html.find("Next step")
    assert i > 0, "the report does not state a next step"
    window = html[i:i + 600]
    assert "Acceptance" in window, (
        f"the next step has no acceptance criterion: {window[:300]}")


def test_the_board_is_built_from_artefacts_not_hand_written():
    """A hand-written status drifts. Every line must come from a file the pipeline produces."""
    import inspect
    import build_report
    src = inspect.getsource(build_report._status_board)
    assert "bench.get" in src, "the board does not read the benchmark report"
    assert "semantic_coverage" in src, "the board does not read the semantic coverage"
    assert "kb.get" in src, "the board does not read the knowledge base"
