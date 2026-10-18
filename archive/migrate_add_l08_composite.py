"""ONE-SHOT MIGRATION: add L08 (a plate is not a swatch) and the composite study metadata.

WHY IT IS ARCHIVED, NOT DELETED
    This is the source proof for the knowledge base's current state: it says exactly which rule
    was added, on what measurement, and with what check. Re-running it is a no-op.

WHAT IT ADDS
    L08  a multi-panel figure must come from figpipe.composite: one 8 pt letter per panel and a
         uniform gutter, verified by composing a plate and reading it back
    the `composite_study` block, pointing at corpus/composite_layouts.json and quoting the
         measured distributions so the evidence travels with the rule

Run:  python archive/migrate_add_l08_composite.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge" / "layout_rules.json"
STUDY = ROOT / "corpus" / "composite_layouts.json"


def rule_from_measurement(study: dict) -> dict:
    g = study.get("gutter") or {}
    pa = study.get("panel_aspect") or {}
    lo = study.get("letter_offsets") or {}
    return {
        "id": "L08",
        "name": "a plate is not a swatch",
        "rule": ("A figure with more than one panel is built by figpipe.composite: every panel "
                 "carries exactly one 8 pt letter, and one gutter width runs through the whole "
                 "plate."),
        "why": ("Six single-panel templates produced one axes each, so the library could draw a "
                "swatch but not the plate a paper actually prints. The composer owns the "
                "geometry; the panel only owns its drawing. An empty grid cell, an uneven "
                "gutter and a missing letter are all visible defects, and a composer without a "
                "read-back check ships them silently."),
        "evidence": (
            f"Measured on the caption-anchored corpus ({study.get('n_measured')} real figures): "
            f"{study.get('n_composites')} composites, of which "
            f"{study.get('n_split_verified')} had every internal boundary inside an empty band; "
            f"gutter median {g.get('median_mm')} mm (n={g.get('n')}), panel aspect median "
            f"{pa.get('median')} (n={pa.get('n')}), and every one of "
            f"{lo.get('n')} detected panel letters was {lo.get('size_pt_median')} pt."),
        "confidence": "enforced",
        "enforced_by": "figpipe.composite.check",
        "mechanism_verified": True,
        "empirically_measured": True,
        "enforced": True,
        "check": {
            "kind": "composite_plate",
            "why": ("composes a real four-panel plate and reads the letters, gutters and page "
                    "size back; a composer that stack panels on top of each other fails it"),
        },
    }


def main() -> int:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    study = json.loads(STUDY.read_text(encoding="utf-8")) if STUDY.is_file() else {}
    ids = [r["id"] for r in kb["rules"]]
    if "L08" in ids:
        print("  L08 already present; nothing to do")
        return 0
    kb["rules"].append(rule_from_measurement(study))
    g, pa = study.get("gutter") or {}, study.get("panel_aspect") or {}
    kb["composite_study"] = {
        "source": "corpus/composite_layouts.json",
        "method": study.get("method"),
        "n_figures_measured": study.get("n_measured"),
        "n_composites": study.get("n_composites"),
        "n_split_verified": study.get("n_split_verified"),
        "n_caption_agreement": study.get("n_caption_agreement"),
        "gutter_mm": {"median": g.get("median_mm"), "p25": g.get("p25_mm"),
                      "p75": g.get("p75_mm"), "n": g.get("n")},
        "panel_aspect": {"median": pa.get("median"), "n": pa.get("n")},
        "grid_distribution": study.get("grid_distribution"),
        "measured_at": "2026-10-18",
    }
    kb["version"] = int(kb.get("version", 0)) + 1
    kb["updated"] = "2026-10-18"
    KB.write_text(json.dumps(kb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  added L08; knowledge base -> v{kb['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
