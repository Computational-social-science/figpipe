"""CRITICAL AUDIT R2 -- test the NEW qc.py via run_qc on isolated violations."""
import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_clean")
print("=" * 100)
print("NEW figpipe/qc.py run_qc() ON THE SAME ISOLATED VIOLATIONS")
print("=" * 100)
for fn, desc, should in [
    ("c0_clean.pdf",         "clean control",           "PASS"),
    ("c1_jet_only.pdf",      "jet colormap only",       "FAIL"),
    ("c2_truncated_axis.pdf","truncated y-axis only",   "FAIL"),
    ("c3_4pt_only.pdf",      "one 4pt annotation only", "FAIL")]:
    p = OUT/fn
    rep = qc.run_qc(p)
    fails, warns, skips = rep.failures(), rep.warnings(), rep.skipped()
    got = "PASS" if rep.ok() else "FAIL"
    mark = "OK " if got == should else "*** WRONG ***"
    print()
    print("  %-24s expected %-4s got %-4s %s" % (fn, should, got, mark))
    print("     failures=%d warnings=%d skipped=%d" % (len(fails), len(warns), len(skips)))
    for c in fails[:5]:
        print("       FAIL %-28s %s" % (getattr(c,"check_id",getattr(c,"tool","?")), str(getattr(c,"detail",c))[:100]))
    for c in warns[:3]:
        print("       warn %-28s %s" % (getattr(c,"check_id",getattr(c,"tool","?")), str(getattr(c,"detail",c))[:100]))
    for c in skips[:2]:
        print("       skip %-28s %s" % (getattr(c,"check_id",getattr(c,"tool","?")), str(getattr(c,"detail",c))[:90]))
