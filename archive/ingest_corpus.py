"""Fold what the real-Nature corpus taught us back into the knowledge base.

WHY THIS IS NOT JUST "ADDING RULES"
    The corpus REFUTED a rule that figpipe had marked as measured: H02 claimed a compliant
    ink-density band of 3.3-17.4 %, derived from six of this project's own line plots. The
    first real Nature figure inspected had an ink density of 35.8 %.

    So this update does three things, and the refutation matters more than the additions:

      1. H02 is marked REFUTED, with the contradicting measurement attached. A knowledge base
         that only ever gains rules is not learning, it is accumulating.
      2. Two new observations enter as HYPOTHESES, not verified rules, because the measurement
         that produced them has not itself been validated (see LEARNINGS.md P0).
      3. A distinction is recorded that was missing before: SPECIFICATION requirements (what a
         submission must satisfy) versus OBSERVED practice (what published figures do). The
         two can differ, and conflating them was the core error.
"""
from __future__ import annotations

import datetime
import json
import pathlib

KB = pathlib.Path(r"E:\2026-AI4S\figpipe\knowledge\layout_rules.json")
DERIVED = pathlib.Path(r"E:\2026-AI4S\figpipe\corpus\derived.json")


def main() -> int:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    d = json.loads(DERIVED.read_text(encoding="utf-8"))["derived"]

    # --- 1. refute H02 ---------------------------------------------------------------
    for r in kb["rules"]:
        if r["id"] == "H02":
            r["confidence"] = "refuted"
            r["enforced"] = False
            r["refuted_on"] = datetime.date.today().isoformat()
            r["refuted_by"] = (
                "The first real Nature figure inspected (nwag582fig1) has an ink density of "
                "35.8 %, far outside the 3.3-17.4 % band this rule claimed. The band was "
                "measured on six line-and-scatter plots from this project and generalised to "
                "'figures', which it never supported.")
            r["scope_where_it_did_hold"] = (
                "This project's own six figures, all of which are line/scatter plots. The "
                "band describes that genre, not figures in general.")
            r["check"] = None
            break

    # --- 2. add the corpus observations as hypotheses ---------------------------------
    existing = {r["id"] for r in kb["rules"]}

    if "E01" not in existing:
        w = d["width_mm"]
        kb["rules"].append({
            "id": "E01",
            "name": "published figures rarely sit at a stated column width",
            "rule": ("Observed published figure bands have a median width of "
                     f"{w['median']} mm; only {100 * w['share_near_a_column']:.1f} % fall "
                     f"within 3 mm of 89 or 183 mm."),
            "why": ("If true, this separates the SPECIFICATION (a submission must be 89 or "
                    "183 mm) from OBSERVED PRACTICE (published figures are often scaled to "
                    "other widths). Conflating the two was a core error in the earlier rules."),
            "evidence": (
                f"Measured on {w['n']} figure bands from 38 local Nature PDFs: "
                f"p10 {w['p10']}, p25 {w['p25']}, median {w['median']}, p75 {w['p75']}, "
                f"p90 {w['p90']} mm; {w['within_3mm_of_89']} near 89 mm, "
                f"{w['within_3mm_of_183']} near 183 mm."),
            "confidence": "hypothesis",
            "enforced": False,
            "mechanism_verified": False,
            "empirically_measured": True,
            "caveat": (
                "NOT YET TRUSTWORTHY. The figure-band detector is a heuristic that merges "
                "overlapping drawing/image rectangles; it may not recover true figure "
                "boundaries. LEARNINGS.md P0 requires a 20-band manual validation before this "
                "becomes verified."),
            "check": None,
        })

    if "E02" not in existing:
        f = d["min_font_pt"]
        kb["rules"].append({
            "id": "E02",
            "name": "a third of published figure bands contain text below 5 pt",
            "rule": (f"{100 * f['share_below_5pt']:.1f} % of measured figure bands contain at "
                     f"least one text span below 5 pt."),
            "why": ("The specification states a 5 pt minimum. If published figures routinely "
                    "fall below it, then judging compliance by PDF RENDERED font size is a "
                    "flawed metric -- the PDF may be generated larger and scaled down for "
                    "print."),
            "evidence": (
                f"Measured on {f['n']} bands: min {f['min']}, p10 {f['p10']}, "
                f"median {f['median']}, p90 {f['p90']} pt; "
                f"{100 * f['share_below_5pt']:.1f} % below 5 pt."),
            "confidence": "hypothesis",
            "enforced": False,
            "mechanism_verified": False,
            "empirically_measured": True,
            "caveat": (
                "Same detector caveat as E01, PLUS an unresolved scale question: PDF rendered "
                "size is not necessarily printed size. LEARNINGS.md P2."),
            "check": None,
        })

    # --- 3. record the specification-vs-practice distinction --------------------------
    kb["distinction"] = {
        "specification": (
            "What a SUBMISSION must satisfy. Stated by the journal. figpipe enforces these: "
            "exact 89/183 mm, 5-7 pt type, vector, fonttype 42."),
        "observed_practice": (
            "What PUBLISHED figures do. Measured from the corpus. May differ from the "
            "specification because of scaling at typesetting, genre differences, or the "
            "specification describing intent rather than outcome."),
        "why_it_matters": (
            "The earlier rules used 'verified' for both, which let a genre-specific "
            "observation (H02) masquerade as a general rule. L-rules are specification; "
            "E-rules are observed practice; they are not interchangeable."),
    }
    kb["corpus"] = {
        "source": d["source"],
        "papers_measured": 38,
        "bands_raw": d["bands_raw"],
        "bands_kept": d["bands_kept"],
        "bands_excluded": d["bands_excluded"],
        "dirty_data_excluded": d.get("dirty_data_excluded"),
        "learnings_doc": "LEARNINGS.md",
    }
    kb["version"] += 1
    kb["updated"] = datetime.date.today().isoformat()
    KB.write_text(json.dumps(kb, indent=2), encoding="utf-8")

    from collections import Counter
    c = Counter(r["confidence"] for r in kb["rules"])
    print(f"  knowledge base -> v{kb['version']}")
    print(f"  rules: {dict(c)}")
    print()
    for r in kb["rules"]:
        if r["id"] in ("H02", "E01", "E02"):
            print(f"  {r['id']:4s} {r['confidence']:12s} {r['name'][:56]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
