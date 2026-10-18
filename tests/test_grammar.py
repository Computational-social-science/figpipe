"""The grammar must be a vocabulary with contracts, not a pile of plotting keywords.

WHY THESE TESTS
    `figpipe.grammar` claims that a panel can be described by WHAT IT MEANS. A claim like that
    is worth nothing unless the vocabulary is complete (every intent maps to a real drawer), the
    contract actually refuses incomplete data, and the encodings carry meaning: a band is drawn
    where uncertainty exists, the reference line is where the claim says it is, and the density
    panel's correlation is computed on the scale that is drawn.

    The final test is the one that matters most: the reproduction builders are re-run on the
    seed paper's derived tables and their statistics compared with what the paper published. A
    template layer that cannot reproduce the paper it was learned from is not a template layer.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

grammar = pytest.importorskip("figpipe.grammar", reason="grammar absent")
from figpipe import composite, drawlib  # noqa: E402

DERIVED = ROOT / "corpus" / "seed" / "derived"

TREND = pd.DataFrame({
    "Year": np.arange(1990, 2014),
    "mean": np.linspace(0.1, 0.9, 24),
    "lo": np.linspace(0.05, 0.85, 24),
    "hi": np.linspace(0.15, 0.95, 24),
})


def test_every_intent_maps_to_a_registered_drawer():
    for item in grammar.catalogue():
        assert item["drawer"] in drawlib.DRAWERS, (
            f"intent {item['intent']} maps to {item['drawer']!r}, which is not a drawer")


def test_unknown_intent_lists_the_vocabulary():
    with pytest.raises(KeyError, match="available"):
        grammar.panel("scatter_of_everything", TREND, x="Year", y="mean")


def test_trend_contract_refuses_incomplete_data():
    with pytest.raises(grammar.IntentContractError, match="requires the parameter 'x'"):
        grammar.panel("trend_with_uncertainty", TREND, y="mean")
    with pytest.raises(grammar.IntentContractError, match="not a column"):
        grammar.panel("trend_with_uncertainty", TREND, x="Year", y="nope")
    with pytest.raises(grammar.IntentContractError, match="together"):
        grammar.panel("trend_with_uncertainty", TREND, x="Year", y="mean", lo="lo")


def test_ranked_contract_requires_label_and_value():
    df = pd.DataFrame({"country": ["A", "B"], "share": [0.2, 0.1]})
    with pytest.raises(grammar.IntentContractError, match="'label'"):
        grammar.panel("ranked_composition", df, value="share")


def test_the_two_kinds_of_band_are_not_interchangeable():
    """A data interval and a fitted line's confidence band are different claims."""
    fig = grammar.plate([grammar.panel("trend_with_uncertainty", TREND, x="Year",
                                       y="mean", lo="lo", hi="hi", band="data")],
                        columns=1.0)
    assert fig.axes[0].collections, "band='data' drew no filled interval"
    fig2 = grammar.plate([grammar.panel("trend_with_uncertainty", TREND, x="Year",
                                        y="mean", fit="lm", band="fit")], columns=1.0)
    assert fig2.axes[0].collections, "band='fit' drew no confidence band"
    with pytest.raises(ValueError, match="band='fit' needs fit"):
        grammar.plate([grammar.panel("trend_with_uncertainty", TREND, x="Year",
                                     y="mean", band="fit")], columns=1.0)
    with pytest.raises(ValueError, match="band='data' needs lo and hi"):
        grammar.plate([grammar.panel("trend_with_uncertainty", TREND, x="Year",
                                     y="mean", band="data")], columns=1.0)


@pytest.mark.parametrize("fit", ["lm", "poly3", "loess"])
def test_every_fit_kind_draws_a_line(fit):
    fig = grammar.plate([grammar.panel("trend_with_uncertainty", TREND, x="Year",
                                       y="mean", fit=fit)], columns=1.0)
    assert fig.axes[0].lines or fig.axes[0].get_lines(), f"fit={fit} drew no line"


def test_an_unknown_fit_is_refused():
    with pytest.raises(ValueError, match="unknown fit"):
        grammar.plate([grammar.panel("trend_with_uncertainty", TREND, x="Year",
                                     y="mean", fit="spline")], columns=1.0)


def test_ranked_composition_is_sorted_and_capped():
    df = pd.DataFrame({"name": list("ABCDE"),
                       "share": [0.10, 0.40, 0.05, 0.30, 0.15]})
    fig = grammar.plate([grammar.panel("ranked_composition", df, label="name",
                                       value="share", top=3)], columns=1.0)
    ax = fig.axes[0]
    heights = [p.get_height() for p in ax.patches]
    assert len(heights) == 3
    assert heights == sorted(heights, reverse=True), "bars are not ordered by value"
    assert heights[0] == pytest.approx(0.40)


def test_density_panel_counts_as_one_panel_even_with_marginals():
    rng = np.random.default_rng(3)
    df = pd.DataFrame({"x": rng.integers(1, 500, 300), "y": rng.integers(1, 500, 300)})
    p = grammar.panel("density_relationship", df, x="x", y="y", marginals="top")
    fig = grammar.plate([p], columns=1.0)
    r = composite.inspect(fig)
    assert r["n_panels"] == 1, (
        "a marginal histogram was counted as a second panel; it is part of one panel")
    assert fig.axes[0].get_xscale() == "log"
    assert composite.check(fig, r) == []


def test_density_correlation_is_computed_on_the_plotted_scale():
    """A log-log cloud with r annotated must quote the log-space r, not the raw one."""
    x = np.array([10, 100, 1000, 5000, 300, 40, 20, 70, 250, 800, 2000, 60])
    y = np.array([1, 10, 500, 5000, 25, 2, 3, 8, 90, 300, 1200, 4])
    df = pd.DataFrame({"x": x, "y": y})
    fig = grammar.plate([grammar.panel("density_relationship", df, x="x", y="y",
                                       gridsize=6)], columns=1.0)
    texts = [t.get_text() for t in fig.axes[0].texts]
    assert any("r =" in t for t in texts), texts
    expected = np.corrcoef(np.log10(x), np.log10(y))[0, 1]
    raw = np.corrcoef(x, y)[0, 1]
    quoted = float([t for t in texts if "r =" in t][0].split("=")[1])
    # the annotation is printed to two decimals, so the tolerance is the rounding step
    assert abs(quoted - expected) < 0.005, (quoted, expected, raw)


def test_signed_matrix_marks_missing_cells_grey_and_refuses_all_missing():
    mat = pd.DataFrame(np.array([[0.3, -0.2], [np.nan, 0.1]]),
                       index=["A", "B"], columns=["X", "Y"])
    fig = grammar.plate([grammar.panel("signed_matrix", mat)], columns=1.0)
    assert composite.inspect(fig)["n_panels"] == 1
    empty = pd.DataFrame(np.array([[np.nan, np.nan]]), columns=["X", "Y"])
    with pytest.raises(ValueError, match="no finite values"):
        grammar.plate([grammar.panel("signed_matrix", empty)], columns=1.0)


def test_letterless_plate_is_allowed_and_a_missing_letter_is_not():
    """The seed's Figs 5 and 7 label panes with titles instead of letters."""
    panels = [grammar.panel("trend_with_uncertainty", TREND, x="Year", y="mean")
              for _ in range(2)]
    fig = grammar.plate(panels, columns=2.0, letters=False,
                        margins={"bottom": 12.0})
    r = fig._figpipe_report
    assert r["letters_expected"] is False
    assert composite.check(fig, r) == []
    fig2 = grammar.plate(panels, columns=2.0, letters=True)
    assert composite.check(fig2, fig2._figpipe_report) == []


def test_the_reproduction_report_declares_its_limits():
    """A reproduction claim must carry its layer, estimator, deviations and own self-check.

    The lesson from the first version: the report said "14 of 14" statistics (there were 15),
    and its reproduction layer was unstated, so "reproduced" was unfalsifiable. The report now
    derives its count from its own agreement tree and declares which layer each figure reaches.
    """
    report_path = ROOT / "templates" / "seed" / "report.json"
    if not report_path.is_file():
        pytest.skip("no reproduction report yet")
    import json
    r = json.loads(report_path.read_text(encoding="utf-8"))
    for key in ("reproduction_layers", "discrepancies", "self_check", "figures",
                "not_reproduced"):
        assert key in r, f"the report no longer declares {key!r}"
    assert set(r["not_reproduced"]) >= {"Fig 2", "Fig 4", "Fig 6"}
    for name, entry in r["not_reproduced"].items():
        assert entry.get("why"), f"{name} has no recorded reason"
    for f in r["figures"]:
        for key in ("layer", "estimator", "deviations", "audit_ok", "text_collisions",
                    "published_panels", "reproduced_panels"):
            assert key in f, f"{f['figure']} does not declare {key!r}"
        assert f["audit_ok"], f"{f['figure']} failed its own audit"
        assert f["text_collisions"] == [], f"{f['figure']}: text printed on text"
    # the count is DERIVED: walking the tree must reproduce the recorded number
    n = 0

    def walk(node):
        nonlocal n
        if isinstance(node, dict):
            if "published" in node and "computed" in node:
                assert "delta" in node
                n += 1 if node["delta"] is not None else 0
                return
            for v in node.values():
                walk(v)

    walk(r["agreement"])
    assert n == r["self_check"]["statistics_recorded"], (
        "the report's statistics count disagrees with its own agreement tree")
    assert n == 15, f"{n} statistics recorded; the paper's reproduction table has 15"
    assert r["self_check"]["worst_abs_delta"] <= 0.01
    assert r["self_check"]["ok"] is True
    # the one unresolved estimator is recorded, not hidden behind the matching value
    d = next(x for x in r["discrepancies"] if x["figure"] == "Fig 1b")
    assert {"raw_scale", "log_scale", "published", "resolution"} <= set(d)
    assert d["raw_scale"] != d["log_scale"], (
        "the Fig 1b raw/log ambiguity must record both estimator values")


def test_the_seed_reproduction_still_matches_the_published_statistics():
    """THE TEST THAT MATTERS: re-build the seed panels and compare with the paper's numbers.

    Skips when the derived tables are absent (they are produced by
    `python scripts/reproduce_seed.py --stage derive` from the 1.57 GB raw package).
    """
    if not (DERIVED / "fig7_mimicry.csv").is_file():
        pytest.skip("seed derived tables absent; run reproduce_seed.py --stage derive")
    sys.path.insert(0, str(ROOT / "scripts"))
    mod = pytest.importorskip("reproduce_seed")
    panels, meta = mod.plate_fig7()
    assert len(panels) == 4
    for pane, published in mod.PUBLISHED["fig7_r"].items():
        assert abs(meta["computed"][pane] - published) <= 0.02, (
            f"{pane}: reproduced r {meta['computed'][pane]} vs published {published}")
    fig = grammar.plate(panels, **meta["layout"])
    report = fig._figpipe_report
    assert composite.check(fig, report) == []
    assert report["n_panels"] == 4
    # the stored report must not be stale: recomputing the panel must reproduce its numbers
    import json
    stored = json.loads((ROOT / "templates" / "seed" / "report.json").read_text(encoding="utf-8"))
    fig7 = next(f for f in stored["figures"] if f["figure"].startswith("fig7"))
    assert fig7["computed"] == meta["computed"], (
        "templates/seed/report.json is stale; run reproduce_seed.py --stage render")
