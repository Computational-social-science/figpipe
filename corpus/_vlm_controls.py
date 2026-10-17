import json, pathlib
ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
d = json.loads((ROOT/"corpus"/"vlm_report.json").read_text(encoding="utf-8"))
L=[]
def p(s=""): L.append(str(s))
p("=" * 96)
p("CONTROLS: can the model tell when there is nothing to see?")
p("=" * 96)
c = d["controls"]
p("model: %s" % c["model"])
for ctl in c["controls"]:
    p()
    p("  %s  kind=%s" % (ctl["image"], ctl["kind"]))
    p("    why: %s" % ctl["why"])
    p("    n_null=%s  n_asserted=%s" % (ctl.get("n_null"), ctl.get("n_asserted")))
    p("    n_trivially_true=%s" % ctl.get("n_trivially_true"))
    p("    n_fabricated=%s" % ctl.get("n_fabricated"))
    fab = ctl.get("fabricated_fields")
    if fab: p("    FABRICATED: %s" % json.dumps(fab, ensure_ascii=False)[:400])
p()
p("=" * 96)
p("VERDICT FROM THE PROJECT'S OWN CONTROLS")
p("=" * 96)
tot_fab = sum(ctl.get("n_fabricated",0) for ctl in c["controls"])
tot_asserted = sum(ctl.get("n_asserted",0) for ctl in c["controls"])
p("  total fabricated assertions on controls: %d (of %d asserted)" % (tot_fab, tot_asserted))
p()
# the report may have a summary
for k in c:
    if k not in ("controls","model"):
        p("  %s: %s" % (k, c[k]))
(ROOT/"corpus"/"_vlm_controls.txt").write_text("\n".join(L), encoding="utf-8")
print("wrote _vlm_controls.txt")
