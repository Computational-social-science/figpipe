"""The reader study must produce material a human can actually look at.

WHY THIS EXISTS
    `corpus/e2e/style_validation.json` says, in its own words:

        No human judgement was collected. This is a deterministic proxy that removes the "the metric was
        never tested at all" gap; IT DOES NOT REPLACE A READER STUDY.

    and

        This tests ORDERING, not expert preference: it can refute a blind or inverted metric, it cannot
        establish that the closer figure is the better figure.

    So the metric's central claim has never been tested by a reader. `scripts/reader_study.py` builds the
    material and scores the result; the judgement is the input and cannot be automated.

THE DEFECTS THIS FILE PINS (both measured while building it)
    1. The study sources are `corpus/extracted/<paper>/figures/fig_001.png` -- PNG under `figures/`, not
       the PDF the stem implied. `StyleProfile.from_pdf` raised FileNotFoundError for every pair.
    2. `render_transfer` returns a PDF. The first version COPIED it to a `.png` name, so the "image" a
       rater was asked to judge began with `%PDF-1.4` and no viewer opens it (PIL:
       UnidentifiedImageError). **A study harness that cannot produce a viewable image is a study
       nobody can take.**
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pd = pytest.importorskip("pandas")


@pytest.fixture(scope="module")
def study():
    import reader_study
    return reader_study


def test_a_study_source_resolves_to_a_real_file(study):
    """DEFECT 1. The stem in style_validation.json must resolve to the PNG on disk."""
    data = json.loads((ROOT / "corpus" / "e2e" / "style_validation.json").read_text(encoding="utf-8"))
    pairs = data.get("pairs") or []
    if not pairs:
        pytest.skip("no pairs recorded")
    resolved = study._resolve(pairs[0]["reference"])
    assert resolved.is_file(), (
        f"the study source {pairs[0]['reference']!r} resolved to {resolved}, which does not exist")


def test_a_rendered_candidate_is_a_real_image(study, tmp_path):
    """DEFECT 2. A PDF renamed to .png is not an image, and a rater cannot open it."""
    import validate_style_metric as V
    from figpipe import styleprofile

    data = json.loads((ROOT / "corpus" / "e2e" / "style_validation.json").read_text(encoding="utf-8"))
    pairs = data.get("pairs") or []
    if not pairs:
        pytest.skip("no pairs recorded")
    src = study._resolve(pairs[0]["reference"])
    if not src.is_file():
        pytest.skip("source absent")
    prof = study._profile(src)
    pdf = V.render_transfer(prof, tmp_path / "cand")
    out = study._rasterise(pathlib.Path(pdf), tmp_path / "cand.png")
    head = out.read_bytes()[:8]
    assert head.startswith(b"\x89PNG"), (
        f"the study's candidate is not a PNG (first bytes {head!r}); a rater cannot open it")
    from PIL import Image
    with Image.open(out) as im:
        assert im.size[0] > 100 and im.size[1] > 100, im.size


def test_the_answer_sheet_carries_no_answers(study, tmp_path, monkeypatch):
    """A BLIND STUDY WITH THE KEY IN THE SHEET IS NOT BLIND."""
    monkeypatch.setattr(study, "STUDY", tmp_path)
    monkeypatch.setattr(study, "ANSWERS", tmp_path / "answers.csv")
    monkeypatch.setattr(study, "KEY", tmp_path / "key.json")
    monkeypatch.setattr(study, "SHEET", tmp_path / "README.txt")
    if study.build(2) != 0:
        pytest.skip("cannot build a study here")
    sheet = (tmp_path / "answers.csv").read_text(encoding="utf-8")
    for word in ("left", "right", "A", "B"):
        # the header may mention the allowed values; a DATA row must not
        for line in sheet.splitlines()[1:]:
            if line.strip():
                assert word not in line.split(",", 1)[1], (
                    f"the answer sheet pre-fills {word!r} in a data row: {line!r}")
    key = json.loads((tmp_path / "key.json").read_text(encoding="utf-8"))
    assert key, "the key is empty but the sheet has rows"


def test_scoring_a_blank_sheet_refuses(study, tmp_path, monkeypatch):
    """A STUDY WITH NO JUDGEMENTS MEASURES NOTHING AND MUST SAY SO."""
    monkeypatch.setattr(study, "STUDY", tmp_path)
    monkeypatch.setattr(study, "ANSWERS", tmp_path / "answers.csv")
    monkeypatch.setattr(study, "KEY", tmp_path / "key.json")
    (tmp_path / "answers.csv").write_text("pair,your_choice\np01,\n", encoding="utf-8")
    (tmp_path / "key.json").write_text(json.dumps({"p01": {"matched_side": "left",
                                                           "metric_picks": "B"}}), encoding="utf-8")
    assert study.score() == 2, "a blank sheet must be refused, not scored as 0 %"


def test_the_metric_states_it_is_not_human_validation():
    """THE CLAIM THE STUDY EXISTS TO CLOSE. If this field disappears, the gap is being hidden."""
    data = json.loads((ROOT / "corpus" / "e2e" / "style_validation.json").read_text(encoding="utf-8"))
    text = str(data.get("not_human_validation") or "")
    assert "human judgement" in text.lower(), (
        "style_validation.json no longer states that no human judgement was collected")
    assert "does not replace" in text.lower() or "not replace" in text.lower(), (
        "style_validation.json no longer states that the proxy does not replace a reader study")
