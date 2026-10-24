"""A candidate's value must survive the trip into the run record.

WHY THIS EXISTS
    Round 102 added style candidates whose `value` is a `StyleProfile`. `Candidate.to_dict()` was
    `dataclasses.asdict(self)`, which copies that object verbatim, and `json.dumps` then refused it:

        TypeError: Object of type StyleProfile is not JSON serializable
        when serializing dict item 'value'

    `cron_run` caught the exception, recorded `mutation.ran = False`, and the loop did not run for
    FOUR CONSECUTIVE SCHEDULED RUNS -- while every one of them reported `ok = True`. The failure lived
    inside a block nobody was reading, and the run still looked healthy.

    That is the defect this project records most often in a new costume: **a failure that is caught,
    recorded, and then not surfaced.**

WHY THE SUMMARY IS NOT A REPR
    `dataclasses.asdict` RECURSES into nested dataclasses, so a `StyleProfile` arrives already
    flattened to a dict. My first fix checked `isinstance(v, dict)` and summarised it as
    `__type__: dict` -- it stopped crashing while still losing the one fact that distinguishes a
    style candidate from a layout one. The fix reads the ORIGINAL attribute, before `asdict` runs.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def space():
    from figpipe import mutation
    return mutation.default_space()


def test_propose_is_json_serialisable(space):
    """THE CRASH. This is what made cron_run record `mutation.ran = False`."""
    from figpipe import mutation
    proposal = mutation.propose(space)
    json.dumps(proposal)          # raises TypeError if any value is not plain data


def test_a_style_candidate_reports_its_type_not_dict(space):
    """THE SECOND DEFECT. `asdict` flattens a nested dataclass before the check sees it."""
    from figpipe import mutation
    proposal = mutation.propose(space)
    style = [c for c in proposal["candidates"] if isinstance(c["value"], dict)
             and c["value"].get("__type__") == "StyleProfile"]
    assert style, (
        "no candidate reports __type__ == 'StyleProfile'; a style candidate's value is being "
        f"flattened or dropped: {[c['value'] for c in proposal['candidates']]}")
    # and the summary must carry what distinguishes it
    summary = style[0]["value"]
    assert "sizes_pt" in summary, summary
    assert isinstance(summary["sizes_pt"], list), summary


def test_a_layout_candidate_keeps_a_plain_scalar(space):
    """THE OTHER DIRECTION. A layout candidate's value must not be wrapped for no reason -- a reader
    comparing 12 with 24 must not have to unwrap a dict."""
    from figpipe import mutation
    proposal = mutation.propose(space)
    scalars = [c for c in proposal["candidates"] if c["parameter"] in ("max_bars", "max_rows")]
    assert scalars, "no layout candidate in the default space"
    for c in scalars:
        assert isinstance(c["value"], int), (c["id"], c["value"])


def test_the_whole_loop_serialises(space):
    """A decision that cannot be written down is not a decision the runner can record."""
    import tempfile
    from figpipe import mutation
    out = pathlib.Path(tempfile.mkdtemp(prefix="serialise-")) / "probe.json"
    result = mutation.probe(space, out_dir=out)
    decision = mutation.compose(result, space)
    json.dumps(decision, default=str)


def test_a_value_summary_survives_asdict_flattening():
    """THE MECHANISM, isolated. `dataclasses.asdict` on a Candidate whose value is a dataclass
    flattens the value; `to_dict` must not be fooled by that."""
    from figpipe import mutation, styleprofile

    prof = styleprofile.StyleProfile(source="t", region="r", modality="pdf")
    cand = mutation.Candidate(id="c", operator="style.profile", parameter="profile",
                              baseline_value=prof, value=prof, rationale="r", skill="styled_trend")
    flattened = dataclasses.asdict(cand)
    assert isinstance(flattened["value"], dict), (
        "asdict no longer recurses; the guard this test exists for may be unnecessary")
    out = cand.to_dict()
    assert isinstance(out["value"], dict)
    assert out["value"].get("__type__") == "StyleProfile", out["value"]
