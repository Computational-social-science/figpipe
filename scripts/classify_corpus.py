"""Classify the 42 NATURE-named PDFs into true Nature-family articles vs
excluded sister journals, using PDF metadata as evidence (not filename alone).

WHY THIS EXISTS
The task says: 42 PDFs have NATURE in the filename, but National Science Review,
Nature Communications, npj * and Scientific Reports must be EXCLUDED -- they are
not Nature proper. Filename text is weak evidence (a paper can cite "Nature
Communications" in its title). So we read each PDF's own metadata + first-page
text and record the evidence for every decision.

Output: corpus/pdf_inventory.json  (one record per unique file, with evidence)
"""
import hashlib
import json
import os
import re
import sys

import pymupdf

D = r"D:\2026-AI4S"
OUT = r"E:\2026-AI4S\figpipe\corpus\pdf_inventory.json"

EXCLUDE_PATTERNS = [
    (r"nature\s+communications", "Nature Communications"),
    (r"\bnpj\b", "npj *"),
    (r"scientific\s+reports", "Scientific Reports"),
    (r"national\s+science\s+review", "National Science Review"),
    (r"\bNSR\b", "National Science Review"),
]


def first_page_text(doc, limit=4000):
    if doc.page_count == 0:
        return ""
    t = doc[0].get_text()
    return t[:limit]


def classify(path):
    rec = {"path": path, "name": os.path.basename(path),
           "size_bytes": os.path.getsize(path)}
    try:
        rec["md5"] = hashlib.md5(open(path, "rb").read()).hexdigest()
    except OSError as e:
        rec["md5"] = None
        rec["error"] = str(e)
    try:
        doc = pymupdf.open(path)
        rec["n_pages"] = doc.page_count
        rec["metadata"] = {k: v for k, v in (doc.metadata or {}).items() if v}
        rec["page0_size"] = [round(doc[0].rect.width, 2), round(doc[0].rect.height, 2)]
        txt = first_page_text(doc)
        doc.close()
    except Exception as e:
        rec["n_pages"] = None
        rec["metadata"] = {}
        rec["page0_size"] = None
        rec["error"] = f"{type(e).__name__}: {e}"
        txt = ""
    rec["page0_text_head"] = txt[:600]

    hay = (rec["name"] + "\n" + json.dumps(rec["metadata"]) + "\n" + txt).lower()
    hits = []
    for pat, label in EXCLUDE_PATTERNS:
        if re.search(pat, hay):
            hits.append(label)
    # a paper that merely mentions these in its body is not excluded; the
    # decisive signal is the journal title in metadata or the page-0 masthead
    meta_hay = (json.dumps(rec["metadata"]) + "\n" + txt[:1500]).lower()
    decisive = [label for pat, label in EXCLUDE_PATTERNS if re.search(pat, meta_hay)]
    rec["exclude_hits_anywhere"] = sorted(set(hits))
    rec["exclude_hits_decisive"] = sorted(set(decisive))
    rec["excluded"] = bool(decisive)
    rec["excluded_reason"] = (
        f"journal identity matched in metadata/page-0: {', '.join(sorted(set(decisive)))}"
        if decisive else None)
    return rec


def main():
    files = []
    for root, _dirs, names in os.walk(D):
        for n in names:
            if n.lower().endswith(".pdf") and "nature" in n.lower():
                files.append(os.path.join(root, n))
    files.sort()
    print(f"found {len(files)} PDFs with NATURE in the name")

    recs = [classify(p) for p in files]

    # ---- dedup by content hash: identical bytes = one paper ----
    by_hash = {}
    for r in recs:
        by_hash.setdefault(r["md5"], []).append(r)
    unique = []
    for _h, group in by_hash.items():
        group.sort(key=lambda r: len(r["name"]))
        keep = group[0]
        keep = dict(keep)
        keep["duplicate_paths"] = [g["path"] for g in group[1:]]
        keep["n_copies"] = len(group)
        unique.append(keep)
    unique.sort(key=lambda r: r["name"])

    kept = [r for r in unique if not r["excluded"]]
    excl = [r for r in unique if r["excluded"]]
    print(f"unique by md5: {len(unique)}   kept: {len(kept)}   excluded: {len(excl)}")
    print("\n=== EXCLUDED ===")
    for r in excl:
        print(f"  {r['name'][:90]:90s} <- {r['excluded_reason']}")
    print("\n=== KEPT ===")
    for r in kept:
        print(f"  {r['n_pages']:3d}pp {r['size_bytes']/1e6:6.2f}MB {r['name'][:88]}")

    payload = {
        "source_root": D,
        "n_files_found": len(files),
        "n_unique_by_md5": len(unique),
        "n_kept": len(kept),
        "n_excluded": len(excl),
        "exclude_rules": [p for p, _ in EXCLUDE_PATTERNS],
        "kept": kept,
        "excluded": excl,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
