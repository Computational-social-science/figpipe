import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pathlib

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\qc_test"); OUT.mkdir(exist_ok=True)
MM = 1/25.4

# V1: 4pt font (violates 5-7pt band)
fig, ax = plt.subplots(figsize=(183*MM, 60*MM))
ax.plot([1,2,3],[1,2,3]); ax.set_xlabel("x", fontsize=4); ax.set_ylabel("y", fontsize=4)
ax.tick_params(labelsize=4); fig.savefig(OUT/"v1_4pt.pdf", bbox_inches=None)
plt.close(fig)

# V2: wrong width (120mm, not 89/183)
fig, ax = plt.subplots(figsize=(120*MM, 60*MM))
ax.plot([1,2,3],[1,2,3]); fig.savefig(OUT/"v2_wrongwidth.pdf", bbox_inches=None)
plt.close(fig)

# V3: jet colormap + 8pt fonts
fig, ax = plt.subplots(figsize=(183*MM, 80*MM))
im = ax.imshow(np.random.rand(10,10), cmap="jet")
fig.colorbar(im); fig.savefig(OUT/"v3_jet.pdf", bbox_inches=None)
plt.close(fig)

# V4: type-3 fonts (Nature rejects)
import matplotlib as mpl
mpl.rcParams["pdf.fonttype"] = 3
fig, ax = plt.subplots(figsize=(183*MM, 60*MM))
ax.plot([1,2,3],[1,2,3]); ax.set_xlabel("x", fontsize=6)
fig.savefig(OUT/"v4_type3.pdf", bbox_inches=None)
plt.close(fig)
print("built 4 violation PDFs in", OUT)
