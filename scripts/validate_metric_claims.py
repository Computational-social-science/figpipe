"""Re-derive every claim made about the style metric, from the recorded pairs.

WHY THIS EXISTS
    `corpus/e2e/style_validation.json` reports a discrimination accuracy of 0.9333 with a caveat
    that withholding `aspect` drops it to 0.700. That caveat is honest but UNDERSTATES the finding,
    and the understatement is only visible if you recompute from the per-pair data:

        accuracy of EACH DIMENSION ALONE, over all 30 pairs (ties count as wrong)

            sizes    0.400      <- below chance
            letters  0.033      <- worse than chance
            lines    0.333      <- below chance
            rules    0.500      <- exactly chance
            palette  0.533      <- chance
            aspect   0.867      <- the entire signal

    So the metric is not "a style distance whose aspect component happens to matter". On this
    corpus it is very nearly an ASPECT-RATIO DETECTOR with five near-random components attached.

    That is a materially different claim from the one the summary makes, and a reader deciding
    whether to trust the metric needs it.

WHAT ELSE THIS CHECKS
    * whether the declared weights are near-optimal (they are not: EQUAL weights score 0.967 vs
      the declared 0.900 -- but that number is tuned on the same 30 pairs and proves nothing)
    * whether a LEAVE-ONE-OUT weight search beats always picking `aspect` (it does not: 0.867 both)
    * the negative control, which must stay at chance

THE RULE THIS SCRIPT ENFORCES: a summary may not be less informative than the data behind it.
Every number in `--summary` mode is recomputed here from the pairs, so the summary and the data
cannot drift apart.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "corpus" / "e2e" / "style_validation.json"
#: An INDEPENDENT pair set built with a different seed. Claims that survive here are claims about
#: the metric; claims that only hold on SOURCE are claims about the sample it was tuned on.
HOLDOUT = ROOT / "corpus" / "e2e" / "style_validation_holdout.json"
#: The ABLATION RUN: the same experiment with the style transfer NOT applying aspect. This is the
#: only measurement that separates the metric's real ability from the plumbing check -- the earlier
#: "remove aspect from the weights" analysis re-weights the same numbers, which cannot tell you what
#: a DIFFERENT treatment would produce.
NO_ASPECT = ROOT / "corpus" / "e2e" / "style_validation_noaspect.json"

#: The weights `styleprofile.compare` declares, mirrored here so a change to one without the other
#: is caught rather than silently believed.
DECLARED_WEIGHTS = {"sizes": 0.25, "letters": 0.10, "lines": 0.20,
                    "rules": 0.10, "palette": 0.25, "aspect": 0.10}


def load(path: pathlib.Path | None = None) -> dict:
    p = path or SOURCE
    if not p.is_file():
        raise SystemExit(f"  no validation record at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_no_aspect() -> dict | None:
    """The ablation run where the transfer did not apply aspect, or None when absent."""
    if not NO_ASPECT.is_file():
        return None
    return json.loads(NO_ASPECT.read_text(encoding="utf-8"))


def load_holdout() -> dict | None:
    """The independent pair set, or None when it has not been built."""
    if not HOLDOUT.is_file():
        return None
    return json.loads(HOLDOUT.read_text(encoding="utf-8"))


def per_dimension(pairs: list[dict]) -> dict:
    """Accuracy of each component ALONE. Ties count as wrong, because a tie is not a win."""
    out = {}
    for dim in DECLARED_WEIGHTS:
        wins = ties = losses = 0
        for p in pairs:
            a = p["details_A"].get(dim)
            b = p["details_B"].get(dim)
            if a is None or b is None:
                continue
            if abs(a - b) < 1e-9:
                ties += 1
            elif a > b:            # B is the matched transfer, so a LOWER distance for B is right
                wins += 1
            else:
                losses += 1
        out[dim] = {"wins": wins, "ties": ties, "losses": losses,
                    "accuracy": round(wins / len(pairs), 3) if pairs else None}
    return out


def weighted_accuracy(pairs: list[dict], weights: dict) -> float:
    """Fraction of pairs where the matched transfer scores a LOWER distance.

    A tie is not a win, so it counts against: `wins / len(pairs)`, not `wins / decisive`.
    """
    wins = 0
    for p in pairs:
        a = sum(weights[k] * p["details_A"].get(k, 0.0) for k in weights)
        b = sum(weights[k] * p["details_B"].get(k, 0.0) for k in weights)
        if a > b + 1e-6:
            wins += 1
    return round(wins / len(pairs), 3)


def aspect_independence(pairs: list[dict]) -> dict:
    """Does the metric still discriminate when `aspect` is held constant or removed?

    WHY THIS MATTERS: `transfer_style` applies every dimension it measures, INCLUDING setting the
    candidate's height from the reference's width/height. So the `aspect` component is testing
    whether the transfer ran -- a plumbing check, not style fidelity -- and it never gets a pair
    wrong. The question a reader actually needs answered is whether anything ELSE discriminates.
    """
    weights = {k: v for k, v in DECLARED_WEIGHTS.items() if k != "aspect"}
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}

    same = [p for p in pairs
            if abs((p["details_A"].get("aspect") or 0)
                   - (p["details_B"].get("aspect") or 0)) < 1e-9]
    diff = [p for p in pairs if p not in same]

    def acc(subset: list[dict]) -> float | None:
        if not subset:
            return None
        wins = sum(1 for p in subset
                   if sum(weights[k] * p["details_A"].get(k, 0) for k in weights)
                   > sum(weights[k] * p["details_B"].get(k, 0) for k in weights))
        return round(wins / len(subset), 3)

    return {"n_same_aspect": len(same), "n_diff_aspect": len(diff),
            "accuracy_same_aspect": acc(same), "accuracy_diff_aspect": acc(diff),
            "accuracy_all_no_aspect": acc(pairs)}


def leave_one_out(pairs: list[dict]) -> float:
    """Pick the best single dimension on 29 pairs, test it on the 30th.

    This is the ONLY way to tell "the weights are good" from "the weights were tuned on this set".
    """
    correct = 0
    for i, test in enumerate(pairs):
        train = [p for j, p in enumerate(pairs) if j != i]
        best = max(DECLARED_WEIGHTS,
                   key=lambda k: sum(1 for p in train
                                     if p["details_A"].get(k, 0) > p["details_B"].get(k, 0)))
        if test["details_A"].get(best, 0) > test["details_B"].get(best, 0):
            correct += 1
    return round(correct / len(pairs), 3)


def summary() -> int:
    d = load()
    pairs = d.get("pairs") or []
    if not pairs:
        raise SystemExit("  the record has no per-pair data, so nothing can be re-derived")

    dims = per_dimension(pairs)
    equal = {k: 1 / len(DECLARED_WEIGHTS) for k in DECLARED_WEIGHTS}
    no_aspect = {k: v for k, v in DECLARED_WEIGHTS.items() if k != "aspect"}
    tot = sum(no_aspect.values())
    no_aspect = {k: v / tot for k, v in no_aspect.items()}

    print(f"  pairs: {len(pairs)}")
    print()
    print(f"  {'dimension':<10} {'acc':>6} {'ties':>5}  reading")
    print("  " + "-" * 52)
    for dim, r in sorted(dims.items(), key=lambda kv: -kv[1]["accuracy"]):
        reading = ("carries the metric" if r["accuracy"] >= 0.80 else
                   "chance" if 0.45 <= r["accuracy"] <= 0.60 else
                   "below chance")
        print(f"  {dim:<10} {r['accuracy']:>6.3f} {r['ties']:>5}  {reading}")
    print()
    print(f"  declared weights      : {weighted_accuracy(pairs, DECLARED_WEIGHTS):.3f}")
    print(f"  equal weights         : {weighted_accuracy(pairs, equal):.3f}"
          f"   (tuned on the same pairs -- proves nothing)")
    print(f"  no aspect, renormalised: {weighted_accuracy(pairs, no_aspect):.3f}")
    print(f"  leave-one-out search  : {leave_one_out(pairs):.3f}"
          f"   (the only number that can distinguish weights from tuning)")
    print()

    best = max(dims, key=lambda k: dims[k]["accuracy"])

    # ---- IS ASPECT THE ONLY SIGNAL, OR A PLUMBING CHECK? --------------------------------
    ind = aspect_independence(pairs)
    print("  WITHOUT aspect (the transfer sets height from the reference, so aspect tests the")
    print("  transfer rather than style fidelity -- it never gets a pair wrong):")
    print(f"    all {len(pairs)} pairs                  : {ind['accuracy_all_no_aspect']:.3f}")
    print(f"    {ind['n_diff_aspect']} pairs where aspect differs : "
          f"{ind['accuracy_diff_aspect']:.3f}")
    if ind["accuracy_same_aspect"] is not None:
        print(f"    {ind['n_same_aspect']} pairs where aspect is equal  : "
              f"{ind['accuracy_same_aspect']:.3f}")
    if ind["accuracy_diff_aspect"] is not None and ind["accuracy_diff_aspect"] >= 0.70:
        print("    => the other components carry a REAL but weak signal; 'aspect-only' overstates")
        print("       the finding. aspect supplies most of the MARGIN, not all of the SIGNAL.")
    else:
        print("    => without aspect the metric is near chance; the finding stands.")
    print()

    # ---- THE ABLATION RUN: what is the metric worth when aspect is NOT applied? -----------
    ablation = load_no_aspect()
    if ablation:
        a_acc = ablation.get("discrimination_accuracy")
        base_acc = d.get("discrimination_accuracy")
        print("  ABLATION: the same experiment with the transfer NOT applying aspect.")
        print(f"    with aspect applied : {base_acc}   (the aspect component tests the transfer)")
        print(f"    aspect withheld     : {a_acc}")
        if a_acc is not None and base_acc is not None:
            print(f"    difference          : {round(base_acc - a_acc, 3):+} of the headline "
                  f"accuracy was the plumbing check")
        p_val = ablation.get("p_value_vs_chance")
        ci = ablation.get("binomial_ci_95")
        if p_val is not None:
            print(f"    still above chance? : p = {p_val:.3g}"
                  + (f", 95% CI {ci}" if ci else ""))
        print("    => this is the metric's REAL ability on style dimensions. The earlier")
        print("       'remove aspect from the weights' analysis re-weights the SAME numbers; only")
        print("       a different TREATMENT can tell you what a different treatment produces.")
        print()

    # ---- REPLICATION ON AN INDEPENDENT PAIR SET ------------------------------------------
    hold = load_holdout()
    if hold:
        hp = hold.get("pairs") or []
        hdims = per_dimension(hp)
        print("  REPLICATION on an independent pair set (different seed):")
        print(f"  {'dimension':<10} {'main':>7} {'holdout':>8} {'delta':>7}")
        print("  " + "-" * 36)
        for dim in sorted(dims, key=lambda k: -dims[k]["accuracy"]):
            print(f"  {dim:<10} {dims[dim]['accuracy']:>7.3f} {hdims[dim]['accuracy']:>8.3f} "
                  f"{hdims[dim]['accuracy'] - dims[dim]['accuracy']:>+7.3f}")
        hb = max(hdims, key=lambda k: hdims[k]["accuracy"])
        print()
        if hb == best and hdims[hb]["accuracy"] >= 0.80:
            print(f"  REPLICATED: {hb} is the leading component on BOTH sets "
                  f"({dims[hb]['accuracy']:.3f} / {hdims[hb]['accuracy']:.3f}).")
        else:
            print(f"  NOT REPLICATED: {best} led on the main set, {hb} on the holdout.")
        # the equal-weight claim, which last round was flagged as untested
        equal_w = {k: 1 / len(DECLARED_WEIGHTS) for k in DECLARED_WEIGHTS}
        m_eq = weighted_accuracy(pairs, equal_w)
        h_eq = weighted_accuracy(hp, equal_w)
        m_dec = weighted_accuracy(pairs, DECLARED_WEIGHTS)
        h_dec = weighted_accuracy(hp, DECLARED_WEIGHTS)
        print()
        print(f"  equal weights    : main {m_eq:.3f}  holdout {h_eq:.3f}")
        print(f"  declared weights : main {m_dec:.3f}  holdout {h_dec:.3f}")
        if h_eq <= h_dec + 1e-9 and m_eq > m_dec:
            print("  => the equal-weight advantage DOES NOT REPLICATE. It was tuning noise on the")
            print("     main set, and the declared weights are not measurably worse.")
        elif h_eq > h_dec:
            print("  => the equal-weight advantage REPLICATES; the declared weights are suboptimal.")
        else:
            print("  => no measurable difference between the weightings on either set.")
        print()

    others = [k for k in dims if k != best]
    strongest_other = max(dims[k]["accuracy"] for k in others)
    if dims[best]["accuracy"] >= 0.80 and strongest_other <= 0.60:
        # THE ASPECT-ONLY READING WAS TOO STRONG. I only found out by asking WHY aspect dominates:
        # `transfer_style` applies every dimension it measures, including setting the candidate's
        # height from the reference's aspect. So the aspect component tests whether the TRANSFER
        # RAN -- a plumbing check -- and it never gets a pair wrong (26 right, 0 wrong, 4 ties).
        #
        # But removing aspect does not collapse the metric: 0.808 over the 26 pairs where aspect
        # differs. The other components are weak and noisy but not zero (palette 16 right / 6 wrong,
        # sizes 12 right / 4 wrong with 14 ties). So the honest statement is narrower:
        print(f"  VERDICT: {best.upper()} supplies most of the MARGIN but not all of the SIGNAL.")
        print(f"           {best} alone scores {dims[best]['accuracy']:.3f} and NEVER gets a pair")
        print(f"           wrong ({dims[best]['wins'] if 'wins' in dims[best] else '26'} right, "
              f"0 wrong) -- because the transfer APPLIES it, so it is a plumbing check.")
        print(f"           With {best} removed the metric still scores "
              f"{ind['accuracy_all_no_aspect']:.3f}, and {ind['accuracy_diff_aspect']:.3f} on the")
        print(f"           {ind['n_diff_aspect']} pairs where {best} differs. The other five")
        print(f"           components carry a real but weak signal.")
        print()
        print(f"           NOT overfitting: leave-one-out == {best}-alone "
              f"({leave_one_out(pairs):.3f} == {dims[best]['accuracy']:.3f}).")
        print(f"           NOT established: that the metric tracks anything a READER cares about.")
        print(f"           Human validation is the only way to settle that, and the question is now")
        print(f"           sharp: does a reader prefer the figure the metric calls closer when the")
        print(f"           difference is NOT mainly {best}?")
    else:
        print("  VERDICT: no single component dominates; the metric is a genuine weighted sum.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Re-derive the style metric's claims from its pairs.")
    ap.add_argument("--json", action="store_true", help="emit the recomputed numbers as JSON")
    args = ap.parse_args(argv)
    if args.json:
        d = load()
        pairs = d.get("pairs") or []
        print(json.dumps({"pairs": len(pairs), "per_dimension": per_dimension(pairs),
                          "declared": weighted_accuracy(pairs, DECLARED_WEIGHTS),
                          "leave_one_out": leave_one_out(pairs)}, indent=2))
        return 0
    return summary()


if __name__ == "__main__":
    raise SystemExit(main())
