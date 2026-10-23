"""A field screen must reserve a value that no other control uses.

WHY THIS EXISTS
    Two models passed every control -- four synthetic plus a real figpipe figure at counts 1, 2, 3,
    4 and 6. Nine of nine. That looked like the answer to the 0.65 vision channel.

    Counts 8 and 9 were then tried, and both models failed both, systematically undercounting by two:

        expect=8 got=6
        expect=9 got=7

    The perfect score was overfitting to the range the controls covered. A control set whose values
    are ALL used in designing the control cannot detect that, and "9 of 9 controls" was true while
    describing a model that cannot count.

    This is the project's recurring defect class -- an aggregate that describes a different set than
    the one beside it -- applied to model screening.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def real():
    import vlm_real_control
    return vlm_real_control


def test_the_real_control_spans_more_than_the_designed_counts(real):
    """1,2,3,4,6 alone cannot detect a model that stops counting at six."""
    counts = sorted(c["expect"] for c in real.real_controls())
    assert max(counts) >= 8, (
        f"the real control tops out at {max(counts)} panels, so a model that undercounts above six "
        f"would pass")
    assert len(counts) >= 5, f"only {len(counts)} real controls; a range needs several points"


def test_every_real_control_declares_a_constructive_answer(real):
    """The expected count must be the INPUT to the drawer, not read back from the image."""
    for c in real.real_controls():
        assert isinstance(c["expect"], int)
        assert c["expect"] >= 1
        assert c["why"], f"{c['name']} does not say why its answer is known"


def test_the_real_controls_are_actually_different_images(real):
    """Five controls that render the same bytes would test one image five times."""
    pngs = {c["expect"]: c["png"] for c in real.real_controls()}
    assert len(set(pngs.values())) == len(pngs), (
        "two real controls render identical bytes, so they are not distinct tests")


def test_ink_grows_with_panel_count(real):
    """A sanity check on the renderer: more panels must mean more ink."""
    import io
    import numpy as np
    from PIL import Image

    inks = []
    for c in real.real_controls():
        arr = np.asarray(Image.open(io.BytesIO(c["png"])).convert("L"))
        inks.append((c["expect"], float((arr < 250).mean())))
    inks.sort()
    for (n1, i1), (n2, i2) in zip(inks, inks[1:]):
        assert i2 >= i1, (
            f"the {n2}-panel figure has less ink ({i2:.4f}) than the {n1}-panel one ({i1:.4f}); the "
            f"renderer is not drawing what the control claims")


def test_a_grid_is_passed_for_counts_that_do_not_fill_the_default(real):
    """figpipe refuses a plate with an empty cell, so 8 and 9 need an explicit grid.

    The drawer is right to refuse: "5 panels do not fill a 2x3 grid, leaving 1 empty cell(s)". A
    control that crashes the drawer tests nothing.
    """
    for n in (8, 9):
        png = real.real_figure(n)
        assert png[:8] == b"\x89PNG\r\n\x1a\n", f"{n} panels did not render"


def test_the_heldout_result_is_recorded():
    """The failure is the finding. It must be on disk, not only in a transcript."""
    path = ROOT / "corpus" / "vlm_heldout_result.json"
    assert path.is_file(), "the held-out screen result was not recorded"
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data, "the held-out result file is empty"
    for model, rows in data.items():
        for row in rows:
            assert "expect" in row and "got" in row and "correct" in row


def test_the_note_records_that_the_perfect_score_was_overfitting():
    """THE LESSON. Without it the next round reads '9 of 9' and believes it."""
    text = (ROOT / "VLM_DECISION.md").read_text(encoding="utf-8")
    assert "overfitting" in text.lower()
    assert "8 got=6" in text or "expect=8" in text, (
        "the note does not show the held-out numbers, so a reader cannot see the failure")
    assert "No local model has passed" in text
