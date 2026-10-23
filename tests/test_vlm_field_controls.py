"""A local VLM may only be trusted on a field whose controls it passes.

WHY THIS EXISTS
    `VLM_DECISION.md` set the condition: build a field-level control set (blank, noise, text-only,
    and a figure whose true value is known by construction), require the model to answer all of them
    before its labels count, and use the labels as a second opinion that is CHECKED -- never as an
    answer key.

    This file pins the harness that does the screening, not the model's verdict. The verdict is
    data: `gemma3:12b` answered 3 of 4 and failed on a pure white page, reporting one panel.

WHY THE CONTROLS ARE GENERATED, NOT STORED
    A stored control image can drift from the answer recorded beside it. These are rendered from a
    panel count, so "the answer is 3" is true by construction and cannot rot.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def vlm():
    import vlm_field_controls
    return vlm_field_controls


def test_there_are_four_controls(vlm):
    ctl = vlm.controls()
    assert len(ctl) == 4
    names = {c["name"] for c in ctl}
    assert names == {"blank", "noise", "one-panel", "three-panel"}


def test_every_control_declares_its_answer(vlm):
    for c in vlm.controls():
        assert isinstance(c["expect"], int), f"{c['name']} has no integer answer"
        assert c["why"], f"{c['name']} does not say what it tests"


def test_the_blank_control_is_actually_blank(vlm):
    """THE CONTROL THAT CAUGHT THE MODEL. If this image has ink, it is not a blank control."""
    from PIL import Image
    import io
    import numpy as np

    blank = next(c for c in vlm.controls() if c["name"] == "blank")
    assert blank["expect"] == 0
    img = Image.open(io.BytesIO(blank["png"])).convert("L")
    arr = np.asarray(img)
    assert len(np.unique(arr)) == 1, (
        f"the blank control has {len(np.unique(arr))} grey levels; it must have exactly one")
    assert float((arr < 250).mean()) == 0.0, "the blank control contains ink"


def test_the_panel_controls_render_their_declared_count(vlm):
    """`expect` must be true BY CONSTRUCTION, or the control tests nothing."""
    for c in vlm.controls():
        if c["name"] in ("one-panel", "three-panel"):
            assert c["png"][:8] == b"\x89PNG\r\n\x1a\n", f"{c['name']} is not a PNG"
            assert c["expect"] in (1, 3)


def test_a_missing_integer_is_not_read_as_zero(vlm):
    """A reply with no digits must yield None, never 0 -- otherwise silence passes the blank test."""
    assert vlm._first_int("I cannot tell") is None
    assert vlm._first_int("") is None
    assert vlm._first_int("There are 3 panels") == 3
    assert vlm._first_int("0") == 0


def test_a_failed_control_fails_the_whole_screen(vlm, monkeypatch):
    """ONE failure is a fail. 'Three of four' is not a pass and the record must say so."""
    fake = [
        {"name": "a", "expect": 0, "png": b"", "why": "t"},
        {"name": "b", "expect": 1, "png": b"", "why": "t"},
    ]
    monkeypatch.setattr(vlm, "controls", lambda: fake)
    answers = iter(["0", "7"])
    monkeypatch.setattr(vlm, "_ask", lambda *a, **k: next(answers))
    out = vlm.run("stub-model")
    assert out["n_correct"] == 1
    assert out["passed"] is False
    assert "must NOT be trusted" in out["verdict"]


def test_an_all_correct_screen_passes(vlm, monkeypatch):
    fake = [{"name": "a", "expect": 0, "png": b"", "why": "t"},
            {"name": "b", "expect": 2, "png": b"", "why": "t"}]
    monkeypatch.setattr(vlm, "controls", lambda: fake)
    answers = iter(["0", "2"])
    monkeypatch.setattr(vlm, "_ask", lambda *a, **k: next(answers))
    out = vlm.run("stub-model")
    assert out["passed"] is True
    assert out["n_correct"] == 2


def test_a_model_error_is_recorded_not_swallowed(vlm, monkeypatch):
    """A connection failure is a result, not a crash and not a pass."""
    monkeypatch.setattr(vlm, "controls",
                        lambda: [{"name": "a", "expect": 0, "png": b"", "why": "t"}])

    def boom(*a, **k):
        raise OSError("connection refused")

    monkeypatch.setattr(vlm, "_ask", boom)
    out = vlm.run("stub-model")
    assert out["passed"] is False
    assert out["controls"][0]["error"], "a model error was not recorded"
    assert "OSError" in out["controls"][0]["error"]
