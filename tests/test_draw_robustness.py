"""A benchmark panel must not crash on real data: NaN gaps and huge x magnitudes.

WHY THIS TEST
    PlotTwin-Bench task arxiv-phys-prx-prl__2603.21981 failed with "SVD did not converge in
    Linear Least Squares": its x values are large, and a NaN in the series poisoned the fit.
    A drawing primitive that fails on ordinary benchmark data is not a capability. The fits are
    now centred/scaled and drop non-finite pairs; a degenerate fit is skipped, not fatal.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import composite, grammar, layout  # noqa: E402


def _render(panels, stem):
    fig = grammar.plate(panels, columns=2.0, height_mm=70.0, letters=True)
    return pathlib.Path(layout.save(fig, stem)[0])


def test_trend_survives_huge_x_and_nan(tmp_path):
    x = 1.7e9 + np.arange(40.0)
    y = np.linspace(0.2, 0.9, 40)
    y[7] = np.nan
    df = pd.DataFrame({"t": x, "v": y})
    panel = grammar.panel("trend_with_uncertainty", df, x="t", y="v", fit="lm",
                          band="fit", reference=0.5)
    pdf = _render([panel], tmp_path / "trend")
    assert pdf.is_file() and pdf.stat().st_size > 0


def test_scatter_survives_nan_and_constant(tmp_path):
    df = pd.DataFrame({"x": [1.0, 2.0, np.nan, 4.0, 5.0],
                       "y": [1.0, np.nan, 3.0, 4.0, 5.0]})
    panel = composite.Panel("scatter_fit", df, {"x": "x", "y": "y"})
    pdf = _render([panel], tmp_path / "scatter")
    assert pdf.is_file() and pdf.stat().st_size > 0
    df2 = pd.DataFrame({"x": [1.0] * 5, "y": [1.0, 2.0, 3.0, 4.0, 5.0]})
    panel2 = composite.Panel("scatter_fit", df2, {"x": "x", "y": "y"})
    assert _render([panel2], tmp_path / "scatter_flat").is_file()
