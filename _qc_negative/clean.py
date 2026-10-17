import matplotlib.pyplot as plt, numpy as np
x = np.arange(1, 21)
fig, ax = plt.subplots(figsize=(89/25.4, 60/25.4))
ax.plot(x, np.sin(x/4) + 2, color='#0072B2')
ax.set_xlabel('sentence position (n)')
ax.set_ylabel('error rate (%)')
fig.savefig('clean.pdf')
