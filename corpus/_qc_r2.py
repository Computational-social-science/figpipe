"""Build a COMPLIANT figure exactly like the negative test does, plus the two
violations, and verify the gate discriminates. My earlier c0_clean.pdf lacked
units/axis labels, which is why it failed -- that was MY test construction error,
not a gate defect."""
import pathlib, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_r2"); OUT.mkdir(exist_ok=True)
MM = 1/25.4
mpl = matplotlib
mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 6,
                     "axes.titlesize": 6, "axes.labelsize": 6,
                     "xtick.labelsize": 6, "ytick.labelsize": 6})

def base(values):
    fig = plt.figure(figsize=(89*MM, 60*MM))
    ax = fig.add_subplot(111)
    ax.plot(values, color="#0072B2", lw=1.0)
    ax.set_xlabel("sentence position (n)")
    ax.set_ylabel("error rate (%)")
    return fig, ax

# compliant
fig, ax = base(np.sin(np.arange(1,21)/4)+2)
fig.savefig(OUT/"ok_clean.pdf", bbox_inches=None); plt.close(fig)

# jet
fig = plt.figure(figsize=(89*MM, 60*MM)); ax = fig.add_subplot(111)
im = ax.imshow(np.random.default_rng(0).random((12,12)), cmap="jet")
fig.colorbar(im, ax=ax)
ax.set_xlabel("column (unitless)"); ax.set_ylabel("row (unitless)")
fig.savefig(OUT/"bad_jet.pdf", bbox_inches=None); plt.close(fig)

# truncated
fig = plt.figure(figsize=(89*MM, 60*MM)); ax = fig.add_subplot(111)
x = np.arange(1,21); y = 100 + np.arange(20)
ax.plot(x, y, color="#D55E00", lw=1.0)
ax.set_ylim(y.min()-1, y.max()+1)
ax.set_xlabel("position (n)"); ax.set_ylabel("count (unitless)")
fig.savefig(OUT/"bad_truncated.pdf", bbox_inches=None); plt.close(fig)

print("=" * 100)
print("QC DISCRIMINATION WITH CORRECTLY-CONSTRUCTED COMPLIANT CONTROL")
print("=" * 100)
for f, should in [("ok_clean.pdf","PASS"), ("bad_jet.pdf","FAIL"), ("bad_truncated.pdf","FAIL")]:
    rep = qc.run_qc(OUT/f)
    ok = rep.ok() if callable(rep.ok) else rep.ok
    got = "PASS" if ok else "FAIL"
    mark = "OK " if got == should else "*** WRONG ***"
    fails = rep.failures if not callable(rep.failures) else rep.failures()
    warns = rep.warnings if not callable(rep.warnings) else rep.warnings()
    print()
    print("  %-20s expected %-4s got %-4s %s  (FAIL=%d WARN=%d)"
          % (f, should, got, mark, len(fails), len(warns)))
    for c in fails:
        print("     FAIL %-24s %s" % (getattr(c,"id","?"), str(getattr(c,"detail",""))[:95]))
