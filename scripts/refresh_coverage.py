"""Recompute check_coverage from the rules themselves, every run.

WHY THIS EXISTS
    The adversarial audit found `check_coverage` claiming "8 rules with a check, 1 without"
    while the truth was "7 with, 4 without" -- and the same JSON's `last_check` block said
    `unchecked: 4`. Two numbers, one file, contradicting each other.

    Root cause: `check_coverage` was written once by a one-shot migration script and never
    maintained. Every rule added afterwards (H02 -> refuted, E01/E02 -> void) changed the truth
    without changing the metadata.

    A metadata field that is written once and never recomputed is worse than no field: it is a
    stale claim that looks authoritative. This module derives it from the rules on every call,
    so it cannot drift.

WHY IT WRITES THROUGH THE SHARED GUARD
    This module rewrites `knowledge/layout_rules.json` -- the whole knowledge base -- to update one
    derived field. A write of the full file can therefore lose rules as easily as the benchmark
    report lost rows, and the fix has to be the same one, not a local copy of it. The guard compares
    the `rules` collection; `--allow-shrink` exists for the deliberate case where rules are merged
    away upstream.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import guard  # noqa: E402

KB = ROOT / "knowledge" / "layout_rules.json"


def compute(rules: list[dict]) -> dict:
    """The only correct value of check_coverage, derived rather than stored."""
    with_check = [r["id"] for r in rules if r.get("check")]
    without = [r["id"] for r in rules if not r.get("check")]
    unchecked_by_confidence: dict[str, int] = {}
    for r in rules:
        if not r.get("check"):
            c = r.get("confidence", "?")
            unchecked_by_confidence[c] = unchecked_by_confidence.get(c, 0) + 1
    return {
        "rules_total": len(rules),
        "rules_with_check": len(with_check),
        "rules_without_check": len(without),
        "without": without,
        "without_by_confidence": unchecked_by_confidence,
        "derived": True,
        "note": ("Derived from the rules on every run, not stored by a migration. A rule with "
                 "check=None is reported UNCHECKED and never counted as passing."),
    }


def refresh(path: pathlib.Path = KB, *, allow_shrink: bool = False) -> dict:
    """Rewrite the stored check_coverage from the current rules; return it.

    The write goes through `figpipe.guard`, which compares the `rules` collection: a refresh that
    would drop rules is refused with both counts and the override named, and the file on disk stays
    exactly as it was. A refresh of a file that is missing or corrupt is allowed -- the guard treats
    an unreadable existing file as empty rather than blocking the run.
    """
    raw, _state = guard.read_json(path)
    if not isinstance(raw, dict) or not isinstance(raw.get("rules"), list):
        raise ValueError(f"{path} does not hold a rules list; refusing to derive coverage from it")
    kb = raw
    derived = compute(kb["rules"])
    stale = kb.get("check_coverage")
    kb["check_coverage"] = derived
    guard.write_or_refuse(path, kb, key="rules", unit="rules", allow_shrink=allow_shrink,
                          override="--allow-shrink", dumps=lambda p: json.dumps(p, indent=2))
    return {"derived": derived, "previous": stale,
            "was_stale": bool(stale) and (
                stale.get("rules_with_check") != derived["rules_with_check"]
                or stale.get("rules_without_check") != derived["rules_without_check"])}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--allow-shrink", action="store_true",
                    help="permit the refresh to write FEWER rules than the file holds. Refused by "
                         "default: the knowledge base is the accumulated rule set.")
    args = ap.parse_args(argv)
    try:
        res = refresh(allow_shrink=args.allow_shrink)
    except guard.ShrinkRefused as exc:
        print(f"  refused: {exc}")
        print("  layout_rules.json is unchanged")
        return 4
    d = res["derived"]
    print(f"  check_coverage recomputed: {d['rules_with_check']} with / "
          f"{d['rules_without_check']} without, of {d['rules_total']}")
    print(f"  without: {d['without']}")
    print(f"  by confidence: {d['without_by_confidence']}")
    if res["was_stale"]:
        p = res["previous"]
        print(f"  WAS STALE: claimed {p.get('rules_with_check')} with / "
              f"{p.get('rules_without_check')} without -> corrected")
    else:
        print("  (already accurate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
