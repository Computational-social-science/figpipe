"""Isolate: do the SPECIFIC palette and truncation checks fire correctly?"""
import pathlib, sys
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_clean")
NEG = pathlib.Path(r"E:\2026-AI4S\figpipe\_qc_negative")
print("=" * 100)
print("CHECK 1: check_colour_policy on jet vs viridis/cividis")
print("=" * 100)
for f in ["neg_jet.pdf","neg_viridis.pdf","neg_cividis.pdf","jet.pdf","probe_jet.pdf","probe_viridis.pdf"]:
    p = NEG/f
    if not p.exists(): p = OUT/f
    if not p.exists(): continue
    try:
        c = qc.check_colour_policy(p)
        status = getattr(c,"status",None) or getattr(c,"ok",None)
        print("  %-22s status=%-8s %s" % (f, status, str(getattr(c,"detail",c))[:95]))
    except Exception as e:
        print("  %-22s EXCEPTION %s: %s" % (f, type(e).__name__, e))

print()
print("=" * 100)
print("CHECK 2: check_honesty_from_artifact on truncated vs clean")
print("=" * 100)
for f in ["c2_truncated_axis.pdf","c0_clean.pdf"]:
    try:
        cs = qc.check_honesty_from_artifact(OUT/f)
        print("  %s -> %d checks" % (f, len(cs)))
        for c in cs:
            print("     %-22s %-8s %s" % (getattr(c,"check_id","?"), getattr(c,"status","?"),
                                          str(getattr(c,"detail",""))[:90]))
    except Exception as e:
        print("  %s EXCEPTION %s: %s" % (f, type(e).__name__, e))
