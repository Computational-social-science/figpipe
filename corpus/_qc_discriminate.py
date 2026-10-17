import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc
NEG = pathlib.Path(r"E:\2026-AI4S\figpipe\_qc_negative")
p = NEG/"neg_viridis.pdf"
rep = qc.run_qc(p)
fails = rep.failures if not callable(rep.failures) else rep.failures()
print("=" * 100)
print("WHY DOES A CLEAN VIRIDIS FIGURE FAIL? (5 failures)")
print("=" * 100)
for c in fails:
    print("  %-26s %s" % (getattr(c,"id","?"), str(getattr(c,"detail",""))[:110]))
print()
print("  => If these are 'no generator script' / 'axes unlabeled', they are")
print("     requirements of a SUBMISSION, not defects of a figure. A gate that")
print("     fails every figure it sees cannot discriminate.")
print()
print("=" * 100)
print("DOES IT DISCRIMINATE AT ALL? clean.pdf vs the violations")
print("=" * 100)
for f in ["clean.pdf","neg_jet.pdf","neg_viridis.pdf","neg_cividis.pdf","truncated.pdf"]:
    q = NEG/f
    if not q.exists(): continue
    r = qc.run_qc(q)
    ok = r.ok() if callable(r.ok) else r.ok
    fa = r.failures if not callable(r.failures) else r.failures()
    wa = r.warnings if not callable(r.warnings) else r.warnings()
    print("  %-20s ok=%-5s FAIL=%d WARN=%d" % (f, ok, len(fa), len(wa)))
