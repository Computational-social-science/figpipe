import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# figpipe -> matplotlib; 1 panel(s), 183.0 x 90.0 mm
fig = plt.figure(figsize=(7.2047, 3.5433))
df = pd.DataFrame({'year': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024], 'group': ['control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'control', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated', 'treated'], 'response': [0.3, 0.3018, 0.3044, 0.3125, 0.3121, 0.3239, 0.3248, 0.3278, 0.3212, 0.3208, 0.3253, 0.3339, 0.3493, 0.3319, 0.3556, 0.3478, 0.3562, 0.3765, 0.3717, 0.3713, 0.2809, 0.2872, 0.3249, 0.3379, 0.3429, 0.3711, 0.3826, 0.3975, 0.4155, 0.4445, 0.4516, 0.468, 0.4794, 0.5082, 0.5074, 0.5402, 0.5483, 0.5791, 0.5834, 0.601], 'se': [0.0106, 0.0082, 0.008, 0.0127, 0.0088, 0.0107, 0.0081, 0.0114, 0.0091, 0.0074, 0.0095, 0.0105, 0.0096, 0.0089, 0.0102, 0.009, 0.0084, 0.0084, 0.0118, 0.0098, 0.0101, 0.0102, 0.0069, 0.0102, 0.014, 0.0076, 0.0112, 0.0114, 0.0113, 0.0086, 0.0091, 0.0076, 0.0096, 0.0123, 0.0084, 0.006, 0.0098, 0.0114, 0.0093, 0.013]})

ax = fig.add_subplot(1, 1, 1)
ax.plot(df['year'], df['response'], 'o', ms=2.8, color='#0072b2', markeredgecolor='black', markeredgewidth=0.3)
xs = np.linspace(df['year'].min(), df['year'].max(), 80)
coef = np.polyfit(df['year'], df['response'], 1)
ax.plot(xs, np.polyval(coef, xs), '-', lw=0.8, color='#d55e00')
ax.set_xlabel('Year')
ax.set_ylabel('Response (a.u.)')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_visible(True)
ax.grid(False)
ax.tick_params(direction='out')
plt.rcParams['font.family'] = 'sans-serif'
ax.legend(frameon=False)
for _line in ax.get_lines(): _line.set_linewidth(0.8)

fig.tight_layout()
fig.savefig('figure.pdf')
fig.savefig('figure.png', dpi=400)
