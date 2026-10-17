"""CRITICAL AUDIT -- reproduce derived.json from measured.json using the project's OWN
documented exclusion rules, implemented independently."""
import json, pathlib
import numpy as np

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
raw = json.loads((ROOT/"corpus"/"measured.json").read_text(encoding="utf-8"))
claim = json.loads((ROOT/"corpus"/"derived.json").read_text(encoding="utf-8"))["derived"]

MAXW, MINW, MINPT = 210.0, 60.0, 2.0
kept, excl = [], {"too_wide":0,"too_narrow":0,"tiny_font":0}
for p in raw["papers"]:
    for f in p["figures"]:
        w = f["width_mm"]
        if w > MAXW: excl["too_wide"] += 1; continue
        if w < MINW: excl["too_narrow"] += 1; continue
        if f.get("min_font_pt") is not None and f["min_font_pt"] < MINPT:
            excl["tiny_font"] += 1; continue
        kept.append(f)

widths = [f["width_mm"] for f in kept]
mins = [f["min_font_pt"] for f in kept if f.get("min_font_pt")]
def near(t, tol=3.0): return sum(1 for w in widths if abs(w-t) <= tol)

print("=" * 100)
print("INDEPENDENT RECOMPUTATION OF derived.json")
print("=" * 100)
print("  %-28s %14s %14s %s" % ("quantity","mine","derived.json","match"))
def row(label, mine, theirs):
    ok = (abs(mine-theirs) < 1e-6) if isinstance(mine,(int,float)) and isinstance(theirs,(int,float)) else mine==theirs
    print("  %-28s %14s %14s %s" % (label, mine, theirs, "OK" if ok else "*** MISMATCH ***"))
    return ok
row("bands_raw", sum(len(p["figures"]) for p in raw["papers"]), claim["bands_raw"])
row("bands_kept", len(kept), claim["bands_kept"])
for k in ["too_wide","too_narrow","tiny_font"]:
    row("excluded."+k, excl[k], claim["bands_excluded"][k])
row("width n", len(widths), claim["width_mm"]["n"])
row("width p10", round(float(np.percentile(widths,10)),1), claim["width_mm"]["p10"])
row("width p25", round(float(np.percentile(widths,25)),1), claim["width_mm"]["p25"])
row("width median", round(float(np.percentile(widths,50)),1), claim["width_mm"]["median"])
row("width p75", round(float(np.percentile(widths,75)),1), claim["width_mm"]["p75"])
row("width p90", round(float(np.percentile(widths,90)),1), claim["width_mm"]["p90"])
row("within 89mm", near(89.0), claim["width_mm"]["within_3mm_of_89"])
row("within 183mm", near(183.0), claim["width_mm"]["within_3mm_of_183"])
row("share near column", round((near(89.0)+near(183.0))/len(widths),4), claim["width_mm"]["share_near_a_column"])
row("minfont n", len(mins), claim["min_font_pt"]["n"])
row("minfont median", round(float(np.median(mins)),2), claim["min_font_pt"]["median"])
row("share below 5pt", round(float(np.mean([m<5 for m in mins])),4), claim["min_font_pt"]["share_below_5pt"])

print()
print("=" * 100)
print("THE REAL PROBLEM: what does the EXCLUSION RULE NOT exclude?")
print("=" * 100)
h = np.array([f["height_mm"] for f in kept])
nf = np.array([f.get("n_text_spans",0) for f in kept])
print("  kept bands: %d" % len(kept))
print("  height_mm: min %.1f  median %.1f  max %.1f" % (h.min(), np.median(h), h.max()))
print("  A page is 279 mm tall. Bands taller than 279 mm survived the filter: %d" % (h>279).sum())
print("  Bands taller than 240 mm (near-page): %d" % (h>240).sum())
print("  Bands with > 100 text spans (text-heavy, likely not figures): %d" % (nf>100).sum())
print("  Bands with 0 text spans (no caption/labels at all): %d" % (nf==0).sum())
print()
print("  *** The exclusion rule checks WIDTH and MIN-FONT only. ***")
print("  *** It never checks HEIGHT, aspect ratio, or text density, so a full page ***")
print("  *** of body text (191.7 x 250.1 mm, 249 spans) passes as a 'figure band'. ***")
