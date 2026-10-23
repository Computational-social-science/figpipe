"""The schedule must record patch candidates, and must not claim to have measured them.

WHY THIS EXISTS
    Three rounds of diagnosis converged on one sentence: the loop's discovery channel is five budget
    integers, so it cannot discover a drawer fix. `patchprobe` can apply one, `probe_patch` can
    score it -- but nothing joined them to the scheduled run.

    This file pins the join AND the honesty of it. The first version set `probed=True` as soon as a
    patch was eligible, before any measurement ran: a field named `probed` reporting a probe that
    never happened. That is the "a control that looks present and does nothing" defect in its
    purest form.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def cron():
    import cron_run
    return cron_run


def test_the_schedule_records_patch_candidates(cron):
    """THE JOIN: mutation_step must see the catalogue, not only the fixed menu."""
    result = cron.mutation_step()
    assert "patch_catalogue" in result, (
        "mutation_step does not record patch candidates, so the loop still cannot see a drawer fix")
    assert result.get("n_patch_candidates", 0) >= 1, (
        "the catalogue is not empty, so the schedule should see at least one candidate")


def test_eligible_is_not_probed(cron):
    """A PATCH IS NOT PROBED BY THE SCHEDULE -- the probe needs the pool lock and minutes.

    Reporting `probed: True` for a patch the schedule did not measure is exactly the defect this
    project has recorded a dozen times: a field that says a check ran when it did not.
    """
    result = cron.mutation_step()
    catalogue = result.get("patch_catalogue") or []
    if not catalogue:
        pytest.skip("no patch candidates")
    for entry in catalogue:
        if entry.get("eligible"):
            assert entry.get("probed") is False, (
                f"{entry['patch']} reports probed=True, but the schedule does not run the probe")
            assert "measure_fix_contribution" in str(entry.get("how", "")), (
                f"{entry['patch']} does not say how its contribution is measured")


def test_the_counts_are_separate(cron):
    result = cron.mutation_step()
    assert "n_patch_eligible" in result
    assert "n_patch_probed" in result
    assert result["n_patch_probed"] <= result["n_patch_eligible"]


def test_a_patch_is_never_auto_selected(cron):
    """THE POSTURE: the loop measures and reports; it does not edit its own drawer unattended."""
    result = cron.mutation_step()
    note = str(result.get("patch_note", ""))
    assert "never auto-selected" in note or "human" in note, (
        "the record does not state that a patch is never auto-selected; an unattended loop editing "
        "its own source is a different project")


def test_the_catalogue_is_readable_from_the_schedule(cron):
    """A failure to read the catalogue must be reported, not swallowed."""
    import inspect
    src = inspect.getsource(cron.mutation_step)
    assert "ImportError" in src or "AttributeError" in src, (
        "a catalogue read failure is not classified, so it would crash the run or vanish")
