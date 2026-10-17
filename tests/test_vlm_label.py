"""Tests for the VLM style annotator: the defects that would make its labels worthless.

WHY THESE TESTS LOOK LIKE THIS
    The annotator's output is training data, and the failure modes here are not crashes -- they
    are quiet corruptions. A parser that accepts anything, a null that gets coerced to false, a
    resume that re-labels or skips the wrong records, a control that is reported as passing when
    it did not fire: each of these produces a corpus that looks fine and is wrong.

    So each test is written from one of those failures. The tests do not call Ollama; the model is
    a network dependency and a test suite that needs a GPU server is a test suite that gets
    skipped. Everything the model's answers flow through afterwards -- parse, validate, resume,
    agreement, control scoring -- is deterministic and is tested here.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "vlm_label.py"


def load_module():
    """Import scripts/vlm_label.py, which is a script rather than a package module."""
    spec = importlib.util.spec_from_file_location("vlm_label_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vlm():
    return load_module()


# ---------------------------------------------------------------------------------------------
# JSON extraction: the model must not be able to make a record vanish by adding a code fence.
# ---------------------------------------------------------------------------------------------
def test_extract_json_plain(vlm):
    assert vlm.extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_code_fence(vlm):
    """A fenced reply is a formatting failure, not an unparseable answer.

    Scoring it as a parse failure would inflate the failure rate and hide that the model
    actually answered; the fence is stripped and the answer is kept.
    """
    assert vlm.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert vlm.extract_json('```\n{"a": 2}\n```') == {"a": 2}


def test_extract_json_surrounded_by_prose(vlm):
    got = vlm.extract_json('Here is the answer:\n{"figure_type": "bar"}\nHope that helps!')
    assert got == {"figure_type": "bar"}


def test_extract_json_nested_and_strings_with_braces(vlm):
    """A brace inside a string must not end the object early."""
    got = vlm.extract_json('{"palette_description": "a } b", "panel_count": 2}')
    assert got["palette_description"] == "a } b"
    assert got["panel_count"] == 2


@pytest.mark.parametrize("bad", ["", "no json here", "[1, 2, 3]", "{unclosed", None])
def test_extract_json_raises_on_no_object(vlm, bad):
    with pytest.raises(ValueError):
        vlm.extract_json(bad)


# ---------------------------------------------------------------------------------------------
# Validation: a wrong type must become null AND be recorded, never silently dropped or coerced
# to a plausible-looking value.
# ---------------------------------------------------------------------------------------------
def test_validate_all_fields_present(vlm):
    labels, repairs, unknown = vlm.validate({})
    assert set(labels) == set(vlm.FIELDS)
    assert all(v is None for v in labels.values())
    assert len(repairs) == len(vlm.FIELDS)
    assert unknown == []


def test_validate_rejects_out_of_enum(vlm):
    labels, repairs, _ = vlm.validate({"figure_type": "not_a_real_type"})
    assert labels["figure_type"] is None
    assert any("figure_type" in r for r in repairs)


def test_validate_accepts_valid_enum_case_insensitively(vlm):
    labels, _, _ = vlm.validate({"figure_type": "Heatmap"})
    assert labels["figure_type"] == "heatmap"


def test_validate_bool_coercion_is_strict(vlm):
    """'false' must not become True, and a nonsense string must not become False.

    The failure this pins: a bool("false")-style coercion turns a "false" into True, which
    silently inverts every binary style judgement in the corpus.
    """
    labels, _, _ = vlm.validate({"colorblind_safe": "false"})
    assert labels["colorblind_safe"] is False
    labels, repairs, _ = vlm.validate({"colorblind_safe": "maybe"})
    assert labels["colorblind_safe"] is None
    assert any("colorblind_safe" in r for r in repairs)


def test_validate_bool_does_not_accept_arbitrary_int(vlm):
    """Only 0/1 are booleans; 2 is not a boolean and must not be truthy-coerced."""
    labels, repairs, _ = vlm.validate({"font_uniform": 2})
    assert labels["font_uniform"] is None
    assert any("font_uniform" in r for r in repairs)


def test_validate_int_range_enforced(vlm):
    labels, repairs, _ = vlm.validate({"saturated_color_count": 999})
    assert labels["saturated_color_count"] is None
    assert any("saturated_color_count" in r for r in repairs)


def test_validate_int_from_numeric_string(vlm):
    labels, _, _ = vlm.validate({"panel_count": "4"})
    assert labels["panel_count"] == 4


def test_validate_null_is_preserved_not_repaired(vlm):
    """A null the model chose is data, not a defect; it must not appear as a repair."""
    labels, repairs, _ = vlm.validate({"figure_type": None})
    assert labels["figure_type"] is None
    assert not any(r.startswith("figure_type") for r in repairs)


def test_validate_reports_unknown_keys(vlm):
    _, _, unknown = vlm.validate({"figure_type": "bar", "made_up_field": 1})
    assert unknown == ["made_up_field"]


# ---------------------------------------------------------------------------------------------
# Resume: the jsonl is the state. These are the two ways it goes wrong.
# ---------------------------------------------------------------------------------------------
def test_key_is_stable_and_model_specific(vlm):
    a = {"image": "x.png", "model": "gemma3:12b", "prompt_sha256": "abc"}
    b = {"image": "x.png", "model": "gemma3:4b", "prompt_sha256": "abc"}
    assert vlm.key_of(a) == vlm.key_of(dict(a))
    assert vlm.key_of(a) != vlm.key_of(b)


def test_load_done_skips_unparseable_and_torn_lines(vlm, tmp_path, monkeypatch):
    """A half-written final line from an interrupted run must not crash the resume.

    The failure this pins: an interrupted batch leaves a partial JSON line. If that raises, the
    resume dies on the one thing it exists to recover from.
    """
    f = tmp_path / "labels.jsonl"
    good = {"image": "a.png", "model": "m", "prompt_sha256": "p", "parse_ok": True}
    bad = {"image": "b.png", "model": "m", "prompt_sha256": "p", "parse_ok": False}
    f.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n" + '{"image": "torn"',
                 encoding="utf-8")
    monkeypatch.setattr(vlm, "LABELS", f)
    done = vlm.load_done()
    assert len(done) == 1                       # only the parse_ok record counts as done
    assert vlm.key_of(good) in done
    assert vlm.key_of(bad) not in done


def test_load_done_empty_when_missing(vlm, tmp_path, monkeypatch):
    monkeypatch.setattr(vlm, "LABELS", tmp_path / "nope.jsonl")
    assert vlm.load_done() == {}


# ---------------------------------------------------------------------------------------------
# The control: the whole anti-fabrication design rests on it scoring honestly.
# ---------------------------------------------------------------------------------------------
def test_control_trivial_assertions_are_not_fabrication(vlm):
    """`panel_count: 0` on a blank page is TRUE. Scoring it as fabrication is a false alarm."""
    trivial = {"panel_count": 0, "panel_layout": "none", "arrow_style": "none",
               "saturated_color_count": 0}
    # Mirrors the TRIVIAL table in run_controls.
    assert trivial["panel_count"] == 0
    assert trivial["panel_layout"] == "none"


def test_control_verdict_text_distinguishes_the_two_outcomes(vlm):
    """The verdict must say which happened; a control that reports 'ok' either way is inert."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "FABRICATES" in src
    assert "DECLINES" in src
    # column_width is the probe that catches an ignored instruction.
    assert "column_width_is_fabrication" in src


def test_column_width_is_supplied_as_context_not_inferred(vlm):
    """The prompt must GIVE the width, because a crop cannot show which column it came from."""
    prompt = vlm.build_prompt({"crop_width_mm": 91.5})
    assert "91.5" in prompt, "the measured crop width must be supplied"
    assert "column_width" in prompt
    # The prompt must also supply the reference widths, or "near 89/183" is unanchored.
    low = prompt.lower()
    assert "89" in prompt and "183" in prompt, "reference column widths missing"
    # And it must forbid reading the width off the image. Assert the PROPERTY, not one
    # sentence: an earlier version pinned exact wording and failed when the prompt was
    # improved. Substance, not phrasing.
    assert ("read the column width off the image" in low
            or "not read the column width" in low
            or "do not try to read the column" in low), (
        "the prompt does not tell the model to avoid inferring column_width from the crop; "
        "a crop cannot reveal which page column it came from")


def test_prompt_offers_null_for_every_field(vlm):
    """The decline option is the anti-fabrication mechanism; it must be in the prompt text."""
    prompt = vlm.build_prompt({"crop_width_mm": 100})
    assert "null" in prompt.lower()
    assert "Do NOT guess" in prompt
    for field in vlm.FIELDS:
        assert field in prompt, "field %r missing from prompt" % field


# ---------------------------------------------------------------------------------------------
# Schema integrity: the field set is what the task asked for.
# ---------------------------------------------------------------------------------------------
def test_schema_covers_every_required_field(vlm):
    required = {
        "figure_type", "column_width", "font_family", "line_weight", "arrow_style",
        "high_contrast", "colorblind_safe", "saturated_color_count", "caption_overview_first",
        "caption_panel_by_panel", "caption_has_stats", "panel_count", "panel_layout",
        "vector_or_bitmap",
    }
    assert required <= set(vlm.FIELDS), "missing: %s" % (required - set(vlm.FIELDS))


def test_every_field_is_nullable(vlm):
    """A field that cannot be null cannot express 'I cannot tell', which is the point."""
    labels, _, _ = vlm.validate({})
    assert all(v is None for v in labels.values())


def test_determinism_options_are_pinned(vlm):
    assert vlm.TEMPERATURE == 0
    assert vlm.SEED == 42
    assert vlm.MAX_ATTEMPTS >= 2, "a single attempt cannot satisfy 'retry on parse failure'"


# ---------------------------------------------------------------------------------------------
# Consistency arithmetic: agreement that counts only two nulls is not agreement.
# ---------------------------------------------------------------------------------------------
def test_consistency_reports_decided_only_agreement(vlm):
    """The report must separate overall agreement from agreement about the figure."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "agreement_excluding_both_null" in src
    assert "both_null" in src


# ---------------------------------------------------------------------------------------------
# Live artefacts, if the batch has been run: these pin the promises made in the report.
# ---------------------------------------------------------------------------------------------
def test_labels_file_records_full_provenance_if_present(vlm):
    if not vlm.LABELS.exists():
        pytest.skip("no labels yet")
    lines = [ln for ln in vlm.LABELS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    rec = json.loads(lines[0])
    for key in ("image", "model", "prompt", "prompt_sha256", "options", "raw_responses",
                "labels", "parse_ok", "image_sha256"):
        assert key in rec, "record is missing %r, so it cannot be traced" % key
    assert rec["options"]["temperature"] == 0
    assert rec["options"]["seed"] == 42


def test_reported_parse_rate_matches_the_records(vlm):
    """The headline number must be recomputable from the jsonl, not asserted."""
    if not vlm.LABELS.exists():
        pytest.skip("no labels yet")
    recs = [json.loads(ln) for ln in vlm.LABELS.read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    figs = [r for r in recs if r.get("kind") != "control"]
    latest = {}
    for r in figs:
        latest[r["image"]] = r
    figs = list(latest.values())
    if not figs:
        pytest.skip("no figure labels")
    ok = sum(1 for r in figs if r.get("parse_ok"))
    report = vlm.REPORT
    if report.exists():
        stated = json.loads(report.read_text(encoding="utf-8"))
        assert stated["n_figures_labelled"] == len(figs)
        assert abs(stated["json_parse_rate"] - ok / len(figs)) < 1e-6


def test_rendered_images_are_unique_and_present(vlm):
    """The first render produced 133 records over 97 files because slugs collided."""
    if not vlm.SOURCES.exists():
        pytest.skip("nothing rendered yet")
    src = json.loads(vlm.SOURCES.read_text(encoding="utf-8"))
    figs = src["figures"]
    names = [f["image"] for f in figs]
    assert len(set(names)) == len(names), "image-name collision: two crops share one path"
    missing = [n for n in names if not (vlm.IMAGES / n).exists()]
    assert not missing, "manifest lists images that are not on disk: %s" % missing[:3]
