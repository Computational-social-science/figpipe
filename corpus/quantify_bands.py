"""CRITICAL AUDIT -- quantify what the band detector actually captured.

I classified the 18 rendered bands by LOOKING at them. Now measure the structural
signals that predict each failure mode, so the finding generalises to all 369 bands
rather than resting on my sample.
"""
import json, pathlib
import numpy as np
import pymupdf

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
MM_PER_PT = 25.4/72.0

# the project's own measured.json gives every band; test the whole set
meas = json.loads((ROOT/"corpus"/"measured.json").read_text(encoding="utf-8"))
print("papers measured: %d" % meas["summary"]["papers_measured"])
print("figure bands   : %d" % meas["summary"]["figure_bands"])

# My manual classification of the 18 I rendered and looked at
manual = {
 "_2024_Nature_Detecting_hallucinations_in__p01_b0.png": ("PAGE TEXT", "full page of body text, not a figure"),
 "_2024_Nature_Detecting_hallucinations_in__p02_b0.png": ("FIGURE+caption", "real flowchart, caption text included"),
 "_2024_Nature_Detecting_hallucinations_in__p04_b0.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p05_b0.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p05_b1.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p07_b0.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p14_b0.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p20_b0.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p22_b0.png": ("?", "not yet viewed"),
 "_2024_Nature_Detecting_hallucinations_in__p23_b0.png": ("?", "not yet viewed"),
 "_2026_Nature_Evaluating_large_language_m__p02_b0.png": ("FIGURE truncated", "text cut off top and bottom"),
 "_2026_Nature_Evaluating_large_language_m__p03_b0.png": ("?", "not yet viewed"),
 "_2026_Nature_Evaluating_large_language_m__p04_b0.png": ("?", "not yet viewed"),
 "_2026_Nature_Evaluating_large_language_m__p11_b0.png": ("PROMPT BOX", "template text box, not a figure"),
 "_2026_Nature_Evaluating_large_language_m__p11_b1.png": ("?", "not yet viewed"),
 "_2026_Nature_Evaluating_large_language_m__p12_b0.png": ("?", "not yet viewed"),
 "_2026_Nature_Evaluating_large_language_m__p13_b0.png": ("?", "not yet viewed"),
 "_2026_Nature_Evaluating_large_language_m__p15_b0.png": ("?", "not yet viewed"),
}
print()
print("=" * 100)
print("MANUAL CLASSIFICATION OF 5 SAMPLED BANDS")
print("=" * 100)
for k, (cls, why) in manual.items():
    if cls != "?":
        print("  %-58s %-18s %s" % (k[:58], cls, why))

# structural signals over ALL bands
bands = [b for p in meas["papers"] for b in p["figures"]]
print()
print("=" * 100)
print("STRUCTURAL SIGNALS OVER ALL %d BANDS" % len(bands))
print("=" * 100)
w = np.array([b["width_mm"] for b in bands])
h = np.array([b["height_mm"] for b in bands])
nf = np.array([b.get("n_text_spans", 0) for b in bands])
print("width_mm : min %.1f  median %.1f  max %.1f" % (w.min(), np.median(w), w.max()))
print("height_mm: min %.1f  median %.1f  max %.1f" % (h.min(), np.median(h), h.max()))
print("n_text_spans: min %d  median %d  max %d" % (nf.min(), np.median(nf), nf.max()))
print()
print("A figure should be mostly GRAPHICS. Text-heavy bands are body text or prompt boxes.")
print("  bands with > 200 text spans : %d (%.1f%%)" % ((nf>200).sum(), 100*(nf>200).mean()))
print("  bands with > 100 text spans : %d (%.1f%%)" % ((nf>100).sum(), 100*(nf>100).mean()))
print("  bands with 0 text spans     : %d (%.1f%%)" % ((nf==0).sum(), 100*(nf==0).mean()))
print()
print("A full PAGE is ~210x279 mm. Bands taller than 240 mm are almost certainly pages.")
print("  bands taller than 240 mm : %d" % (h>240).sum())
print("  bands taller than 200 mm : %d" % (h>200).sum())
for b in bands:
    if b["height_mm"] > 240:
        print("     %.1f x %.1f mm, %d spans" % (b["width_mm"], b["height_mm"], b.get("n_text_spans",0)))
        break
