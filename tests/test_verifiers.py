"""The verification layer must catch planted defects and produce no false positives.

WHY THIS TEST
    LOGICAL_AUDIT.md names the verification layer as the project's highest-risk area. `audit` and
    `composite` are what everything else trusts, and until now they had only been tested on good
    figures -- a verifier tested only on correct input has not been tested at all.

    A verifier fails in two directions, and both are defects:
      * FALSE NEGATIVE -- it certifies broken output
      * FALSE POSITIVE -- it teaches its users to ignore it

    The sweep plants each defect the project exists to catch (sub-5pt text, wrong width, Type-3
    fonts, a real glyph collision) and asserts it is caught; then asserts a correct figure passes
    and that rotated tick labels are NOT reported as collisions.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_verifiers.py"


def test_the_verification_layer_catches_planted_defects():
    if not SCRIPT.is_file():
        pytest.skip("verifier audit absent")
    cp = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True,
                        text=True, timeout=900)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert "BROKEN" not in cp.stdout, (
        "the verification layer has a defect:\n" + cp.stdout[-3000:])
    # and it must actually have run the cases, not skipped them
    assert "13 verifier cases" in cp.stdout, cp.stdout[-1500:]
    assert "ok=13" in cp.stdout, cp.stdout[-800:]


def test_audit_catches_sub_5pt_text():
    """The defect this whole project exists to catch must never pass unnoticed."""
    sys.path.insert(0, str(ROOT))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figpipe import audit, layout, style
    out = ROOT / "examples" / "output" / "verifiers"
    out.mkdir(parents=True, exist_ok=True)
    style.apply()
    fig, _, _ = layout.figure(columns=2.0, height_mm=60.0)
    ax = fig.add_subplot(111)
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("tiny", fontsize=4.0)
    pdf = pathlib.Path(layout.save(fig, out / "_sub5")[0])
    rep = audit.audit(pdf, expect_width_mm=183.0, check_overlap=False)
    assert any(f["check"] == "font_size" for f in rep["findings"]), rep["findings"]


def test_composite_refuses_overlapping_cells():
    sys.path.insert(0, str(ROOT))
    import numpy as np
    import pandas as pd
    from figpipe import composite
    df = pd.DataFrame({"x": np.arange(8.0), "y": np.linspace(0, 1, 8)})

    def panel(at):
        return composite.Panel("trend_band", df, {"x": "x", "y": "y"}, at=at)

    with pytest.raises(ValueError, match="overlap"):
        composite.composite([panel((0, 0)), panel((0, 0))], columns=2.0, height_mm=80.0)
