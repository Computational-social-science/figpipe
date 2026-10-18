"""The pairing rule must not skip over another picture. Measured and pinned.

WHAT WAS FOUND
    Inspecting page 5 of the 2019 magnetoelectric paper showed the pairing rule pairing a
    figure with a caption two pictures away:

        picture  y 644..732  (right column, top)
        picture  y 443..626  (right column, middle)   <-- this is fig_004
        picture  y 238..431  (right column, lower)
        caption  y  72..231  "Fig. 4 | Performance and area of MESO device..."

    fig_004 was paired with that caption at a gap of 211.7 pt, with a whole picture in between.
    The old rule -- "nearest caption below with horizontal overlap" -- could not see the
    blocker, because distance was the only thing it measured.

MEASURED IMPACT
    Over the whole 84-paper corpus, 11 figure/caption pairs exceed 120 pt. Of those:
        8  have another picture blocking the path   <- the rule is wrong, not the layout
        3  have a clear path                        <- genuine layout variation

    So two thirds of what looked like "layout variation" is a systematic pairing defect. That
    is why a containment test, not a distance threshold, is the right instrument: a threshold
    can be tuned until it passes, a blocker is either there or it is not.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pairing = pytest.importorskip("figpipe.pairing", reason="pairing module absent")

CORPUS = ROOT / "corpus" / "extracted"
#: A gap this large is never normal for a plotted figure whose path is clear (corpus p95 is
#: 26.4 pt), so it is used to select the pairs worth checking.
SUSPICIOUS_PT = 120.0


def _box(l, b, r, t):
    return {"l": l, "b": b, "r": r, "t": t}


# ---------------------------------------------------------------- the rule itself

def test_a_blocker_between_figure_and_caption_is_detected():
    """THE DEFECT, as a unit test. Geometry is the real page-5 case, in points."""
    fig = _box(310.1, 443.2, 549.5, 626.0)
    cap = _box(306.1, 72.2, 558.4, 231.6)
    blocker = _box(310.1, 238.3, 555.0, 431.0)
    assert pairing.path_is_clear(fig, cap, [fig, cap, blocker]) is False
    found = pairing.find_blocker(fig, cap, [fig, cap, blocker])
    assert found is not None and abs(found["b"] - 238.3) < 0.1


def test_a_clear_path_is_clear():
    fig = _box(310.1, 443.2, 549.5, 626.0)
    cap = _box(306.1, 72.2, 558.4, 231.6)
    assert pairing.path_is_clear(fig, cap, [fig, cap]) is True
    assert pairing.find_blocker(fig, cap, [fig, cap]) is None


def test_a_picture_in_the_other_column_does_not_block():
    """Columns are separate stacks; a left-column picture must not block a right-column pair."""
    fig = _box(310.1, 443.2, 549.5, 626.0)
    cap = _box(306.1, 72.2, 558.4, 231.6)
    left_column = _box(50.0, 300.0, 285.0, 420.0)
    assert pairing.path_is_clear(fig, cap, [fig, cap, left_column]) is True


def test_a_caption_above_the_figure_is_not_a_pair():
    fig = _box(300, 400, 550, 600)
    cap = _box(300, 620, 550, 700)
    assert pairing.path_is_clear(fig, cap, [fig, cap]) is False


def test_the_figure_does_not_block_itself():
    fig = _box(310.1, 443.2, 549.5, 626.0)
    cap = _box(306.1, 72.2, 558.4, 231.6)
    assert pairing.path_is_clear(fig, cap, [fig, cap]) is True


# ---------------------------------------------------------------- the corpus measurement

def test_blocked_pairs_are_a_small_minority_of_all_pairs():
    """The rule must not be so strict that it rejects normal layouts.

    Measured: of 11 pairs above 120 pt, 8 are blocked. The corpus has ~270 pairs, so blocked
    large-gap pairs are ~3 % -- a defect worth fixing, not a majority.
    """
    if not CORPUS.is_dir():
        pytest.skip("corpus not extracted")
    checked = blocked = 0
    for d in sorted(CORPUS.iterdir()):
        if not d.is_dir():
            continue
        lay_p, meta_p = d / "layout.json", d / "figures_meta.json"
        if not (lay_p.is_file() and meta_p.is_file()):
            continue
        lay = json.loads(lay_p.read_text(encoding="utf-8"))
        pages = {p.get("page_no"): p for p in lay.get("pages", [])}
        fm = json.loads(meta_p.read_text(encoding="utf-8"))
        for f in fm.get("figures", []):
            bb, cb = f.get("bbox"), f.get("caption_bbox")
            if not (bb and cb):
                continue
            checked += 1
            if bb["b"] - cb["t"] <= SUSPICIOUS_PT:
                continue
            pg = pages.get(f.get("page"))
            if not pg:
                continue
            pics = [e["bbox"] for e in pg.get("elements", [])
                    if e.get("label") in ("picture", "table")]
            if pairing.find_blocker(bb, cb, pics) is not None:
                blocked += 1
    assert checked > 200, f"only {checked} pairs examined"
    share = blocked / checked
    assert share < 0.10, (
        f"{blocked}/{checked} = {100*share:.1f}% of pairs are blocked by another picture. "
        f"If this rises, the pairing rule itself is broken rather than a few papers.")
