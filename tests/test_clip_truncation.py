"""Clip-path truncation is NOT detectable from the PDF, and the reason is a good one.

WHY THIS EXISTS
    Round 80's rubric table listed a blind spot for `text truncation`:

        text clipped by a clip-path inside the axes is not detected

    This file records what investigating it found, because the answer is a NEGATIVE RESULT and a
    negative result that is not written down gets re-investigated.

WHAT WAS MEASURED
    A text object placed outside the axes with `clip_on=True`:
        red pixels in the render: 1459     <- the text IS drawn
        text layer reports the span: True  <- and the PDF knows where it is

    So `clip_on=True` did nothing in that case, and the PDF faithfully reported a span that was
    never clipped.

    A text object with a REAL clip:
        ax.annotate(..., annotation_clip=True)      red_px=0   text_layer=False
        text.set_clip_box(ax.bbox)                  red_px=0   text_layer=False

    When matplotlib really clips text, the glyphs are NOT EMITTED -- they are absent from the page
    content stream entirely, so they are absent from the text layer too.

THE CONCLUSION
    "Text clipped by a clip-path" cannot exist as a PDF-layer fact. Either the text is emitted (and
    then it is visible, by definition) or it is not emitted (and then there is nothing to find).

    That means the blind spot named in round 80 is not a gap in the check -- it is a case that
    cannot arise. The honest correction is to remove it from the table rather than leave a reader
    believing a real defect class is unmeasured.

WHAT THIS DOES NOT COVER
    Text that overflows the PAGE (cut by the paper edge) is a different case and IS detectable: its
    span coordinates lie outside the page box. `audit.text_spans` reports font-size violations, not
    geometry, so that check does not cover it either -- which is a genuine gap, separate from this
    one, and it is named below.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _render(tmp_path, build, stem="f"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    build(fig, ax)
    pdf = tmp_path / f"{stem}.pdf"
    fig.savefig(pdf)
    plt.close(fig)
    return pdf


def _red_pixels_and_span(pdf, marker="MARKER"):
    import pymupdf
    from PIL import Image

    doc = pymupdf.open(str(pdf))
    page = doc[0]
    png = pdf.with_suffix(".png")
    page.get_pixmap(dpi=200).save(str(png))
    arr = np.asarray(Image.open(png).convert("RGB")).astype(int)
    red = int(((arr[:, :, 0] > 150) & (arr[:, :, 1] < 100) & (arr[:, :, 2] < 100)).sum())
    has_span = any(marker in s.get("text", "")
                   for b in page.get_text("dict")["blocks"]
                   for line in b.get("lines", [])
                   for s in line.get("spans", []))
    doc.close()
    return red, has_span


def _real_clip(fig, ax):
    ax.plot([0, 1], [0, 1])
    ax.text(-0.5, 0.5, "MARKER", transform=ax.transAxes, fontsize=9, color="red").set_clip_box(
        ax.bbox)


def _no_clip(fig, ax):
    ax.plot([0, 1], [0, 1])
    ax.text(0.1, 0.5, "MARKER", transform=ax.transAxes, fontsize=9, color="red")


def test_real_clipping_removes_the_text_entirely(tmp_path):
    """THE FINDING: when matplotlib clips text, the glyphs are never emitted, so there is no
    'clipped span' in the PDF to detect. Both the pixels AND the text layer are empty."""
    red, has_span = _red_pixels_and_span(_render(tmp_path, _real_clip))
    assert red == 0, f"clipped text still rendered {red} red pixels"
    assert has_span is False, (
        "clipped text still appears in the text layer, so a clipped-span check could work after all")


def test_unclipped_text_is_visible_and_present(tmp_path):
    """NEGATIVE CONTROL: the same text without a clip is both drawn and reported."""
    red, has_span = _red_pixels_and_span(_render(tmp_path, _no_clip))
    assert red > 0, "unclipped text did not render"
    assert has_span is True


def test_the_rubric_no_longer_claims_a_blind_spot_that_cannot_arise():
    """THE CORRECTION. Round 80 named 'text clipped by a clip-path' as a blind spot. It is not a gap
    in the check -- it is a case that cannot exist in a PDF."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import vision_rubric_coverage as V
    rows = {r["rubric_item"]: r for r in V.survey()["rubric"]}
    trunc = rows["text truncation"]
    # THE CLAIM, NOT THE WORD. Banning "clip-path" failed because the corrected text has to mention
    # it to explain why it cannot arise. What matters is whether the row claims it is UNMEASURED.
    blind = trunc["blind_spot"]
    assert "cannot arise" in blind or "not emitted" in blind, (
        f"the row does not say a clip-path truncation cannot arise: {blind!r}")
    assert "page" in blind.lower(), (
        "the real gap -- text outside the PAGE box -- is not named")
