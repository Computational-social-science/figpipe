"""CRITICAL AUDIT R2 -- test the NEW qc.py against the same isolated violations."""
import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_clean")
print("=" * 100)
print("NEW figpipe/qc.py ON THE SAME ISOLATED VIOLATIONS")
print("=" * 100)
print("public API:", [n for n in dir(qc) if not n.startswith("_") and callable(getattr(qc,n))][:14])
print()
for fn, desc, should in [
    ("c0_clean.pdf",         "clean control",           "PASS"),
    ("c1_jet_only.pdf",      "jet colormap only",       "FAIL"),
    ("c2_truncated_axis.pdf","truncated y-axis only",   "FAIL"),
    ("c3_4pt_only.pdf",      "one 4pt annotation only", "FAIL")]:
    p = OUT/fn
    try:
        rep = qc.audit(p)
    except TypeError:
        rep = qc.audit(str(p))
    except Exception as e:
        print("  %-24s EXCEPTION: %s: %s" % (fn, type(e).__name__, e)); continue
    fails = rep.failures()
    warns = rep.warnings()
    got = "PASS" if rep.ok() else "FAIL"
    mark = "OK " if got == should else "*** WRONG ***"
    print("  %-24s expected %-4s got %-4s %s  failures=%d warnings=%d"
          % (fn, should, got, mark, len(fails), len(warns)))
    for c in fails[:4]:
        print("       FAIL [%s] %s" % (getattr(c,"check_id",getattr(c,"tool","?")), str(getattr(c,"detail",c))[:110]))
    for c in warns[:3]:
        print("       warn [%s] %s" % (getattr(c,"check_id",getattr(c,"tool","?")), str(getattr(c,"detail",c))[:110]))
