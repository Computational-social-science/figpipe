import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
MM=1/25.4
matplotlib.rcParams.update({"pdf.fonttype":42,"ps.fonttype":42,"font.size":6,
 "axes.titlesize":6,"axes.labelsize":6,"xtick.labelsize":6,"ytick.labelsize":6})
fig=plt.figure(figsize=(89*MM,60*MM)); ax=fig.add_subplot(111)
im=ax.imshow(np.random.default_rng(0).random((12,12)),cmap="jet")
fig.colorbar(im,ax=ax)
ax.set_xlabel("column (unitless)"); ax.set_ylabel("row (unitless)")
fig.savefig(r"E:\2026-AI4S\figpipe\corpus\qc_r2\bad2_jet.pdf", bbox_inches=None)
