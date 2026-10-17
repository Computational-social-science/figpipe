import json, pathlib, io, sys
p = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\figures_caption_anchored.json")
d = json.loads(p.read_text(encoding="utf-8"))
print("type:", type(d).__name__)
if isinstance(d, dict):
    print("keys:", list(d.keys()))
    for k, v in d.items():
        if isinstance(v, list): print("  %s: list len %d" % (k, len(v)))
        elif isinstance(v, dict): print("  %s: dict keys %s" % (k, list(v.keys())[:10]))
        else: print("  %s = %s" % (k, str(v)[:120]))
