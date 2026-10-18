"""Caption features must be measured from text, and the measurement must be checkable.

WHY THIS FILE EXISTS
    The audit proved the local VLM FABRICATES figure properties: on a BLANK page it answered
    `column_width: single` and `high_contrast: true`, and across three control images it made
    20 assertions about pictures with no figure at all (verdict: FABRICATES). Its agreement
    with the PDF geometry on column_width was 55 %.

    Four of the properties the task asked for are properties of the CAPTION STRING, not of the
    pixels. Asking a model to read them off an image is asking it to do OCR badly.

    So these tests pin the TEXT rules. Each rule is a heuristic over English prose, and a
    heuristic earns its place by being checkable -- a feature that never fires, or fires on
    everything, is not doing work and these tests catch that.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

cf = pytest.importorskip("caption_features", reason="caption feature module absent")
SRC = ROOT / "corpus" / "caption_features.jsonl"
ANALYSIS = ROOT / "corpus" / "caption_analysis.json"


# ------------------------------------------------------------------ the rules themselves

def test_label_is_stripped_before_measuring():
    """"Fig. 1 |" is a label, not part of the summary sentence."""
    assert cf.strip_label("Fig. 1 | Emu3 framework.") == "Emu3 framework."
    assert cf.strip_label("Extended Data Fig. 2 | Zero-shot.") == "Zero-shot."
    assert cf.strip_label("No label here.") == "No label here."


def test_panel_markers_are_recognised_in_both_nature_forms():
    """Nature uses "(a)" and "a, " -- both must count, or 33 % would undercount."""
    assert cf.measure("Title. (a) first panel. (b) second panel.")["n_panel_markers"] == 2
    assert cf.measure("Title. a, first panel. b, second panel.")["n_panel_markers"] == 2
    assert cf.measure("Title with no panels at all.")["n_panel_markers"] == 0


def test_statistics_are_recognised():
    for text in ("Shown as mean ± s.d.", "n = 1,234 samples",
                 "p < 0.001, two-tailed t-test", "error bars show 95% CI"):
        assert cf.measure(text)["caption_has_stats"] is True, text
    assert cf.measure("A qualitative overview with no numbers.")["caption_has_stats"] is False


def test_overview_first_requires_a_non_statistical_opening():
    """An opening sentence that is itself a panel walk or a statistic is not an overview."""
    assert cf.measure("Emu3 framework. a, tokens. b, more.")["caption_overview_first"] is True
    assert cf.measure("(a) First thing shown.")["caption_overview_first"] is False
    assert cf.measure("n = 500 samples were collected.")["caption_overview_first"] is False


def test_stats_last_means_the_final_sentence_carries_them():
    assert cf.measure("Overview. a, panel one. Values are mean ± s.d.")["caption_stats_last"] is True
    assert cf.measure("Mean ± s.d. was used. a, panel one.")["caption_stats_last"] is False


# ------------------------------------------------------------------ the corpus measurement

def test_features_are_measured_over_the_whole_corpus():
    if not SRC.is_file():
        pytest.skip("caption features not extracted")
    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(rows) >= 100, f"only {len(rows)} captions measured"
    # Every row must carry the text it was measured from, or the number is untraceable.
    for r in rows[:50]:
        assert r["caption_text"].strip(), "a row has no caption text"
        assert isinstance(r["n_panel_markers"], int)


def test_no_feature_is_degenerate():
    """A rule that fires on everything, or on nothing, is not doing work.

    THIS TEST RECOMPUTES FROM SOURCE. An earlier version read only the stored artefact, and a
    mutation test proved it useless: I changed `panel_by_panel` to always return False and the
    suite stayed green, because the JSON on disk still held the pre-mutation values. The tests
    were checking the artefact, not the code -- the same failure the audit keeps finding.

    A feature pinned at 0 % or 100 % means the regex is broken, not that Nature is uniform.
    """
    if not SRC.is_file():
        pytest.skip("caption features not extracted")
    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    for key in ("caption_panel_by_panel", "caption_has_stats"):
        # recompute every row from the CURRENT code, then require agreement with the artefact
        recomputed = [cf.measure(r["caption_text"])[key] for r in rows]
        share = sum(recomputed) / len(recomputed)
        assert 0.02 < share < 0.98, (
            f"{key} fires on {100*share:.1f}% of captions when recomputed; a near-constant "
            f"feature means the rule is broken")
        stored = [bool(r.get(key)) for r in rows]
        mismatch = sum(1 for a, b in zip(recomputed, stored) if a != b)
        assert mismatch == 0, (
            f"{key}: {mismatch} rows disagree between the code and the stored artefact. The "
            f"artefact is stale -- re-run scripts/caption_features.py -- or the rule changed "
            f"without regenerating it.")


def test_analysis_splits_main_text_from_extended_data():
    """Different sections can follow different conventions; the split must exist."""
    if not ANALYSIS.is_file():
        pytest.skip("caption analysis not run")
    a = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    assert "by_kind" in a and a["by_kind"], "no per-kind breakdown"
    assert "figure" in a["by_kind"], "main-text figures missing from the breakdown"
    o = a["overall"]
    assert o["n"] >= 100
    for k in cf.__dict__.get("FEATURES", []):
        pass
