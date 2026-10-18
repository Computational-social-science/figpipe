"""Candidate selection must use the reference, not the answer key.

WHY THESE TESTS
    The benchmark showed style transfer helps most tasks and hurts a minority (78 tasks: 49
    improved, 15 worse, 6 ties). A pipeline that always transfers cannot beat one that decides.
    The decision must be legitimate at inference time: only the reference is available, never the
    target. `figpipe/select.py` implements exactly that, and these tests pin the two failure modes
    that would make it dishonest or useless: (1) choosing the candidate that is NOT closest to the
    reference, and (2) flipping on a difference smaller than the measurement resolution.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

select_mod = pytest.importorskip("figpipe.select", reason="selection module absent")
from figpipe import grammar, layout, styleprofile  # noqa: E402

TREND = pd.DataFrame({"x": list(range(20)), "y": [0.1 + 0.02 * i for i in range(20)]})


def _render(tmp_path, name, *, height=90.0):
    """Render one candidate; the ASPECT is the axis the profile measures exactly.

    NOTE: a `rc={"font.size": ...}` override does NOT change the rendered size, because the
    drawers set explicit sizes for labels and ticks -- the first version of this test varied font
    size and measured 0.0 for every candidate. Aspect is a real, measurable difference, so the
    fixtures vary that instead of pretending to vary type size.
    """
    panel = grammar.panel("trend_with_uncertainty", TREND, x="x", y="y", fit="lm",
                          reference=0.2, xlabel="x", ylabel="y")
    fig = grammar.plate([panel], columns=2.0, height_mm=height)
    return pathlib.Path(layout.save(fig, tmp_path / name)[0])


def test_the_closer_candidate_wins(tmp_path):
    reference = styleprofile.StyleProfile.from_pdf(_render(tmp_path, "ref", height=90.0))
    near = _render(tmp_path, "near", height=90.0)
    far = _render(tmp_path, "far", height=150.0)
    picked = select_mod.select(reference, {"near": near, "far": far})
    assert picked["choice"] == "near"
    assert picked["distances"]["near"] < picked["distances"]["far"]
    assert picked["margin"] > 0
    assert "reference is an input" in picked["rule"]


def test_transfer_is_refused_when_the_plain_figure_is_closer(tmp_path):
    reference = styleprofile.StyleProfile.from_pdf(_render(tmp_path, "ref", height=90.0))
    plain = _render(tmp_path, "plain", height=90.0)
    styled = _render(tmp_path, "styled", height=150.0)
    verdict = select_mod.should_transfer(reference, plain, styled)
    assert verdict["transfer"] is False
    assert verdict["choice"] == "plain"


def test_a_negligible_difference_does_not_flip_the_decision(tmp_path):
    reference = styleprofile.StyleProfile.from_pdf(_render(tmp_path, "ref", height=90.0))
    plain = _render(tmp_path, "plain", height=90.0)
    same = _render(tmp_path, "same", height=90.0)
    verdict = select_mod.should_transfer(reference, plain, same, min_margin=0.005)
    assert verdict["transfer"] is False
    assert verdict["margin"] == pytest.approx(0.0, abs=1e-9)


def test_selection_is_reproducible(tmp_path):
    reference = styleprofile.StyleProfile.from_pdf(_render(tmp_path, "ref", height=90.0))
    a = select_mod.select(reference, {"p": _render(tmp_path, "p", height=90.0),
                                      "q": _render(tmp_path, "q", height=150.0)})
    b = select_mod.select(reference, {"p": _render(tmp_path, "p2", height=90.0),
                                      "q": _render(tmp_path, "q2", height=150.0)})
    assert a["choice"] == b["choice"]
    assert a["distances"] == b["distances"]


def test_an_empty_candidate_set_is_refused():
    with pytest.raises(ValueError, match="at least one candidate"):
        select_mod.select(object(), {})


def test_a_missing_candidate_is_an_error_not_a_default(tmp_path):
    reference = styleprofile.StyleProfile.from_pdf(_render(tmp_path, "ref", height=90.0))
    with pytest.raises(FileNotFoundError):
        select_mod.select(reference, {"ghost": tmp_path / "nope.pdf"})


def test_the_shipped_figure_can_never_be_worse_than_always_transferring(tmp_path):
    """A minimum of two numbers cannot exceed either of them -- so this must hold.

    It did NOT hold on the first integration attempt: selection measured PDF profiles while the
    reported distances came from cropped PNGs, and the "shipped" mean came out 0.158 WORSE than
    always-styled. That is impossible by construction and was the signal that the two numbers were
    measured on different instruments. The benchmark now selects on the same cropped PNGs it
    scores with, and this test pins the invariant on the selector itself.
    """
    reference = styleprofile.StyleProfile.from_pdf(_render(tmp_path, "ref", height=90.0))
    plain = _render(tmp_path, "plain", height=150.0)
    styled = _render(tmp_path, "styled", height=90.0)
    picked = select_mod.select(reference, {"plain": plain, "styled": styled})
    always_styled = select_mod.distance_to(reference, styled)["distance"]
    always_plain = select_mod.distance_to(reference, plain)["distance"]
    assert picked["distance"] <= always_styled + 1e-9
    assert picked["distance"] <= always_plain + 1e-9
    assert picked["distance"] == pytest.approx(min(always_styled, always_plain))
