import json, pathlib
import numpy as np
d = json.loads(pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\figures_caption_anchored.json").read_text(encoding="utf-8"))
w = np.array([r["width_mm"] for r in d])
for tol in (3.0, 3.5, 4.0, 5.0):
    n89 = int((np.abs(w-89)<=tol).sum()); n183 = int((np.abs(w-183)<=tol).sum())
    print("  tol=%.1f mm: near89=%2d near183=%2d total=%2d share=%.3f" % (tol,n89,n183,n89+n183,(n89+n183)/len(w)))
print()
print("  exact counts: near89=%d near183=%d of %d -> %.3f"
      % (int((np.abs(w-89)<=3).sum()), int((np.abs(w-183)<=3).sum()), len(w),
         ((np.abs(w-89)<=3)|(np.abs(w-183)<=3)).mean()))
print()
print("  papers in JSON: %d" % len(set(r["paper"] for r in d)))
print()
print("  width distribution (sorted, all 73):")
print("   " + " ".join("%.1f" % x for x in sorted(w)))
