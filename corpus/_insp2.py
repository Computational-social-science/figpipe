import json, pathlib
import numpy as np
d = json.loads(pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\figures_caption_anchored.json").read_text(encoding="utf-8"))
L=[]
def p(s=""): L.append(str(s))
p("records: %d" % len(d))
p("keys: %s" % list(d[0].keys()))
p()
r = d[0]
p("record[0]: figure_number=%s kind=%s page=%s width=%.1f height=%.1f" %
  (r["figure_number"], r["kind"], r["page"], r["width_mm"], r["height_mm"]))
p("  caption_text[:120]: %s" % r["caption_text"][:120].replace("\n"," "))
p()
w = np.array([r["width_mm"] for r in d], dtype=float)
h = np.array([r["height_mm"] for r in d], dtype=float)
papers = sorted(set(r["paper"] for r in d))
kinds = {}
for r in d: kinds[r["kind"]] = kinds.get(r["kind"],0)+1
p("=" * 90)
p("NEW DETECTOR: %d figures across %d papers" % (len(d), len(papers)))
p("=" * 90)
p("kinds: %s" % kinds)
p("width_mm : min %.1f  median %.1f  max %.1f" % (w.min(), np.median(w), w.max()))
p("height_mm: min %.1f  median %.1f  max %.1f" % (h.min(), np.median(h), h.max()))
p()
p("PHYSICAL IMPOSSIBILITY CHECK (old detector's failure):")
p("  height > 279 mm (A4): %d" % int((h>279).sum()))
p("  width  > 210 mm (A4): %d" % int((w>210).sum()))
p("  height > 240 mm     : %d" % int((h>240).sum()))
p("  height <  20 mm     : %d" % int((h<20).sum()))
p()
p("near 89mm: %d   near 183mm: %d   share: %.3f"
  % (int((np.abs(w-89)<=3).sum()), int((np.abs(w-183)<=3).sum()),
     ((np.abs(w-89)<=3)|(np.abs(w-183)<=3)).mean()))
p()
p("per-paper figure counts:")
for pp in papers:
    n = sum(1 for r in d if r["paper"]==pp)
    p("  %-58s %d" % (pp[:58], n))
pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\_insp2.txt").write_text("\n".join(L), encoding="utf-8")
print("wrote _insp2.txt (%d lines)" % len(L))
