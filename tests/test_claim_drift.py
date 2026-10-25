"""The claim document must state the numbers its own scripts produce.

WHY THIS EXISTS
    `CLAIM.md` cites the style-metric discrimination accuracy in eleven places. Re-running the script it
    cites (`scripts/validate_style_metric.py`) on 2026-10-25 gave **0.900 (27/30)** while the document
    said **0.933 (28/30)**.

    Five commits between 2026-10-23 and 2026-10-25 changed `styleprofile.py` -- the palette area floor,
    the font-tier generator, the palette cap, the tick-direction probe, and the count-misalignment fix.
    Every one was measured on the OFFICIAL channel and every one was a real fix. Together they moved a
    DIFFERENT measurement by one pair, and the document was never re-derived.

    The document opens with: "Everything below is measured by scripts in this repository and can be
    re-run." **That sentence is the promise this test enforces.** A claim that cannot be re-derived is
    marketing, and a claim that re-derives to a different number is worse -- it is a stale measurement
    wearing present-tense confidence.

WHY THE CONCLUSION STILL HOLDS
    0.900 with a 95 % CI of [0.744, 0.965] still excludes chance (0.5) by a wide margin, so
    "the style distance discriminates a matched transfer from a mismatched one" is still supported. What
    was wrong was the NUMBER, not the finding.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIM = ROOT / "CLAIM.md"
VALIDATION = ROOT / "corpus" / "e2e" / "style_validation.json"


def _arm() -> dict:
    if not VALIDATION.is_file():
        pytest.skip("no style validation data")
    return (json.loads(VALIDATION.read_text(encoding="utf-8")).get("arms") or {}).get("same_paper") or {}


def test_the_claim_states_the_measured_discrimination_accuracy():
    """THE DRIFT. 0.933 was stale by one pair for two days."""
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    arm = _arm()
    if not arm:
        pytest.skip("no same_paper arm")
    acc = arm["discrimination_accuracy"]
    text = CLAIM.read_text(encoding="utf-8")
    assert f"{acc:.3f}" in text, (
        f"CLAIM.md does not state the measured discrimination accuracy {acc:.3f}; the document has "
        f"drifted from corpus/e2e/style_validation.json")
    assert f"{acc:.4f}" in text, (
        f"CLAIM.md does not state {acc:.4f}; the four-decimal form is used in the dated updates")


def test_the_claim_states_the_measured_pair_count():
    """A bare accuracy hides whether it is 27/30 or 27/28; both are 0.964 and one is 0.900."""
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    arm = _arm()
    if not arm:
        pytest.skip("no same_paper arm")
    text = CLAIM.read_text(encoding="utf-8")
    assert f"{arm['n_correct']}/{arm['n_pairs']}" in text or \
           f"{arm['n_correct']} of {arm['n_pairs']}" in text, (
        f"CLAIM.md does not state the pair count {arm['n_correct']}/{arm['n_pairs']}")


def test_the_claim_states_the_measured_confidence_interval():
    """An accuracy without its interval is a point estimate presented as a fact."""
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    data = json.loads(VALIDATION.read_text(encoding="utf-8"))
    ci = data.get("binomial_ci_95")
    if not ci:
        pytest.skip("no CI recorded")
    text = CLAIM.read_text(encoding="utf-8")
    lo, hi = f"{ci[0]:.3f}", f"{ci[1]:.3f}"
    assert lo in text and hi in text, (
        f"CLAIM.md does not state the 95 % CI [{lo}, {hi}] measured in style_validation.json")


def test_the_claim_still_supports_its_conclusion():
    """THE OTHER DIRECTION. The number moved; the FINDING must still hold, or the document is wrong in
    a way that updating a figure would not fix."""
    data = json.loads(VALIDATION.read_text(encoding="utf-8"))
    ci = data.get("binomial_ci_95") or [0, 1]
    chance = data.get("chance_level", 0.5)
    assert ci[0] > chance, (
        f"the 95 % CI lower bound {ci[0]} no longer excludes chance {chance}; the claim's conclusion "
        f"does not survive and CLAIM.md must say so rather than being updated")


def test_no_superseded_accuracy_is_quoted_as_current():
    """A DATED UPDATE may quote an old number, but the HEADLINE must not.

    THE PROPERTY IS NARROW ON PURPOSE. My first version matched every three-decimal number in the
    headline and flagged `0.869` (the figure_aspect dimension score), `0.965` (spines_removed) and two
    component accuracies -- none of which is the discrimination accuracy. **A regex over numbers is not
    a check of a claim**; the check has to know which quantity it is about.

    So this test looks only at numbers that are EXPLICITLY the discrimination accuracy: those written
    as "N of M pairs correct" or directly labelled "discrimination accuracy".
    """
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    arm = _arm()
    if not arm:
        pytest.skip("no same_paper arm")
    current = f"{arm['discrimination_accuracy']:.3f}"
    text = CLAIM.read_text(encoding="utf-8")
    head = text.split("## Update")[0]

    labelled = re.findall(r"[Dd]iscrimination accuracy[^0-9]{0,24}(0\.\d{3})", head)
    pair_forms = re.findall(r"(\d+) of (\d+) pairs correct, accuracy (0\.\d{3})", head)
    quoted = set(labelled) | {m[2] for m in pair_forms}
    stale = {v for v in quoted if v != current}
    assert not stale, (
        f"the headline of CLAIM.md states the discrimination accuracy as {sorted(stale)}, but the "
        f"measured value is {current}; superseded numbers belong inside a dated update")
    # and the pair count, when quoted in that form, must agree
    for correct, total, acc in pair_forms:
        assert int(correct) == arm["n_correct"] and int(total) == arm["n_pairs"], (
            f"the headline quotes {correct}/{total} pairs, measured {arm['n_correct']}/{arm['n_pairs']}")
