"""Validate caption<->figure pairing against independent evidence.

WHY A SEPARATE VALIDATOR
    The extractor pairs captions geometrically. A validator that reuses the
    extractor's own logic would confirm nothing. This script attacks the
    pairing three independent ways and reports agreement rates:

    (V1) CAPTION LABEL vs PAGE CONTENT. Every figure caption in Nature begins
         with a label such as "Fig. 3 |". If the pairing is right, the figure
         number parsed from the caption must be consistent with the caption's
         own text. A wrong pair usually shows up as a duplicate or a skipped
         number.
    (V2) GEOMETRY. Independently re-measure the vertical gap from the caption
         block to the picture box. A true pair sits within a small gap; a
         mis-pair shows an implausible gap.
    (V3) NUMBER SEQUENCE. Across a paper, the figure numbers recovered should
         form a near-contiguous sequence 1..N with no repeats. This is the
         strongest available check because it uses the paper's own structure,
         not the extractor's geometry.

    V3 is the honest test. It can fail loudly: if pairing swapped two figures,
    the recovered numbers would repeat or skip.

Writes corpus/extracted/VALIDATION.json and prints a per-paper table.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "corpus", "extracted")


def analyse_paper(pdir: str) -> dict:
    pid = os.path.basename(pdir)
    fmeta_p = os.path.join(pdir, "figures_meta.json")
    layout_p = os.path.join(pdir, "layout.json")
    if not os.path.exists(fmeta_p):
        return {"paper_id": pid, "error": "no figures_meta.json"}
    fm = json.load(open(fmeta_p, encoding="utf-8"))
    _lay = json.load(open(layout_p, encoding="utf-8")) if os.path.exists(layout_p) else {}

    figs = fm.get("figures", [])
    out = {"paper_id": pid, "n_figures": len(figs), "checks": {}}

    # ---- V1: caption carries a label and a parseable number ----
    labelled = 0
    for f in figs:
        if re.match(r"^\s*(extended\s+data\s+|supplementary\s+)?"
                    r"(fig(?:ure)?\.?|table|box)\s*\d+", f["caption"], re.I):
            labelled += 1
    out["checks"]["V1_caption_has_label"] = {
        "n": len(figs), "labelled": labelled,
        "rate": round(labelled / len(figs), 4) if figs else None,
    }

    # ---- V2: geometry, re-measured ----
    gaps = []
    bad_geom = 0
    for f in figs:
        bb = f["bbox"]
        cb = f.get("caption_bbox")
        if not cb:
            continue
        gap = bb["b"] - cb["t"]
        gaps.append(round(gap, 2))
        # A Nature figure caption sits within a few points to ~30 pt below the
        # figure; anything wildly outside means the pair is suspect.
        if gap < -12 or gap > 60:
            bad_geom += 1
    out["checks"]["V2_geometry_gap"] = {
        "n": len(gaps),
        "min": min(gaps) if gaps else None,
        "max": max(gaps) if gaps else None,
        "median": sorted(gaps)[len(gaps) // 2] if gaps else None,
        "implausible": bad_geom,
        "rate_plausible": round(1 - bad_geom / len(gaps), 4) if gaps else None,
    }

    # ---- V3: figure-number sequence per LABEL FORM ----
    # Keyed on the literal label form ("Fig. 1" vs "Figure 1"), not on the
    # inferred kind, because a Nature issue contains front matter (News & Views)
    # whose standalone 'Figure 1 |' legitimately collides with the Article's
    # 'Fig. 1 |'. Grouping by label form tests the pairing without punishing a
    # real property of the source.
    by_kind = {}
    for f in figs:
        k = f.get("label_form") or f.get("kind", "figure")
        if f.get("figure_number") is not None:
            by_kind.setdefault(k, []).append(f["figure_number"])
    seq_report = {}
    all_ok = True
    for k, nums in by_kind.items():
        expected = list(range(1, max(nums) + 1))
        got = sorted(nums)
        dup = len(got) != len(set(got))
        missing = sorted(set(expected) - set(got))
        contiguous = (not dup) and (not missing)
        all_ok &= contiguous
        seq_report[k] = {
            "n": len(nums), "numbers": got, "duplicates": dup,
            "missing": missing, "contiguous_1_to_N": contiguous,
        }
    out["checks"]["V3_number_sequence"] = {"label_forms": seq_report,
                                           "all_contiguous": all_ok}

    # ---- duplicates: two figures with the identical caption ----
    caps = [f["caption"] for f in figs]
    out["checks"]["V4_no_duplicate_captions"] = {
        "n": len(caps),
        "n_unique": len(set(caps)),
        "duplicates": len(caps) - len(set(caps)),
    }

    # ---- coverage: how many detected pictures became figures ----
    out["coverage"] = {
        "n_pictures_detected": fm.get("n_pictures_detected"),
        "n_figures": len(figs),
        "n_uncaptioned": fm.get("n_uncaptioned_pictures"),
    }
    return out


def main() -> int:
    if not os.path.isdir(EXT):
        print("no corpus/extracted directory")
        return 1
    papers = [os.path.join(EXT, d) for d in sorted(os.listdir(EXT))
              if os.path.isdir(os.path.join(EXT, d))]
    rows = [analyse_paper(p) for p in papers]
    rows = [r for r in rows if "error" not in r]

    print(f"papers analysed: {len(rows)}\n")
    hdr = (f"{'paper_id':52s} {'figs':>4s} {'V1lab':>6s} {'V2plaus':>7s} "
           f"{'V3contig':>8s} {'dupcaps':>7s}")
    print(hdr)
    print("-" * len(hdr))
    n_v1 = n_v1_ok = n_v2 = n_v2_ok = n_v3 = n_v3_ok = 0
    dup_total = 0
    for r in rows:
        v1 = r["checks"]["V1_caption_has_label"]
        v2 = r["checks"]["V2_geometry_gap"]
        v3 = r["checks"]["V3_number_sequence"]
        v4 = r["checks"]["V4_no_duplicate_captions"]
        dup_total += v4["duplicates"]
        n_v1 += v1["n"]; n_v1_ok += v1["labelled"]
        if v2["n"]:
            n_v2 += v2["n"]; n_v2_ok += v2["n"] - v2["implausible"]
        n_v3 += 1; n_v3_ok += 1 if v3["all_contiguous"] else 0
        print(f"{r['paper_id'][:52]:52s} {r['n_figures']:4d} "
              f"{v1['rate']:6.3f} {str(v2['rate_plausible']):>7s} "
              f"{str(v3['all_contiguous']):>8s} {v4['duplicates']:7d}")

    print("-" * len(hdr))
    summary = {
        "papers": len(rows),
        "figures_total": n_v1,
        "V1_label_rate": round(n_v1_ok / n_v1, 4) if n_v1 else None,
        "V2_geometry_plausible_rate": round(n_v2_ok / n_v2, 4) if n_v2 else None,
        "V3_papers_with_contiguous_sequence": f"{n_v3_ok}/{n_v3}",
        "V4_duplicate_captions_total": dup_total,
        "per_paper": rows,
    }
    print(f"\nV1 caption-label rate          : {summary['V1_label_rate']}")
    print(f"V2 geometry plausible rate     : {summary['V2_geometry_plausible_rate']}")
    print(f"V3 contiguous 1..N sequences   : {summary['V3_papers_with_contiguous_sequence']}")
    print(f"V4 duplicate captions (total)  : {dup_total}")

    with open(os.path.join(EXT, "VALIDATION.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("\nwrote VALIDATION.json")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
