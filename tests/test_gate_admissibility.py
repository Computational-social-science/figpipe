"""A CLOSED verdict is only admissible if the gate has been shown able to reject anything.

WHY THIS EXISTS
    BootLoops' standard, which `gate.py` quotes in its own docstring:

        CLOSED only if every dimension passed AND the controls fired.

    The module separates the two, for a real reason: `run_gate` never sets controls, so folding them
    into `close()` made EVERY gate OPEN -- including one whose every check passed. A verdict that
    cannot be reached is as meaningless as one that is always reached.

    But the separation left a hole. Measured: a figure could be judged while the controls had never
    run in this process, and the certificate said only "OPEN" or "CLOSED" with `controls: {}`. That
    is exactly "the gate that cannot fail" -- the first failure mode BootLoops names and the one
    this project kept skipping.

    The fix is NOT to fold controls back into `close()`; that re-creates the unreachable verdict.
    It is to make the CERTIFICATE state whether the mechanism behind the verdict was ever exercised,
    and to mark a CLOSED verdict INADMISSIBLE when it was not.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import gate  # noqa: E402


def _closed_gate() -> gate.Gate:
    """A gate that closes on a dimension nobody controls -- the thing being guarded against."""
    g = gate.declare("synthetic")
    g.add("invented_dimension", 1, ">= 1", True, "this check exists only to close the gate")
    g.close()
    return g


def test_a_closed_gate_with_no_controls_is_INADMISSIBLE():
    """THE LOAD-BEARING CASE. A CLOSED verdict nobody has seen fail certifies nothing."""
    d = _closed_gate().to_dict()
    assert d["verdict"] == gate.CLOSED
    assert d["controls_exercised"] is False
    assert d["admissible"] is False, (
        "a CLOSED verdict from a gate with no recorded control run was marked admissible; that is "
        "the gate that cannot fail")


def test_a_closed_gate_with_controls_recorded_is_admissible():
    """NEGATIVE CONTROL: the field must not always be False, or it carries no information."""
    g = _closed_gate()
    g.controls["gate_can_fire"] = True
    d = g.to_dict()
    assert d["verdict"] == gate.CLOSED
    assert d["controls_exercised"] is True
    assert d["admissible"] is True


def test_an_open_gate_is_admissible_without_controls():
    """An OPEN verdict does not depend on the controls: it claims nothing passed.

    `admissible` means "this verdict may be relied on", and "OPEN" is always a claim one may rely
    on -- it asserts a failure. Only a positive claim needs the mechanism behind it to be shown.
    """
    g = gate.declare("synthetic-open")
    g.add("invented_dimension", 0, ">= 1", False, "deliberately failing")
    g.close()
    d = g.to_dict()
    assert d["verdict"] == gate.OPEN
    assert d["admissible"] is True


def test_the_empty_gate_still_cannot_pass():
    """An empty gate is OPEN -- unchanged, and still the reason the controls are separate."""
    g = gate.declare("empty")
    assert g.close() == gate.OPEN
    assert g.to_dict()["verdict"] == gate.OPEN


def test_validate_records_its_outcome_for_later_verdicts(tmp_path):
    """`validate()` is the only thing that can show the gate can fire; it must leave a trace."""
    result = gate.validate(tmp_path)
    assert result["gate_can_fire"] is True
    assert gate._CONTROL_STATE["validated"] is True, (
        "validate() ran the controls but recorded nothing, so a later verdict cannot cite them")
    assert gate._CONTROL_STATE["gate_can_fire"] is True


def test_run_gate_carries_the_control_state_onto_the_certificate(tmp_path):
    """A figure's certificate must say whether the mechanism behind it was exercised."""
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import pandas as pd
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": np.arange(10.0), "y": rng.random(10)})
    panel = composite.Panel("scatter_fit", df, {"x": "x", "y": "y"})
    fig = composite.composite([panel], columns=2.0, height_mm=80.0, letters=False)
    paths = layout.save(fig, tmp_path / "fig")
    g = gate.run_gate(paths[0])
    assert g.controls.get("gate_can_fire") is True, (
        "run_gate did not carry the validated control state onto the certificate")
    assert g.controls.get("validated_at")
