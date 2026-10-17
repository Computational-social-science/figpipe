"""CRITICAL AUDIT -- my OWN figure extractor, independent of the project's code.

Reproduces the project's band detection so I can (a) check whether measured.json is
reproducible and (b) render the bands to PNG so I can LOOK at them.
"""
import json, pathlib, re
import numpy as np
import pymupdf

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
OUT = ROOT / "corpus" / "extracted"
OUT.mkdir(parents=True, exist_ok=True)
MM_PER_PT = 25.4 / 72.0
PDF_ROOT = pathlib.Path(r"D:\2026-AI4S")

DIRTY = [(r"national\s+science\s+review","NSR"),(r"natl\s+sci\s+rev","NSR"),
         (r"nature\s+communications","NatComm"),(r"npj\s","npj"),(r"scientific\s+reports","SciRep")]

def is_nature(name):
    low = name.lower()
    for pat, why in DIRTY:
        if re.search(pat, low): return False, why
    if "nature" not in low: return False, "no-nature"
    if not low.endswith(".pdf"): return False, "not-pdf"
    return True, "ok"

def find_bands(page):
    rects = []
    for d in page.get_drawings():
        r = d.get("rect")
        if r is not None and r.width > 4 and r.height > 4:
            rects.append(pymupdf.Rect(r))
    for im in page.get_images(full=True):
        try:
            for r in page.get_image_rects(im[0]):
                if r.width > 4 and r.height > 4:
                    rects.append(pymupdf.Rect(r))
        except Exception:
            continue
    if not rects: return []
    rects.sort(key=lambda r: (r.y0, r.x0))
    bands = []
    for r in rects:
        merged = False
        for b in bands:
            if r.y0 <= b["y1"] + 6 and r.y1 >= b["y0"] - 6:
                b["x0"]=min(b["x0"],r.x0); b["x1"]=max(b["x1"],r.x1)
                b["y0"]=min(b["y0"],r.y0); b["y1"]=max(b["y1"],r.y1)
                merged=True; break
        if not merged:
            bands.append({"x0":r.x0,"x1":r.x1,"y0":r.y0,"y1":r.y1})
    out=[]
    for b in bands:
        w=(b["x1"]-b["x0"])*MM_PER_PT; h=(b["y1"]-b["y0"])*MM_PER_PT
        if w < 60 or h < 25: continue
        out.append({"bbox":[round(v,1) for v in (b["x0"],b["y0"],b["x1"],b["y1"])],
                    "width_mm":round(w,1),"height_mm":round(h,1)})
    return out

# pick a few real papers and render their bands
pdfs = []
for p in sorted(PDF_ROOT.rglob("*.pdf")):
    ok, why = is_nature(p.name)
    if ok: pdfs.append(p)
print("accepted Nature PDFs: %d" % len(pdfs))

# dedupe by name
seen=set(); uniq=[]
for p in pdfs:
    if p.name in seen: continue
    seen.add(p.name); uniq.append(p)
print("unique: %d" % len(uniq))

rendered = []
for p in uniq[:6]:
    doc = pymupdf.open(str(p))
    for pno in range(min(len(doc), 24)):
        page = doc[pno]
        bands = find_bands(page)
        for bi, b in enumerate(bands):
            x0,y0,x1,y1 = b["bbox"]
            # pad slightly, clamp to page
            clip = pymupdf.Rect(max(0,x0-3), max(0,y0-3),
                                min(page.rect.width, x1+3), min(page.rect.height, y1+3))
            if clip.width < 20 or clip.height < 20: continue
            try:
                pix = page.get_pixmap(clip=clip, dpi=110)
            except Exception:
                continue
            tag = re.sub(r'[^A-Za-z0-9]+','_', p.stem)[:40]
            fn = OUT / f"{tag}__p{pno+1:02d}_b{bi}.png"
            pix.save(str(fn))
            rendered.append((str(fn), b["width_mm"], b["height_mm"], p.name, pno+1))
    doc.close()
    if len(rendered) >= 12: break

print("rendered %d figure bands to %s" % (len(rendered), OUT))
for r in rendered:
    print("  %-70s %6.1f x %6.1f mm  %s p%d" % (pathlib.Path(r[0]).name, r[1], r[2], r[3][:40], r[4]))
json.dump(rendered, open(OUT/"_index.json","w"), indent=1)
