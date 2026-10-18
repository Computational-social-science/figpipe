"""The composer must build real multi-panel plates, and refuse layouts that only look right.

THE GAP THIS CLOSES
    The template library drew one panel per figure. "我们需要的往往是优雅的组图，组图，组图" --
    the deliverable is the PLATE: a wide key panel, two quantifications beneath it, panel letters
    a-d, one gutter everywhere. These tests hold `figpipe.composite` to that promise on the
    finished figure, not on the intent: every geometry assertion here reads the axes rectangles
    and the figure's own text objects back.

WHAT IS CHECKED
    * the page is exactly one of Nature's column widths and fits the height limit
      (tests/test_style.py already checks the format; here the format must survive composition)
    * every panel gets exactly one 8 pt letter, in reading order
    * the gutters are UNIFORM and equal to what the planner asked for -- a composer that says
      3.0 mm and draws 7.5 mm is a composer that lies about its own output
    * a span layout puts the wide panel across the full content width
    * shared axes are actually shared (identical limits, inner labels hidden)
    * the refusals: an empty grid cell, spans with sharing, an unknown drawer, a colour bar on
      an artist that cannot carry one, a non-DataFrame panel
    * a real plate driven by corpus tables renders and passes `audit.audit`
"""
from __future__ import annotations

import json
import pathlib
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

composite = pytest.importorskip("figpipe.composite", reason="composite absent")
from figpipe import audit, drawlib, layout, style  # noqa: E402

OUT = ROOT / "templates" / "out"

FRAME = pd.DataFrame({
    "group": ["g1", "g2", "g3", "g4", "g5"],
    "value": [12.0, 18.5, 9.2, 21.1, 15.4],
    "err": [0.8, 1.1, 0.6, 1.4, 0.9],
    "value2": [10.1, 16.0, 8.4, 19.3, 14.0],
})


def _panel(draw="grouped_bars", **kwargs):
    kw = {"x": "group", "ycols": ["value", "value2"], "xlabel": "group",
          "ylabel": "value", "legend": False}
    kw.update(kwargs)
    return composite.Panel(draw, FRAME, kw)


def _four():
    return [
        composite.Panel("grouped_bars", FRAME, {"x": "group", "ycols": ["value", "value2"],
                                                "xlabel": "group", "ylabel": "value",
                                                "legend": False}),
        composite.Panel("line_series", FRAME, {"x": "group", "ycols": ["value", "value2"],
                                               "xlabel": "group", "ylabel": "value",
                                               "legend": False}),
        composite.Panel("scatter_fit", FRAME, {"x": "value", "y": "value2",
                                               "xlabel": "value", "ylabel": "value2"}),
        composite.Panel("bar_with_errors", FRAME, {"x": "group", "y": "value", "err": "err",
                                                   "xlabel": "group", "ylabel": "value"}),
    ]


def test_page_is_exact_column_width_and_within_height():
    fig = composite.composite(_four(), columns=2.0)
    r = composite.inspect(fig)
    assert abs(r["width_mm"] - style.WIDTH_DOUBLE_MM) < 0.6
    assert r["height_mm"] <= style.MAX_HEIGHT_MM
    assert composite.check(fig, r) == []


def test_single_column_plate_is_89_mm():
    fig = composite.composite(_four()[:3], columns=1.0)
    r = composite.inspect(fig)
    assert abs(r["width_mm"] - style.WIDTH_SINGLE_MM) < 0.6
    # three panels on 89 mm stack, they do not squeeze into a row
    assert len(r["panels"]) == 3
    widths = [p["w"] for p in r["panels"]]
    assert max(widths) - min(widths) < 0.1
    assert widths[0] > 60.0


def test_every_panel_gets_one_8pt_letter_in_reading_order():
    fig = composite.composite(_four(), columns=2.0)
    letters = composite.inspect(fig)["letters"]
    assert [lt["letter"] for lt in letters] == ["a", "b", "c", "d"]
    assert all(abs(lt["size_pt"] - style.PANEL_LETTER_PT) < 0.2 for lt in letters)
    # reading order: a and b share the top row, c and d the bottom one
    assert letters[0]["y_mm"] > letters[2]["y_mm"]
    assert letters[0]["x_mm"] < letters[1]["x_mm"]


def test_gutters_are_uniform_and_equal_to_the_plan():
    fig = composite.composite(_four(), columns=2.0)
    r = fig._figpipe_report
    planned_x = r["planned"]["gap_x_mm"]
    planned_y = r["planned"]["gap_y_mm"]
    assert len(r["gaps_x_mm"]) == 1 and len(r["gaps_y_mm"]) == 1
    assert abs(r["gaps_x_mm"][0] - planned_x) < 0.15, (r["gaps_x_mm"], planned_x)
    assert abs(r["gaps_y_mm"][0] - planned_y) < 0.15, (r["gaps_y_mm"], planned_y)


def test_a_span_layout_makes_the_top_panel_full_width():
    panels = [
        composite.Panel("grouped_bars", FRAME, {"x": "group", "ycols": ["value"],
                                                "xlabel": "", "ylabel": "value",
                                                "legend": False}, at=(0, 0, 1, 2)),
        composite.Panel("line_series", FRAME, {"x": "group", "ycols": ["value"],
                                               "xlabel": "group", "ylabel": "value",
                                               "legend": False}, at=(1, 0)),
        composite.Panel("scatter_fit", FRAME, {"x": "value", "y": "value2",
                                               "xlabel": "value", "ylabel": "value2"},
                        at=(1, 1)),
    ]
    fig = composite.composite(panels, columns=2.0, height_mm=120.0)
    r = composite.inspect(fig)
    assert composite.check(fig, r) == []
    top, left, right = r["panels"]
    assert top["w"] > left["w"] + right["w"], (
        "the spanning panel is not wider than the two beneath it")
    assert abs(top["x0"] - left["x0"]) < 0.1 and abs(top["x1"] - right["x1"]) < 0.1


def test_shared_axes_are_shared_and_labelled_once():
    fig = composite.composite(_four()[:2], columns=2.0, sharey=True)
    fig.canvas.draw()
    axes = fig.axes
    assert axes[0].get_ylim() == axes[1].get_ylim()
    # the outer panel keeps its labels; the inner one has none to draw
    assert axes[0].get_yticklabels(), "the outer panel lost its y tick labels"
    assert not axes[1].get_yticklabels(), (
        "the inner panel still shows y tick labels although the axis is shared")
    assert axes[1].get_ylabel() == ""
    assert axes[0].get_ylabel() != ""


def test_a_grid_with_an_empty_cell_is_refused():
    with pytest.raises(ValueError, match="empty cell"):
        composite.composite(_four()[:3], columns=2.0, ncols=2, nrows=2)


def test_sharing_with_spans_is_refused():
    panels = [_panel(), composite.Panel("grouped_bars", FRAME,
                                        {"x": "group", "ycols": ["value"], "legend": False},
                                        at=(0, 0))]
    with pytest.raises(ValueError, match="only defined for a plain grid"):
        composite.composite(panels, columns=2.0, sharey=True)


def test_unknown_drawer_is_refused_with_the_available_names():
    with pytest.raises(KeyError, match="unknown drawer"):
        composite.Panel("pie_chart", FRAME, {})


def test_a_colour_bar_on_a_capable_drawer_is_placed_inside_the_cell():
    p = composite.Panel("heatmap", FRAME[["value", "value2"]],
                        {"xlabel": "col", "ylabel": "row", "label": "value"},
                        colorbar=True)
    fig = composite.composite([p], columns=1.0)
    r = composite.inspect(fig)
    assert composite.check(fig, r) == []
    # the colour bar is an extra axes, but still ONE panel
    assert r["n_panels"] == 1 and len(fig.axes) == 2


def test_colour_bar_on_a_non_capable_drawer_is_refused():
    with pytest.raises(ValueError, match="colour bar"):
        composite.Panel("bar_with_errors", FRAME,
                        {"x": "group", "y": "value"}, colorbar=True)


def test_non_dataframe_panel_is_refused():
    with pytest.raises(TypeError, match="DataFrame"):
        composite.Panel("grouped_bars", [[1, 2, 3]], {})


def test_measured_priors_are_read_and_reported(tmp_path):
    """The geometry must come from the measured artefact, and say so."""
    j = {"gutter": {"n": 40, "median_mm": 4.2},
         "panel_aspect": {"n": 90, "median": 1.45},
         "letter_offsets": {"n": 40, "dx_median_mm": 1.5, "dy_median_mm": -1.0}}
    p = tmp_path / "composite_layouts.json"
    p.write_text(json.dumps(j), encoding="utf-8")
    pri = composite.priors(path=p)
    assert pri["gutter_mm"] == 4.2 and pri["gutter_n"] == 40
    assert pri["panel_aspect"] == 1.45
    assert pri["letter_dx_mm"] == 1.5
    assert pri["measured"] is True and pri["source"] == p.name
    # a missing artefact is declared, not silently dressed as measured
    absent = composite.priors(path=tmp_path / "nope.json")
    assert absent["measured"] is False and "default" in absent["source"]


def test_a_corrupt_prior_artefact_is_an_error_not_a_fallback(tmp_path):
    p = tmp_path / "composite_layouts.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(composite.CompositeGeometryError):
        composite.priors(path=p)


def test_a_bare_panel_needs_no_axis_labels():
    """A drawer used to raise NameError when `ylabel` was empty.

    THE DEFECT, found by the L08 mechanism check on its first run: `ax_grouped_bars` still
    referenced a variable `y` left over from the single-panel version. Every plate in the
    demonstration passed a ylabel, so nothing caught it -- a panel must be allowed to be bare.
    """
    p = composite.Panel("grouped_bars", FRAME,
                        {"x": "group", "ycols": ["value"], "legend": False})
    fig = composite.composite([p], columns=1.0)
    assert composite.inspect(fig)["n_panels"] == 1


def test_the_knowledge_base_records_the_plate_rule():
    """The rule must travel with the measurement, not live only in this test file."""
    kb = json.loads((ROOT / "knowledge" / "layout_rules.json").read_text(encoding="utf-8"))
    rule = next((r for r in kb["rules"] if r["id"] == "L08"), None)
    assert rule is not None, "the knowledge base has no rule about multi-panel figures"
    assert rule["confidence"] == "enforced", (
        f"L08 is {rule['confidence']!r}; the composer and its read-back check exist, so a "
        f"demotion here means the mechanism regressed")
    assert rule["check"]["kind"] == "composite_plate"
    assert rule["mechanism_verified"] and rule["empirically_measured"]
    study = kb.get("composite_study") or {}
    assert study.get("n_composites"), (
        "the rule claims to be measured but the study block records no composites")


def test_render_writes_both_twins_and_audits_clean(tmp_path):
    stem = tmp_path / "plate"
    rep = composite.render(_four(), stem, columns=2.0)
    pdf, png = (pathlib.Path(p) for p in rep["paths"])
    assert pdf.is_file() and png.is_file()
    assert rep["problems"] == []
    a = audit.audit(pdf, expect_width_mm=style.WIDTH_DOUBLE_MM, check_overlap=False)
    hard = [f for f in a["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    assert not hard, hard


def test_real_corpus_plate_renders_and_passes_the_audit(tmp_path):
    """A capability demonstrated only on invented numbers has not been demonstrated."""
    sys.path.insert(0, str(ROOT / "scripts"))
    mod = pytest.importorskip("render_composites", reason="plate script absent")
    plates = mod.build_plates()
    assert len(plates) >= 3
    spec = plates[-1]                                    # the smallest: 1x3 shared y
    rep = composite.render(spec["panels"], tmp_path / spec["name"], **spec["kw"])
    a = audit.audit(pathlib.Path(rep["paths"][0]),
                    expect_width_mm=style.WIDTH_DOUBLE_MM, check_overlap=False)
    assert a["ok"], a["findings"]
    assert rep["problems"] == []
    assert rep["n_panels"] == len(spec["panels"])
