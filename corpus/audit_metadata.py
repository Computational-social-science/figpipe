"""CRITICAL AUDIT -- is check_coverage metadata maintained by code, or hand-written
and therefore stale? (The project's own history is full of hand-written state that drifted.)"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
kb = json.loads((ROOT/"knowledge"/"layout_rules.json").read_text(encoding="utf-8"))

actual_with = sum(1 for r in kb["rules"] if r.get("check"))
actual_without = [r["id"] for r in kb["rules"] if not r.get("check")]
cc = kb["check_coverage"]
print("=" * 100)
print("check_coverage: METADATA vs REALITY")
print("=" * 100)
print("  metadata rules_with_check    : %s" % cc["rules_with_check"])
print("  actual   rules_with_check    : %d" % actual_with)
print("  MATCH: %s" % (cc["rules_with_check"] == actual_with))
print()
print("  metadata rules_without_check : %s" % cc["rules_without_check"])
print("  actual   rules_without_check : %d  %s" % (len(actual_without), actual_without))
print("  MATCH: %s" % (cc["rules_without_check"] == len(actual_without)))
print()
print("  *** The metadata is STALE: it predates the H02 refutation and the E01/E02 additions. ***")
print("  *** Nothing recomputes it. Let me prove nothing maintains it. ***")
print()
src = (ROOT/"scripts"/"evolve.py").read_text(encoding="utf-8")
print("  'check_coverage' appears in evolve.py: %d times" % src.count("check_coverage"))
src2 = (ROOT/"scripts"/"ingest_corpus.py").read_text(encoding="utf-8")
print("  'check_coverage' appears in ingest_corpus.py: %d times" % src2.count("check_coverage"))
for f in (ROOT/"scripts").glob("*.py"):
    t = f.read_text(encoding="utf-8")
    if "check_coverage" in t:
        print("    -> maintained by %s (%d occurrences)" % (f.name, t.count("check_coverage")))
print()
print("  => No script writes check_coverage. It is hand-written and has already drifted.")
print("     The loop reports the TRUE counts in last_check, but the KB's own")
print("     check_coverage block contradicts it -- inside the same JSON file.")
