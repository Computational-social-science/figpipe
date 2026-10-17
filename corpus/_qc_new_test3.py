import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc
OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_clean")
print("=" * 100)
print("NEW figpipe/qc.py run_qc() ON ISOLATED VIOLATIONS")
print("=" * 100)
for fn, desc, should in [
    ("c0_clean.pdf",         "clean control",           "PASS"),
    ("c1_jet_only.pdf",      "jet colormap only",       "FAIL"),
    ("c2_truncated_axis.pdf","truncated y-axis only",   "FAIL"),
    ("c3_4pt_only.pdf",      "one 4pt annotation only", "FAIL")]:
    rep = qc.run_qc(OUT/fn)
    ok = rep.ok() if callable(rep.ok) else rep.ok
    fails = rep.failures if not callable(rep.failures) else rep.failures()
    got = "PASS" if ok else "FAIL"
    mark = "OK " if got == should else "*** WRONG ***"
    print()
    print("  %-24s expected %-4s got %-4s %s   (failures=%d)"
          % (fn, should, got, mark, len(fails)))
    for c in fails[:5]:
        cid = getattr(c, "check_id", None) or getattr(c, "tool", None) or "?"
        det = getattr(c, "detail", None) or str(c)
        print("       FAIL %-26s %s" % (cid, str(det)[:105]))
