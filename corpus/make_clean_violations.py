"""CRITICAL AUDIT -- isolate the QC checks. Make figures that are CLEAN except for ONE
violation each, so the gate's behaviour is not masked by unrelated failures."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np, pathlib

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_clean"); OUT.mkdir(exist_ok=True)
MM = 1/25.4
mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                     "font.size": 6, "axes.titlesize": 6, "axes.labelsize": 6,
                     "xtick.labelsize": 6, "ytick.labelsize": 6,
                     "savefig.bbox": None, "savefig.pad_inches": 0})

def base(w=183, h=60):
    fig, ax = plt.subplots(figsize=(w*MM, h*MM))
    ax.plot([1,2,3],[1,2,3])
    return fig, ax

# C0: clean control (should PASS)
fig, ax = base(); ax.set_xlabel("x"); ax.set_ylabel("y")
fig.savefig(OUT/"c0_clean.pdf"); plt.close(fig)

# C1: ONLY the jet colormap is wrong; everything else compliant
fig, ax = plt.subplots(figsize=(183*MM, 80*MM))
im = ax.imshow(np.random.rand(10,10), cmap="jet")
cb = fig.colorbar(im); cb.ax.tick_params(labelsize=6)
fig.savefig(OUT/"c1_jet_only.pdf"); plt.close(fig)

# C2: ONLY truncated y-axis (starts at 5, data spans 0-10)
fig, ax = base(); ax.plot([0,1,2],[6,8,10]); ax.set_ylim(5.5, 10.5)
ax.set_xlabel("x"); ax.set_ylabel("y")
fig.savefig(OUT/"c2_truncated_axis.pdf"); plt.close(fig)

# C3: ONLY a 4pt annotation (base 6pt, one label at 4pt)
fig, ax = base(); ax.set_xlabel("x"); ax.set_ylabel("y")
ax.annotate("tiny", (2,2), fontsize=4)
fig.savefig(OUT/"c3_4pt_only.pdf"); plt.close(fig)
print("built clean-context violations in", OUT)
