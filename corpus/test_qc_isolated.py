import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
from figpipe.audit import audit
OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_clean")
print()
print("=" * 100)
print("QC GATE ON ISOLATED VIOLATIONS (everything else compliant)")
print("=" * 100)
for fn, desc, should in [
    ("c0_clean.pdf",        "clean control", "PASS"),
    ("c1_jet_only.pdf",     "jet colormap only", "FAIL"),
    ("c2_truncated_axis.pdf","truncated y-axis only", "FAIL"),
    ("c3_4pt_only.pdf",     "one 4pt annotation only", "FAIL")]:
    r = audit(OUT/fn, expect_width_mm=None)
    checks = [f["check"] for f in r["findings"]]
    verdict = "PASS" if r["ok"] else "FAIL"
    mark = "OK " if verdict == should else "*** WRONG ***"
    print("  %-24s expected %-4s got %-4s %s  findings=%s"
          % (fn, should, verdict, mark, checks if checks else "none"))
    for f in r["findings"]:
        print("       [%s] %s" % (f["check"], f["detail"][:100]))
