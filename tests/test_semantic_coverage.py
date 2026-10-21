"""Whether the semantic check RAN must be recorded, not inferred from an empty list.

WHY THIS TEST
    `semantic_findings` is an empty list in two opposite situations:

        the check RAN and found nothing          -> the task is verified
        the check NEVER RAN for this drawer      -> the task is unverified

    14 of 16 drawers skip `verify.semantics` (only `scatter_fit` and `trend_band` are checked), so
    most pool tasks fall in the second case -- and the report could not tell them apart. A pass on
    an unverified task is a statement about geometry, not about correctness, and a reader could not
    see the difference.

    `semantic_state()` records the distinction, and `report["semantic_coverage"]` counts it.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def bench():
    import bench_plottwin
    return bench_plottwin


def test_a_checked_task_is_reported_as_checked(bench):
    """When EVERY panel is in scope the operator appends only the bare summary line."""
    assert bench.semantic_state({"trace": ["encode.trend(x,y)", "verify.semantics"]}) == "checked"


def test_a_skipped_task_is_reported_as_skipped(bench):
    """THE BUG: the operator appends a skip line PER PANEL and then a bare summary line.

    My first check saw the summary and called the task "checked", so the coverage came back
    139/139 -- every task looked verified, which is the confidently-wrong number this project keeps
    finding. A skip line means at least one panel was NOT verified, whatever else the step did.
    """
    got = bench.semantic_state(
        {"trace": ["encode.bars(x,y)",
                   "verify.semantics(skip panel 0: grouped_bars)",
                   "verify.semantics"]})
    assert got == "skipped"


def test_a_task_with_no_semantic_step_is_absent(bench):
    """NEGATIVE CONTROL: a trace with no semantic step at all must not be called checked."""
    assert bench.semantic_state({"trace": ["encode.bars(x,y)", "layout.plate"]}) == "absent"
    assert bench.semantic_state({"trace": []}) == "absent"
    assert bench.semantic_state({}) == "absent"


def test_the_three_states_are_distinct(bench):
    """If two states collapsed into one, the coverage count would lie."""
    traces = {
        "checked": {"trace": ["verify.semantics"]},
        "skipped": {"trace": ["verify.semantics(skip panel 0: boxplot)", "verify.semantics"]},
        "absent": {"trace": ["layout.plate"]},
    }
    got = {bench.semantic_state(t) for t in traces.values()}
    assert got == {"checked", "skipped", "absent"}, f"states collapsed: {got}"


def test_the_report_records_coverage(bench):
    """The report must carry the count, or the gap is invisible to a reader."""
    import inspect
    src = inspect.getsource(bench)
    assert "semantic_coverage" in src, (
        "the report does not record semantic coverage, so an unverified pass looks verified")
    assert "semantic_checked" in src, (
        "per-task state is not recorded, so the aggregate cannot be computed")
    assert "NOT re-derived" in src, (
        "the report does not warn that a skipped task's numbers were never re-derived")


def test_the_state_call_references_a_defined_variable(bench):
    """REGRESSION: `semantic_state(chosen)` referenced a name that does not exist.

    The selected result is `(styled if chosen_is_styled else plain)`. The mistake broke the WHOLE
    POOL -- 139 of 139 tasks came back `NameError: name 'chosen' is not defined` -- and the only
    reason it was caught is that the re-measure was actually run instead of assumed.

    `run_task` needs the network and a real target CSV, so a unit test cannot drive it cheaply. A
    static check catches the class that mattered: the argument must be a name bound in the function.
    """
    import ast
    import inspect
    src = inspect.getsource(bench.run_task)
    tree = ast.parse(src.lstrip())
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "semantic_state"]
    assert calls, "run_task never records the semantic state"
    # every Name used as an argument must be assigned somewhere in the function
    assigned = {n.id for n in ast.walk(tree)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    for call in calls:
        for arg in call.args:
            for name_node in ast.walk(arg):
                if isinstance(name_node, ast.Name) and isinstance(name_node.ctx, ast.Load):
                    if name_node.id in ("styled", "plain", "chosen_is_styled"):
                        continue          # bound by the tuple unpacking / comparison above
                    assert name_node.id in assigned, (
                        f"semantic_state is called with {name_node.id!r}, which is never assigned "
                        f"in run_task -- this is the NameError that broke the whole pool")


def test_the_selected_result_is_the_one_recorded(bench):
    """The state must describe the figure that was SHIPPED, not the candidate that was not."""
    import inspect
    src = inspect.getsource(bench.run_task)
    assert "styled if chosen_is_styled else plain" in src, (
        "the state is not computed from the selected result")


def test_a_mesh_drawer_is_UNVERIFIABLE_not_merely_skipped(bench):
    """A pcolormesh is ONE path: the cell values never reach the PDF.

    That is a property of the FORMAT, not unfinished work, and the two must not be counted
    together -- otherwise the coverage number says the wrong thing about what remains to be done.
    """
    trace = ["verify.semantics(mesh panel 0: tile_diverging -- a signed matrix is one pcolormesh "
             "path; the cell values are not in the PDF)", "verify.semantics"]
    assert bench.semantic_state({"trace": trace}) == "unverifiable"


def test_the_four_states_are_distinct(bench):
    """checked / skipped / unverifiable / absent must not collapse into each other."""
    traces = {
        "checked": {"trace": ["verify.semantics"]},
        "skipped": {"trace": ["verify.semantics(skip panel 0: boxplot)", "verify.semantics"]},
        "unverifiable": {"trace": ["verify.semantics(mesh panel 0: field_2d -- one path)",
                                   "verify.semantics"]},
        "absent": {"trace": ["layout.plate"]},
    }
    got = {name: bench.semantic_state(v) for name, v in traces.items()}
    assert got == {name: name for name in traces}, got


def test_the_coverage_report_counts_unverifiable_separately(bench):
    import inspect
    src = inspect.getsource(bench)
    assert '"unverifiable": states.count("unverifiable")' in src, (
        "the coverage report does not count unverifiable tasks separately from skipped ones")
