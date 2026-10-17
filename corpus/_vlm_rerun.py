"""CRITICAL AUDIT R2 -- independently rerun the VLM on 3 images with the EXACT recorded
prompt, and compare field-by-field to the stored labels."""
import base64, json, pathlib, hashlib, urllib.request
import random

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
recs = [json.loads(l) for l in (ROOT/"corpus"/"vlm_labels.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("stored records: %d" % len(recs))

# pick 3 that are not the Lead's example
random.seed(2026)
idx = [0, len(recs)//2, len(recs)-1]
picks = [recs[i] for i in idx]

def ollama(prompt, img_path):
    b64 = base64.b64encode(img_path.read_bytes()).decode()
    body = json.dumps({"model": "gemma3:12b", "prompt": prompt, "images": [b64],
                       "stream": False, "format": "json",
                       "options": {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 900}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]

results = []
for rec in picks:
    img = ROOT/"corpus"/"pages_for_vlm"/rec["image"]
    if not img.exists():
        # try subdirs
        cand = list((ROOT/"corpus").rglob(rec["image"]))
        img = cand[0] if cand else None
    print()
    print("=" * 90)
    print("image: %s" % rec["image"])
    print("  exists: %s  sha256 match: %s" % (bool(img),
          hashlib.sha256(img.read_bytes()).hexdigest()==rec["image_sha256"] if img else "n/a"))
    if not img: continue
    print("  rerunning gemma3:12b with the recorded prompt...")
    try:
        raw = ollama(rec["prompt"], img)
        new = json.loads(raw)
    except Exception as e:
        print("  RERUN FAILED: %s" % e); continue
    old = rec["labels"]
    same = [k for k in old if old.get(k) == new.get(k)]
    diff = [k for k in old if old.get(k) != new.get(k)]
    print("  fields: %d  identical: %d  differing: %d" % (len(old), len(same), len(diff)))
    for k in diff:
        print("     %-26s stored=%-22r rerun=%r" % (k, old.get(k), new.get(k)))
    results.append((rec["image"], len(same), len(diff), diff))
    print("  stored nulls: %d" % rec.get("n_null", -1))

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)
for img, s, d, diff in results:
    print("  %-62s %d/%d identical" % (img[:62], s, s+d))
