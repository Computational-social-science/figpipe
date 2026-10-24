"""The honest mode must not read the reference code. Round 99 did, and it was worth 9 points.

WHY THIS EXISTS
    `score_official.py` has three modes:

        naive   matplotlib defaults -- the BASELINE a claim must beat
        code    style copied from the reference CODE -- a CEILING, documented as a tautology:
                "measures can the emitter copy a spec, not can the pipeline infer a style"
        image   style inferred from the reference IMAGE -- HONEST MODE, "what a real user has"

    In round 99 I read `extract_style_features(ref_code)["linewidth"]` inside the shared code that
    runs AFTER the mode branch, and wrote the value into `style`. So the HONEST number contained a
    value copied from the reference CODE.

THE COST, measured: on a reference with lw=2.25, the honest candidate scores 48.66 and the
code-copied one 98.66. Across 149 tasks that was the +9.01 I reported. The honest number went
82.02 -> 91.03 -> back to 82.02 once removed.

WHY THE ASPECT IS DIFFERENT AND STAYS
    `style_from_image_profile` returns `figure_aspect` derived FROM THE IMAGE DIMENSIONS -- its
    docstring lists aspect among what "a raster CAN give". The canvas height is 183.0 / that aspect.
    The value is the same kind of quantity either way; the SOURCE is what the premise is about.

WHAT THIS FILE PINS
    No call to `extract_style_features(ref_code)` may appear as CODE (not a comment) in the honest
    branch, and the image profile must be what supplies the style.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "score_official.py"


def _honest_segment() -> str:
    """The source between the HONEST MODE marker and the next top-level def."""
    text = SOURCE.read_text(encoding="utf-8")
    i = text.find("HONEST MODE")
    assert i > 0, "the HONEST MODE marker is gone; this test cannot locate the branch"
    j = text.find("\ndef ", i)
    return text[i:j if j > i else len(text)]


def _code_only(segment: str) -> str:
    """Strip comments so a docstring that MENTIONS the forbidden call does not fail the test."""
    return "\n".join(line.split("#")[0] for line in segment.splitlines())


def test_the_honest_mode_does_not_read_the_reference_code():
    """THE DEFECT. Reading it makes the honest number partly tautological."""
    code = _code_only(_honest_segment())
    assert "extract_style_features(ref_code)" not in code, (
        "the honest (image) mode reads the reference CODE; the number it produces is not the "
        "benchmark's premise")
    assert "style_from_features" not in code, (
        "the honest mode calls style_from_features, which is the ceiling mode's helper")


def test_the_honest_mode_uses_the_image_profile():
    """THE OTHER DIRECTION: it must actually derive the style from the image."""
    code = _code_only(_honest_segment())
    assert "style_from_image_profile" in code, (
        "the honest mode does not use the image profile, so it is not measuring image inference")


def test_the_image_profile_reports_linewidth_as_unavailable():
    """THE REASON the dimension cannot be won honestly. If this ever changes, the honest score
    should change with it -- and this test will say so."""
    sys.path.insert(0, str(ROOT))
    from figpipe import codegen
    import inspect

    src = inspect.getsource(codegen.style_from_image_profile)
    assert '"linewidth": None' in src, (
        "style_from_image_profile now returns a linewidth; the honest mode could use it and this "
        "whole premise discussion should be revisited")


def test_the_canvas_height_comes_from_the_image_aspect():
    """The aspect STAYS, and it comes from the image profile rather than the reference code.

    The height is `183.0 / aspect`, and the aspect is `style["figure_aspect"]` -- a value
    `style_from_image_profile` computed from the image dimensions.
    """
    code = _code_only(_honest_segment())
    assert "figure_aspect" in code, (
        "the honest mode no longer uses an aspect at all; the canvas height would be a constant")
    assert "_ref_aspect" in code, "the aspect is not threaded into the height computation"
    # and it must be read from `style`, not from the reference features
    assert 'style or {}' in code or 'style.get(' in code, (
        "the aspect is not taken from the image-derived style dict")
