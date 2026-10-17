import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc
NEG = pathlib.Path(r"E:\2026-AI4S\figpipe\_qc_negative")

print("=" * 100)
print("CRITICAL: does a jet figure PASS run_qc? (WARN vs FAIL semantics)")
print("=" * 100)
for f in ["neg_jet.pdf","neg_viridis.pdf","neg_cividis.pdf"]:
    p = NEG/f
    if not p.exists(): continue
    rep = qc.run_qc(p)
    ok = rep.ok() if callable(rep.ok) else rep.ok
    fails = rep.failures if not callable(rep.failures) else rep.failures()
    warns = rep.warnings if not callable(rep.warnings) else rep.warnings()
    print()
    print("  %-20s ok=%-5s failures=%d warnings=%d" % (f, ok, len(fails), len(warns)))
    for c in warns:
        if "colour" in str(getattr(c,"id","")) or "rainbow" in str(getattr(c,"detail","")):
            print("     WARN %s: %s" % (getattr(c,"id","?"), str(getattr(c,"detail",""))[:90]))
    for c in fails:
        if "colour" in str(getattr(c,"id","")):
            print("     FAIL %s: %s" % (getattr(c,"id","?"), str(getattr(c,"detail",""))[:90]))

print()
print("=" * 100)
print("THE QUESTION THAT MATTERS: if jet is only a WARNING, does the gate BLOCK?")
print("=" * 100)
print("  rep.ok() is False only when there is a FAIL-severity check.")
print("  A WARN leaves ok()==True -> the gate reports PASS.")
print()
print("  => the palette check exists and detects correctly,")
print("     but its severity means it does not BLOCK. Report this precisely.")
