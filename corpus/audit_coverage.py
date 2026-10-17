import json, pathlib
ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
kb = json.loads((ROOT/"knowledge"/"layout_rules.json").read_text(encoding="utf-8"))
rules = kb["rules"]
print("rules total: %d" % len(rules))
print()
print("=== generic check coverage (the fix for defect 2) ===")
with_check = [r["id"] for r in rules if r.get("check")]
without = [r["id"] for r in rules if not r.get("check")]
print("  rules WITH a check   : %d  %s" % (len(with_check), with_check))
print("  rules WITHOUT a check: %d  %s" % (len(without), without))
print()
print("  kb.check_coverage says:", json.dumps(kb.get("check_coverage"), indent=2)[:400])
print()
print("=== does the loop execute checks GENERICALLY or still hardcode? ===")
ev = (ROOT/"scripts"/"evolve.py").read_text(encoding="utf-8")
print("  'H02' appears %d times in evolve.py" % ev.count("H02"))
print("  'check' appears %d times" % ev.count("check"))
import re
# look for hardcoded rule ids
ids = sorted(set(re.findall(r'"([LHKE]\d\d)"', ev)))
print("  hardcoded rule ids in evolve.py: %s" % ids)
print()
print("=== last_check summary in the KB ===")
print(json.dumps(kb.get("last_check"), indent=2))
