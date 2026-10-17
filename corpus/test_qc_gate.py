"""CRITICAL AUDIT -- does the QC gate ACTUALLY catch violations?"""
import json, pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
from figpipe.audit import audit

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_test")
cases = [
 ("v1_4pt.pdf",         "4 pt font (below the 5 pt floor)"),
 ("v2_wrongwidth.pdf",  "120 mm width (not 89/183)"),
 ("v3_jet.pdf",         "jet colormap (not Okabe-Ito)"),
 ("v4_type3.pdf",       "Type-3 fonts (Nature rejects)"),
]
print("=" * 100)
print("QC GATE: constructed violations vs what figpipe.audit reports")
print("=" * 100)
for fn, desc in cases:
    p = OUT / fn
    r = audit(p, expect_width_mm=None)
    checks = [f["check"] for f in r["findings"]]
    print()
    print("  %-22s %s" % (fn, desc))
    print("    ok=%s  findings=%s" % (r["ok"], checks if checks else "NONE"))
    for f in r["findings"]:
        print("       [%s] %s" % (f["check"], f["detail"][:110]))
    if r["ok"]:
        print("    *** GATE PASSED A VIOLATING FIGURE ***")

print()
print("=" * 100)
print("KEY QUESTION: is there ANY palette / colormap check in audit.py?")
print("=" * 100)
import inspect
src = inspect.getsource(audit)
for word in ["palette", "okabe", "colormap", "jet", "hue", "color"]:
    print("  %-12s in audit(): %s" % (word, word.lower() in src.lower()))
