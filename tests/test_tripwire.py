"""The answer key must never be reachable from the inputs that produce a measurement.

WHY THIS TEST
    This project once reported an official score of 100.0 that came entirely from copying the
    reference figure's own code. The answer key was in the input and nothing noticed, because the
    number looked like a triumph.

    Harness^2 (google-research/harness2, Apache 2.0) reached the same conclusion independently and
    built a mechanical guard: `assert_tree_has_no_grader_verdicts` refuses harness files whose name
    or body carries a grader verdict, because such files "cannot be served as evidence". Two
    projects arriving at the same rule is evidence the rule is real. `figpipe/tripwire.py` is the
    figpipe-side equivalent for figures.

    Every test here has a NEGATIVE CONTROL: the detector must fire on a planted leak, and must NOT
    fire on a clean input. A detector that always fires is as useless as one that never does.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

tripwire = pytest.importorskip("figpipe.tripwire", reason="tripwire module absent")


def test_a_file_named_as_an_answer_key_is_refused(tmp_path):
    (tmp_path / "reference_code.py").write_text("print('the answer')", encoding="utf-8")
    with pytest.raises(tripwire.AnswerKeyLeak, match="answer key reachable"):
        tripwire.assert_no_answer_key(tmp_path)


def test_a_file_containing_a_verdict_is_refused(tmp_path):
    (tmp_path / "notes.md").write_text("the official_code_channel is 75.41", encoding="utf-8")
    with pytest.raises(tripwire.AnswerKeyLeak, match="verdict marker"):
        tripwire.assert_no_answer_key(tmp_path)


def test_a_clean_input_passes(tmp_path):
    """Negative control: the detector must not fire on legitimate input."""
    (tmp_path / "data.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    tripwire.assert_no_answer_key(tmp_path)          # must not raise


def test_an_explicit_allow_permits_a_deliberate_read(tmp_path):
    """The ceiling run DOES read reference_code -- that is what it measures.

    An unstated exception is how the original tautology survived, so the exception must be written
    at the call site.
    """
    (tmp_path / "reference_code.py").write_text("x = 1", encoding="utf-8")
    with pytest.raises(tripwire.AnswerKeyLeak):
        tripwire.assert_no_answer_key(tmp_path)
    tripwire.assert_no_answer_key(tmp_path, allow=("reference_code",))   # must not raise


def test_unknown_style_sources_are_refused():
    for bad in ("magic", "guess", ""):
        with pytest.raises(tripwire.AnswerKeyLeak):
            tripwire.assert_style_source_is_honest(bad)
    for good in ("image", "naive", "code", "ceiling"):
        tripwire.assert_style_source_is_honest(good)


def test_every_measured_artefact_declares_its_style_source():
    """A ceiling must never be quotable without its label."""
    sources = tripwire.audit_measurement_sources()
    if not sources:
        pytest.skip("no official score artefacts yet")
    assert "official_scores.json" in sources
    assert sources["official_scores.json"] == "image", (
        "the headline artefact must be the HONEST image-inferred run, not the ceiling")
    for name, source in sources.items():
        assert source in ("image", "code", "naive", "ceiling"), (
            f"{name} declares an unknown style source {source!r}")
