"""A patch candidate must produce the same probe shape `compose` already reads.

WHY THIS EXISTS
    Round 65 made a fix probe-able (`patchprobe`) and measured one fix's contribution by hand. The
    loop could not yet PROPOSE a patch: `mutation.probe` applies an override PER TASK
    (`params.update({parameter: value})`) and a patch edits the SOURCE, so the apply/restore
    discipline is different and cannot be a flag on the same function.

    `mutation.probe_patch` produces the SAME shape `compose` reads -- `outcomes`, `mean_score` --
    so the decision rule needs no second code path. A second path is where two implementations
    drift apart.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import mutation, patchprobe  # noqa: E402


class _PatchCandidate:
    """The minimum `compose` needs from a candidate: an id and a skill."""

    id = "fake"
    skill = "__patch__"


class _FakePatch:
    id = "fake"

    def to_dict(self):
        return {"id": "fake", "path": "x", "old": "a", "new": "b", "rationale": "test"}


def test_a_patch_probe_produces_the_shape_compose_reads():
    """THE CONTRACT: `compose` reads `outcomes` and `mean_score`. Nothing else."""
    result = mutation.probe_patch(
        _FakePatch(), tasks=["t1", "t2"],
        baseline_runner=lambda: {"t1": {"score": 1.0}, "t2": {"score": 0.5}},
        patched_runner=lambda: {"t1": {"score": 0.0}, "t2": {"score": 0.5}},
    )
    assert "outcomes" in result and "mean_score" in result
    assert set(result["outcomes"]) == {"baseline", "fake"}
    assert result["mean_score"]["baseline"] == pytest.approx(0.75)
    assert result["mean_score"]["fake"] == pytest.approx(0.25)
    assert result["patch"]["id"] == "fake"


def test_compose_can_judge_a_patch_probe():
    """The decision rule must accept a patch probe without a second code path.

    THE SPACE MUST MATCH WHAT WAS PROBED. `compose` refuses to decide from a partial probe --
    "candidate 'split-max-bars-24' was proposed but never probed" -- which is the project's own
    completeness guard doing its job. A patch probe therefore needs a space that names its own
    candidate, and that is what the caller builds.
    """
    # THE ROWS MUST CARRY `outcome`, because that is what `compose` reads to tell a refusal from a
    # render. A stub with only `score` raised KeyError: 'outcome' -- the contract is the ROW SHAPE,
    # not just the top-level keys.
    result = mutation.probe_patch(
        _FakePatch(), tasks=["t1"],
        baseline_runner=lambda: {"t1": {"score": 1.0, "outcome": "rendered"}},
        patched_runner=lambda: {"t1": {"score": 0.0, "outcome": "rendered"}},
    )
    # a one-candidate space, matching exactly what was probed. `MutationSpace` is FROZEN, so the
    # candidate goes in at construction -- assigning after the fact raises FrozenInstanceError,
    # which is the dataclass doing its job.
    space = mutation.MutationSpace(candidates=[_PatchCandidate()], tasks=[],
                                   min_margin=0.1, min_score=None)
    verdict = mutation.compose(result, space)
    assert "fake" not in verdict["selected"], (
        "a patch that scores worse than the baseline was selected")
    # THE DECISION DICT KEYS THE CANDIDATE AS `id`. `compose` records
    #   {"id": cand.id, "operator": ..., "kind": "patch"/"scalar", ...}
    # so filtering on "candidate" found nothing and the test read that as "no decision".
    decided = [d for d in verdict["decisions"] if d.get("id") == "fake"]
    assert decided, (
        f"compose produced no decision for the patch candidate; it returned {list(verdict)}")


class _PatchCandidate:
    """The minimum `compose` needs from a candidate: an id and a skill."""

    id = "fake"
    skill = "__patch__"

def test_a_patch_probe_never_leaves_the_tree_edited():
    """The source must be restored whether the runner succeeds or raises."""
    target = ROOT / "figpipe" / "drawlib.py"
    before = target.read_text(encoding="utf-8")
    patch = patchprobe.Patch(
        id="tmp", path="figpipe/drawlib.py",
        old="POLAR_LABEL_WRAP = 10", new="POLAR_LABEL_WRAP = 99", rationale="test")

    def boom():
        raise RuntimeError("probe crashed")

    with pytest.raises(RuntimeError):
        patchprobe.probe_with_patch(ROOT, patch, boom)
    assert target.read_text(encoding="utf-8") == before


def test_probe_patch_does_not_import_patchprobe():
    """The dependency points ONE WAY: mutation must not import patchprobe.

    The caller supplies the runners, so `mutation` stays testable with stubs and a patch probe
    cannot acquire a hidden dependency on the filesystem.

    CHECK THE IMPORTS, NOT THE SOURCE TEXT. The first version asserted the string `patchprobe` was
    absent from the function source -- and the DOCSTRING explains why it is not imported, so the
    word appears there. A test that fails on its own explanation is testing the wrong thing.
    """
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(mutation.probe_patch).lstrip())
    fn = tree.body[0]
    imported: list[str] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("patchprobe" in name for name in imported), (
        f"probe_patch imports patchprobe ({imported}); the caller should supply the runners")
