"""Tests for code-patch candidates and fix-contribution measurement.

WHY THIS EXISTS
    The mutation loop's Candidate is (operator, parameter, value) and run_task applies it as
    params.update({parameter: value}). Measured over 152 runs: 4 knowledge changes, 222 ties, 149
    runs that selected NOTHING -- because every real fix this project made was a DRAWER CHANGE that
    no parameter value can express.

    patchprobe makes a declared textual edit a probe-able candidate. These tests pin the safety
    properties that let it run unattended, and the two-direction state that makes a catalogue entry
    honest.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import patchprobe, proposals  # noqa: E402


def _patch(**kw) -> patchprobe.Patch:
    base = {"id": "t", "path": "figpipe/drawlib.py",
            "old": "POLAR_LABEL_WRAP = 10", "new": "POLAR_LABEL_WRAP = 99",
            "rationale": "test"}
    base.update(kw)
    return patchprobe.Patch(**base)


# ---------------------------------------------------------------------------------------
# Safety: the four guards that let this run unattended
# ---------------------------------------------------------------------------------------

def test_an_unambiguous_patch_applies():
    ok, why = patchprobe.patch_applies(ROOT, _patch())
    assert ok, why


def test_an_ambiguous_patch_is_REFUSED():
    """A replacement that matches twice would edit whichever place str.replace reaches first."""
    ok, why = patchprobe.patch_applies(ROOT, _patch(old="def ", new="def  "))
    assert not ok
    assert "times" in why or "ambiguous" in why


def test_an_absent_patch_is_REFUSED():
    ok, why = patchprobe.patch_applies(ROOT, _patch(old="THIS TEXT IS NOT IN THE FILE"))
    assert not ok
    assert "not present" in why


def test_a_path_escape_is_REFUSED():
    ok, why = patchprobe.patch_applies(ROOT, _patch(path="../../../etc/passwd"))
    assert not ok
    assert "escapes" in why


def test_a_crash_mid_probe_still_reverts():
    """THE `finally` IS THE POINT: an unattended loop must not leave a source file edited."""
    target = ROOT / "figpipe" / "drawlib.py"
    before = target.read_text(encoding="utf-8")

    def boom():
        raise RuntimeError("probe crashed")

    with pytest.raises(RuntimeError):
        patchprobe.probe_with_patch(ROOT, _patch(), boom)
    assert target.read_text(encoding="utf-8") == before, (
        "a crashed probe left the source file edited")


def test_a_successful_probe_also_reverts():
    target = ROOT / "figpipe" / "drawlib.py"
    before = target.read_text(encoding="utf-8")
    assert patchprobe.probe_with_patch(ROOT, _patch(), lambda: "ok") == "ok"
    assert target.read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------------------
# The catalogue must be honest about which direction it applies
# ---------------------------------------------------------------------------------------

def test_a_fix_already_in_the_tree_reads_as_REVERT():
    """A patch that fixes a defect already fixed cannot apply -- and that is the right failure.

    The catalogue must distinguish `fix` (the defect is present) from `revert` (the fix is in, so
    applying it reintroduces the defect to measure the fix). Recording only one direction made the
    catalogue report `applies=False` for its own example, which reads as broken rather than fixed.
    """
    entry = {"id": "polar_label_overflow", "path": "figpipe/drawlib.py",
             "old": "            ax.set_xticklabels(labels, fontsize=6)",
             "new": "            ax.set_xticklabels([_wrap_spoke(v) for v in labels], fontsize=6)",
             "rationale": "polar label overflow"}
    state = proposals.patch_state(ROOT, entry)
    assert state["state"] in ("fix", "revert", "stale")
    if state["state"] == "revert":
        # the fix is in the tree, so the reported patch must be the REVERSE of the catalogue entry
        assert state["patch"]["old"] == entry["new"]
        assert state["patch"]["new"] == entry["old"]


def test_a_finding_with_no_declared_patch_is_reported():
    """The defects the loop cannot express must be SAID, not dropped."""
    result = proposals.patches_for([{"check": "a_defect_with_no_patch"}])
    assert result["n"] == 0
    assert result["n_missing"] == 1
    assert "no declared code patch" in result["missing"][0]["why"]


def test_every_catalogued_patch_is_applicable_in_one_direction():
    """A catalogue entry that applies in NEITHER direction is stale and must be noticed."""
    for key, (path, old, new, rationale) in proposals.CODE_PATCHES.items():
        entry = {"id": key, "path": path, "old": old, "new": new, "rationale": rationale}
        state = proposals.patch_state(ROOT, entry)
        assert state["state"] in ("fix", "revert"), (
            f"{key} applies in neither direction -- the catalogue entry no longer describes this "
            f"tree: {state['why']}")


def test_the_contribution_script_exists_and_reports_a_file():
    script = ROOT / "scripts" / "measure_fix_contribution.py"
    assert script.is_file(), (
        "nothing measures whether a fix was load-bearing; a fix that changes no metric is either "
        "unexercised by the benchmark or not a fix")
    src = script.read_text(encoding="utf-8")
    assert "load_bearing" in src
    assert "probe_with_patch" in src
