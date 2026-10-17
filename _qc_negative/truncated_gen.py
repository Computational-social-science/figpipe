import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
matplotlib.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'font.size':6})
fig=plt.figure(figsize=(89/25.4,60/25.4)); ax=fig.add_subplot(111)
x=np.arange(1,21); y=100+np.arange(20)
ax.plot(x,y,color='#D55E00',lw=1.0)
ax.set_ylim(y.min()-1,y.max()+1)
ax.set_xlabel('position (n)'); ax.set_ylabel('count (unitless)')
fig.savefig(r'E:\2026-AI4S\figpipe\_qc_negative\truncated_withgen.pdf', bbox_inches=None)
