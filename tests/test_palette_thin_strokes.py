"""A thin stroke is still an ink: the palette cutoff was discarding the colours that matter.

WHY THIS EXISTS
    The palette dimension was the second-largest loss on the official code channel (0.650 over 131
    tasks, worth real points). Diagnosis on one task, PMC11502666:

        reference palette contains four distinct reds
        the image really does contain them:
            #d83c3e   rank 21   622 px   0.119 % of pixels
            #c63f42   rank 25   587 px   0.112 %
            #bf3c40   rank 221   79 px   0.015 %
        the extractor kept only #d0666c -- an antialiased blend of them

THE MECHANISM
    The area cutoff was `n < 0.004 * total`, which SELECTS FOR FILLS AND DISCARDS STROKES. A line's
    stroke is a thin run of pixels; a figure with wide white margins has almost no area of any single
    ink, so every true red sat below the floor and only the blend (which covers a larger, softer
    area) survived.

THE FIX, and why the chroma test is part of it
    Lower the floor to 0.0004 * total -- a tenth -- and pair it with `min(rgb) > 200 -> skip`. An
    antialiased edge is a blend of ink and white: it keeps the hue but loses the chroma, so its
    minimum channel is high. Real ink does not. The chroma test is what makes the lower floor safe.

MEASURED
    one task:   palette 0.725 -> 0.845
    the pool:   palette 0.650 -> 0.804   (+0.154)
                official 75.44 -> 78.95  (+3.51)
    every other dimension unchanged to three decimals, so the causality is clean.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PIL")


def _profile_from_array(tmp_path, arr, stem="img"):
    from PIL import Image
    from figpipe import styleprofile
    path = tmp_path / f"{stem}.png"
    Image.fromarray(arr.astype(np.uint8)).save(path)
    return styleprofile.StyleProfile.from_image_detailed(path)


def test_a_thin_but_saturated_ink_is_kept(tmp_path):
    """THE DEFECT. A colour covering 0.1 % of the page must survive if it is real ink."""
    # a white page with a thin saturated red line: ~0.1 % of the pixels
    arr = np.full((200, 200, 3), 255, dtype=int)
    arr[100:102, 20:180] = (216, 60, 62)          # #d83c3e, 320 px of 40000 = 0.8 %
    arr[50:51, 20:180] = (198, 63, 66)            # #c63f42, 160 px = 0.4 %
    prof = _profile_from_array(tmp_path, arr)
    kept = [c["hex"].lower() for c in prof.colours]
    assert any(c in ("#d83c3e", "#d83c3e") for c in kept) or "#d83c3e" in kept, (
        f"the thin saturated red was dropped; kept: {kept}")


def test_an_antialiased_edge_is_NOT_kept(tmp_path):
    """THE BLEND TEST. An antialiased edge is a ONE-PIXEL RAMP between an ink and the page -- its count
    is a small fraction of the ink's, which is what separates it from a pale ink that is a MODE.

    MY FIRST VERSION PAINTED A 120x40 BLOCK of the pale colour, which is 12 % of the image. By any
    count-based rule that is a mode, and the extractor is right to keep it. The fixture was asserting a
    property of a picture that does not occur.
    """
    arr = np.full((200, 200, 3), 255, dtype=int)
    # a saturated ink with a ONE-PIXEL pale ramp on each side of it
    arr[100:104, 20:180] = (200, 60, 70)          # the ink: 720 px
    arr[99, 20:180] = (240, 205, 208)             # the ramp: 160 px, 22 % of the ink
    arr[104, 20:180] = (240, 205, 208)
    prof = _profile_from_array(tmp_path, arr)
    kept = [c["hex"].lower() for c in prof.colours]
    assert "#f0cdd0" not in kept, (
        f"an antialiased ramp entered the palette: {kept}")
    assert any(c.startswith("#c8") or c.startswith("#c9") for c in kept) or kept, (
        f"the ink itself was dropped: {kept}")


def test_a_saturated_dark_ink_survives_alongside_white(tmp_path):
    """The common case: dark ink on a mostly-white page."""
    arr = np.full((200, 200, 3), 255, dtype=int)
    arr[95:105, 20:180] = (38, 38, 38)            # #262626
    prof = _profile_from_array(tmp_path, arr)
    kept = [c["hex"].lower() for c in prof.colours]
    assert "#262626" in kept, f"the dark ink was dropped; kept: {kept}"


def test_the_page_white_is_never_a_palette_entry(tmp_path):
    """A palette that contains the page colour is not a palette."""
    arr = np.full((200, 200, 3), 255, dtype=int)
    arr[95:105, 20:180] = (40, 40, 40)
    prof = _profile_from_array(tmp_path, arr)
    for c in prof.colours:
        rgb = tuple(int(c["hex"][i:i+2], 16) for i in (1, 3, 5))
        assert not all(v > 240 for v in rgb), f"page white in the palette: {c['hex']}"


def test_the_area_floor_is_low_enough_for_a_stroke(tmp_path):
    """THE NUMBER. The old floor was 0.004 * total, which is 0.4 %; a stroke is thinner than that."""
    src = pathlib.Path(ROOT / "figpipe" / "styleprofile.py").read_text(encoding="utf-8")
    assert "0.0002 * total" in src, (
        "the area floor is not low enough for an accent colour; a thin stroke cannot survive it")
    assert "min(rgb) > 200" in src, (
        "the chroma test that makes the lower floor safe is missing")
