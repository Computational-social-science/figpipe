import json, pathlib
import numpy as np
ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
kb = json.loads((ROOT/"knowledge"/"layout_rules.json").read_text(encoding="utf-8"))
new = json.loads((ROOT/"corpus"/"figures_caption_anchored.json").read_text(encoding="utf-8"))
old_derived = json.loads((ROOT/"corpus"/"derived.json").read_text(encoding="utf-8"))["derived"]

w = np.array([r["width_mm"] for r in new])
h = np.array([r["height_mm"] for r in new])

L=[]
def p(s=""): L.append(str(s))
p("=" * 96)
p("THE KNOWLEDGE BASE NOW CONTRADICTS THE NEW DETECTOR -- in the same repo")
p("=" * 96)
p()
p("E01 (in layout_rules.json) says:")
p("  median width 171.6 mm; 27.6%% within 3 mm of 89/183")
p("  evidence: 369 bands from 38 papers (OLD detector)")
p()
p("NEW detector (figures_caption_anchored.json) says:")
p("  %d figures from %d papers" % (len(new), len(set(r["paper"] for r in new))))
p("  median width %.1f mm" % np.median(w))
p("  within 3mm of 89/183: %d (%.1f%%)"
  % (int(((np.abs(w-89)<=3)|(np.abs(w-183)<=3)).sum()),
     100*((np.abs(w-89)<=3)|(np.abs(w-183)<=3)).mean()))
p()
p("  => E01's headline numbers (171.6 mm, 27.6%%) come from a detector the")
p("     project has now declared ~50%% WRONG and rewritten.")
p("     The KB still presents them as 'Measured'.")
p()
p("=" * 96)
p("QUANTIFY THE DISAGREEMENT")
p("=" * 96)
p("  old median 171.6 mm  vs  new median %.1f mm   (delta %+.1f mm)"
  % (np.median(w), np.median(w)-171.6))
p("  old near-column 27.6%%  vs  new %.1f%%  (delta %+.1f pp)"
  % (100*((np.abs(w-89)<=3)|(np.abs(w-183)<=3)).mean(),
     100*((np.abs(w-89)<=3)|(np.abs(w-183)<=3)).mean()-27.6))
p("  old n=369 bands      vs  new n=%d figures" % len(new))
p()
p("  E02: 34.0%% below 5pt on 188 bands -- the new detector does not compute")
p("  font sizes at all (no min_font_pt key in the 73 records):")
keys = set()
for r in new: keys |= set(r.keys())
p("    new record keys: %s" % sorted(keys))
p("    min_font_pt present: %s" % ("min_font_pt" in keys))
p()
p("  => E02 has NO replacement measurement. It cites a detector that no longer exists,")
p("     and the new detector does not measure the quantity E02 is about.")
p()
p("=" * 96)
p("DOES THE KB FLAG THIS?")
p("=" * 96)
for r in kb["rules"]:
    if r["id"] in ("E01","E02"):
        p("  %s confidence=%s caveat=%s" % (r["id"], r["confidence"], str(r.get("caveat"))[:80]))
p()
p("  The caveat says 'NOT YET TRUSTWORTHY ... P0 requires a 20-band manual validation'.")
p("  P0 has NOW been done (detector_verification.json: 5/5) -- but on the NEW detector.")
p("  So the caveat's stated condition is met for a detector E01 does not use.")
p()
p("=" * 96)
p("IS THE OLD DETECTOR STILL THE SOURCE OF ANY LIVE NUMBER?")
p("=" * 96)
p("  corpus/derived.json (tracked): bands_kept=%d, median=%.1f"
  % (old_derived["bands_kept"], old_derived["width_mm"]["median"]))
p("  corpus/measured.json (tracked): 420 bands from 38 papers")
p("  knowledge/layout_rules.json corpus block: bands_kept=369, papers=38")
p("  corpus/figures_caption_anchored.json (NEW, tracked): %d figures, %d papers"
  % (len(new), len(set(r["paper"] for r in new))))
p()
p("  => FOUR tracked artefacts; TWO incompatible corpora definitions coexist.")
p("     Nothing marks derived.json/measured.json as superseded.")
(ROOT/"corpus"/"_insp5.txt").write_text("\n".join(L), encoding="utf-8")
print("wrote _insp5.txt (%d lines)" % len(L))
