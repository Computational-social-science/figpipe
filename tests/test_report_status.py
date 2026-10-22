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
    window = html[i:i + 900]
    assert "tasks" in window, f"the gap does not name its unit: {window[:300]}"
    # THE REQUIREMENT IS A COUNT, NOT A PARTICULAR FORMAT. The comment always said so, but the
    # assertion only accepted "N of M" or "N%". When every task became verified the board began
    # saying "ALL 139 executed tasks ... 110 by full re-derivation, 29 by the colour-scale check",
    # which states three counts and failed the regex.
    import re as _re
    assert (_re.search(r"\d+\s+of\s+\d+", window)
            or _re.search(r"\d+%", window)
            or _re.search(r"\bALL \d+\b", window)), (
        f"the gap is not stated as a number: {window[:300]}")
    # and it must account for the unverifiable mesh tasks rather than quietly excluding them
    assert "MESH" in window or "mesh" in window, (
        "the gap omits the unverifiable tasks, so it understates what is not verified")


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


def test_unchecked_rules_are_grouped_by_REASON_not_just_counted():
    """A bare count of unchecked rules reads as a to-do list. It is not one.

    Measured 2026-10-21: of the 8 unchecked rules, 4 are about CAPTION TEXT (out of scope for a
    figure pipeline), 2 are VOID (measured on a detector the audit showed was wrong), 1 is REFUTED
    (a real Nature figure contradicted it), and 1 has NO DATA to check against. Reporting "8 rules
    have no machine check" invites a future round to "verify" rules that cannot or should not be.
    """
    import json
    kb = json.loads((ROOT / "knowledge" / "layout_rules.json").read_text(encoding="utf-8"))
    unchecked = [r for r in kb.get("rules", []) if not r.get("check")]
    assert unchecked, "no unchecked rules; this test would be vacuous"
    for r in unchecked:
        assert r.get("unchecked_reason"), (
            f"rule {r.get('id')} has no stated reason for being unchecked, so a reader cannot tell "
            f"an unfinished task from an impossible one")
        assert r.get("unchecked_why"), f"rule {r.get('id')} has no explanation"
        assert r["unchecked_reason"] in ("no_data", "refuted", "void", "out_of_scope"), (
            f"rule {r.get('id')} has an unknown reason {r['unchecked_reason']!r}")


def test_the_board_states_the_reason_grouping(report_src):
    if not report_src.is_file():
        pytest.skip("report not built")
    html = report_src.read_text(encoding="utf-8")
    assert "Unchecked rules, by reason" in html, (
        "the board still reports a bare count of unchecked rules")
    for reason in ("out_of_scope", "void", "refuted"):
        assert reason in html, f"the board does not name the {reason!r} class"


# ---------------------------------------------------------------------------------------
# THE STATUS BOARD MUST APPEAR ONCE
#
# `{status_board}` was inserted twice: once under the hero (section 00, correct) and again inside
# section "04 Authoritative benchmark". The second insertion repeated the whole table verbatim, so a
# reader scrolling to the benchmark saw the project-status board a second time and could not tell
# whether the two were the same board or two boards that happened to agree.
#
# This is the same defect class as the duplicate `summarise`/`compare` names: one piece of content
# presented in two places as if it were two.
# ---------------------------------------------------------------------------------------

def test_the_status_board_appears_exactly_once():
    import re
    report = ROOT / "reports" / "figpipe_report.html"
    if not report.is_file():
        pytest.skip("no report")
    html = report.read_text(encoding="utf-8")
    for heading in ("Where this project is right now", "Biggest known gap", "Sharpest limit"):
        n = html.count(heading)
        assert n == 1, f"{heading!r} appears {n} times in the report; it must appear exactly once"


def test_the_template_inserts_the_board_once():
    """The SOURCE must not contain two placeholders either -- the HTML check alone would pass if
    one branch of the template stopped rendering."""
    src = (ROOT / "scripts" / "build_report.py").read_text(encoding="utf-8")
    assert src.count("{status_board}") == 1, (
        "the template inserts {status_board} more than once")


def test_no_negative_count_in_the_board():
    """A count of tasks cannot be negative, and one was.

    The board computed `unverifiable - partial`, assuming the partially-verified tasks were a SUBSET
    of the unverifiable ones. They are not: `mesh_scale_checked` is its own coverage state and the
    two counts are disjoint, so the subtraction produced "-9 are UNVERIFIABLE BY CONSTRUCTION".
    """
    import re
    report = ROOT / "reports" / "figpipe_report.html"
    if not report.is_file():
        pytest.skip("no report")
    html = report.read_text(encoding="utf-8")
    body = re.sub(r"<[^>]+>", " ", html)
    body = re.sub(r"\s+", " ", body)
    assert not re.search(r"(?<![\d.])-\d+ (?:of|are|tasks|more)", body), (
        "the report states a negative task count")


def test_the_board_total_counts_every_coverage_state():
    """`partial` is a coverage state, not a subset of `unverifiable`.

    Leaving it out of the total made the board say "ALL 110 executed tasks" when 139 were executed.
    """
    import json
    import re
    report = ROOT / "reports" / "figpipe_report.html"
    data = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not (report.is_file() and data.is_file()):
        pytest.skip("no report")
    b = json.loads(data.read_text(encoding="utf-8"))
    cov = b.get("semantic_coverage") or {}
    expected = sum(cov.get(k, 0) or 0 for k in
                   ("checked", "mesh_scale_checked", "skipped", "unverifiable", "absent"))
    html = report.read_text(encoding="utf-8")
    i = html.find("Biggest known gap")
    if i < 0:
        pytest.skip("no status board")
    text = re.sub(r"<[^>]+>", " ", html[i:i + 900])
    text = re.sub(r"\s+", " ", text)
    assert f"ALL {expected} executed tasks" in text, (
        f"the board does not report all {expected} executed tasks; it says: {text[:220]}")
