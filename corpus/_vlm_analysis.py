import json, pathlib
from collections import Counter
ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
recs = [json.loads(l) for l in (ROOT/"corpus"/"vlm_labels.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
L=[]
def p(s=""): L.append(str(s))
p("records: %d" % len(recs))
p("models: %s" % dict(Counter(r["model"] for r in recs)))
p("parse_ok: %s" % dict(Counter(r["parse_ok"] for r in recs)))
p()
p("=" * 90)
p("NULL RATE PER FIELD (the anti-fabrication design)")
p("=" * 90)
fields = list(recs[0]["labels"].keys())
p("%-28s %8s %8s %8s" % ("field","null","non-null","null%"))
for f in fields:
    n = sum(1 for r in recs if r["labels"].get(f) is None)
    p("%-28s %8d %8d %7.1f%%" % (f, n, len(recs)-n, 100*n/len(recs)))
p()
p("=" * 90)
p("FABRICATION CHECK: fields the model CANNOT see from a cropped figure")
p("=" * 90)
# caption_* fields require the caption TEXT; is it in the prompt? yes it is.
# But 'vector_or_bitmap' from a raster render is unanswerable -> should be high null
for f in ["vector_or_bitmap","colorblind_safe","saturated_color_count","palette_description",
          "caption_has_stats","caption_overview_first","caption_panel_by_panel","caption_stats_last"]:
    n = sum(1 for r in recs if r["labels"].get(f) is None)
    p("  %-26s null in %2d/%2d = %5.1f%%" % (f, n, len(recs), 100*n/len(recs)))
p()
p("=" * 90)
p("CONTRADICTION CHECK: does any record claim a value the image contradicts?")
p("=" * 90)
# column_width is derived from measured geometry, so it should NEVER be null and should
# agree with source_geometry.column_from_geometry
bad = 0
for r in recs:
    sg = r.get("source_geometry", {})
    cw = r["labels"].get("column_width")
    cg = sg.get("column_from_geometry")
    if cw != cg:
        bad += 1
        if bad <= 6:
            p("  MISMATCH %s: label=%s geometry=%s (width=%s)"
              % (r["image"][:50], cw, cg, sg.get("crop_width_mm")))
p("  column_width vs measured geometry mismatches: %d/%d" % (bad, len(recs)))
p()
p("  panel_count distribution: %s" % dict(Counter(r["labels"].get("panel_count") for r in recs).most_common(8)))
p("  figure_type distribution: %s" % dict(Counter(r["labels"].get("figure_type") for r in recs).most_common()))
(ROOT/"corpus"/"_vlm_analysis.txt").write_text("\n".join(L), encoding="utf-8")
print("wrote _vlm_analysis.txt")
