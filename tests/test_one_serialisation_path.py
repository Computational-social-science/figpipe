"""A fix applied at one of three call sites is not a fix.

WHY THIS EXISTS
    Round 102 added style candidates whose `value` is a `StyleProfile`. That broke the mutation loop
    in THREE separate places, and I fixed them one at a time across two rounds:

        place                          failure
        figpipe/mutation.py propose()   dict item 'value'
        scripts/mutate.py record        dict item 'proposed'
        figpipe/mutation.py compose()   dict item 'decisions'

    Each was found by running the thing, not by looking for the shape. Between the first fix and the
    last, FOUR CONSECUTIVE SCHEDULED RUNS had the loop dead while every one reported `ok = True`.

THE RULE THIS FILE DEFENDS
    Every place a candidate's `value` or `baseline_value` enters a record must go through ONE
    predicate. If a fourth site is ever added without it, this test should fail rather than a
    scheduled run dying quietly.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MUTATION = ROOT / "figpipe" / "mutation.py"
MUTATE = ROOT / "scripts" / "mutate.py"


@pytest.fixture(scope="module")
def space():
    from figpipe import mutation
    return mutation.default_space()


def test_the_three_known_records_serialise(space):
    """ALL THREE, in one place, so a regression in any of them is one failure not three surprises."""
    from figpipe import mutation

    proposal = mutation.propose(space)
    json.dumps(proposal)

    # the shape scripts/mutate.py builds
    hand_built = [{**c.to_dict(), "rationale": c.rationale} for c in space.candidates]
    json.dumps(hand_built)

    # compose's decisions need a probe; a dry compose over an empty outcome map is not possible, so
    # exercise the decision builder through the real path with a tiny space
    import tempfile
    out = pathlib.Path(tempfile.mkdtemp(prefix="three-")) / "p.json"
    result = mutation.probe(space, out_dir=out)
    decision = mutation.compose(result, space)
    json.dumps(decision, default=str)
    # and WITHOUT the default escape hatch, because that is what the runner does
    json.dumps({k: v for k, v in decision.items() if k != "ledger"})


def test_no_record_reads_a_candidate_value_raw():
    """THE MECHANISM. A `"value": c.value` in a record is the defect; it must be `_plain(...)`."""
    src = MUTATION.read_text(encoding="utf-8")
    # a record assignment that reads the raw attribute
    offenders = []
    for m in re.finditer(r'"(value|baseline_value)":\s*(?:c|cand)\.(value|baseline_value)', src):
        line_no = src[:m.start()].count("\n") + 1
        offenders.append(f"mutation.py:{line_no}")
    assert not offenders, (
        f"a record reads a candidate value raw (it will fail on a StyleProfile): {offenders}")

    # STRIP COMMENTS FIRST. The module documents the defect it fixed by quoting `"value": c.value`,
    # and a plain substring search matches that comment -- a search over text where the property is
    # about code.
    mutate_code = "\n".join(line.split("#")[0]
                            for line in MUTATE.read_text(encoding="utf-8").splitlines())
    assert '"value": c.value' not in mutate_code, (
        "scripts/mutate.py builds the record by hand again; it must use Candidate.to_dict()")


def test_the_summary_is_used_for_non_scalars_only(space):
    """A LAYOUT candidate must not be wrapped: a reader comparing 12 with 24 should not unwrap."""
    from figpipe import mutation
    proposal = mutation.propose(space)
    for c in proposal["candidates"]:
        if c["parameter"] in ("max_bars", "max_rows"):
            assert isinstance(c["value"], int), (c["id"], c["value"])
        if c["parameter"] == "profile":
            assert isinstance(c["value"], dict), (c["id"], type(c["value"]))
            assert c["value"].get("__type__") == "StyleProfile", c["value"]


def test_the_runner_records_mutation_health():
    """A FAILURE NOBODY SEES IS NOT A FINDING. Four runs were dead and every one said ok = True."""
    src = (ROOT / "scripts" / "cron_run.py").read_text(encoding="utf-8")
    assert '"mutation_ok"' in src, (
        "cron_run does not record whether the mutation loop ran; a dead loop is invisible")
    assert "MUTATION DID NOT RUN" in src, (
        "cron_run does not PRINT the mutation failure; opening the JSON must not be required")
