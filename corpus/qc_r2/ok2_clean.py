import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
MM=1/25.4
matplotlib.rcParams.update({"pdf.fonttype":42,"ps.fonttype":42,"font.size":6,
 "axes.titlesize":6,"axes.labelsize":6,"xtick.labelsize":6,"ytick.labelsize":6})
fig=plt.figure(figsize=(89*MM,60*MM)); ax=fig.add_subplot(111)
ax.plot(np.sin(np.arange(1,21)/4)+2,color="#0072B2",lw=1.0)
ax.set_xlabel("sentence position (n)"); ax.set_ylabel("error rate (%)")
fig.savefig(r"E:\2026-AI4S\figpipe\corpus\qc_r2\ok2_clean.pdf", bbox_inches=None)
