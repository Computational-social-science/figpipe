"""The style metric's validation must be a MEASUREMENT, and the measurement must be able to fail.

WHY THESE TESTS
    `CLAIM.md` now states a measured discrimination accuracy instead of "not validated by human
    judgement". That is only an improvement if the number is internally consistent and if the
    experiment that produced it could have produced a different answer. So these tests check
    three different things:

      1. INTERNAL CONSISTENCY of `corpus/e2e/style_validation.json` -- the accuracy is a
         proportion of the recorded pairs, n matches the pair records, the interval contains the
         point estimate, and the per-pair margins agree with the per-pair verdicts. An artefact
         that contradicts itself cannot be quoted.
      2. THE CLAIM DOCUMENT agrees with the artefact. The whole point of replacing a sentence is
         that the sentence now carries the number, including when the number is bad.
      3. A NEGATIVE CONTROL. The ranking arithmetic is re-run on a deliberately INVERTED
         ordering and must score below 0.5. Without this, "accuracy 0.87" could be produced by a
         harness that always answers "B" -- which would be a fabricated result of exactly the
         kind this project already documented once.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTEFACT = ROOT / "corpus" / "e2e" / "style_validation.json"
CLAIM = ROOT / "CLAIM.md"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def artefact() -> dict:
    if not ARTEFACT.is_file():
        pytest.skip("style_validation.json not measured yet")
    raw = ARTEFACT.read_text(encoding="utf-8")
    if not raw.strip():
        pytest.skip("style_validation.json is empty (not measured yet)")
    try:
        data = json.loads(raw)
    except ValueError:
        pytest.skip("style_validation.json is not valid JSON (not measured yet)")
    if not data.get("pairs"):
        pytest.skip("style_validation.json holds no pairs")
    return data


def test_the_artefact_exists_and_records_its_design(artefact):
    for key in ("n_pairs", "discrimination_accuracy", "binomial_ci_95", "per_dimension",
                "official_scorer", "pairs", "verdict"):
        assert key in artefact, f"the artefact is missing {key!r}"
    design = artefact["design"]
    assert design["n_pairs"] == artefact["n_pairs"] == len(artefact["pairs"])
    # A and B must be described as the experiment defines them, or the number means something
    # else than CLAIM.md says it means.
    assert "MISMATCHED" in design["A"].upper()
    assert "MATCHED" in design["B"].upper()


def test_the_numbers_are_internally_consistent(artefact):
    n = artefact["n_pairs"]
    acc = artefact["discrimination_accuracy"]
    assert 0.0 <= acc <= 1.0, f"accuracy {acc} is not a proportion"
    assert n == len(artefact["pairs"]), "n_pairs does not match the number of pair records"
    assert artefact["n_correct"] == sum(1 for p in artefact["pairs"] if p["correct"])
    assert acc == pytest.approx(artefact["n_correct"] / n, abs=1e-4), (
        f"accuracy {acc} is not n_correct/n_pairs = {artefact['n_correct']}/{n}")
    lo, hi = artefact["binomial_ci_95"]
    assert 0.0 <= lo <= hi <= 1.0, f"CI {lo}-{hi} is not a valid interval"
    assert lo <= acc <= hi, f"the 95 % interval {lo}-{hi} does not contain the estimate {acc}"


def test_both_contrast_arms_are_measured_and_the_hard_one_is_the_headline(artefact):
    """The headline must be the SAME-PAPER arm, not the easy cross-paper one.

    A cross-paper mismatch is nearly free: two unrelated Nature papers differ in palette,
    typography and layout at once, so a perfect score there says the metric can tell one paper
    from another. The same-paper arm holds the house style constant and asks whether the metric
    separates a faithful transfer from a sibling figure's style -- the question it exists for.

    If this artefact ever reports the easy arm as the headline, the claim has quietly weakened.
    """
    arms = artefact.get("arms") or {}
    assert arms.get("same_paper") and arms.get("different_paper"), (
        f"both arms must be measured; got {sorted(arms)}")
    assert artefact["design"]["arms"]["headline"] == "same_paper", (
        "the headline arm must be the hard (same-paper) contrast")
    assert artefact["discrimination_accuracy"] == pytest.approx(
        arms["same_paper"]["discrimination_accuracy"], abs=1e-9), (
        "the headline accuracy is not the same-paper arm's accuracy")
    assert artefact["n_pairs"] == arms["same_paper"]["n_pairs"]
    # the easy arm can never be WORSE than the hard one by construction of the contrast, and a
    # negative gap would mean the two arms are mislabelled
    gap = artefact.get("contrast_gap") or {}
    assert gap.get("easy_minus_hard") is not None
    assert gap["easy_minus_hard"] >= 0.0, (
        f"the easy arm scored below the hard arm ({gap['easy_minus_hard']}); "
        f"the arms are probably mislabelled")


def test_the_hard_arm_pairs_really_are_same_paper(artefact):
    """The headline arm's pairs must be sibling figures, not accidentally cross-paper.

    `reference` and `mismatch` are recorded as `paper/figure_id`. If the sampler silently fell
    back to a cross-paper draw (which it does when a paper has only one measurable figure), the
    headline would be the easy condition wearing the hard arm's name.
    """
    pairs = artefact["pairs"]
    contrast = artefact["design"]["mismatch_contrast"]
    assert contrast["same_paper"] == len(pairs), (
        f"the headline arm should be all same-paper pairs; got {contrast}")
    for pair in pairs:
        ref_paper = pair["reference"].rsplit("/", 1)[0]
        mis_paper = pair["mismatch"].rsplit("/", 1)[0]
        assert ref_paper == mis_paper, (
            f"pair {pair['reference']} has a cross-paper mismatch {pair['mismatch']}")


def test_every_pair_record_agrees_with_its_own_verdict(artefact):
    """`correct` must be a function of the two distances, not a separate assertion."""
    for pair in artefact["pairs"]:
        assert pair["correct"] == (pair["distance_B"] < pair["distance_A"]), (
            f"pair {pair['reference']} claims correct={pair['correct']} while "
            f"dA={pair['distance_A']} dB={pair['distance_B']}")
        assert pair["margin"] == pytest.approx(pair["distance_A"] - pair["distance_B"], abs=1e-4)
        assert pair["reference"] != pair["mismatch"], (
            "a pair whose mismatch IS the reference measures nothing")
        assert 0.0 <= pair["distance_A"] <= 1.0 and 0.0 <= pair["distance_B"] <= 1.0


def test_the_mismatch_is_a_real_contrast(artefact):
    """The headline arm's mismatches must be sibling figures of the SAME paper.

    Two figures in one paper share a house style, so a same-paper mismatch is the HARD contrast
    -- the one a style metric is actually for. A cross-paper draw is much easier and would
    inflate the accuracy; the artefact records which draw produced each pair so this cannot pass
    silently.
    """
    contrast = artefact["design"]["mismatch_contrast"]
    assert contrast["same_paper"] == len(artefact["pairs"]), (
        f"the headline arm is not a same-paper contrast: {contrast}")


def test_the_negative_control_scores_below_chance(artefact):
    """THE CONTROL THAT MAKES THE RESULT MEANINGFUL.

    The same arithmetic is applied to an INVERTED ranking. If the harness reported the same
    accuracy for the inverted ordering, it would be measuring nothing -- and "accuracy 0.93"
    would be an artefact of the code rather than a property of the metric. An inverted ranking
    must land below 0.5, and forward + inverted + ties must account for every pair.
    """
    control = artefact["negative_control"]
    assert control["accuracy"] < 0.5, (
        f"the inverted ranking scored {control['accuracy']}, which is not below chance; the "
        f"harness cannot distinguish a correct ranking from an inverted one")
    assert control["passes"] is True
    # ties belong to neither direction, so the three counts must exactly partition the pairs
    assert (artefact["n_correct"] + control["n_correct"] + control["n_ties"]
            == artefact["n_pairs"]), (
        "forward + inverted + ties does not equal the number of pairs; a pair was counted twice "
        "or dropped")


def test_the_control_is_recomputed_from_the_pairs_rather_than_trusted(artefact):
    """Re-derive both numbers from the raw pair records.

    The stored `accuracy` and the stored control are claims about the same records; recomputing
    them here means a stale artefact (edited by hand, or written by an older version of the
    script) cannot pass on its own say-so.
    """
    pairs = artefact["pairs"]
    forward = sum(1 for p in pairs if p["distance_B"] < p["distance_A"]) / len(pairs)
    inverted = sum(1 for p in pairs if p["distance_B"] > p["distance_A"]) / len(pairs)
    assert forward == pytest.approx(artefact["discrimination_accuracy"], abs=1e-4)
    assert inverted == pytest.approx(artefact["negative_control"]["accuracy"], abs=1e-4)
    # ties are counted in neither direction, so the two must not sum past one
    assert forward + inverted <= 1.0 + 1e-9


def test_the_per_dimension_breakdown_is_complete_and_consistent(artefact):
    """Every dimension the metric actually used must be reported, with its own n.

    TIES ARE NOT LOSSES. A dimension that measures the same value on both candidates carries no
    information for that pair; the accuracy is over DECISIVE pairs only. The first version of
    the harness divided by all pairs and reported `lines` at 0.286 (8 wins, 1 loss, 19 ties),
    which would have been read as "the linewidth component is actively misleading". It is
    silent, not wrong, and the tie count is what distinguishes the two.
    """
    per_dim = artefact["per_dimension"]
    assert per_dim, "no per-dimension breakdown"
    used = {k for p in artefact["pairs"] for k in p["details_A"]}
    assert set(per_dim) == used, (
        f"per-dimension keys {sorted(per_dim)} do not match the components the metric used "
        f"{sorted(used)}")
    for name, dim in per_dim.items():
        assert 0 < dim["n"] <= artefact["n_pairs"]
        assert dim["wins"] + dim["losses"] + dim["ties"] == dim["n"], (
            f"{name}: W/L/T does not sum to n")
        assert dim["n_decisive"] == dim["wins"] + dim["losses"]
        if dim["n_decisive"]:
            assert 0.0 <= dim["accuracy"] <= 1.0
            assert dim["accuracy"] == pytest.approx(
                dim["wins"] / dim["n_decisive"], abs=1e-4), (
                f"{name}: accuracy is not wins/decisive")
            lo, hi = dim["ci"]
            assert lo <= dim["accuracy"] <= hi, (
                f"{name}: CI {lo}-{hi} excludes {dim['accuracy']}")
        else:
            assert dim["accuracy"] is None, (
                f"{name}: an accuracy was reported with no decisive pair")


def test_a_dimension_that_never_moved_is_flagged_rather_than_reported_as_zero(artefact):
    """Treatment reach: a dimension where A and B never differ was not tested.

    The first run of this experiment used a transfer that applied only font size and aspect, so
    `palette`, `rules`, `letters` and `lines` were identical between the two candidates on almost
    every pair. The aggregate accuracy looked excellent and four of the six dimensions had not
    been exercised at all. `treatment_reach` records this explicitly, and any dimension that is
    never decisive must be marked `exercised: False` rather than silently reported as a number.
    """
    reach = artefact["treatment_reach"]
    per_dim = artefact["per_dimension"]
    assert set(reach) == set(per_dim)
    for name, rec in reach.items():
        assert rec["exercised"] == bool(per_dim[name]["n_decisive"]), (
            f"{name}: exercised flag disagrees with the decisive count")
        if not rec["exercised"]:
            assert per_dim[name]["accuracy"] is None


def test_leave_one_out_shows_which_component_carries_the_result(artefact):
    """The aggregate must be decomposable, or a single component can hide inside it.

    `without_aspect` is the case that matters: aspect is derived directly from the reference's
    measured width/height and is the easiest thing to reproduce, so if the accuracy collapses
    without it the metric is substantially an aspect check wearing five other components. The
    artefact must therefore carry that number, and CLAIM.md must state it.
    """
    loo = artefact.get("leave_one_out") or {}
    assert "all_dimensions" in loo, "leave-one-out must include the full model"
    assert loo["all_dimensions"]["accuracy"] == pytest.approx(
        artefact["discrimination_accuracy"], abs=1e-4), (
        "the leave-one-out baseline does not reproduce the headline accuracy")
    for name, rec in loo.items():
        if name == "all_dimensions":
            continue
        assert name.startswith("without_")
        assert 0 <= rec["n"] <= artefact["n_pairs"]
        assert 0.0 <= rec["accuracy"] <= 1.0
        assert rec["delta_vs_all"] == pytest.approx(
            rec["accuracy"] - loo["all_dimensions"]["accuracy"], abs=1e-4)
    # the concentration claim in the verdict must be backed by a real leave-one-out drop
    if "CONCENTRATION" in artefact["verdict"].upper():
        worst = min((v["delta_vs_all"] for k, v in loo.items() if k != "all_dimensions"))
        assert worst <= -0.15, (
            "the verdict claims concentration but no component's removal drops accuracy by 0.15")


def test_the_official_scorer_result_is_reported_honestly(artefact):
    """Agreement is a count over comparable, DECISIVE pairs.

    Two failure modes are forbidden here. An unavailable channel is an absence: counting it as a
    disagreement would manufacture evidence that the two metrics conflict, and counting it as
    agreement would manufacture the opposite. A TIE is also neither: the deviation score is a
    mean over the reference-activated dimensions, so two candidates that deviate identically land
    on the same number and the channel expresses no preference.
    """
    off = artefact["official_scorer"]
    n_scored = off["n_pairs_scored"]
    assert 0 <= n_scored <= artefact["n_pairs"]
    assert off["n_agree"] + off["n_disagree"] + off["n_tie"] == n_scored
    assert off["n_decisive"] == off["n_agree"] + off["n_disagree"]
    assert off["n_pairs_unavailable"] == artefact["n_pairs"] - n_scored
    if off["n_decisive"]:
        assert off["agreement_rate"] == pytest.approx(
            off["n_agree"] / off["n_decisive"], abs=1e-4)
        lo, hi = off["agreement_ci"]
        assert lo <= off["agreement_rate"] <= hi
    else:
        assert off["agreement_rate"] is None, (
            "an agreement rate was reported with no decisive pair")
    # the cross-metric table must partition the same pairs
    cross = artefact["cross_metric"]
    assert cross["n_pairs_both_scored"] == n_scored
    assert cross["both_agree"] == off["n_agree"]
    assert cross["figpipe_right_official_wrong"] + cross["figpipe_wrong_official_right"] \
        <= n_scored


def test_the_verdict_matches_the_measured_number(artefact):
    """The verdict sentence is a function of the numbers, not an editorial choice."""
    acc = artefact["discrimination_accuracy"]
    lo = artefact["binomial_ci_95"][0]
    verdict = artefact["verdict"].upper()
    if acc <= 0.5:
        assert "REFUTED" in verdict, (
            f"accuracy {acc} is at or below chance but the verdict does not say so: "
            f"{artefact['verdict']!r}")
    elif lo > 0.5:
        assert "SUPPORTED" in verdict
    else:
        assert "INCONCLUSIVE" in verdict


def test_the_claim_states_the_measured_result_and_not_a_promise(artefact):
    """CLAIM.md must carry the number, and must not still say human validation is pending."""
    if not CLAIM.is_file():
        pytest.skip("CLAIM.md absent")
    text = CLAIM.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "not validated by human judgement" not in lowered, (
        "CLAIM.md still carries the old 'pending' sentence")
    assert "human" in lowered, "the claim must still state what was NOT done"
    acc = f"{artefact['discrimination_accuracy']:.2f}"
    assert acc in text, (
        f"CLAIM.md does not state the measured discrimination accuracy {acc}")
    # and it must be honest about the instrument: a discrimination test is not a reader study
    assert "discriminat" in lowered or "proxy" in lowered, (
        "CLAIM.md must name what was measured instead of human judgement")


def _pair(i: int, *, win: bool, official_a=None, official_b=None) -> dict:
    """One synthetic pair record, in the shape `summarise` consumes.

    `reference` and `mismatch` are `paper/figure_id`, so the paper part is deliberately shared:
    the summary must work on the SAME-PAPER (hard) contrast, which is the headline arm.
    """
    d_a, d_b = (0.40, 0.10) if win else (0.10, 0.40)
    # the per-component values follow the same direction as the aggregate: a winning pair has
    # SMALLER component distances on B, which is what a per-dimension accuracy is computed from
    c_a, c_b = (0.30, 0.20) if win else (0.20, 0.30)
    return {
        "reference": f"paper{i // 2}/fig_{i}",
        "mismatch": f"paper{i // 2}/fig_{i + 1}",
        "reference_size_pt": [100.0, 80.0],
        "mismatch_contrast": "same_paper",
        "distance_A": d_a, "distance_B": d_b,
        "margin": round(d_a - d_b, 4),
        "correct": win, "tie": d_a == d_b,
        "details_A": {"sizes": c_a, "palette": c_a},
        "details_B": {"sizes": c_b, "palette": c_b},
        "official_A": official_a, "official_B": official_b,
        "official_available": official_a is not None and official_b is not None,
        "official_reason": None,
    }


def test_the_inverted_control_can_actually_fail():
    """A control that cannot fail is not a control -- check the arithmetic directly.

    This is the unit-level version of the negative control: on a hand-built ranking where the
    matched candidate is ALWAYS farther, the harness's own counting rule must report 0.0, and on
    the reversed ranking 1.0. No files, no rendering, no corpus.
    """
    import validate_style_metric as vsm

    pairs = [_pair(i, win=False, official_a=90.0, official_b=40.0) for i in range(10)]
    bad = vsm.summarise_discrimination(pairs, seed=1, skipped={}, n_refs=10)
    assert bad["discrimination_accuracy"] == 0.0
    assert bad["negative_control"]["accuracy"] == 1.0
    assert bad["negative_control"]["passes"] is False, (
        "an inverted ranking scored above chance and the control still passed")
    assert "REFUTED" in bad["verdict"].upper()

    good_pairs = [_pair(i, win=True, official_a=40.0, official_b=90.0) for i in range(10)]
    good = vsm.summarise_discrimination(good_pairs, seed=1, skipped={}, n_refs=10)
    assert good["discrimination_accuracy"] == 1.0
    assert good["negative_control"]["accuracy"] == 0.0
    assert good["negative_control"]["passes"] is True
    assert "SUPPORTED" in good["verdict"].upper()


def test_a_tie_is_not_counted_as_a_loss(artefact=None):
    """A dimension that says "same" on both candidates must not be scored as "wrong".

    This was a real defect in the first version: `lines` had 8 wins, 1 loss and 19 ties across
    30 pairs and was reported at 0.286, because the denominator was every pair. A reader would
    have concluded the linewidth component was actively misleading. It is silent on two thirds of
    the pairs, and the tie count is what distinguishes "silent" from "wrong".
    """
    import validate_style_metric as vsm

    pairs = []
    for i in range(20):
        p = _pair(i, win=True)
        if i < 10:
            # ten pairs where the component measures identically on both sides
            p["details_A"]["sizes"] = 0.25
            p["details_B"]["sizes"] = 0.25
        pairs.append(p)
    res = vsm.summarise_discrimination(pairs, seed=1, skipped={}, n_refs=20)
    sizes = res["per_dimension"]["sizes"]
    assert sizes["ties"] == 10
    assert sizes["n_decisive"] == 10
    assert sizes["accuracy"] == pytest.approx(1.0), (
        f"ties were counted against the dimension: {sizes}")
    assert res["treatment_reach"]["sizes"]["exercised"] is True


def test_a_component_that_never_moves_is_reported_as_unexercised():
    """If A and B never differ on a component, no accuracy may be invented for it."""
    import validate_style_metric as vsm

    pairs = []
    for i in range(10):
        p = _pair(i, win=True)
        p["details_A"]["lines"] = 0.5
        p["details_B"]["lines"] = 0.5
        pairs.append(p)
    res = vsm.summarise_discrimination(pairs, seed=1, skipped={}, n_refs=10)
    lines = res["per_dimension"]["lines"]
    assert lines["n_decisive"] == 0
    assert lines["accuracy"] is None, "an accuracy was reported for a component that never moved"
    assert lines["ties"] == 10
    assert res["treatment_reach"]["lines"]["exercised"] is False


def test_the_interval_widens_when_the_sample_shrinks():
    """Wilson, not Wald: the interval stays inside [0,1] and keeps width at the boundary.

    At k = n the Wilson upper bound is EXACTLY 1.0 (the formula's centre-plus-half saturates),
    so the property worth pinning is the LOWER bound: a perfect result on 30 pairs must still
    admit a non-zero error rate, and a smaller sample must admit a larger one. A Wald interval
    would report zero width here and claim certainty the experiment does not have.
    """
    import validate_style_metric as vsm

    lo30, hi30 = vsm.wilson_interval(30, 30)
    lo10, hi10 = vsm.wilson_interval(10, 10)
    assert 0.0 <= lo30 <= hi30 <= 1.0
    assert 0.0 <= lo10 <= hi10 <= 1.0
    assert (hi10 - lo10) > (hi30 - lo30), (
        "a 10-pair perfect result must be LESS certain than a 30-pair one")
    assert lo30 < 1.0 and lo10 < 1.0, (
        "a perfect result must still admit a non-zero error rate at its lower bound")
    assert lo10 < lo30, "fewer pairs must widen the interval downward"
    # the midpoint case must straddle chance
    lo, hi = vsm.wilson_interval(15, 30)
    assert lo < 0.5 < hi


def test_a_chance_result_is_not_dressed_up_as_success():
    """15/30 must read as a refutation, not as 'trending positive'."""
    import validate_style_metric as vsm

    pairs = [_pair(i, win=(i % 2 == 0)) for i in range(30)]
    res = vsm.summarise_discrimination(pairs, seed=1, skipped={}, n_refs=30)
    assert res["discrimination_accuracy"] == 0.5
    assert "REFUTED" in res["verdict"].upper(), (
        "a chance-level result must be reported as a refutation, not spun")
    # the official channel was unavailable everywhere: no rate may be invented
    assert res["official_scorer"]["n_pairs_scored"] == 0
    assert res["official_scorer"]["agreement_rate"] is None
    assert res["official_scorer"]["agreement_rate_including_ties"] is None


def test_an_official_tie_is_neither_agreement_nor_disagreement():
    """The deviation score can return the same number for both candidates.

    That is the channel expressing no preference, not the channel disagreeing with figpipe.
    Counting ties as disagreements would understate agreement and manufacture a conflict between
    two metrics that in fact never conflicted on this experiment.
    """
    import validate_style_metric as vsm

    pairs = []
    for i in range(10):
        # figpipe always right; official ties on four pairs and agrees on the other six
        if i < 4:
            pairs.append(_pair(i, win=True, official_a=80.0, official_b=80.0))
        else:
            pairs.append(_pair(i, win=True, official_a=40.0, official_b=90.0))
    res = vsm.summarise_discrimination(pairs, seed=1, skipped={}, n_refs=10)
    off = res["official_scorer"]
    assert off["n_pairs_scored"] == 10
    assert off["n_tie"] == 4
    assert off["n_agree"] == 6
    assert off["n_disagree"] == 0
    assert off["n_decisive"] == 6
    assert off["agreement_rate"] == pytest.approx(1.0), (
        "ties were counted against the official channel")
    assert off["agreement_rate_including_ties"] == pytest.approx(0.6)
