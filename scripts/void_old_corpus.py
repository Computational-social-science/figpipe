"""Mark the superseded corpus as void, and record why.

WHY THIS IS URGENT RATHER THAN TIDY
    The adversarial audit's second round found TWO incompatible corpora living side by side:

        corpus/measured.json   420 bands / 38 papers  <- OLD detector, ~50% wrong
        corpus/derived.json    369 bands / 38 papers  <- derived from the old detector
        knowledge base corpus  369 bands / 38 papers  <- derived from the old detector
        corpus/figures_caption_anchored.json  73 figures / 11 papers  <- NEW detector

    and nothing marked the old files as superseded. A reader -- or a future run -- would take
    the 369-band numbers as current.

    Worse, E02 is a rule ABOUT FONT SIZE, and the new caption-anchored records do not carry
    `min_font_pt` at all. So E02 has no measurement basis whatsoever now; it is not merely
    stale, it is unsupported.

WHAT THIS DOES
    1. stamps the old artefacts with `superseded_by` and `do_not_use`
    2. downgrades E01 and E02 to `void` with the reason attached
    3. corrects E01's quoted figure: the audit showed my "52.1 %" used a +/-5 mm tolerance
       while E01 itself states +/-3 mm, where the figure is 38.4 %. Reporting the wider
       tolerance made the effect look twice as large.
"""
from __future__ import annotations

import datetime
import json
import pathlib

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
CORPUS = ROOT / "corpus"
KB = ROOT / "knowledge" / "layout_rules.json"
TODAY = datetime.date.today().isoformat()

STAMP = {
    "superseded_by": "corpus/figures_caption_anchored.json",
    "do_not_use": True,
    "superseded_on": TODAY,
    "why": ("Produced by the ink-rectangle-merging detector, which the adversarial audit "
            "found wrong for roughly half its output (a full page of news prose was "
            "classified as a figure; 67 bands exceeded the 240 mm page height; one reached "
            "14,437 mm). Replaced by caption-anchored detection."),
}


def stamp(path: pathlib.Path) -> str:
    if not path.is_file():
        return "absent"
    j = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(j, dict):
        j.update(STAMP)
        path.write_text(json.dumps(j, indent=2), encoding="utf-8")
        return "stamped"
    return "not-a-dict"


def main() -> int:
    for name in ("measured.json", "derived.json"):
        print(f"  {name:<22} {stamp(CORPUS / name)}")

    kb = json.loads(KB.read_text(encoding="utf-8"))

    # re-derive E01's figure at the tolerance E01 itself declares (+/-3 mm)
    anchor = CORPUS / "figures_caption_anchored.json"
    corrected = None
    if anchor.is_file():
        figs = json.loads(anchor.read_text(encoding="utf-8"))
        widths = [f["width_mm"] for f in figs]
        papers = len({f.get("paper") for f in figs})
        near = sum(1 for w in widths if abs(w - 89) <= 3 or abs(w - 183) <= 3)
        near5 = sum(1 for w in widths if abs(w - 89) <= 5 or abs(w - 183) <= 5)
        corrected = {
            "n_figures": len(widths), "n_papers": papers,
            "share_near_column_3mm": round(near / len(widths), 4),
            "share_near_column_5mm": round(near5 / len(widths), 4),
            "median_width_mm": round(sorted(widths)[len(widths) // 2], 1),
        }

    for r in kb["rules"]:
        if r["id"] in ("E01", "E02"):
            r["confidence"] = "void"
            r["enforced"] = False
            r["voided_on"] = TODAY
            r["voided_because"] = (
                "Measured on the ink-rectangle-merging detector, which the adversarial audit "
                "showed was wrong for roughly half its output. The numbers are not merely "
                "imprecise, they are about a different population.")
            r["check"] = None
            if r["id"] == "E01" and corrected:
                r["corrected_measurement"] = corrected
                r["correction_note"] = (
                    "My earlier report said '52.1 % within a stated column width'. That used "
                    "a +/-5 mm tolerance while this rule itself states +/-3 mm. At +/-3 mm the "
                    "figure is 38.4 %. Reporting the wider tolerance doubled the apparent "
                    "effect. Both are now recorded so the discrepancy is visible rather than "
                    "replaced silently.")
            if r["id"] == "E02":
                r["unsupported_because"] = (
                    "E02 is about FONT SIZE, and the caption-anchored records do not carry "
                    "min_font_pt at all. The new detector does not measure type, so this rule "
                    "has no measurement basis and cannot be re-derived until it does.")

    kb["corpus"]["superseded"] = True
    kb["corpus"]["superseded_on"] = TODAY
    kb["corpus"]["superseded_because"] = (
        "The 369-band figures came from the ink-rectangle detector the audit found ~50 % "
        "wrong. Current corpus is corpus/figures_caption_anchored.json (73 figures, 11 "
        "papers, caption-anchored).")
    if corrected:
        kb["corpus"]["current"] = corrected
    kb["version"] += 1
    kb["updated"] = TODAY
    KB.write_text(json.dumps(kb, indent=2), encoding="utf-8")

    from collections import Counter
    c = Counter(r["confidence"] for r in kb["rules"])
    print(f"\n  knowledge base -> v{kb['version']}")
    print(f"  rules: {dict(c)}")
    if corrected:
        print(f"\n  E01 corrected at its OWN tolerance (+/-3 mm): "
              f"{100 * corrected['share_near_column_3mm']:.1f} % "
              f"(not the 52.1 % I reported at +/-5 mm)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
