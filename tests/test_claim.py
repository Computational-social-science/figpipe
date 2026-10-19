"""The claim must stay true, and must stay limited.

WHY THIS TEST
    CLAIM.md states what this project does and does not claim. A claim document that drifts from
    the measurements is worse than none: it is the artefact people quote. These tests pin both
    halves -- the numbers, and the limits.

    The report itself carried "this is not an SOTA claim" and "official scorer not integrated" for
    several rounds AFTER both became false. That is the drift this test prevents.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIM = ROOT / "CLAIM.md"


def _numbers() -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    import score_official as so
    return so.comparison()


def test_the_claim_document_exists_and_states_the_three_points():
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    text = CLAIM.read_text(encoding="utf-8")
    cmp = _numbers()
    for label, key in (("baseline", "baseline"), ("figpipe", "pipeline"), ("ceiling", "ceiling")):
        if cmp.get(key) is None:
            pytest.skip(f"{key} not measured")
        value = cmp[key]["mean"]
        assert str(value) in text, (
            f"CLAIM.md does not state the measured {label} value {value}; the document has drifted")


def test_the_claim_states_the_limits_it_must_not_cross():
    """A claim without limits is marketing."""
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    text = CLAIM.read_text(encoding="utf-8")
    assert "not run" in text.lower() and "vision" in text.lower(), (
        "the claim must state that the vision channel is not run")
    assert "no combined-score claim" in text.lower() or "not a combined-score" in text.lower(), (
        "the claim must explicitly disclaim a combined score")
    assert "head-to-head" in text.lower(), (
        "the claim must state that no head-to-head comparison with another system was performed")
    assert "human" in text.lower(), "the claim must state that human validation is pending"


def test_the_report_no_longer_contradicts_the_evidence():
    """The report said "not an SOTA claim" and "scorer not integrated" after both became false."""
    report = ROOT / "reports" / "figpipe_report.html"
    if not report.is_file():
        pytest.skip("report absent")
    text = report.read_text(encoding="utf-8")
    stale = [
        "this is not an SOTA claim",
        "Official scorer not integrated",
        "110/150 tasks are mapped",
    ]
    found = [phrase for phrase in stale if phrase in text]
    assert not found, f"the report still carries stale statements: {found}"


def test_the_claim_does_not_claim_a_combined_score():
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    text = CLAIM.read_text(encoding="utf-8").lower()
    # A sentence that describes the FORMULA ("the code channel is 35% of the combined score") is a
    # fact, not a claim. What must never appear is an ASSERTION of a combined result. So the check
    # looks for assertion words near "combined score", not for every mention.
    risky = re.findall(r"[^.\n]*combined[- ]score[^.\n]*", text)
    for sentence in risky:
        has_assertion = any(w in sentence for w in
                            ("we score", "we achieve", "our combined", "achieves", "reaches",
                             "outperforms", "beats"))
        assert not has_assertion, (
            f"a sentence asserts a combined-score result: {sentence.strip()!r}")
    # and the disclaimer must be present somewhere
    assert "no combined-score claim" in text or "not a combined-score" in text
