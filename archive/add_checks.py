"""Declare a machine-executable check for every enforced rule.

WHY THIS EXISTS
    The audit found the regression detector covered only 3 of 8 rules, because `evolve.py`
    hard-coded the checks in a dict keyed by rule ID. Adding a rule meant editing the loop;
    rules nobody edited were never re-checked, and the loop still reported "3/3 hold" -- a
    healthy-looking number over the wrong denominator.

    This script writes a `check` block into each rule, so the loop can be generic: read the
    rule, run its check, record the result. New rules become checkable by adding data, not by
    editing the loop.

    A rule with no possible machine check is left without one and is reported as such --
    the honest alternative to silently not checking it.
"""
from __future__ import annotations

import json
import pathlib

KB = pathlib.Path(r"E:\2026-AI4S\figpipe\knowledge\layout_rules.json")

# Each entry: rule id -> a check the loop can execute without knowing the rule's meaning.
CHECKS = {
    "L02": {"kind": "rcparams", "assert": {"savefig.bbox": None, "savefig.pad_inches": 0.0},
            "why": "an unpinned bbox pads the output past the column width"},
    "L03": {"kind": "rcparams_range",
            "keys": ["font.size", "axes.titlesize", "axes.labelsize",
                     "xtick.labelsize", "ytick.labelsize", "legend.fontsize"],
            "min": 5.0, "max": 7.0,
            "why": "a named size such as 'large' resolves to 1.2x the base and lands above "
                   "the ceiling"},
    "L04": {"kind": "symbol_exists", "module": "figpipe.style",
            "symbol": "suppress_log_exponents",
            "why": "10^n exponents cannot meet the 5-7 pt band at any admissible base"},
    "L05": {"kind": "rcparams", "assert": {"savefig.bbox": None},
            "why": "the save call can silently resize the figure"},
    "L06": {"kind": "rcparams", "assert": {"pdf.fonttype": 42, "ps.fonttype": 42},
            "why": "Type-3 outlines are rejected by Nature"},
    "L01": {"kind": "symbol_exists", "module": "figpipe.style", "symbol": "panel_letter",
            "why": "axes-relative panel letters get clipped in narrow panels"},
    "L07": {"kind": "symbol_exists", "module": "figpipe.audit", "symbol": "audit",
            "why": "source linting cannot catch these defects; the output must be audited"},
    "H02": {"kind": "ink_density_band", "min_pct": 3.0, "max_pct": 20.0,
            "why": "measured ink density on this pipeline's own figures",
            "note": "measured but NOT enforced: nothing in the code forces a figure into "
                    "this band, so the rule cannot be more than 'measured'"},
}


def main() -> int:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    added, skipped = [], []
    for r in kb["rules"]:
        chk = CHECKS.get(r["id"])
        if chk:
            r["check"] = chk
            added.append(r["id"])
        else:
            r["check"] = None
            skipped.append(r["id"])

    kb["check_coverage"] = {
        "rules_with_check": len(added),
        "rules_without_check": len(skipped),
        "without": skipped,
        "note": ("The loop executes each rule's `check` generically, so coverage is a property "
                 "of the data rather than of the loop's source. A rule with check=None is "
                 "reported as UNCHECKED, not counted as passing."),
    }
    kb["version"] += 1
    KB.write_text(json.dumps(kb, indent=2), encoding="utf-8")

    print(f"  knowledge base v{kb['version']}")
    print(f"  rules with an executable check: {len(added)}/{len(kb['rules'])}")
    if skipped:
        print(f"  rules without a check        : {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
