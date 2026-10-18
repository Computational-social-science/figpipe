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
"""
from __future__ import annotations

import json
import pathlib

KB = pathlib.Path(__file__).resolve().parents[1] / "knowledge" / "layout_rules.json"


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


def refresh(path: pathlib.Path = KB) -> dict:
    """Rewrite the stored check_coverage from the current rules; return it."""
    kb = json.loads(path.read_text(encoding="utf-8"))
    derived = compute(kb["rules"])
    stale = kb.get("check_coverage")
    kb["check_coverage"] = derived
    path.write_text(json.dumps(kb, indent=2), encoding="utf-8")
    return {"derived": derived, "previous": stale,
            "was_stale": bool(stale) and (
                stale.get("rules_with_check") != derived["rules_with_check"]
                or stale.get("rules_without_check") != derived["rules_without_check"])}


if __name__ == "__main__":
    res = refresh()
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
