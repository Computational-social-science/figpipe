"""Style transfer must measurably move a rendered figure toward a measured reference.

WHY THIS TEST FILE EXISTS
    The user's demand was a capability that CONVERTS into a better figure, not a report about
    style. `scripts/style_transfer.py` is that conversion: reference profile in, compliant styled
    figure out, with the distance before and after both computed from rendered PDFs. These tests
    pin the mechanics: the derived style stays inside Nature's band, every variant is a legal
    page, the best page is not worse than the default, and the result is reproducible.
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

transfer_mod = pytest.importorskip("style_transfer", reason="style_transfer script absent")
styleprofile = pytest.importorskip("figpipe.styleprofile")
from figpipe import grammar, layout  # noqa: E402

TREND = pd.DataFrame({"Year": range(1990, 2014),
                      "mean": [0.1 + 0.008 * i for i in range(24)]})


def _reference_pdf(tmp_path) -> pathlib.Path:
    panel = grammar.panel("trend_with_uncertainty", TREND, x="Year", y="mean",
                          fit="lm", band="fit", reference=0.0,
                          xlabel="Year", ylabel="z-score")
    fig = grammar.plate([panel], columns=2.0, height_mm=90.0)
    return pathlib.Path(layout.save(fig, tmp_path / "reference")[0])


def test_derived_style_stays_inside_the_submission_band(tmp_path):
    ref = styleprofile.StyleProfile.from_pdf(_reference_pdf(tmp_path))
    # pretend the reference was rendered much larger than a Nature submission
    ref.sizes_pt = [9.5] * 10
    style = styleprofile.style_from_profile(ref)
    rc = style["rc"]
    assert 5.0 <= rc["font.size"] <= 7.0
    assert 5.0 <= rc["axes.labelsize"] <= 7.0
    assert 5.0 <= rc["xtick.labelsize"] <= 7.0
    ref.sizes_pt = [4.0] * 10
    assert styleprofile.style_from_profile(ref)["rc"]["font.size"] == 5.0


def test_palette_comes_from_the_reference_and_drops_page_white(tmp_path):
    ref = styleprofile.StyleProfile.from_pdf(_reference_pdf(tmp_path))
    palette = styleprofile.palette_from_profile(ref, n=3)
    assert palette, "the reference's colours were not extracted"
    for h in palette:
        rgb = styleprofile._rgb(h)
        assert not all(c > 240 for c in rgb), f"page white leaked into the palette: {h}"


def test_the_derived_height_matches_the_reference_aspect(tmp_path):
    """The derived height depends on the CANVAS WIDTH, not on a hard-coded 183 mm.

    Getting this wrong is not cosmetic: applying a 183 mm-derived height to an 89 mm
    single-column figure doubles the aspect error, which the benchmark measured as an aspect
    component of 0.75 on every Field 2D task versus 0.001 on two-column Line tasks.
    """
    ref = styleprofile.StyleProfile.from_pdf(_reference_pdf(tmp_path))
    ref.width_mm, ref.height_mm = 183.0, 122.0
    assert styleprofile.style_from_profile(ref, columns=2.0)["height_mm"] == pytest.approx(
        122.0, abs=0.5)
    # the same reference on a one-column canvas must give half the height (89/1.5 = 59.3,
    # clamped by the 60 mm floor)
    assert styleprofile.style_from_profile(ref, columns=1.0)["height_mm"] == pytest.approx(
        60.0, abs=0.5)
    ref.height_mm = 40.0        # absurdly wide reference: the lower bound must win
    assert styleprofile.style_from_profile(ref)["height_mm"] == pytest.approx(60.0, abs=0.1)


def test_transfer_improves_or_holds_and_audits_the_best_page(tmp_path):
    ref = styleprofile.StyleProfile.from_pdf(_reference_pdf(tmp_path))
    panels = [grammar.panel("trend_with_uncertainty", TREND, x="Year", y="mean",
                            fit="lm", band="fit", reference=0.0,
                            xlabel="Year", ylabel="z-score")]
    layout_kw = {"columns": 2.0, "height_mm": 90.0, "letters": True,
                 "margins": {"bottom": 12.0}}
    report = transfer_mod.transfer(panels, layout_kw, ref, out_dir=tmp_path / "out",
                                   panel_style="single")
    assert report["best"]["distance"]["distance"] <= report["baseline"]["distance"]["distance"]
    assert len(report["variants"]) == 8
    for v in report["variants"]:
        assert v["hard_findings"] == [], f"variant {v['variant']} broke the format: {v}"
        assert v["collisions"] == 0
    assert (tmp_path / "out" / "style_transfer_best.pdf").is_file()
    assert report["score"]["dimensions"], "the NPF-style score was not produced"
    assert report["score"]["dimensions"]["execution_pass_rate"]["value"] == 1.0


def test_transfer_is_reproducible(tmp_path):
    ref = styleprofile.StyleProfile.from_pdf(_reference_pdf(tmp_path))
    panels = [grammar.panel("trend_with_uncertainty", TREND, x="Year", y="mean",
                            fit="lm", band="fit", reference=0.0)]
    layout_kw = {"columns": 2.0, "height_mm": 90.0, "letters": True,
                 "margins": {"bottom": 12.0}}
    a = transfer_mod.transfer(panels, layout_kw, ref, out_dir=tmp_path / "a",
                              panel_style="single")
    b = transfer_mod.transfer(panels, layout_kw, ref, out_dir=tmp_path / "b",
                              panel_style="single")
    assert a["best"]["variant"] == b["best"]["variant"]
    assert a["best"]["distance"]["distance"] == b["best"]["distance"]["distance"]
