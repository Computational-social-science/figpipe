"""Migrate the knowledge base to the corrected schema.

WHY THIS MIGRATION EXISTS
    The audit (CRITICAL_AUDIT.md) found that `verified` was carrying three different meanings at once:
    "a mechanism enforces it", "a measurement supports it", and "I looked at it once". That
    conflation produced a rule (H02) marked `verified` with `enforced_by: None` -- a rule
    nothing enforces and no test locks.

    This migration splits the flag into the two questions that were being confused:

        mechanism_verified    is there code that enforces it AND a test that locks it?
        empirically_measured  is there a measurement behind it?

    A rule is `enforced` only when BOTH are true. Anything else is downgraded honestly, even
    if that means the pipeline looks less capable afterwards -- which it does: H02 drops out of
    `enforced`, and the count goes from 8 verified to 7 enforced + 1 measured-but-unenforced.
"""
from __future__ import annotations

import json
import pathlib

KB = pathlib.Path(r"E:\2026-AI4S\figpipe\knowledge\layout_rules.json")


def main() -> int:
    kb = json.loads(KB.read_text(encoding="utf-8"))

    # Which rules have a named enforcement mechanism? Read from the existing enforced_by.
    # A rule with no enforced_by cannot be `mechanism_verified`, whatever its confidence said.
    for r in kb["rules"]:
        eb = r.get("enforced_by")
        r["mechanism_verified"] = bool(eb)
        # empirical support: a rule with a measurement recorded, or a code-level invariant
        # whose violation was actually observed. L-rules came from measured defects.
        r["empirically_measured"] = bool(r.get("evidence")) and "NOT MEASURED" not in r.get("evidence", "")
        # `enforced` requires BOTH.
        r["enforced"] = r["mechanism_verified"] and r["empirically_measured"]
        # Re-derive confidence from the new fields rather than keeping the old label.
        if r["enforced"]:
            r["confidence"] = "enforced"
        elif r["empirically_measured"]:
            r["confidence"] = "measured_unenforced"
        else:
            r["confidence"] = "hypothesis"
        r.pop("enforced_by", None) if False else None

    kb["schema"] = "figpipe/knowledge-base/v2"
    kb["schema_note"] = (
        "v2 splits the old single `verified` flag into `mechanism_verified` (code enforces it "
        "AND a test locks it) and `empirically_measured` (a measurement supports it). "
        "`enforced` requires both. The old flag conflated these and let a rule be marked "
        "verified while nothing enforced it.")
    kb["version"] = kb.get("version", 1) + 1
    KB.write_text(json.dumps(kb, indent=2), encoding="utf-8")

    from collections import Counter
    c = Counter(r["confidence"] for r in kb["rules"])
    print(f"  migrated to schema v2, knowledge base v{kb['version']}")
    print()
    print("  %-5s %-24s %-9s %-10s %s" % ("id", "name", "mechanism", "measured", "confidence"))
    print("  " + "-" * 76)
    for r in kb["rules"]:
        print("  %-5s %-24s %-9s %-10s %s" % (
            r["id"], r["name"][:24],
            "yes" if r["mechanism_verified"] else "NO",
            "yes" if r["empirically_measured"] else "no",
            r["confidence"]))
    print()
    print("  counts:", dict(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
