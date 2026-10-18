"""Build a labelled baseline for J01-J04, so a model can be compared against something.

WHY A BASELINE COMES BEFORE A MODEL
    figpipe has four judgemental decisions (inventory_decisions.py):
        J01 which page region is a figure
        J02 which caption belongs to which figure
        J03 is the opening sentence an overview or a panel walk
        J04 what TYPE of figure is this
    All four are currently decided by regexes whose accuracy is UNMEASURED.

    Replacing a check of unknown accuracy with a model gives TWO unknowns, not one. So the
    order must be: label a sample by hand, measure the regex, then decide whether a model earns
    its place.

WHAT THIS PRODUCES
    A stratified sample with the current code's answer recorded alongside a blank for the human
    label. The sample is DETERMINISTIC (seeded) so it can be re-drawn and compared.

    Stratification matters: figures come from main text, Extended Data and supplements, whose
    conventions differ. A sample that was 90 % main text would measure only that.
"""
from __future__ import annotations

import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "baseline_sample.json"
SEED = 20261018
PER_KIND = 20          # 20 per document kind = enough to estimate a proportion to ~+-0.2


def load_figures() -> list[dict]:
    rows = []
    for d in sorted((ROOT / "corpus" / "extracted").iterdir()):
        if not d.is_dir():
            continue
        meta = d / "figures_meta.json"
        if not meta.is_file():
            continue
        fm = json.loads(meta.read_text(encoding="utf-8"))
        for f in fm.get("figures", []):
            cap = (f.get("caption_text") or "").strip()
            if not cap:
                continue
            bb = f.get("bbox") or {}
            rows.append({
                "paper": d.name,
                "figure_id": f.get("figure_id"),
                "kind": str(f.get("kind") or "figure"),
                "page": f.get("page"),
                "caption_text": cap,
                "width_mm": round(bb.get("w", 0) * 25.4 / 72, 1) if bb.get("w") else None,
                "height_mm": round(bb.get("h", 0) * 25.4 / 72, 1) if bb.get("h") else None,
            })
    return rows


def main() -> int:
    import sys
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))
    import caption_features as cf          # lives in scripts/
    from figpipe import figuretypes as ft  # lives in the package

    rows = load_figures()
    by_kind: dict[str, list[dict]] = {}
    for r in rows:
        by_kind.setdefault(r["kind"], []).append(r)

    rng = random.Random(SEED)
    sample = []
    for kind, items in sorted(by_kind.items()):
        rng.shuffle(items)
        for r in items[:PER_KIND]:
            feat = cf.measure(r["caption_text"])
            typ = ft.classify(r["caption_text"], r["width_mm"], r["height_mm"], r["kind"])
            sample.append({
                **r,
                # what the CODE currently says -- the thing being measured
                "code": {
                    "J03_caption_overview_first": feat["caption_overview_first"],
                    "J03_caption_panel_by_panel": feat["caption_panel_by_panel"],
                    "J03_n_panel_markers": feat["n_panel_markers"],
                    "J04_figure_type": typ["figure_type"],
                    "J04_confidence": typ["confidence"],
                    "J04_evidence": typ["evidence"],
                },
                # the human label, to be filled in
                "label": {
                    "J03_overview_first": None,
                    "J03_panel_by_panel": None,
                    "J04_figure_type": None,
                    "notes": "",
                },
            })

    OUT.write_text(json.dumps({
        "about": ("A stratified, seeded sample for measuring the accuracy of the code's four "
                  "judgemental decisions. `code` is what figpipe currently answers; `label` "
                  "is to be filled by a human. J01/J02 are not in this sample because they "
                  "require the rendered page, not the caption text."),
        "seed": SEED,
        "per_kind": PER_KIND,
        "n": len(sample),
        "by_kind": {k: min(PER_KIND, len(v)) for k, v in sorted(by_kind.items())},
        "how_to_label": [
            "For each row, read caption_text and decide:",
            "  J03_overview_first: does the FIRST sentence summarise the whole figure?",
            "  J03_panel_by_panel: does the caption then address two or more panels?",
            "  J04_figure_type: which of the types in figuretypes.TYPE_RULES fits best, or 'unclassified'?",
            "Then run scripts/score_baseline.py to compare against the code.",
        ],
        "items": sample,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  sample size: {len(sample)}")
    print("  by kind:")
    for k, v in sorted(by_kind.items()):
        print(f"    {k:<26} {min(PER_KIND, len(v)):3d} of {len(v):4d}")
    print()
    print("  code's current answers on the sample:")
    from collections import Counter
    print("    J03 overview_first :", Counter(i["code"]["J03_caption_overview_first"] for i in sample))
    print("    J03 panel_by_panel :", Counter(i["code"]["J03_caption_panel_by_panel"] for i in sample))
    print("    J04 type           :", Counter(i["code"]["J04_figure_type"] for i in sample).most_common(6))
    print(f"\n  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
