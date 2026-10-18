"""The search must use the vendored engine, improve on the default, and be reproducible.

WHY THESE TESTS
    `figpipe/search.py` is the integration of a peer resource (the MIT MCTS library vendored from
    DeTi*k*Zify) with our own deterministic oracle. The claim is narrow and checkable: given a
    reference style profile, the search evaluates candidate variants of a template, keeps the one
    with the smaller distance, and produces the same answer twice. If any of those fail, the
    integration is a dependency, not a capability.
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

search = pytest.importorskip("figpipe.search", reason="search absent")
styleprofile = pytest.importorskip("figpipe.styleprofile")
DATA = ROOT / "corpus" / "seed" / "derived" / "fig7_mimicry.csv"
REFERENCE = ROOT / "corpus" / "style" / "published_fig7.json"


def _data():
    if not DATA.is_file():
        pytest.skip("seed derived data absent")
    df = pd.read_csv(DATA, encoding="utf-8")
    part = df[(df["sender_cp"] == "Core") & (df["receiver_cp"] == "Core")]
    return part[["Year", "mean"]].sort_values("Year").reset_index(drop=True)


def _reference():
    if not REFERENCE.is_file():
        pytest.skip("reference profile absent")
    return styleprofile.StyleProfile.load(REFERENCE)


def test_the_vendored_mcts_is_importable_and_attributed():
    from mcts.montecarlo import MonteCarlo
    from mcts.node import Node
    assert callable(MonteCarlo) and callable(Node)
    notice = ROOT / "third_party" / "mcts" / "NOTICE.md"
    license_file = ROOT / "third_party" / "mcts" / "LICENSE"
    assert notice.is_file() and license_file.is_file(), (
        "vendored code must keep its licence and attribution")


def test_search_improves_on_the_default_and_records_every_variant(tmp_path):
    result = search.search(_data(), _reference(), budget=3, seed=0,
                           space={"size": ["6.0", "6.5"]}, out_dir=tmp_path)
    assert result["baseline"], "the default variant was not evaluated"
    assert result["trace"], "no variant was evaluated"
    assert result["best"]["reward"] >= result["baseline"]["reward"], (
        f"search returned a worse variant than the default: {result['best']} vs "
        f"{result['baseline']}")
    for row in result["trace"]:
        assert "distance" in row and "reward" in row
        assert row["distance"] is not None, row.get("error")


def test_search_is_deterministic_for_a_fixed_seed(tmp_path):
    kwargs = dict(budget=3, seed=7, space={"size": ["6.0", "6.5"]})
    a = search.search(_data(), _reference(), out_dir=tmp_path / "a", **kwargs)
    b = search.search(_data(), _reference(), out_dir=tmp_path / "b", **kwargs)
    assert a["best"]["state"] == b["best"]["state"]
    assert a["best"]["reward"] == b["best"]["reward"]
    assert a["improvement"] == b["improvement"]


def test_a_variant_with_a_bad_size_is_penalised(tmp_path):
    """A 7.4 pt 'variant' leaves the 5-7 band and must not win on style distance alone."""
    result = search.search(_data(), _reference(), budget=2, seed=0,
                           space={"size": ["6.0", "7.4"]}, out_dir=tmp_path)
    bad = [r for r in result["trace"] if r["params"].get("size") == "7.4"]
    assert bad, "the out-of-band variant was not evaluated"
    assert bad[0]["reward"] < result["baseline"]["reward"] + 1.0
    assert any("font_size" in r.get("hard_findings", []) for r in bad if r.get("hard_findings"))
