"""The summary of the style metric must not be less informative than the data behind it.

WHY THIS TEST
    `corpus/e2e/style_validation.json` reports discrimination accuracy 0.9333 with a caveat that
    withholding `aspect` drops it to 0.700. That caveat is honest and UNDERSTATES the finding.

    Recomputing each component ALONE over the same 30 pairs gives:

        aspect   0.867     <- the entire signal
        palette  0.533     <- chance
        rules    0.500     <- chance
        sizes    0.400     <- below chance
        lines    0.333     <- below chance
        letters  0.033     <- worse than chance

    So the metric is not "a style distance whose aspect component matters". On this corpus it is
    very nearly an ASPECT-RATIO DETECTOR with five near-random components attached. A reader
    deciding whether to trust the metric needs that sentence, not the softer one.

    `scripts/validate_metric_claims.py` recomputes every claim from the pairs, so the summary and
    the data cannot drift apart.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SOURCE = ROOT / "corpus" / "e2e" / "style_validation.json"


@pytest.fixture(scope="module")
def claims():
    import validate_metric_claims as v
    return v


@pytest.fixture(scope="module")
def pairs():
    if not SOURCE.is_file():
        pytest.skip("no validation record")
    return json.loads(SOURCE.read_text(encoding="utf-8")).get("pairs") or []


def test_the_record_has_per_pair_data(pairs):
    """Without per-pair detail nothing can be re-derived, and the summary is unfalsifiable."""
    assert pairs, "the validation record has no pairs"
    assert len(pairs) >= 20
    for p in pairs[:3]:
        assert "details_A" in p and "details_B" in p
        assert set(p["details_A"]) >= {"sizes", "letters", "lines", "rules", "palette", "aspect"}


def test_aspect_alone_carries_the_metric(claims, pairs):
    """THE FINDING THE SUMMARY UNDERSTATES."""
    dims = claims.per_dimension(pairs)
    assert dims["aspect"]["accuracy"] >= 0.80, (
        f"aspect alone scores {dims['aspect']['accuracy']}, which does not carry the metric")
    others = {k: v["accuracy"] for k, v in dims.items() if k != "aspect"}
    assert max(others.values()) <= 0.60, (
        f"another component is also discriminative ({others}), so the metric is a genuine sum")


def test_the_leave_one_out_search_does_not_beat_aspect_alone(claims, pairs):
    """If a tuned search beat a fixed dimension, the weights would be doing real work.

    It does not: 0.867 either way. So `aspect` is not overfitting to this corpus -- it genuinely
    carries the discrimination here, and whether it carries it elsewhere is what human validation
    would settle.
    """
    dims = claims.per_dimension(pairs)
    loo = claims.leave_one_out(pairs)
    assert abs(loo - dims["aspect"]["accuracy"]) < 0.10, (
        f"leave-one-out ({loo}) differs from aspect-alone ({dims['aspect']['accuracy']}); "
        f"the weights may be doing real work after all")


def test_the_declared_weights_are_not_optimal(claims, pairs):
    """Equal weights score HIGHER, but on the same pairs -- so this is a statement about the
    weights, not evidence of an improvement. Recorded so nobody reports 0.967 as a result."""
    equal = {k: 1 / len(claims.DECLARED_WEIGHTS) for k in claims.DECLARED_WEIGHTS}
    assert claims.weighted_accuracy(pairs, equal) > claims.weighted_accuracy(
        pairs, claims.DECLARED_WEIGHTS), (
        "the declared weights are already optimal on this set; the tuning question is moot")


def test_the_validator_runs_and_reports_a_verdict(claims, capsys):
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "VERDICT" in out
    assert "aspect" in out.lower()
    assert "leave-one-out" in out
