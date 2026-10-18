"""The style profile must measure exact properties and its distance must be explainable.

WHY THESE TESTS
    `styleprofile` is the answer to the raster-and-a-VLM approach the peer projects use: read the
    style from the PDF's own objects instead of guessing it from a screenshot. That claim only
    holds if the measurement is exact and the distance moves for the right reason. So the tests
    build a figure whose properties are known by construction and check the recovered numbers,
    then check that comparing a profile with itself is zero and that moving one property moves
    exactly one component.
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

styleprofile = pytest.importorskip("figpipe.styleprofile", reason="styleprofile absent")
from figpipe import drawlib, layout, style  # noqa: E402


def _fixture_pdf(tmp_path, columns=1.0, height_mm=60.0):
    """A figure with KNOWN style: 6 pt ticks, an 8 pt panel letter, Okabe blue bars."""
    style.apply()
    fig, _, _ = layout.figure(columns=columns, height_mm=height_mm)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.20, right=0.97, top=0.90, bottom=0.22)
    df = pd.DataFrame({"x": list("abcde"), "y": [3.0, 5.0, 2.0, 4.0, 3.5]})
    drawlib.ax_bar_with_errors(ax, df, x="x", y="y", xlabel="x", ylabel="y")
    style.panel_letter(ax, "a", dx_pt=-24, dy_pt=4)
    paths = layout.save(fig, tmp_path / "fixture")
    return pathlib.Path(paths[0])


def test_measurement_recovers_known_type_sizes_and_letters(tmp_path):
    pdf = _fixture_pdf(tmp_path)
    prof = styleprofile.StyleProfile.from_pdf(pdf)
    s = np.asarray(prof.sizes_pt)
    assert s.size > 0
    # tick labels are 6 pt, axis labels 7 pt; the median must sit in the 5-7 band
    assert 5.0 <= float(np.median(s)) <= 7.0, sorted(set(prof.sizes_pt))
    assert prof.panel_letters, "the 8 pt panel letter was not detected"
    assert prof.panel_letters[0]["char"] == "a"
    assert abs(prof.panel_letters[0]["size_pt"] - 8.0) < 0.2


def test_measurement_recovers_the_palette_and_the_spines(tmp_path):
    pdf = _fixture_pdf(tmp_path)
    prof = styleprofile.StyleProfile.from_pdf(pdf)
    hexes = {c["hex"] for c in prof.colours}
    assert "#0072b2" in hexes, f"the Okabe blue fill is missing from {sorted(hexes)[:8]}"
    okabe_names = {c["okabe"] for c in prof.colours}
    assert "blue" in okabe_names
    assert prof.spines["left"] and prof.spines["bottom"]
    assert not prof.spines["right"], "right spine reported although the style hides it"
    assert prof.rules_h == 0 and prof.rules_v == 0, "no gridlines were drawn"


def test_a_profile_compared_with_itself_is_zero(tmp_path):
    pdf = _fixture_pdf(tmp_path)
    prof = styleprofile.StyleProfile.from_pdf(pdf)
    result = styleprofile.compare(prof, prof)
    assert result["distance"] == 0.0
    assert all(v == 0.0 for v in result["details"].values()), result["details"]


def test_changing_the_type_changes_only_the_type_component(tmp_path):
    pdf = _fixture_pdf(tmp_path)
    base = styleprofile.StyleProfile.from_pdf(pdf)
    moved = styleprofile.StyleProfile.from_pdf(pdf)
    moved.sizes_pt = [s + 2.0 for s in moved.sizes_pt]     # same figure, larger type
    result = styleprofile.compare(base, moved)
    assert result["details"]["sizes"] > 0.15, result["details"]
    # the palette, line widths and page shape did not change and must not pretend to
    assert result["details"]["palette"] == 0.0
    assert result["details"]["lines"] == 0.0
    assert result["details"]["aspect"] == 0.0


def test_shape_is_compared_as_an_aspect_ratio_not_a_width(tmp_path):
    """Two figures of the same width but different height are different compositions."""
    pdf = _fixture_pdf(tmp_path)
    a = styleprofile.StyleProfile.from_pdf(pdf)
    b = styleprofile.StyleProfile.from_pdf(pdf)
    b.height_mm = b.height_mm * 1.25
    result = styleprofile.compare(a, b)
    assert result["details"]["aspect"] > 0.05, result["details"]


def test_profiles_round_trip_through_json(tmp_path):
    pdf = _fixture_pdf(tmp_path)
    prof = styleprofile.StyleProfile.from_pdf(pdf)
    p = prof.save(tmp_path / "profile.json")
    loaded = styleprofile.StyleProfile.load(p)
    assert loaded.summary() == prof.summary()
    again = styleprofile.compare(prof, loaded)
    assert again["distance"] == 0.0


def test_the_first_cut_suggestion_stays_inside_natures_band(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    mod = pytest.importorskip("profile_figure")
    pdf = _fixture_pdf(tmp_path)
    prof = styleprofile.StyleProfile.from_pdf(pdf)
    sug = mod._suggest(prof)
    assert 5.0 <= sug["base_font_pt"] <= 7.0
    assert 5.0 <= sug["tick_label_pt"] <= 7.0
    assert sug["panel_letter_pt"] == pytest.approx(8.0, abs=0.2)
    assert set(sug["palette_okabe"]) <= set(styleprofile.OKABE_RGB)
