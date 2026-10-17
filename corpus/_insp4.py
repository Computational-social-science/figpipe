import json, pathlib
kb = json.loads(pathlib.Path(r"E:\2026-AI4S\figpipe\knowledge\layout_rules.json").read_text(encoding="utf-8"))
for r in kb["rules"]:
    if r["id"] in ("E01","E02","H02"):
        print("=" * 90)
        print("%s  conf=%s  enforced=%s" % (r["id"], r["confidence"], r.get("enforced")))
        print("  rule   : %s" % r.get("rule","")[:150])
        print("  evidence: %s" % r.get("evidence","")[:250])
        print("  caveat : %s" % str(r.get("caveat",""))[:250])
print()
print("=" * 90)
print("kb.corpus block (the provenance for E01/E02):")
print(json.dumps(kb.get("corpus"), indent=1, ensure_ascii=False))
