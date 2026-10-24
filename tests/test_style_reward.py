"""The loop's reward must have resolution. Round 101 gave it some.

WHY THIS EXISTS
    `mutation._render_score(hard_failures)` returns 1.0 whenever nothing hard failed, and nothing
    hard fails for any task in the pool:

        hard_failures = 0 : 139 of 139 tasks
        reward = 1.0      : one distinct value

    So every candidate tied with every other, the loop recorded 222 ties over 152 runs, and the
    official score's seven moves in five days were all made by a human reading dimension tables.

    Round 101 added `style_score`: `run_task` compares the rendered figure against the reference the
    task declares, using the benchmark's own style profile comparison. It is REPORTED SEPARATELY from
    `score` -- merging two questions into one number is how a reward stops being legible.

THE MEASUREMENT THIS FILE PINS
    A style candidate must move the aggregate. If it does not, the reward is still flat and the loop
    is still blind, whatever the code says it measures.
"""
from __future__ import annotations

import copy
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")


@pytest.fixture(scope="module")
def style_probe():
    """One reference figure and one style candidate that should beat it."""
    from figpipe import mutation, skills, styleprofile

    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": np.arange(12), "y": rng.random(12)})
    import tempfile
    out = pathlib.Path(tempfile.mkdtemp(prefix="style-reward-"))
    ref = skills.run("trend_with_uncertainty", df, out_stem=out / "ref", x="x", y="y")
    prof = styleprofile.StyleProfile.from_pdf(ref["pdf"])
    # a candidate profile: every measured text size bumped by half a point
    bumped = copy.deepcopy(prof)
    bumped.sizes_pt = [s + 0.5 for s in bumped.sizes_pt]
    task = mutation.Task(
        id="style-as-is", skill="styled_trend",
        params={"x": "x", "y": "y", "profile": prof},
        data=lambda: df.copy(), expect="clean",
        why="a style probe: the reference's own figure is the target",
        reference_pdf=ref["pdf"],
    )
    space = mutation.MutationSpace(
        candidates=(mutation.Candidate(
            id="sizes-plus-half", operator="style", parameter="profile",
            baseline_value=prof, value=bumped,
            rationale="a half-point bump on every measured text size", skill="styled_trend"),),
        tasks=(task,), min_margin=0.01,
    )
    return mutation, space


def test_the_refusal_reward_is_flat_on_this_task_set(style_probe):
    """THE DEFECT, pinned. If this ever stops being flat, the round-101 change may be redundant."""
    mutation, space = style_probe
    result = mutation.probe(space, budget=10)
    values = set(result["mean_score"].values())
    assert values == {1.0}, (
        f"the refusal reward is no longer flat ({values}); the style aggregate may be unnecessary")


def test_a_style_candidate_moves_the_style_aggregate(style_probe):
    """THE FIX. A half-point text-size change must be visible to the aggregate."""
    mutation, space = style_probe
    result = mutation.probe(space, budget=10)
    style = result.get("mean_style") or {}
    assert style, "no mean_style aggregate: the loop cannot see style at all"
    assert "baseline" in style and "sizes-plus-half" in style, style
    assert style["sizes-plus-half"] > style["baseline"], (
        f"a style candidate did not improve the style aggregate: {style}")


def test_compose_uses_the_style_aggregate_and_says_so(style_probe):
    """A TIE ON A FLAT AGGREGATE MEANS "cannot see", NOT "no difference". The decision must name the
    aggregate it used, or a reader cannot tell those apart."""
    mutation, space = style_probe
    result = mutation.probe(space, budget=10)
    decision = mutation.compose(result, space)
    assert decision.get("aggregate") == "mean_style", (
        f"compose decided on {decision.get('aggregate')!r}, which has no resolution on this task set")
    assert decision["selected"] == ["sizes-plus-half"], decision
    assert decision["verdict"] == "selected"


def test_a_non_scalar_override_gets_a_path_safe_artefact_name():
    """THE CRASH. A StyleProfile's repr contains characters Windows rejects, so the artefact path was
    illegal and the candidate was scored as `crashed` -- a total failure that never rendered."""
    from figpipe import mutation
    from figpipe import styleprofile

    prof = styleprofile.StyleProfile(source="test", region="r", modality="pdf")
    task = mutation.Task(id="t", skill="x", params={}, data=lambda: pd.DataFrame(),
                         expect="clean", why="w")
    stem = mutation._probe_stem(task.id, {"profile": prof})
    # the FILENAME, not the whole path: `E:\` contains a colon and always will
    name = stem.name
    for bad in ('<', '>', ':', '"', '|', '?', '*'):
        assert bad not in name, f"the artefact filename still contains {bad!r}: {name}"
    assert "StyleProfile" in name, (
        f"a non-scalar override should still be identifiable in the name: {name}")


def test_a_scalar_override_still_names_itself():
    """THE OTHER DIRECTION: the fix must not hide what a layout candidate changed."""
    from figpipe import mutation
    task = mutation.Task(id="t", skill="x", params={}, data=lambda: pd.DataFrame(),
                         expect="clean", why="w")
    stem = str(mutation._probe_stem(task.id, {"max_bars": 24}))
    assert "max_bars=24" in stem, stem
