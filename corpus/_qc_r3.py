import pathlib, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_r2")
MM = 1/25.4
matplotlib.rcParams.update({"pdf.fonttype":42,"ps.fonttype":42,"font.size":6,
  "axes.titlesize":6,"axes.labelsize":6,"xtick.labelsize":6,"ytick.labelsize":6})

def build(kind, name):
    src = OUT/(name+".py")
    body = f'''import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
MM=1/25.4
matplotlib.rcParams.update({{"pdf.fonttype":42,"ps.fonttype":42,"font.size":6,
 "axes.titlesize":6,"axes.labelsize":6,"xtick.labelsize":6,"ytick.labelsize":6}})
fig=plt.figure(figsize=(89*MM,60*MM)); ax=fig.add_subplot(111)
'''
    if kind=="clean":
        body += 'ax.plot(np.sin(np.arange(1,21)/4)+2,color="#0072B2",lw=1.0)\nax.set_xlabel("sentence position (n)"); ax.set_ylabel("error rate (%)")\n'
    elif kind=="jet":
        body += 'im=ax.imshow(np.random.default_rng(0).random((12,12)),cmap="jet")\nfig.colorbar(im,ax=ax)\nax.set_xlabel("column (unitless)"); ax.set_ylabel("row (unitless)")\n'
    elif kind=="trunc":
        body += 'x=np.arange(1,21); y=100+np.arange(20)\nax.plot(x,y,color="#D55E00",lw=1.0)\nax.set_ylim(y.min()-1,y.max()+1)\nax.set_xlabel("position (n)"); ax.set_ylabel("count (unitless)")\n'
    body += f'fig.savefig(r"{OUT/name}.pdf", bbox_inches=None)\n'
    src.write_text(body, encoding="utf-8")
    # run it
    import subprocess
    subprocess.run([sys.executable, str(src)], check=True, capture_output=True)
    return src

print("=" * 100)
print("QC GATE WITH PROVENANCE SUPPLIED (as the tests do)")
print("=" * 100)
for kind, name, should in [("clean","ok2_clean","PASS"),("jet","bad2_jet","FAIL"),("trunc","bad2_trunc","FAIL")]:
    gen = build(kind, name)
    rep = qc.run_qc(OUT/(name+".pdf"), source_script=gen)
    ok = rep.ok() if callable(rep.ok) else rep.ok
    got = "PASS" if ok else "FAIL"
    mark = "OK " if got==should else "*** WRONG ***"
    fails = rep.failures if not callable(rep.failures) else rep.failures()
    print()
    print("  %-16s expected %-4s got %-4s %s  (FAIL=%d)" % (name, should, got, mark, len(fails)))
    for c in fails:
        print("     FAIL %-24s %s" % (getattr(c,"id","?"), str(getattr(c,"detail",""))[:95]))
