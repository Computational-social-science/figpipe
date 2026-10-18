"""Caption pairing must not skip over another picture.

THE DEFECT, FOUND BY INSPECTING ONE PAGE
    Page 5 of the 2019 magnetoelectric paper, in PDF points (origin bottom-left):

        picture  y  245..733  x  50..285     left column, tall
        picture  y  644..732  x 309..539     right column, top
        picture  y  443..626  x 310..549     right column, middle   <-- fig_004
        picture  y  238..431  x 310..555     right column, lower
        caption  y  146..239  x  42..289     "Fig. 3 | Energy and delay of the MESO device..."
        caption  y   72..231  x 306..558     "Fig. 4 | Performance and area of MESO device..."

    fig_004 was paired with "Fig. 4" at a gap of 211.7 pt -- but ANOTHER PICTURE (y 238..431)
    sits between them. The caption that actually belongs to fig_004 is the caption of the
    picture below it, i.e. the pairing is off by one picture.

    The existing rule -- "nearest caption below with horizontal overlap" -- cannot see this,
    because it never asks whether something blocks the path.

THE RULE ADDED HERE
    A caption may pair with a figure only when NO other picture lies strictly between the
    figure's bottom and the caption's top, within the same horizontal band. This is a
    containment test, not a distance test: it does not need a threshold, so it cannot be tuned
    to pass.
"""
from __future__ import annotations

#: Two boxes share a horizontal band when their x-ranges overlap by at least this fraction of
#: the narrower one. Column-adjacent items are separate; stacked items in one column are not.
H_OVERLAP_MIN = 0.35


def _x_overlap(a: dict, b: dict) -> float:
    lo = max(a["l"], b["l"])
    hi = min(a["r"], b["r"])
    if hi <= lo:
        return 0.0
    narrower = min(a["r"] - a["l"], b["r"] - b["l"])
    return (hi - lo) / narrower if narrower > 0 else 0.0


def shares_column(fig: dict, cap: dict) -> bool:
    """Do the figure and caption sit in the same horizontal band?"""
    return _x_overlap(fig, cap) >= H_OVERLAP_MIN


def path_is_clear(fig: dict, cap: dict, pictures: list[dict]) -> bool:
    """True when no other picture sits between this figure's bottom and this caption's top.

    `pictures` are the same-kind boxes on the page. The figure itself must be excluded by the
    caller or by identity, otherwise every figure blocks its own path.
    """
    if not shares_column(fig, cap):
        return False
    bottom, top = fig["b"], cap["t"]
    if top >= bottom:
        return False                       # caption is not below the figure
    for p in pictures:
        if p is fig:
            continue
        if abs(p["b"] - fig["b"]) < 0.01 and abs(p["t"] - fig["t"]) < 0.01 \
                and abs(p["l"] - fig["l"]) < 0.01:
            continue                       # same box
        # a blocker occupies space strictly between the two, in the same column
        if p["t"] <= bottom and p["b"] >= top and shares_column(fig, p):
            return False
    return True


def find_blocker(fig: dict, cap: dict, pictures: list[dict]) -> dict | None:
    """The picture that blocks a pairing, for reporting. None when the path is clear."""
    if not shares_column(fig, cap):
        return {"reason": "different column"}
    bottom, top = fig["b"], cap["t"]
    if top >= bottom:
        return {"reason": "caption is above the figure"}
    for p in pictures:
        if p is fig:
            continue
        if p["t"] <= bottom and p["b"] >= top and shares_column(fig, p):
            return p
    return None
