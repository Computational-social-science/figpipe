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

#: The weights `styleprofile.compare` declares, mirrored here so a change to one without the other
#: is caught rather than silently believed.
DECLARED_WEIGHTS = {"sizes": 0.25, "letters": 0.10, "lines": 0.20,
                    "rules": 0.10, "palette": 0.25, "aspect": 0.10}


def load() -> dict:
    if not SOURCE.is_file():
        raise SystemExit(f"  no validation record at {SOURCE}")
    return json.loads(SOURCE.read_text(encoding="utf-8"))


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
    others = [k for k in dims if k != best]
    strongest_other = max(dims[k]["accuracy"] for k in others)
    if dims[best]["accuracy"] >= 0.80 and strongest_other <= 0.60:
        print(f"  VERDICT: the metric is, on this corpus, very nearly a {best.upper()}-ONLY check.")
        print(f"           {best} alone scores {dims[best]['accuracy']:.3f}; every other component is")
        print(f"           at or below {strongest_other:.3f}, i.e. chance or worse. The summary's")
        print(f"           caveat understates this: it is not that aspect 'matters', it is that the")
        print(f"           other five components contribute nothing here.")
        print()
        print(f"           leave-one-out == aspect-alone ({leave_one_out(pairs):.3f} == "
              f"{dims[best]['accuracy']:.3f}), so this is NOT overfitting -- aspect genuinely")
        print(f"           carries it on THIS corpus. Whether it carries it on a broader one is")
        print(f"           exactly what human validation would settle.")
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
