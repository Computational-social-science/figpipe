import json, pathlib
from collections import Counter
ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
recs = [json.loads(l) for l in (ROOT/"corpus"/"vlm_labels.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
L=[]
def p(s=""): L.append(str(s))
p("=" * 96)
p("THE column_width CONTRADICTION -- verify it is real, not my bug")
p("=" * 96)
p()
p("The PROMPT contains, verbatim:")
p('  "- crop_width_mm: <w>"')
p('  "- nature_single_column_mm: 89.0 / nature_double_column_mm: 183.0"')
p('  "For column_width, use the measured crop_width_mm: a figure near 89.0 mm wide is')
p('   single; near 183.0 mm is double; clearly wider than the text block is full."')
p()
p("So column_width is a DETERMINISTIC function of a number handed to the model.")
p("It is not a visual judgement. Any disagreement is a labelling error, not ambiguity.")
p()
p("%-58s %8s %10s %s" % ("image","label","geometry","crop_mm"))
n = 0
for r in recs:
    sg = r.get("source_geometry", {})
    cw = r["labels"].get("column_width"); cg = sg.get("column_from_geometry")
    if cw != cg:
        n += 1
        if n <= 18:
            p("%-58s %8s %10s %.1f" % (r["image"][:58], cw, cg, sg.get("crop_width_mm", -1)))
p()
p("TOTAL mismatches: %d / %d = %.1f%%" % (n, len(recs), 100*n/len(recs)))
p()
p("breakdown of the wrong ones (label -> geometry):")
c = Counter()
for r in recs:
    sg = r.get("source_geometry", {})
    cw = r["labels"].get("column_width"); cg = sg.get("column_from_geometry")
    if cw != cg: c[(cw,cg)] += 1
for k,v in c.most_common(): p("   %s -> %s : %d" % (k[0],k[1],v))
p()
p("=" * 96)
p("IS THIS FIELD USED DOWNSTREAM AS A VERIFIED FACT?")
p("=" * 96)
kb = json.loads((ROOT/"knowledge"/"layout_rules.json").read_text(encoding="utf-8"))
for r in kb["rules"]:
    if "column" in r.get("name","").lower() or "width" in r.get("name","").lower():
        p("  rule %s (%s): conf=%s enforced=%s" % (r["id"], r["name"], r["confidence"], r.get("enforced")))
p()
p("  column_width is one of the 21 VLM label fields. If it is used to derive any")
p("  'Nature figures are X%% single-column' claim, that claim inherits a 45%% error rate.")
p("  I found NO current rule citing VLM column_width -- so the damage is CONTAINED")
p("  for now, but the field is silently wrong and would corrupt any future rule.")
p()
p("=" * 96)
p("SECOND ISSUE: panel_count / panel_layout / panel_labels_present are 0%% null")
p("=" * 96)
p("  panel_count null rate: %d%%" % (100*sum(1 for r in recs if r["labels"].get("panel_count") is None)/len(recs)))
p("  Yet panel count IS hard to determine reliably from a crop.")
p("  Values: %s" % dict(Counter(r["labels"].get("panel_count") for r in recs).most_common()))
p()
p("  Cross-check: does panel_count agree with panel_labels_present?")
bad = 0
for r in recs:
    pc = r["labels"].get("panel_count"); lp = r["labels"].get("panel_labels_present")
    if pc is not None and pc >= 2 and lp is False: bad += 1
p("  records with panel_count>=2 but panel_labels_present=False: %d" % bad)
p("  (possible, but worth flagging: unlabelled multi-panel figures)")
(ROOT/"corpus"/"_vlm_contradiction.txt").write_text("\n".join(L), encoding="utf-8")
print("wrote _vlm_contradiction.txt")
