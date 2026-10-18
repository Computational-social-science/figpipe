"""Composite benchmark tasks must become several panels, or refuse.

WHY THIS TEST
    PlotTwin-Bench "Composite" tasks carry several sub-figures in one long table, distinguished
    by a panel_group/block column. Before this operator they failed with no mapping. The failure
    mode to guard is the tempting shortcut: draw ONE panel from the whole table, which silently
    drops the other sub-figures while looking like a finished figure.
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import skills  # noqa: E402

LONG = pd.DataFrame({
    "panel_group": ["A", "A", "A", "B", "B", "B"],
    "outcome": ["x", "y", "z", "x", "y", "z"],
    "estimate": [0.3, 0.5, 0.2, 0.7, 0.4, 0.6],
})


def test_one_panel_per_group(tmp_path):
    res = skills.run("composite_groups", LONG, out_stem=tmp_path / "cg",
                     by="panel_group", x="outcome", y="estimate")
    assert res["panels"] == 2, res["panels"]
    assert res["hard_failures"] == 0, res["findings"]
    assert any(step.startswith("layout.split_panels") for step in res["trace"])


def test_too_many_groups_is_refused_not_truncated(tmp_path):
    many = pd.DataFrame({"g": list("ABCDEF"), "x": list("abcdef"), "v": range(6)})
    with pytest.raises(skills.SkillError, match="max_panels"):
        skills.run("composite_groups", many, out_stem=tmp_path / "many",
                   by="g", x="x", y="v")


def test_missing_group_column_is_refused():
    with pytest.raises(skills.SkillError, match="grouping column"):
        skills.run("composite_groups", LONG, by="nope", x="outcome", y="estimate")


def test_error_comparison_draws_bars(tmp_path):
    res = skills.run("error_comparison", LONG, out_stem=tmp_path / "eb",
                     x="outcome", y="estimate")
    assert res["panels"] == 1
    assert res["hard_failures"] == 0


def test_an_oversized_panel_is_aggregated_and_the_trace_says_so(tmp_path):
    """300 rows in one sub-figure is a smear, not a comparison. Aggregating is allowed;
    doing it SILENTLY is not."""
    import numpy as np
    rng = np.random.default_rng(0)
    big = pd.DataFrame({
        "panel_group": ["A"] * 300 + ["B"] * 300,
        "outcome": [f"o{i % 5}" for i in range(600)],
        "estimate": rng.normal(size=600),
    })
    res = skills.run("composite_groups", big, out_stem=tmp_path / "big",
                     by="panel_group", x="outcome", y="estimate")
    assert res["panels"] == 2
    assert any("aggregate" in step for step in res["trace"]), res["trace"]
    assert res["hard_failures"] == 0
