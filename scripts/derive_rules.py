"""Clean the corpus measurements and derive rules grounded in published practice.

WHY A SEPARATE CLEANING STEP
    The raw measurement of 420 figure bands contained values that are physically impossible:
    29 bands wider than the 210 mm page, and 22 with a "minimum font" below 2 pt (those are
    mathematical superscripts and artefact glyphs, not body text). Reporting percentiles over
    that mixture would have produced confident numbers about nothing.

    Every excluded band is counted WITH ITS REASON, so the cleaning is auditable and a reader
    can see how much data survived and why the rest did not.

WHAT IS DERIVED
    Only bands that pass the physical filters. For those, the distribution of:
      * width in mm -- compared against Nature's stated 89 / 183 mm columns
      * minimum font size -- compared against the stated 5 pt floor
    The comparison is the point: the specification states rules, and this checks whether
    published practice matches them.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "corpus" / "measured.json"
OUT = ROOT / "corpus" / "derived.json"
KB = ROOT / "knowledge" / "layout_rules.json"

#: A4 is 210 mm wide; a figure cannot be wider than the page it is printed on.
MAX_PAGE_MM = 210.0
#: Bands narrower than this are fragments, not figures.
MIN_WIDTH_MM = 60.0
#: Below 2 pt is a superscript or artefact, never body text.
MIN_MEANINGFUL_PT = 2.0


def clean(papers: list[dict]) -> tuple[list[dict], dict]:
    kept, excl = [], {"too_wide": 0, "too_narrow": 0, "tiny_font": 0}
    for p in papers:
        for f in p["figures"]:
            w = f["width_mm"]
            if w > MAX_PAGE_MM:
                excl["too_wide"] += 1
                continue
            if w < MIN_WIDTH_MM:
                excl["too_narrow"] += 1
                continue
            if f.get("min_font_pt") is not None and f["min_font_pt"] < MIN_MEANINGFUL_PT:
                excl["tiny_font"] += 1
                continue
            kept.append({**f, "paper": p["file"]})
    return kept, excl


def pct(vals, q):
    return round(float(np.percentile(vals, q)), 1) if vals else None


def main() -> int:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    kept, excl = clean(raw["papers"])

    widths = [f["width_mm"] for f in kept]
    mins = [f["min_font_pt"] for f in kept if f.get("min_font_pt")]

    # How close is published practice to the two stated column widths?
    def near(target, tol=3.0):
        return sum(1 for w in widths if abs(w - target) <= tol)

    derived = {
        "source": "local Nature PDF corpus (D:\\2026-AI4S), filenames containing NATURE",
        "dirty_data_excluded_at_harvest": raw["summary"].get("dirty_data_excluded"),
        "bands_raw": sum(len(p["figures"]) for p in raw["papers"]),
        "bands_kept": len(kept),
        "bands_excluded": excl,
        "exclusion_reasons": {
            "too_wide": f"wider than the {MAX_PAGE_MM} mm page -- band merging fused the page",
            "too_narrow": f"narrower than {MIN_WIDTH_MM} mm -- a fragment, not a figure",
            "tiny_font": f"minimum font below {MIN_MEANINGFUL_PT} pt -- a superscript or "
                         f"artefact glyph, not body text",
        },
        "width_mm": {
            "n": len(widths),
            "min": round(min(widths), 1) if widths else None,
            "p10": pct(widths, 10), "p25": pct(widths, 25),
            "median": pct(widths, 50), "p75": pct(widths, 75),
            "p90": pct(widths, 90),
            "max": round(max(widths), 1) if widths else None,
            "within_3mm_of_89": near(89.0),
            "within_3mm_of_183": near(183.0),
            "within_3mm_of_either": near(89.0) + near(183.0),
            "share_near_a_column": round((near(89.0) + near(183.0)) / len(widths), 4)
            if widths else None,
        },
        "min_font_pt": {
            "n": len(mins),
            "min": round(min(mins), 2) if mins else None,
            "p10": pct(mins, 10), "median": pct(mins, 50), "p90": pct(mins, 90),
            "max": round(max(mins), 2) if mins else None,
            "share_below_5pt": round(float(np.mean([m < 5.0 for m in mins])), 4) if mins else None,
        },
    }
    OUT.write_text(json.dumps({"derived": derived, "bands": kept}, indent=2), encoding="utf-8")

    print("  === CLEANED, FROM REAL NATURE FIGURES ===")
    print(f"  bands raw      : {derived['bands_raw']}")
    print(f"  bands kept     : {derived['bands_kept']}")
    print(f"  excluded       : {excl}")
    print()
    w = derived["width_mm"]
    print(f"  width mm   n={w['n']}  p10 {w['p10']}  p25 {w['p25']}  median {w['median']}  "
          f"p75 {w['p75']}  p90 {w['p90']}")
    print(f"    near 89 mm  : {w['within_3mm_of_89']}")
    print(f"    near 183 mm : {w['within_3mm_of_183']}")
    print(f"    share near a stated column: {w['share_near_a_column']}")
    print()
    f = derived["min_font_pt"]
    print(f"  min font   n={f['n']}  min {f['min']}  p10 {f['p10']}  median {f['median']}  "
          f"p90 {f['p90']}")
    print(f"    share below 5 pt: {f['share_below_5pt']}")
    print()
    print(f"  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
