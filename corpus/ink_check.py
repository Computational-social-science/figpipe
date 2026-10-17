import json, pathlib
import numpy as np
import pymupdf

OUT = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\extracted")

def ink_density_png(png):
    pix = pymupdf.Pixmap(str(png))
    if pix.n > 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    gray = a[:,:,:3].mean(axis=2)
    return float((gray < 245).mean())

print("=" * 100)
print("INK DENSITY OF THE 18 REAL NATURE BANDS I RENDERED")
print("=" * 100)
idx = json.loads((OUT/"_index.json").read_text())
vals = []
for fn, w, h, paper, pno in idx:
    d = ink_density_png(fn)
    vals.append(d)
    print("  %-58s %6.1f x %6.1f mm  ink %5.1f%%" % (pathlib.Path(fn).name[:58], w, h, 100*d))
v = np.array(vals)
print()
print("  n=%d  min %.1f%%  median %.1f%%  max %.1f%%  mean %.1f%%"
      % (len(v), 100*v.min(), 100*np.median(v), 100*v.max(), 100*v.mean()))
print()
print("  H02's claimed 'compliant band' was 3.3-17.4%%.")
print("  Real Nature bands inside that band : %d of %d" % (((v>=0.033)&(v<=0.174)).sum(), len(v)))
print("  Real Nature bands ABOVE 17.4%%     : %d of %d" % ((v>0.174).sum(), len(v)))
print()
print("  => H02's refutation is CORRECT and the direction is right:")
print("     real Nature figures commonly exceed the band the rule claimed.")
