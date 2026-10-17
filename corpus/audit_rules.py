"""CRITICAL AUDIT -- can I reproduce each rule's evidence from its own claim?

For every rule with a numeric evidence claim, recompute it independently.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
kb = json.loads((ROOT/"knowledge"/"layout_rules.json").read_text(encoding="utf-8"))

print("=" * 100)
print("RULE-BY-RULE EVIDENCE REPRODUCIBILITY")
print("=" * 100)
for r in kb["rules"]:
    print()
    print("  %-5s %-46s conf=%-11s enforced=%s" % (r["id"], r["name"][:46], r["confidence"], r.get("enforced")))
    ev = r.get("evidence", "")
    print("     evidence: %s" % ev[:150])

print()
print("=" * 100)
print("REPRODUCE THE NUMERIC CLAIMS")
print("=" * 100)

# E01 / E02 come from corpus/derived.json -- recompute from measured.json
meas = json.loads((ROOT/"corpus"/"measured.json").read_text(encoding="utf-8"))
derived = json.loads((ROOT/"corpus"/"derived.json").read_text(encoding="utf-8"))["derived"]
bands = [b for p in meas["papers"] for b in p["figures"]]
print()
print("E01 claim: 'median width 171.6 mm; only 27.6%% within 3 mm of 89 or 183'")
w = np.array([b["width_mm"] for b in bands])
print("  measured.json raw: n=%d median=%.1f" % (len(w), np.median(w)))
print("  derived.json says: n=%d median=%s" % (derived["width_mm"]["n"], derived["width_mm"]["median"]))
print("  MATCH: %s" % (abs(np.median(w) - derived["width_mm"]["median"]) < 0.2))

# the derived pipeline excludes bands; check the exclusion arithmetic
kept = derived["bands_kept"]; raw = derived["bands_raw"]
exc = derived["bands_excluded"]
print()
print("  exclusion arithmetic: raw %d - kept %d = %d excluded" % (raw, kept, raw-kept))
print("  derived bands_excluded sum = %d" % sum(exc.values()))
print("  MATCH: %s" % ((raw-kept) == sum(exc.values())))

print()
print("E02 claim: '34.0%% of bands contain text below 5 pt; median 5.0'")
mins = [b["min_font_pt"] for b in bands if "min_font_pt" in b]
print("  measured.json: n=%d median=%.2f  share<5 = %.4f"
      % (len(mins), np.median(mins), np.mean([m<5 for m in mins])))
print("  derived.json: n=%s median=%s share=%s"
      % (derived["min_font_pt"]["n"], derived["min_font_pt"]["median"], derived["min_font_pt"]["share_below_5pt"]))
print("  MATCH: %s" % (abs(np.mean([m<5 for m in mins]) - derived["min_font_pt"]["share_below_5pt"]) < 0.005))

print()
print("L02 claim: 'a 198.8 mm figure rescaled to 183 mm shrinks 5 pt to 4.61 pt'")
print("  arithmetic: 5 * 183/198.8 = %.4f pt" % (5*183/198.8))
print("  MATCH: %s" % (abs(5*183/198.8 - 4.61) < 0.01))

print()
print("L03 claim: \"'large' resolves to 1.2x base; 7 pt base -> 8.4 pt\"")
print("  arithmetic: 7 * 1.2 = %.1f pt" % (7*1.2))
print("  MATCH: %s" % (abs(7*1.2 - 8.4) < 1e-9))

print()
print("L04 claim: 'matplotlib draws the exponent at ~0.7x base; base 7.0 -> 4.90 pt'")
print("  arithmetic: 7 * 0.7 = %.2f pt" % (7*0.7))
print("  MATCH: %s" % (abs(7*0.7 - 4.90) < 1e-9))
print("  base 6.0 -> %.2f ; base 5.0 -> %.2f" % (6*0.7, 5*0.7))
print("  claim says 6.0 -> 4.20, 5.0 -> 3.50 : %s"
      % (abs(6*0.7-4.20)<1e-9 and abs(5*0.7-3.50)<1e-9))
