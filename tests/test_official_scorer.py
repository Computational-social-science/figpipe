"""The OFFICIAL scorer must run, and our emitted code must score against it.

WHY THESE TESTS
    PlotTwin-Bench's official score is `S = 0.35 * S_code + 0.65 * S_vision`. This project can only
    run the deterministic code channel, so the honest claim is "code channel", never "combined
    score". These tests pin three things:

      1. the vendored scorer is the real one and gives 100 for identical code, <100 for deviations
      2. figpipe can EMIT code that the scorer accepts (otherwise the official channel is
         unreachable, which was the actual state before this module)
      3. the emitted code actually renders -- a script the scorer accepts but matplotlib rejects
         would be a score for a figure that does not exist
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "third_party"))

scorer = pytest.importorskip("plottwin_scorer", reason="official scorer not vendored")
codegen = pytest.importorskip("figpipe.codegen", reason="codegen absent")
from figpipe import composite  # noqa: E402

TREND = pd.DataFrame({"year": np.arange(1990, 2014),
                      "value": 0.1 + 0.008 * np.arange(24)})


def _panel():
    return composite.Panel("trend_band", TREND,
                           {"x": "year", "y": "value", "fit": "lm", "reference": 0.5,
                            "xlabel": "Year", "ylabel": "z-score"})


def test_the_vendored_scorer_is_the_real_one():
    assert scorer.DEVIATION_DEFECT_SCORE_VERSION == "deviation-defect-v1"
    code = ("import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots(figsize=(3.6, 2.4))\n"
            "ax.plot([1, 2, 3], [1, 2, 3], color='#0072b2', linewidth=1.2)\n"
            "ax.grid(False)\n")
    same = scorer.score_code_deviation(code, code)
    assert same["available"] is True
    assert same["score"] == pytest.approx(100.0)
    worse = scorer.score_code_deviation(
        code, code.replace("#0072b2", "#d55e00").replace("linewidth=1.2", "linewidth=0.4"))
    assert worse["score"] < 100.0


def test_figpipe_can_emit_code_the_official_scorer_accepts(tmp_path):
    script = codegen.write([_panel()], tmp_path / "candidate.py", columns=2.0,
                           height_mm=90.0)
    text = script.read_text(encoding="utf-8")
    assert "matplotlib" in text and "savefig" in text
    reference = text                      # a perfect candidate is its own reference
    res = scorer.score_code_deviation(reference, text)
    assert res["available"] is True
    assert res["score"] == pytest.approx(100.0)


def test_the_emitted_script_actually_runs(tmp_path):
    """A score for a script that cannot render is a score for a figure that does not exist."""
    script = codegen.write([_panel()], tmp_path / "run_me.py", columns=2.0, height_mm=90.0)
    cp = subprocess.run([sys.executable, str(script)], cwd=tmp_path,
                        capture_output=True, text=True, timeout=180)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert (tmp_path / "figure.png").is_file()


def test_an_unknown_drawer_is_refused_rather_than_emitted():
    panel = composite.Panel("polar_profile", TREND,
                            {"theta": "year", "value": "value"})
    with pytest.raises(codegen.CodegenError, match="cannot be emitted"):
        codegen.emit([panel])


def test_deviating_code_scores_lower_than_matching_code(tmp_path):
    base = codegen.emit([_panel()], columns=2.0, height_mm=90.0)
    deviating = base.replace("ax.grid(False)", "ax.grid(True)")
    deviating = deviating.replace("color='#0072b2'", "color='#d55e00'")
    res = scorer.score_code_deviation(base, deviating)
    assert res["available"] is True
    assert res["score"] < 100.0
    assert "grid" in res["scored_dimensions"] or "palette" in res["scored_dimensions"]
