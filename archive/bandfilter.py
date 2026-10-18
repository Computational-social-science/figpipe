"""Physically-impossible band filters. These are the CRITICAL audit's findings, made executable.

WHY THIS MODULE EXISTS
    The adversarial audit found the figure-band detector produced bands that are physically
    impossible:

        height_mm max          = 14,437.1   (A4 is 279 mm tall)
        bands taller than 240mm= 67
        bands with >200 spans  = 10         (these are full pages of body text)
        bands with 0 spans     = 181  (43.1%)

    `derive_rules.clean()` only checked WIDTH and minimum font size. It never checked height,
    aspect ratio, or text density, so a whole page of prose counted as a "figure".

    The audit's own sampling (18 bands, inspected visually) put the error rate near 50 %. By
    the project's own rule in LEARNINGS.md P0, that invalidates every number derived from the
    corpus. This module is the repair: every rejection carries a named reason, and the numbers
    it produces state how much data survived.

WHAT A FIGURE MUST SATISFY (each is a physical or structural constraint, not a taste)
    1. fit on the page            -- a figure cannot be taller or wider than the page
    2. plausible height           -- Nature's max printed figure height is 170 mm; allow
                                     margin, but a 250 mm "figure" is a page
    3. plausible aspect           -- a band 10x taller than wide is a column of text
    4. not a wall of text         -- >200 text spans in one band means prose, not a figure
    5. contain something          -- 0 text spans AND no drawings means nothing was captured
"""
from __future__ import annotations

#: A4 page, in mm. Nothing printed in a paper can exceed it.
PAGE_W_MM = 210.0
PAGE_H_MM = 279.0
#: Nature's stated maximum figure height is 170 mm; a generous ceiling still rejects pages.
MAX_FIGURE_H_MM = 200.0
#: Below this a band is a fragment (a logo, a rule, an axis stub).
MIN_FIGURE_H_MM = 20.0
MIN_FIGURE_W_MM = 60.0
#: A band this much taller than wide is a text column, not a figure.
MAX_ASPECT = 6.0
#: More text spans than this in one band means body copy.
MAX_TEXT_SPANS = 200


def reject_reason(band: dict) -> str | None:
    """Return why a band cannot be a figure, or None if it survives.

    Order matters only for reporting: the first failing constraint is named.
    """
    w = band.get("width_mm")
    h = band.get("height_mm")
    if w is None or h is None:
        return "no_bbox"
    if w > PAGE_W_MM:
        return "wider_than_page"
    if h > PAGE_H_MM:
        return "taller_than_page"
    if h > MAX_FIGURE_H_MM:
        return "implausibly_tall"
    if h < MIN_FIGURE_H_MM:
        return "too_short"
    if w < MIN_FIGURE_W_MM:
        return "too_narrow"
    if h / w > MAX_ASPECT:
        return "text_column_aspect"
    spans = band.get("n_text_spans")
    if spans is not None and spans > MAX_TEXT_SPANS:
        return "wall_of_text"
    if spans == 0 and not band.get("has_drawings", True):
        return "empty_band"
    return None


def filter_bands(bands: list[dict]) -> tuple[list[dict], dict]:
    """Split bands into survivors and a reason-counted rejection tally."""
    kept, reasons = [], {}
    for b in bands:
        why = reject_reason(b)
        if why is None:
            kept.append(b)
        else:
            reasons[why] = reasons.get(why, 0) + 1
    return kept, reasons
