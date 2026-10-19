"""The specification layer must declare a figure, or refuse -- never quietly pick a chart.

WHY THESE TESTS
    `figpipe/spec.py` is the structural answer to the benchmark gap: a benchmark hands over data
    (or a figure) and expects a figure, while the old pipeline expected a hand-written intent and
    column mapping. The spec layer infers that declaration from column roles with an ordered rule
    set and records WHY. Its contract matters as much as its output: ambiguous data must raise a
    `SpecError` that names the roles, because a silent default is how a figure ends up encoding a
    claim nobody made.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = pytest.importorskip("figpipe.spec", reason="spec absent")
from figpipe import audit, layout  # noqa: E402


def _trend() -> pd.DataFrame:
    years = pd.date_range("1990-01-01", periods=24, freq="YS")
    return pd.DataFrame({"year": years, "value": np.linspace(0.1, 0.9, 24)})


def test_column_roles_are_explicit():
    df = pd.DataFrame({"t": pd.date_range("2020-01-01", periods=5),
                       "v": [1.0, 2, 3, 4, 5], "g": list("aabba")})
    roles = spec.column_roles(df)
    assert roles["datetime"] == ["t"]
    assert roles["numeric"] == ["v"]
    assert roles["categorical"] == ["g"]


def test_time_series_becomes_a_trend_panel():
    s = spec.infer_spec(_trend())
    assert len(s.panels) == 1
    assert s.panels[0].intent == "trend_with_uncertainty"
    assert s.panels[0].kwargs["x"] == "year"
    assert s.to_dict()["panels"][0]["rationale"]


def test_repeated_category_becomes_a_distribution():
    df = pd.DataFrame({"g": ["a"] * 4 + ["b"] * 4 + ["c"] * 4,
                       "v": list(range(12))})
    s = spec.infer_spec(df)
    assert s.panels[0].intent == "distribution"
    assert s.panels[0].kwargs == {"group": "g", "value": "v",
                                  "xlabel": "g", "ylabel": "v"}


def test_single_value_per_category_becomes_ranked():
    df = pd.DataFrame({"country": ["a", "b", "c", "d"], "pct": [0.4, 0.3, 0.2, 0.1]})
    s = spec.infer_spec(df)
    assert s.panels[0].intent == "ranked_composition"
    assert s.panels[0].kwargs["label"] == "country"


def test_two_continuous_measures_become_density_not_scatter():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": rng.normal(size=200), "y": rng.normal(size=200)})
    s = spec.infer_spec(df)
    assert s.panels[0].intent == "density_relationship"


def test_two_categorical_measures_become_grouped_bars():
    df = pd.DataFrame({"model": ["a", "b", "c", "d"], "m1": [1.0, 2, 3, 4],
                       "m2": [4.0, 3, 2, 1]})
    s = spec.infer_spec(df)
    assert s.panels[0].intent == "comparison_with_error"
    assert s.panels[0].kwargs["ycols"] == ["m1", "m2"]


def test_ambiguous_data_raises_with_the_roles_in_the_message():
    df = pd.DataFrame({"only": [1.0, 2, 3, 4]})
    with pytest.raises(spec.SpecError, match="roles="):
        spec.infer_spec(df)


def test_explicit_intent_is_validated_against_the_grammar():
    df = pd.DataFrame({"g": list("abcd"), "v": [1.0, 2, 3, 4]})
    s = spec.infer_spec(df, intent="comparison_with_error", x="g", y="v")
    assert s.panels[0].intent == "comparison_with_error"
    with pytest.raises(Exception):
        spec.infer_spec(df, intent="comparison_with_error", x="g")   # missing y


def test_a_spec_serialises_without_the_data_and_rebuilds_to_an_audited_figure(tmp_path):
    s = spec.infer_spec(_trend())
    payload = json.dumps(s.to_dict(), ensure_ascii=False)
    assert "DataFrame" not in payload and "year" in payload
    fig = spec.build(s)
    pdf = pathlib.Path(layout.save(fig, tmp_path / "spec")[0])
    rep = audit.audit(pdf, expect_width_mm=183.0, check_overlap=False)
    hard = [f for f in rep["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    assert not hard, hard


def test_spec_is_deterministic():
    df = _trend()
    a = spec.infer_spec(df).to_dict()
    b = spec.infer_spec(df).to_dict()
    assert a == b
