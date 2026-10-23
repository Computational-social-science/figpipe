"""The code channel was scoring a different chart type than the figure.

WHY THIS EXISTS
    The official code score compares the EMITTED SCRIPT against the reference code. For
    `grouped_measures` that comparison was meaningless, because the bench rebuilt the panel as
    `line_series` while the skill draws `grouped_bars`:

        op_encode_bars:  composite.Panel("grouped_bars", ...)     <- what is DRAWN
        _panel_for:      composite.Panel("line_series",  ...)     <- what is EMITTED

    So the emitted script drew LINES where the reference draws BARS.

WHY THE FALLBACK EXISTED
    `codegen.SUPPORTED` had no `grouped_bars` entry, so emitting the real drawer raised
    CodegenError and the bench fell back to the nearest emittable drawer. The fallback was not a
    typo -- it was the only option while the emitter did not exist.

THE COST, measured
    18 of the 22 tasks scoring below 90 were `grouped_measures`, mean 79.67 against the pool's
    95.54. On a reference that looks like a grouped bar chart:

        line_series   score = 72.94
        grouped_bars  score = 99.46      (+26.5)

    Same activated dimensions both times, so the difference is the chart type, not the scoring.

WHAT IS PINNED HERE
    The emitter exists, it draws bars, it gives each series its own colour, and the emitted script
    actually runs.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def _df():
    rng = np.random.default_rng(0)
    return pd.DataFrame({"model": [f"m{i}" for i in range(6)],
                         "acc": rng.random(6), "f1": rng.random(6)})


def test_grouped_bars_is_emittable():
    """THE ROOT CAUSE. Without this entry the bench has no choice but to emit a different drawer."""
    from figpipe import codegen
    assert "grouped_bars" in codegen.SUPPORTED, (
        "codegen cannot emit grouped_bars, so the bench must fall back to another drawer and the "
        "code channel compares a different chart type than the figure")


def test_the_emitter_draws_BARS_not_lines():
    """THE SYMPTOM. The emitted script must use ax.bar."""
    from figpipe import codegen, composite
    panel = composite.Panel("grouped_bars", _df(), {"x": "model", "ycols": ["acc", "f1"]})
    cand = codegen.emit([panel], columns=2.0, height_mm=90.0)
    assert "ax.bar(" in cand, "the grouped-bar emitter produced no ax.bar call"
    assert "ax.plot(" not in cand, (
        "the emitter still draws lines; the code channel would compare against a bar reference")


def test_each_series_gets_its_own_colour():
    """A TWO-SERIES GROUPED BAR CHART WITH ONE COLOUR TWICE fails the palette dimension by
    construction -- which is exactly the dimension the code channel scores."""
    import re
    from figpipe import codegen, composite
    panel = composite.Panel("grouped_bars", _df(), {"x": "model", "ycols": ["acc", "f1"]})
    cand = codegen.emit([panel], columns=2.0, height_mm=90.0)
    colours = re.findall(r"color='(#[0-9a-fA-F]{6})'", cand)
    bar_colours = colours[:2]
    assert len(set(bar_colours)) == 2, (
        f"both series got the same colour: {bar_colours}")


def test_the_bench_emits_the_panel_the_skill_draws():
    """THE INVARIANT THAT WAS BROKEN. `_panel_for` must return the drawer `op_encode_bars` creates."""
    import bench_plottwin as B
    panel = B._panel_for("grouped_measures", _df(), {"x": "model", "ycols": ["acc", "f1"]})
    assert panel.draw == "grouped_bars", (
        f"_panel_for rebuilt grouped_measures as {panel.draw!r}; the emitted code would describe a "
        f"different chart than the figure")


def test_the_emitted_script_RUNS(tmp_path):
    """An emitter that produces code the benchmark cannot execute scores nothing."""
    import subprocess
    from figpipe import codegen, composite
    panel = composite.Panel("grouped_bars", _df(), {"x": "model", "ycols": ["acc", "f1"]})
    cand = codegen.emit([panel], columns=2.0, height_mm=90.0)
    script = tmp_path / "c.py"
    script.write_text(cand, encoding="utf-8")
    r = subprocess.run([sys.executable, str(script)], cwd=tmp_path,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"the emitted script failed:\n{r.stderr[-400:]}"


def test_the_score_improves_against_a_bar_reference():
    """THE MEASUREMENT THAT MOTIVATED THE FIX. A bar reference must score higher against bar output
    than against line output."""
    import bench_plottwin as B
    from figpipe import codegen, composite
    ref = (
        'import matplotlib.pyplot as plt\n'
        'fig, ax = plt.subplots(figsize=(7.2, 3.5))\n'
        'ax.bar(x, acc, color="#0072b2", edgecolor="black", linewidth=0.4, label="acc")\n'
        'ax.bar(x, f1, color="#d55e00", edgecolor="black", linewidth=0.4, label="f1")\n'
        'ax.legend(frameon=False)\n'
        'ax.spines["top"].set_visible(False)\n'
        'ax.spines["right"].set_visible(False)\n'
        'ax.grid(False)\n'
    )
    bars = codegen.emit([composite.Panel("grouped_bars", _df(),
                                         {"x": "model", "ycols": ["acc", "f1"]})],
                        columns=2.0, height_mm=90.0)
    lines = codegen.emit([composite.Panel("line_series", _df(),
                                          {"x": "model", "ycols": ["acc", "f1"]})],
                         columns=2.0, height_mm=90.0)
    oc_bars = B.official.score_code_deviation(ref, bars)
    oc_lines = B.official.score_code_deviation(ref, lines)
    if oc_bars.get("score") is None or oc_lines.get("score") is None:
        pytest.skip("the scorer is unavailable")
    assert oc_bars["score"] > oc_lines["score"] + 10, (
        f"bar output scored {oc_bars['score']:.1f} against {oc_lines['score']:.1f} on a bar "
        f"reference; the fix did not help")
