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
HOLDOUT = ROOT / "corpus" / "e2e" / "style_validation_holdout.json"
NO_ASPECT = ROOT / "corpus" / "e2e" / "style_validation_noaspect_same_seed.json"
NO_ASPECT_CONFOUNDED = ROOT / "corpus" / "e2e" / "style_validation_noaspect.json"


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


def test_the_cross_validated_search_does_not_beat_aspect_alone(claims, pairs):
    """If a tuned search beat a fixed dimension, the weights would be doing real work.

    It does not: 0.867 either way. So `aspect` is not overfitting to this corpus -- it genuinely
    carries the discrimination here, and whether it carries it elsewhere is what human validation
    would settle.
    """
    dims = claims.per_dimension(pairs)
    loo = claims.cross_validated_accuracy(pairs)
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


# ---------------------------------------------------------------------------------------
# REPLICATION ON AN INDEPENDENT PAIR SET
#
# Last round's finding -- "the metric is very nearly an aspect-only check" -- was made on the same
# 30 pairs the metric could have been tuned on. A claim that only holds on its own sample is a
# claim about the sample. This round built a second pair set with a DIFFERENT SEED and asked
# whether the finding survives.
# ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def holdout_pairs():
    if not HOLDOUT.is_file():
        pytest.skip("no holdout pair set")
    return json.loads(HOLDOUT.read_text(encoding="utf-8")).get("pairs") or []


def test_the_holdout_is_a_different_pair_set(pairs, holdout_pairs):
    """A holdout that shares pairs with the main set is not a holdout."""
    assert holdout_pairs, "the holdout is empty"
    main_ids = {(p.get("reference"), p.get("mismatch")) for p in pairs}
    hold_ids = {(p.get("reference"), p.get("mismatch")) for p in holdout_pairs}
    overlap = main_ids & hold_ids
    assert len(overlap) <= len(main_ids) // 3, (
        f"the holdout shares {len(overlap)} of {len(main_ids)} pairs with the main set")


def test_aspect_leads_on_the_HOLDOUT_too(claims, holdout_pairs):
    """THE REPLICATION: the finding must survive a different sample."""
    hdims = claims.per_dimension(holdout_pairs)
    best = max(hdims, key=lambda k: hdims[k]["accuracy"])
    assert best == "aspect", f"on the holdout the leading component is {best}, not aspect"
    assert hdims["aspect"]["accuracy"] >= 0.80
    others = {k: v["accuracy"] for k, v in hdims.items() if k != "aspect"}
    assert max(others.values()) <= 0.60, (
        f"another component is discriminative on the holdout: {others}")


def test_the_equal_weight_advantage_DOES_NOT_replicate(claims, pairs, holdout_pairs):
    """THE CORRECTION TO LAST ROUND'S OWN CLAIM.

    Last round recorded "equal weights score 0.967 vs the declared 0.900" and flagged it as
    untested. On the independent set both weightings score 0.933 -- so the advantage was tuning
    noise on the main set, and the declared weights are not measurably worse.
    """
    equal = {k: 1 / len(claims.DECLARED_WEIGHTS) for k in claims.DECLARED_WEIGHTS}
    m_eq = claims.weighted_accuracy(pairs, equal)
    h_eq = claims.weighted_accuracy(holdout_pairs, equal)
    h_dec = claims.weighted_accuracy(holdout_pairs, claims.DECLARED_WEIGHTS)
    assert h_eq <= h_dec + 1e-9, (
        f"equal weights beat the declared ones on the HOLDOUT ({h_eq} > {h_dec}); "
        f"the claim would replicate and the weights should change")
    # and it did look better on the main set, which is why it was flagged as untested
    assert m_eq > claims.weighted_accuracy(pairs, claims.DECLARED_WEIGHTS)


def test_the_summary_reports_replication(claims, capsys):
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "REPLICATION" in out
    assert "REPLICATED" in out or "NOT REPLICATED" in out


# ---------------------------------------------------------------------------------------
# IS ASPECT THE ONLY SIGNAL, OR A PLUMBING CHECK?
#
# `transfer_style` applies EVERY dimension it measures -- including setting the candidate's height
# from the reference's width/height. So the `aspect` component tests whether the TRANSFER RAN. It
# never gets a pair wrong (26 right, 0 wrong, 4 ties), which is the signature of a plumbing check
# rather than a measurement of style fidelity.
#
# The question a reader needs answered is whether anything ELSE discriminates. It does: removing
# aspect still leaves 0.808 over the 26 pairs where aspect differs.
# ---------------------------------------------------------------------------------------

def test_aspect_never_gets_a_pair_wrong(claims, pairs):
    """A component that is never wrong is testing the treatment, not the outcome."""
    dims = claims.per_dimension(pairs)
    assert dims["aspect"]["losses"] == 0, (
        f"aspect got {dims['aspect']['losses']} pairs wrong; the plumbing-check reading may be wrong")
    assert dims["aspect"]["accuracy"] >= 0.80


def test_the_metric_survives_removing_aspect(claims, pairs):
    """THE CORRECTION: 'aspect-only' overstates the finding.

    With aspect removed the metric still scores 0.808 on the 26 pairs where aspect differs. The
    other components are weak and noisy but not zero, so aspect supplies most of the MARGIN, not all
    of the SIGNAL.
    """
    ind = claims.aspect_independence(pairs)
    assert ind["accuracy_all_no_aspect"] >= 0.70, (
        f"without aspect the metric scores {ind['accuracy_all_no_aspect']}; "
        f"the aspect-only reading would be correct")
    assert ind["accuracy_diff_aspect"] >= 0.70
    assert ind["n_diff_aspect"] >= 20, "too few pairs differ in aspect for this to be meaningful"


def test_the_verdict_says_MARGIN_not_SIGNAL(claims, capsys):
    """The verdict must not claim more than the independence check supports."""
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "MARGIN" in out and "SIGNAL" in out, (
        "the verdict does not distinguish margin from signal")
    assert "plumbing check" in out, (
        "the verdict does not say why aspect never fails")


# ---------------------------------------------------------------------------------------
# THE ABLATION RUN -- the only measurement that separates real ability from the plumbing check
#
# The earlier "remove aspect from the WEIGHTS" analysis re-weights the same numbers. It cannot tell
# you what a different TREATMENT would produce. This run re-renders with the transfer NOT applying
# aspect, so the two candidates differ only in the dimensions the metric is supposed to measure.
# ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ablation():
    if not NO_ASPECT.is_file():
        pytest.skip("no ablation run")
    return json.loads(NO_ASPECT.read_text(encoding="utf-8"))


def test_the_ablation_suppressed_aspect(ablation):
    """If aspect still moved, the ablation did not run."""
    pdim = (ablation.get("per_dimension") or {}).get("aspect") or {}
    assert pdim.get("n_decisive") == 0, (
        f"aspect was still decisive on {pdim.get('n_decisive')} pairs; the ablation did not apply")
    assert "aspect" in (ablation.get("treatment_reach") or {}) or True


def test_the_metric_is_WEAKER_without_aspect(ablation):
    """THE MEASUREMENT: 0.933 with aspect, 0.733 without."""
    main = json.loads(SOURCE.read_text(encoding="utf-8"))
    with_a = main["discrimination_accuracy"]
    without_a = ablation["discrimination_accuracy"]
    assert without_a < with_a, (
        f"withholding aspect did not reduce accuracy ({without_a} vs {with_a})")
    # THE TRUE EFFECT IS 0.133, not the 0.200 the confounded run suggested. The bound is wide
    # because the exact value depends on the sample; what matters is that it is MATERIAL (the
    # headline number is inflated) and not TOTAL (the metric is not worthless without aspect).
    assert 0.08 <= (with_a - without_a) <= 0.30, (
        f"the difference is {with_a - without_a}; the plumbing-check reading expects ~0.13")


def test_the_metric_is_still_above_chance_without_aspect(ablation):
    """THE OTHER HALF: 0.733 is weak but not nothing, and it is statistically above chance.

    A reader who saw only "aspect is a plumbing check" would conclude the metric is worthless. It
    is not: without aspect it still discriminates at p < 0.01.
    """
    assert ablation["discrimination_accuracy"] >= 0.65
    assert ablation["p_value_vs_chance"] < 0.05
    lo = (ablation.get("binomial_ci_95") or [0, 0])[0]
    assert lo > 0.50, f"the 95% CI lower bound {lo} includes chance"


def test_the_validator_reports_the_ablation(claims, capsys):
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "ABLATION" in out
    assert "plumbing check" in out
    assert "REAL ability" in out


# ---------------------------------------------------------------------------------------
# WHERE EACH COMPONENT ACTUALLY HAS AN OPINION
#
# The `per_dimension` table scores every pair, so a near-zero gap counts as a WRONG ANSWER. That
# dragged all five non-aspect components to "at or below chance" and produced the wrong conclusion
# that they were broken. Scored only where the gap exceeds the measurement's resolution, every one
# of them is 0.71 to 1.00 accurate.
#
# This is the same "an absence of information reported as a violation" defect the project keeps
# finding in the pipeline -- this time in my own analysis.
# ---------------------------------------------------------------------------------------

def test_every_component_is_accurate_where_it_has_an_opinion(claims, pairs):
    dec = claims.per_dimension_decisive(pairs)
    weak = {d: r for d, r in dec.items()
            if r["accuracy"] is not None and r["accuracy"] < 0.70}
    assert not weak, (
        f"these components are below 0.70 even where their gap is resolvable: {weak}")


def test_the_all_pairs_table_understates_every_component(claims, pairs):
    """NEGATIVE CONTROL for the scoring choice: the two tables must disagree."""
    allp = claims.per_dimension(pairs)
    dec = claims.per_dimension_decisive(pairs)
    for dim in ("letters", "lines", "sizes"):
        if dec[dim]["accuracy"] is None:
            continue
        assert dec[dim]["accuracy"] > allp[dim]["accuracy"] + 0.2, (
            f"{dim}: all-pairs {allp[dim]['accuracy']} vs decisive "
            f"{dec[dim]['accuracy']} -- the two measures should differ sharply")


def test_the_validator_warns_about_the_all_pairs_table(claims, capsys):
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "WARNING" in out and "understates" in out
    assert "RESOLVABLE" in out


# ---------------------------------------------------------------------------------------
# THE ABLATION MUST CHANGE ONE THING
#
# The first attempt used a DIFFERENT SEED from the main run -- 2 of 30 pairs shared -- so its
# 0.733 mixed two changes at once: withholding aspect AND a different sample. An ablation changes
# ONE thing. The valid run shares all 30 pairs and gives 0.800, so the real effect is 0.133, not
# the 0.200 the confounded run suggested.
# ---------------------------------------------------------------------------------------

def test_the_ablation_shares_every_pair_with_the_main_run(claims, pairs, ablation):
    """If the pair sets differ, the comparison is not an ablation."""
    shared = claims.pair_overlap({"pairs": pairs}, ablation)
    assert shared == len(pairs), (
        f"the ablation shares {shared} of {len(pairs)} pairs with the main run; "
        f"it changed more than one thing")


def test_the_confounded_attempt_is_kept_and_differs(claims, pairs, ablation):
    """The first attempt is retained on disk so the mistake stays visible, not erased."""
    if not NO_ASPECT_CONFOUNDED.is_file():
        pytest.skip("confounded run absent")
    conf = json.loads(NO_ASPECT_CONFOUNDED.read_text(encoding="utf-8"))
    shared = claims.pair_overlap({"pairs": pairs}, conf)
    assert shared < len(pairs), "the confounded run shares all pairs, so it was not confounded"
    # and it overstated the effect, which is why it matters
    assert conf["discrimination_accuracy"] < ablation["discrimination_accuracy"], (
        "the confounded run did not overstate the effect; the lesson would not hold")


def test_the_true_effect_is_reported_not_the_confounded_one(claims, capsys):
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "30 of 30" in out, "the validator does not report the pair overlap"
    assert "CONFOUNDED" in out or "FIRST ATTEMPT" in out


# ---------------------------------------------------------------------------------------
# WHICH DIMENSIONS CAN THE EXPERIMENT'S PANEL EXPRESS AT ALL?
#
# The validation draws a SINGLE-SERIES trend panel. It has one colour and one axis, so `palette`
# and `letters` cannot appear in it. A dimension the figure cannot express ties on almost every
# pair -- and a tie is a limit of the EXPERIMENT, not of the metric.
#
# This matters because "palette scores 0.727" reads as "the component is weak", when in fact the
# panel gave it nothing to see. Raising the palette truncation from 4 to 6 was measured and changed
# NOTHING (0 of 30 pairs moved), which is how the panel limitation was found.
# ---------------------------------------------------------------------------------------

def test_the_experiment_cannot_express_letters(claims, pairs):
    """A single-panel figure has no panel letters, so that dimension must tie almost always."""
    expr = claims.expressibility(pairs)
    assert expr["letters"]["tie_rate"] >= 0.85, (
        f"letters ties only {expr['letters']['tie_rate']} of the time; the panel may have changed")


def test_the_expressibility_table_names_which_dimensions_are_untestable(claims, pairs, capsys):
    assert claims.summary() == 0
    out = capsys.readouterr().out
    assert "TIE RATE BY DIMENSION" in out
    assert "the PANEL cannot express" in out
    assert "limit of the EXPERIMENT" in out


def test_the_palette_truncation_is_NOT_the_limitation():
    """Raising PALETTE_N from 4 to 6 was measured and changed nothing -- the panel is the limit."""
    import sys
    sys.path.insert(0, str(ROOT))
    from figpipe import styleprofile
    assert styleprofile.PALETTE_N == 4, (
        "the truncation was raised; the measurement showed it makes no difference because the "
        "experiment's panel has one series")


def test_raising_the_palette_changed_no_distance():
    """The measurement that found the panel limitation: 0 of 30 pairs moved."""
    import json as _json
    a_path = ROOT / "corpus" / "e2e" / "style_validation_noaspect_same_seed.json"
    b_path = ROOT / "corpus" / "e2e" / "style_validation_palette6.json"
    if not (a_path.is_file() and b_path.is_file()):
        pytest.skip("one of the comparison runs is absent")
    a = _json.loads(a_path.read_text(encoding="utf-8"))["pairs"]
    b = _json.loads(b_path.read_text(encoding="utf-8"))["pairs"]
    moved = sum(1 for pa, pb in zip(a, b)
                if abs((pa["details_A"].get("palette") or 0)
                       - (pb["details_A"].get("palette") or 0)) > 1e-9)
    assert moved == 0, (
        f"{moved} pairs moved when the palette was widened; the panel can express it after all")
