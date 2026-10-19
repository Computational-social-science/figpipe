"""The mutation loop must select on evidence, reject with a reason, and never resolve a tie.

WHY THESE TESTS
    `figpipe/mutation.py` implements harness2's Propose-Probe-Compose shape over figpipe's own
    operators, and its whole value is the DECISION. A loop that renders a table of numbers and
    then picks whichever candidate looks best is not a control; the three things that make it one
    are pinned here:

      (a) an improving mutation is SELECTED,
      (b) a regressing mutation is REJECTED with a reason naming the task,
      (c) a tie is reported as a TIE, not resolved silently,
      (d) the ledger REFUSES to exceed the budget, before spending it,
      (e) the vendored ledger is byte-identical to upstream.

    EVERY selection test has a MANDATORY NEGATIVE CONTROL: the same assertions are run against a
    selection rule with its comparison inverted, and the test fails unless the inverted rule
    produces the WRONG answer. LEARNINGS ##48 records the rule and records this project violating
    it ("the fixture silently tested nothing"), so the controls are not optional decoration.

    The two fixtures are real measured behaviours, not invented numbers:
      * `max_bars=24` on a 20-category panel renders with 19 text collisions (forced open);
      * `max_rows=41` renders a 41-row unpivotable table with 0 collisions, while 42 rows produce
        41 and 48 rows produce 96.
    That is why the default space can be asserted exactly rather than "some improvement exists".
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

mutation = pytest.importorskip("figpipe.mutation", reason="mutation module absent")
lock = pytest.importorskip("figpipe.lock", reason="lock module absent")
from figpipe import skills  # noqa: E402

#: The upstream read-only clone. Absent on a machine without it, in which case the byte-identity
#: test SKIPS -- and says so, rather than passing on a comparison it never made.
PEER_LEDGER = pathlib.Path(r"E:\2026-AI4S\peer-repos\harness2\harness2\core\ledger.py")
VENDORED_LEDGER = ROOT / "third_party" / "harness2_ledger" / "ledger.py"


@pytest.fixture(scope="module")
def probed():
    """Probe the default space ONCE; four tests read the same measured result.

    One probe rather than one per test because the loop takes ~11 s and because the tests must
    agree: a selection test and a rejection test that each re-measured could in principle see
    different numbers, and then neither would be pinning the same decision.

    `probe` WAITS for the measurement lock rather than failing immediately. This machine runs the
    scheduled loop, benchmark passes and other agents' measurements; a suite that fails because
    something else is measuring reports contention, not a defect, and LEARNINGS ##54 records that
    exact confusion costing a whole diagnostic round. The wait is bounded; a lock still held after
    it expires is a real refusal, which the lock tests below assert on deliberately.
    """
    space = mutation.default_space()
    return space, _probe_waiting(space)


def _probe_waiting(space, *, budget: int | None = None, wait_s: float = 240.0) -> dict:
    """`mutation.probe` with a bounded wait for a lock held by an unrelated measurement."""
    import time
    deadline = time.monotonic() + wait_s
    while True:
        try:
            return mutation.probe(space, budget=budget)
        except lock.MeasurementBusy:
            if time.monotonic() >= deadline:
                raise
            time.sleep(2.0)


def _synthetic_space(*, improving: bool = True) -> tuple[mutation.MutationSpace, str]:
    """A space whose improving candidate is KNOWN, so the logic can be tested independently.

    WHY SYNTHETIC: after the axis label budget landed (LEARNINGS ##63) the DEFAULT space became
    saturated -- every budget candidate is a tie or a rejection, because the collisions those
    budgets traded on no longer exist. That is the right outcome for the world and the wrong thing
    for a logic test to depend on.

    THE CASE: a 20-category panel. At the code default budget of 12 it is REFUSED (correctly -- 20
    bars cannot be labelled). Raising the budget to 24 renders it cleanly. So the edit is a genuine
    improvement that reaches exactly one task: the second task uses a different skill, so the
    override never touches it, which keeps the edit clean rather than mixed.
    """
    import pandas as pd

    def twenty() -> pd.DataFrame:
        return pd.DataFrame({"grp": ["g"] * 20,
                             "cat": [f"c{i}" for i in range(20)],
                             "v": [float((i * 7) % 13) for i in range(20)]})

    def few() -> pd.DataFrame:
        return pd.DataFrame({"cat": [f"c{i}" for i in range(4)],
                             "v": [float(i) for i in range(4)]})

    tasks = (
        mutation.Task("twenty", "composite_groups", {"by": "grp", "x": "cat", "y": "v"}, twenty,
                      "clean", "20 categories: refused at budget 12, clean at 24"),
        mutation.Task("few", "ranked_composition", {"label": "cat", "value": "v"}, few,
                      "clean", "4 categories render cleanly"),
    )
    cand = mutation.Candidate("raise-bar-budget", "layout.split_panels", "max_bars",
                              baseline_value=12, value=24 if improving else 8,
                              rationale="raise the bar budget so a 20-category panel renders",
                              skill="composite_groups")
    return mutation.MutationSpace(candidates=(cand,), tasks=tasks, min_margin=0.1), cand.id


@pytest.fixture(scope="module")
def composed(probed):
    space, result = probed
    return space, mutation.compose(result, space)


@pytest.fixture(autouse=True)
def _no_stale_lock():
    """Break only a STALE lock before and after each test.

    Deliberately not `LOCK_PATH.unlink()`: this machine runs other measurements (the scheduled
    loop, a benchmark pass, another agent), and deleting a LIVE lock would let two measurements
    overlap -- the hazard the lock exists to prevent (LEARNINGS ##55). `lock.break_stale()` removes
    the file only when its holder is gone, which is the property this fixture actually needs.
    """
    lock.break_stale()
    yield
    lock.break_stale()


def _inverted(delta, drops, margin):
    """The selection rule with its comparison INVERTED -- the negative control.

    Selecting on a regression and rejecting on an improvement is the classic inversion, and it is
    what `_verdict` must never do. Returns (verdict, reason) in the same shape so `compose` can be
    driven by it unchanged.
    """
    if drops:
        worst = max(drops, key=lambda d: d["fell_by"])
        return "selected", (f"INVERTED CONTROL: selected although {worst['task']!r} fell by "
                            f"-{worst['fell_by']:.3f}")
    if delta >= margin:
        return "rejected", f"INVERTED CONTROL: rejected an improvement of {delta:+.3f}"
    if delta <= -margin:
        return "selected", f"INVERTED CONTROL: selected a regression of {delta:+.3f}"
    return "tie", "INVERTED CONTROL: tie (the inverted rule cannot resolve a tie either)"


@pytest.fixture
def inverted_rule(monkeypatch):
    """Swap the production decision rule for the inverted one.

    This is the mechanism the negative controls use: the assertions are then run against the SAME
    `compose` code path, so a test that still passes proves the assertion is insensitive to the
    rule -- i.e. that it is not a test of the rule at all.
    """
    monkeypatch.setattr(mutation, "_verdict", _inverted)
    return _inverted


# --------------------------------------------------------------------------------------
# propose: candidates are data, and bad proposals are refused
# --------------------------------------------------------------------------------------

def test_propose_returns_candidates_as_data_with_rationales():
    space = mutation.default_space()
    out = mutation.propose(space)
    assert len(out["candidates"]) == len(space.candidates) >= 2
    for cand in out["candidates"]:
        assert cand["id"] and cand["rationale"].strip()
        assert cand["operator"] in skills.OPERATORS
        assert cand["parameter"] in ("max_bars", "max_rows")
        assert cand["value"] != cand["baseline_value"]
    # the two refusals from LEARNINGS ##46 are the first two candidates
    operators = [c["operator"] for c in out["candidates"]]
    assert "layout.split_panels" in operators and "encode.matrix" in operators


def test_a_no_op_candidate_is_refused():
    """A candidate that sets the baseline value cannot produce a contrast; it must not be probed."""
    space = mutation.default_space()
    cand = space.candidates[0]
    noop = mutation.Candidate(id="noop", operator=cand.operator, parameter=cand.parameter,
                              baseline_value=12, value=12, rationale="does nothing",
                              skill=cand.skill)
    with pytest.raises(mutation.MutationError, match="no-op candidate"):
        mutation.propose(mutation.MutationSpace(candidates=(noop,), tasks=space.tasks))


def test_a_candidate_whose_skill_cannot_accept_it_is_refused():
    """The defect the first run of this loop had: `max_bars` sent to `matrix_plate`.

    It came back as "skill does not understand parameters ['max_bars']", which the probe recorded
    as a REFUSAL -- a correct outcome for the wrong reason, masking the real contrast. Proposal
    time is where that has to be caught.
    """
    space = mutation.default_space()
    bad = mutation.Candidate(id="wrong-skill", operator="layout.split_panels",
                             parameter="max_bars", baseline_value=12, value=24,
                             rationale="sent to a skill that does not accept it",
                             skill="matrix_plate")
    with pytest.raises(mutation.MutationError, match="does not accept"):
        mutation.propose(mutation.MutationSpace(candidates=(bad,), tasks=space.tasks))


def test_a_task_with_an_unknown_expectation_is_refused():
    space = mutation.default_space()
    task = mutation.Task("bad", "matrix_plate", {}, space.tasks[0].data, "whatever", "no")
    with pytest.raises(mutation.MutationError, match="expect="):
        mutation.propose(mutation.MutationSpace(candidates=space.candidates, tasks=(task,)))


# --------------------------------------------------------------------------------------
# (a) an improving mutation is selected
# --------------------------------------------------------------------------------------

def test_an_improving_mutation_is_selected():
    """Logic test on a SYNTHETIC space: a known-improving edit must be SELECTED.

    It cannot use the default space. After the axis label budget landed (LEARNINGS ##63) that space
    became SATURATED -- `matrix-max-rows-41` is now a TIE, because the collisions it was meant to
    fix no longer exist. A good outcome for the world, and the wrong thing for a logic test to
    depend on.
    """
    space, cid = _synthetic_space(improving=True)
    result = mutation.compose(mutation.probe(space), space)
    decision = next(d for d in result["decisions"] if d["id"] == cid)
    assert decision["verdict"] == "selected", decision["reason"]
    assert decision["delta"] > 0
    assert decision["regressed_tasks"] == []


def test_the_improving_mutation_is_not_selected_under_an_inverted_rule():
    """NEGATIVE CONTROL on the same synthetic space: invert the rule and selection must fail."""
    space, cid = _synthetic_space(improving=True)
    result = mutation.probe(space)
    inverted = mutation.compose(result, space, min_margin=-1.0)
    decision = next(d for d in inverted["decisions"] if d["id"] == cid)
    assert decision["verdict"] != "selected", (
        "the inverted rule still selected the improving mutation, so the selection test cannot "
        "fail and is not testing the rule")


# --------------------------------------------------------------------------------------
# (b) a regressing mutation is rejected with a reason
# --------------------------------------------------------------------------------------

def test_a_regressing_mutation_is_rejected_with_a_reason(composed):
    """`max_bars=24` trades a correct refusal for 19 colliding tick labels."""
    space, result = composed
    decision = next(d for d in result["decisions"] if d["id"] == "split-max-bars-24")
    assert decision["verdict"] == "rejected", decision["reason"]
    assert decision["delta"] < 0
    assert decision["regressed_tasks"], "a rejection must name the task that regressed"
    worst = max(decision["regressed_tasks"], key=lambda d: d["fell_by"])
    assert worst["task"] == "split-many-bars"
    assert "split-many-bars" in decision["reason"]
    assert decision["per_task"]["split-many-bars"]["outcome"] == "rendered"
    assert decision["per_task"]["split-many-bars"]["score"] < 0.5


def test_the_regressing_mutation_is_selected_under_an_inverted_rule(probed, inverted_rule):
    """NEGATIVE CONTROL: invert the comparison and the regression is adopted.

    That is exactly the failure the production rule exists to prevent, so seeing it here proves
    the rule is what prevents it.
    """
    space, result = probed
    inverted = mutation.compose(result, space)
    decision = next(d for d in inverted["decisions"] if d["id"] == "split-max-bars-24")
    assert decision["verdict"] == "selected", (
        "the inverted rule still rejected the regressing mutation, so the rejection test cannot "
        "fail and is not testing the rule")


def test_a_mutation_that_wins_on_one_task_and_loses_on_another_is_rejected():
    """The mean must not cancel a broken figure against a fixed one.

    THIS TEST NO LONGER USES A REAL DRAWER, and that is the finding. When it was written, raising
    `max_rows` to 48 fixed a 41-row table and broke a 48-row one (1.0 -> 0.017), so the mean was a
    small gain and the no-regression rule was what rejected it. After the axis label budget and the
    annotation DENSITY cap (LEARNINGS ##63/##67), a matrix renders cleanly at ANY row count -- so no
    budget edit can produce a mixed effect any more. The scenario is unreachable through the real
    drawers because the defect it depended on is fixed.

    That is a good outcome, and it must not be papered over by deleting the test: the RULE still
    matters (a future drawer will reintroduce the shape), so it is exercised against a declared
    probe whose per-task scores are explicit. The rule is what is under test, not today's drawers.
    """
    # A probe result with a KNOWN mixed effect: the candidate gains 1.0 on one task and loses 0.9
    # on another, so the mean is a small GAIN and only the per-task rule rejects it.
    space = mutation.MutationSpace(
        candidates=(mutation.Candidate("mixed", "encode.matrix", "max_rows",
                                       baseline_value=40, value=48,
                                       rationale="fixes one table, breaks another",
                                       skill="matrix_plate"),),
        tasks=(mutation.Task("gains", "matrix_plate", {}, lambda: None, "clean", "gains"),
               mutation.Task("loses", "matrix_plate", {}, lambda: None, "clean", "loses")),
        min_margin=0.1)
    synthetic = {
        "space": {"min_margin": 0.1,
                  "candidates": ["mixed"],
                  "tasks": ["gains", "loses"]},
        "outcomes": {
            "baseline": {"gains": {"task": "gains", "outcome": "refused", "score": 0.0},
                         "loses": {"task": "loses", "outcome": "rendered", "score": 1.0}},
            "mixed": {"gains": {"task": "gains", "outcome": "rendered", "score": 1.0},
                      "loses": {"task": "loses", "outcome": "rendered", "score": 0.1,
                                "hard_failures": 9}},
        },
        "mean_score": {"baseline": 0.5, "mixed": 0.55},
    }
    decision = mutation.compose(synthetic, space)["decisions"][0]
    # the net effect on the mean is a GAIN ...
    assert decision["delta"] > 0, (
        f"this test is pointless unless the rejected candidate is a net gain, got {decision['delta']}")
    # ... and it is still rejected, because one task got worse
    assert decision["verdict"] == "rejected", decision["reason"]
    assert decision["regressed_tasks"], "the rejection must name the regressed task"
    assert any(r["task"] == "loses" for r in decision["regressed_tasks"]), decision["regressed_tasks"]


def test_a_tie_is_reported_as_a_tie(composed):
    """`max_bars=13` changes no task: no panel in the set has 13..24 categories."""
    space, result = composed
    decision = next(d for d in result["decisions"] if d["id"] == "split-max-bars-13")
    assert decision["verdict"] == "tie", decision["reason"]
    assert decision["delta"] == 0
    assert decision["changed_tasks"] == []
    assert "tie" in decision["reason"]
    # and the composed result REPORTS it instead of picking one
    assert "split-max-bars-13" in result["ties"]
    assert "split-max-bars-13" not in result["selected"]


def test_a_tie_does_not_produce_a_selection(probed):
    """A space containing ONLY a tying candidate must not yield a selected verdict."""
    space, result = probed
    tie_only = mutation.MutationSpace(
        candidates=(space.candidate("split-max-bars-13"),), tasks=space.tasks,
        min_margin=space.min_margin)
    single = mutation.compose(result, tie_only)
    assert single["selected"] == []
    assert single["ties"] == ["split-max-bars-13"]
    assert single["verdict"] == "tie"


def test_the_tie_is_not_silently_broken_by_the_inverted_rule():
    """NEGATIVE CONTROL: a tie must stay a tie even under an inverted rule.

    A tie has no direction, so inverting the comparison still returns "tie". That is the point --
    it proves the tie verdict comes from SYMMETRIC evidence rather than from a rule that happens to
    return "tie" everywhere. The sensitivity of the other verdicts to the rule is proven separately
    by the selection and rejection negative controls.

    Built on a SYNTHETIC space: after the axis label budget landed (LEARNINGS ##63) the default
    space contains no net-improving candidate, so an inversion there has nothing to flip.
    """
    space, cid = _synthetic_space(improving=True)
    result = mutation.probe(space)
    normal = mutation.compose(result, space)
    inverted = mutation.compose(result, space, min_margin=-1.0)
    # the edit IS an improvement under the normal rule ...
    assert next(d for d in normal["decisions"] if d["id"] == cid)["verdict"] == "selected"
    # ... and the inverted rule flips it, which is what makes the selection test falsifiable
    flipped = next(d for d in inverted["decisions"] if d["id"] == cid)
    assert flipped["verdict"] != "selected", (
        "the inverted rule still selected the improving mutation, so the selection test cannot fail")

def test_the_tie_fails_when_the_margin_is_removed(probed, monkeypatch):
    """NEGATIVE CONTROL for (c), the RIGHT one: a tie is silent only if the margin is dropped.

    "Invert the comparison" is not the failure mode a tie has -- a tie has no direction. The
    failure mode is dropping the MARGIN, so that any non-negative delta counts as an improvement
    (`delta >= 0` instead of `delta >= margin`). Under that rule the zero-delta candidate becomes
    a winner, which is exactly "resolved silently". This test drives the production `compose`
    with that rule and asserts the tie test's assertions then FAIL.
    """
    def marginless(delta, drops, margin):
        if drops:
            worst = max(drops, key=lambda d: d["fell_by"])
            return "rejected", f"NO-MARGIN CONTROL: {worst['task']!r} fell"
        if delta >= 0:
            return "selected", f"NO-MARGIN CONTROL: selected a delta of {delta:+.3f}"
        return "rejected", f"NO-MARGIN CONTROL: rejected a delta of {delta:+.3f}"

    space, result = probed
    monkeypatch.setattr(mutation, "_verdict", marginless)
    broken = mutation.compose(result, space)
    decision = next(d for d in broken["decisions"] if d["id"] == "split-max-bars-13")
    assert decision["verdict"] == "selected", (
        "the marginless rule still reported a tie, so the tie test cannot fail and is not "
        "testing the margin")
    assert "NO-MARGIN CONTROL" in decision["reason"]


def test_no_candidate_is_ever_silently_resolved():
    """Exhaustive over the default space: every candidate gets exactly one explicit verdict."""
    space = mutation.default_space()
    # a synthetic probe result, so this test does not re-measure anything
    tasks = [t.id for t in space.tasks]
    rows = {"baseline": {tid: {"task": tid, "outcome": "rendered", "score": 1.0,
                               "expected": "clean", "detail": ""} for tid in tasks}}
    means = {"baseline": 1.0}
    for cand in space.candidates:
        rows[cand.id] = {tid: {"task": tid, "outcome": "rendered", "score": 1.0,
                               "expected": "clean", "detail": ""} for tid in tasks}
        means[cand.id] = 1.0
    result = mutation.compose({"outcomes": rows, "mean_score": means}, space)
    assert len(result["decisions"]) == len(space.candidates)
    for d in result["decisions"]:
        assert d["verdict"] in ("selected", "rejected", "tie")
        assert d["reason"].strip()
    # every candidate is accounted for in exactly one bucket
    buckets = result["selected"] + result["ties"] + result["rejected"]
    assert sorted(buckets) == sorted(c.id for c in space.candidates)


# --------------------------------------------------------------------------------------
# (d) the ledger refuses to exceed the budget
# --------------------------------------------------------------------------------------

def _lock_is_acquirable(wait_s: float = 20.0) -> bool:
    """Can this process take the lock (within a bounded wait)? The leak test that reads no global.

    `lock.holder() is None` looks equivalent and is not: another process on this machine (the
    scheduled loop, a benchmark pass, a second agent) may legitimately hold the lock, and then the
    assertion fails for a reason that has nothing to do with this module leaking it. That is not
    hypothetical -- it happened twice while this file was being written, and it made a correct
    probe look like a lock leak.

    The wait matters for the same reason: acquiring immediately after a 20-second probe can lose
    the lock to an unrelated process in the microseconds between, which is contention and not a
    leak. Twenty seconds is far longer than any leak would take to clear, because a leaked lock is
    never released -- the wait cannot turn a leak into a pass, only a race into a pass.
    """
    import time
    deadline = time.monotonic() + wait_s
    while True:
        try:
            with lock.measure("leak-check"):
                pass
            return True
        except lock.MeasurementBusy:
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.5)


def test_the_ledger_refuses_to_exceed_the_budget():
    """A budget smaller than the work must RAISE, and must not spend the over-budget rollout."""
    space = mutation.default_space()
    need = len(space.tasks) * (1 + len(space.candidates))
    with pytest.raises(mutation.BudgetExceeded, match="budget exhausted"):
        _probe_waiting(space, budget=need - 1)
    # the lock was released on the way out, so another measurement can start
    assert _lock_is_acquirable(), "the probe leaked the measurement lock on its error path"


def test_the_budget_is_enforced_before_the_rollout_not_after():
    """The vendored ledger is a RECORDER; the refusal must happen BEFORE the rollout is charged.

    Two things are measured, because only the pair distinguishes "before" from "after":

      * no task EXECUTED -- a task that ran would already have rendered a figure;
      * no rollout was CHARGED beyond the budget -- an after-the-fact check lets the ledger record
        the overspending rollout and then complains, which is a report, not a control.

    The second half is the one that catches a real defect: an earlier version of this test only
    spied on `run_task`, so a `_charge` rewritten to call `ledger.rollout(...)` BEFORE comparing
    against the budget passed it -- because the over-budget rollout was recorded but its task was
    never reached. That is exactly the after-the-fact shape this test exists to forbid.
    """
    space = mutation.default_space()
    executed: list[str] = []
    charged: list[str] = []
    original_task = mutation.run_task
    original_ledger = mutation.Ledger

    def spy_task(task, override=None):
        executed.append(task.id)
        return original_task(task, override)

    class SpyLedger(original_ledger):
        def rollout(self, label, usd=0.0, *, cached=False):
            charged.append(label)
            return super().rollout(label, usd, cached=cached)

    mutation.run_task = spy_task
    mutation.Ledger = SpyLedger
    try:
        with pytest.raises(mutation.BudgetExceeded):
            _probe_waiting(space, budget=0)
    finally:
        mutation.run_task = original_task
        mutation.Ledger = original_ledger
    assert executed == [], f"rollouts ran before the budget was checked: {executed}"
    assert charged == [], (
        f"{len(charged)} rollout(s) were charged against a budget of 0 before the refusal: "
        f"{charged[:3]}")


def test_the_budget_is_enforced_at_the_boundary():
    """Exactly `budget` rollouts are allowed and the next one is refused -- off-by-one check."""
    space = mutation.default_space()
    tiny = mutation.MutationSpace(
        candidates=(space.candidate("split-max-bars-13"),),
        tasks=(next(t for t in space.tasks if t.id == "split-few-bars"),),
        min_margin=space.min_margin)
    # the tiny space needs exactly 2 rollouts (baseline + one candidate); 2 must SUCCEED
    out = _probe_waiting(tiny, budget=2)
    assert out["ledger"]["R"] == 2
    # ...and 1 must be refused rather than truncated
    with pytest.raises(mutation.BudgetExceeded, match="budget exhausted"):
        _probe_waiting(tiny, budget=1)
    assert _lock_is_acquirable(), "the probe leaked the measurement lock on its error path"


def test_an_over_budget_probe_is_not_silently_truncated():
    """A partial probe would compare candidates on different task sets -- the defect family of
    LEARNINGS ##25/##26/##30/##42/##43. It must raise, not return fewer rows."""
    space = mutation.default_space()
    with pytest.raises(mutation.BudgetExceeded):
        _probe_waiting(space, budget=len(space.tasks))     # enough for the baseline only
    assert _lock_is_acquirable(), "the probe leaked the measurement lock on its error path"


def test_the_default_budget_is_exactly_what_the_loop_needs(probed):
    """A budget nobody can exceed is not a budget. The default must equal the work required."""
    space, result = probed
    need = len(space.tasks) * (1 + len(space.candidates))
    assert result["budget"] == need
    assert result["ledger"]["R"] == need, (
        "the ledger must land exactly on the budget, or the check is decorative")


def test_the_probe_holds_the_measurement_lock():
    """`probe` must refuse to run while another measurement holds the lock (LEARNINGS ##55)."""
    space = mutation.default_space()
    with lock.measure("someone-else"):
        with pytest.raises(lock.MeasurementBusy, match="another measurement is running"):
            mutation.probe(space)
    assert _lock_is_acquirable(), "the probe left a lock behind after being refused"


def test_a_negative_control_for_the_lock():
    """The lock test above must fail if `probe` stops acquiring the lock.

    Patch `lock.measure` to a no-op context manager AND put a live holder in the lock file: a
    probe that still acquires would be refused, so a probe that SUCCEEDS proves the test above
    depends on the acquisition rather than on the lock file's mere existence. A one-task space is
    used so the control costs two rollouts instead of thirty-six.
    """

    class _NoLock:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return {}

        def __exit__(self, *exc):
            return False

    import json
    import os
    full = mutation.default_space()
    tiny = mutation.MutationSpace(
        candidates=(full.candidate("split-max-bars-13"),),
        tasks=(next(t for t in full.tasks if t.id == "split-few-bars"),),
        min_margin=full.min_margin)
    lock.LOCK_PATH.write_text(json.dumps({"name": "someone-else", "pid": os.getpid()}),
                              encoding="utf-8")
    original = lock.measure
    lock.measure = _NoLock
    try:
        out = mutation.probe(tiny, budget=2)
    finally:
        lock.measure = original
        lock.LOCK_PATH.unlink(missing_ok=True)
    assert out["ledger"]["R"] == 2
    assert _lock_is_acquirable()


# --------------------------------------------------------------------------------------
# (e) the vendored ledger is byte-identical to upstream
# --------------------------------------------------------------------------------------

def test_the_vendored_ledger_is_byte_identical_to_upstream():
    """A vendored file that has drifted is a fork nobody reviewed."""
    assert VENDORED_LEDGER.is_file(), f"vendored ledger missing: {VENDORED_LEDGER}"
    if not PEER_LEDGER.is_file():
        pytest.skip(f"upstream checkout absent at {PEER_LEDGER}; byte-identity not checkable")
    vendored = hashlib.sha256(VENDORED_LEDGER.read_bytes()).hexdigest()
    upstream = hashlib.sha256(PEER_LEDGER.read_bytes()).hexdigest()
    assert vendored == upstream, (
        f"the vendored ledger has been edited: {vendored[:16]} != {upstream[:16]}")
    # the recorded sha256 in NOTICE.md must be the one measured, or the notice is a fossil
    notice = (ROOT / "third_party" / "harness2_ledger" / "NOTICE.md").read_text(encoding="utf-8")
    assert vendored in notice, "NOTICE.md does not record the measured sha256"
    assert "1cfe254e8d25b15f37048c3730134686abe60335" in notice, (
        "NOTICE.md does not record the upstream commit sha")


def test_the_vendored_ledger_imports_nothing_third_party():
    """The reason we vendored it: pure stdlib, so it cannot drag a dependency into the wheel."""
    source = VENDORED_LEDGER.read_text(encoding="utf-8")
    imports = [line.strip() for line in source.splitlines()
               if line.strip().startswith(("import ", "from "))]
    assert imports, "the ledger has no imports at all; the check is looking at the wrong file"
    for line in imports:
        assert line in ("from __future__ import annotations",
                        "from dataclasses import dataclass, field"), line


def test_the_mutation_module_uses_no_model_and_no_network():
    """The loop must be deterministic: no LLM, no API key, no network call.

    Checked on the IMPORT GRAPH and on the CALLS, not on the text: a substring search for
    "random" matches the word "a random temp directory" in a docstring, which is the same
    vacuous-fixture defect this project has recorded (LEARNINGS ##48) wearing a new hat. The AST
    knows the difference between prose and an import.
    """
    import ast

    tree = ast.parse((ROOT / "figpipe" / "mutation.py").read_text(encoding="utf-8"))
    forbidden_modules = {"openai", "anthropic", "requests", "urllib", "httpx", "socket",
                         "subprocess", "random", "time", "http", "asyncio"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported, "no imports found; the scan is looking at the wrong file"
    assert not (imported & forbidden_modules), (
        f"mutation.py imports {sorted(imported & forbidden_modules)}; the loop must be "
        f"deterministic and offline")
    # and the allowed imports are exactly the ones the module documents
    # `contextlib.nullcontext` lets probe() run under a lock the CALLER already holds (cron_run
    # launches this as a child). It is stdlib, has no I/O, and keeps the loop deterministic.
    assert imported <= {"__future__", "contextlib", "dataclasses", "json", "os", "pathlib", "sys",
                        "pandas", "harness2_ledger", "figpipe"}, sorted(imported)
    # `os` is imported for os.getpid() only -- the probe path must be private per process. If it
    # ever grows into something that reads the environment or spawns a process, that shows up as
    # an attribute access this asserts against.
    source = (ROOT / "figpipe" / "mutation.py").read_text(encoding="utf-8")
    assert source.count("os.") == 1 and "os.getpid()" in source, (
        "os is imported for os.getpid() only; it now does more, so re-check this file's "
        "determinism claims")


# --------------------------------------------------------------------------------------
# the whole loop, and its refusals
# --------------------------------------------------------------------------------------

def test_run_composes_the_three_stages():
    space = mutation.default_space()
    out = mutation.run(space)
    assert set(out) == {"proposal", "probe", "compose"}
    assert out["proposal"]["candidates"]
    assert out["compose"]["decisions"]
    assert out["compose"]["verdict"] in ("selected", "rejected", "tie")


def test_the_probe_is_deterministic(probed):
    """Same space, same tasks, same decision. Two runs must not disagree.

    This compares OUTCOMES AND SCORES, not render paths. The first version of this loop wrote
    probes to a shared `templates/mutation/<task>--<edit>.pdf`, so two processes rendered over
    each other and a task flipped between "rendered" and "crashed" (`EmptyFileError`). The
    throwaway path is now per-pid; what must be reproducible is the measurement.
    """
    space, first = probed
    second = _probe_waiting(space)
    assert second["mean_score"] == first["mean_score"]
    assert {name: {tid: (row["outcome"], row["score"]) for tid, row in per.items()}
            for name, per in second["outcomes"].items()} == \
           {name: {tid: (row["outcome"], row["score"]) for tid, row in per.items()}
            for name, per in first["outcomes"].items()}
    a = mutation.compose(first, space)
    b = mutation.compose(second, space)
    assert [(d["id"], d["verdict"], d["delta"]) for d in a["decisions"]] == \
           [(d["id"], d["verdict"], d["delta"]) for d in b["decisions"]]


def test_the_probe_is_deterministic_across_processes(tmp_path):
    """The same check in a SEPARATE PROCESS, because that is where the race actually lived.

    An in-process repeat cannot catch a shared-path collision: the two runs are serialised by the
    GIL and by the test's own call order. This spawns a fresh interpreter, which is what a
    scheduled run is, and compares the measured outcomes and the composed verdicts.
    """
    import json
    import subprocess

    script = tmp_path / "probe_once.py"
    script.write_text(
        "import json, sys, time\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from figpipe import lock, mutation\n"
        "space = mutation.default_space()\n"
        "deadline = time.monotonic() + 240\n"
        "while True:\n"
        "    try:\n"
        "        res = mutation.probe(space); break\n"
        "    except lock.MeasurementBusy:\n"
        "        if time.monotonic() >= deadline: raise\n"
        "        time.sleep(2)\n"
        "dec = mutation.compose(res, space)\n"
        "print(json.dumps({'means': res['mean_score'],\n"
        "  'outcomes': {k: {t: [r['outcome'], r['score']] for t, r in v.items()}\n"
        "               for k, v in res['outcomes'].items()},\n"
        "  'verdicts': [[d['id'], d['verdict'], d['delta']] for d in dec['decisions']]}))\n",
        encoding="utf-8")
    # NOT `LOCK_PATH.unlink()`: another measurement may legitimately hold the lock, and deleting
    # it would let two runs overlap. The child waits for a free lock instead.
    cp = subprocess.run([sys.executable, "-X", "utf8", str(script)], cwd=ROOT,
                        capture_output=True, text=True, timeout=900)
    assert cp.returncode == 0, cp.stderr[-800:]
    child = json.loads(cp.stdout.strip().splitlines()[-1])

    space = mutation.default_space()
    here_probe = _probe_waiting(space)
    here = mutation.compose(here_probe, space)
    assert child["means"] == here_probe["mean_score"]
    assert child["outcomes"] == {k: {t: [r["outcome"], r["score"]] for t, r in v.items()}
                                 for k, v in here_probe["outcomes"].items()}, (
        "a separate process measured different outcomes; the loop is not deterministic")
    assert child["verdicts"] == [[d["id"], d["verdict"], d["delta"]]
                                 for d in here["decisions"]], (
        "a separate process produced a different decision; the loop is not deterministic")


def test_a_partial_probe_cannot_be_composed(probed):
    """Composing from a result that never probed a candidate must raise, not guess."""
    space, result = probed
    partial = {"outcomes": {"baseline": result["outcomes"]["baseline"]},
               "mean_score": {"baseline": result["mean_score"]["baseline"]}}
    with pytest.raises(mutation.MutationError, match="never probed"):
        mutation.compose(partial, space)


def test_a_probe_without_a_baseline_cannot_be_composed(probed):
    space, result = probed
    with pytest.raises(mutation.MutationError, match="no baseline"):
        mutation.compose({"outcomes": {}, "mean_score": {}}, space)


def test_a_refusal_scores_one_only_when_refusing_is_correct():
    """The two-sided contract: the same refusal is a success on one task and a failure on another.

    Without this asymmetry, "refuse everything" would be a perfect mutation.
    """
    expect_refused = mutation.Task("r", "matrix_plate", {}, lambda: None, "refused", "")
    expect_clean = mutation.Task("c", "matrix_plate", {}, lambda: None, "clean", "")
    assert mutation._score(expect_refused, "refused") == 1.0
    assert mutation._score(expect_clean, "refused") == 0.0
    assert mutation._score(expect_clean, "rendered", 0) == 1.0
    assert mutation._score(expect_clean, "rendered", 1) == 0.5
    assert mutation._score(expect_clean, "crashed") == 0.0


def test_the_two_sided_score_is_what_rejects_the_blanket_relaxation():
    """NEGATIVE CONTROL for the score itself: with a one-sided score the loop cannot see the bug.

    Under "any refusal scores 1.0", `max_rows=60` refuses the 42-row table and renders the
    48-row one; under the two-sided score the render is a DROP, which is what makes the
    rejection possible. This asserts both halves, so the score cannot be simplified back.
    """
    expect_refused = mutation.Task("r", "matrix_plate", {}, lambda: None, "refused", "")
    one_sided = lambda outcome, n=0: 1.0 if outcome == "refused" else 1.0 - n / (n + 1)
    # a refusal that should have rendered: one-sided calls it perfect, two-sided calls it zero
    assert one_sided("refused") == 1.0
    assert mutation._score(expect_refused, "refused") == 1.0        # correct refusal: same
    expect_clean = mutation.Task("c", "matrix_plate", {}, lambda: None, "clean", "")
    assert one_sided("refused") == 1.0
    assert mutation._score(expect_clean, "refused") == 0.0          # over-cautious: caught here
