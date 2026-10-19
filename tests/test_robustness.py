"""Adversarial inputs must be refused or handled correctly -- never silently wrong.

WHY THIS TEST
    The last four rounds of fixes all landed in styleprofile / codegen / select, and none of those
    modules had been run against inputs that are not the benchmark's. That is exactly how the matrix
    pivot regression happened. This sweep is the systematic version, and it immediately found two
    fabricated claims:

      * a solid-black and a pure-noise image reported FOUR SPINES, because np.convolve(mode="same")
        divides by the full kernel even where it runs off the ends, so the first and last few
        entries of a UNIFORM signal look like high contrast (measured 0.444). A blank page claimed
        structure it does not have.
      * a non-finite `figure_aspect` emitted `figsize=(7.2047, nan)` -- a script that cannot render,
        reported as a success.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_robustness.py"


def test_no_module_is_broken_by_adversarial_input():
    if not SCRIPT.is_file():
        pytest.skip("robustness audit absent")
    cp = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True,
                        text=True, timeout=900)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert "BROKEN" not in cp.stdout, (
        "an adversarial input produced a silently wrong result:\n" + cp.stdout[-3000:])


def test_a_blank_image_claims_no_structure():
    """The edge artefact of np.convolve made a uniform image report four spines."""
    sys.path.insert(0, str(ROOT))
    import numpy as np
    from PIL import Image
    from figpipe import styleprofile
    out = ROOT / "examples" / "output" / "robustness"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "_blank_probe.png"
    Image.fromarray(np.full((120, 160, 3), 255, np.uint8)).save(path)
    prof = styleprofile.StyleProfile.from_image_detailed(path)
    assert prof.spines == {} or not any(prof.spines.values()), prof.spines
    assert prof.rules_h == 0 and prof.rules_v == 0
    assert prof.tick_direction is None


def test_a_non_finite_aspect_is_refused_not_emitted():
    sys.path.insert(0, str(ROOT))
    import numpy as np
    import pandas as pd
    from figpipe import codegen, composite
    df = pd.DataFrame({"x": np.arange(10.0), "y": np.linspace(0, 1, 10)})
    panel = composite.Panel("trend_band", df, {"x": "x", "y": "y", "fit": "lm"})
    for bad in (float("nan"), float("inf"), 0.0, -1.5, "wide"):
        with pytest.raises(codegen.CodegenError):
            codegen.emit([panel], style={"figure_aspect": bad})
