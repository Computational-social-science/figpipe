"""Fold the caption measurements into the knowledge base -- as hypotheses, not rules.

WHY NOT RULES
    The numbers are real: 196 captions, measured from text, reproducible, with the rule that
    produced each marked. But "Nature captions are 96.4 % overview-first" is a description of a
    corpus, not a constraint a submission must satisfy. Promoting it to an enforced rule would
    repeat the H02 mistake -- taking a measured regularity and pretending it is a requirement.

    So these enter as OBSERVED PRACTICE with `confidence: hypothesis`, and are explicitly
    labelled as observations a figure may depart from.
"""
from __future__ import annotations

import datetime
import json
import pathlib

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
KB = ROOT / "knowledge" / "layout_rules.json"
ANALYSIS = ROOT / "corpus" / "caption_analysis.json"
TODAY = datetime.date.today().isoformat()

OBS = {
    "C01": ("caption opens with a summary sentence",
            "caption_overview_first",
            "Does the caption's first sentence state what the whole figure shows, rather than "
            "starting a panel walk or a statistic?"),
    "C02": ("captions walk the panels when there are panels",
            "caption_panel_by_panel",
            "Does the caption address two or more panels explicitly ((a)/(b) or 'a, b,')?"),
    "C03": ("captions state their statistics",
            "caption_has_stats",
            "Does the caption state n, a test, an interval, or an error definition?"),
    "C04": ("captions usually do NOT put statistics last",
            "caption_stats_last",
            "Is the statistical material carried by the FINAL sentence?"),
}


def main() -> int:
    a = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    overall = a["overall"]
    main_text = a["by_kind"].get("figure") or {}

    kb = json.loads(KB.read_text(encoding="utf-8"))
    existing = {r["id"] for r in kb["rules"]}
    added = []
    for rid, (name, key, question) in OBS.items():
        if rid in existing:
            continue
        f = overall[key]
        mt = main_text.get(key) if main_text.get("n") else None
        kb["rules"].append({
            "id": rid,
            "name": name,
            "rule": f"Observed in {f['count']}/{overall['n']} ({100*f['share']:.1f} %) of the "
                    f"corpus captions.",
            "why": question,
            "evidence": (
                f"Measured from caption TEXT (not a vision model) over {overall['n']} captions "
                f"from 34 Nature PDFs: {f['count']}/{overall['n']} = {100*f['share']:.1f} %. "
                f"Main-text figures only: "
                + (f"{mt['count']}/{main_text['n']} = {100*mt['share']:.1f} %."
                   if mt else "n/a")),
            "confidence": "hypothesis",
            "enforced": False,
            "mechanism_verified": False,
            "empirically_measured": True,
            "observed_practice": True,
            "caveat": (
                "This describes what published captions DO, not what a submission MUST do. It "
                "is not enforced and must not be treated as a requirement. The classifier is a "
                "text heuristic; its rules are pinned by tests and a mutation test proves the "
                "tests fail when the rule is broken."),
            "check": None,
        })
        added.append(rid)

    kb["caption_study"] = {
        "source": "corpus/caption_features.jsonl",
        "method": ("measured from the caption string; no VLM involved, because the local model "
                   "was shown to fabricate figure properties (20 assertions across 3 control "
                   "images, verdict FABRICATES)"),
        "n_captions": overall["n"],
        "by_kind": {k: v["n"] for k, v in a["by_kind"].items()},
        "measured_at": TODAY,
    }
    from refresh_coverage import compute as _cov
    kb["check_coverage"] = _cov(kb["rules"])
    kb["version"] += 1
    kb["updated"] = TODAY
    KB.write_text(json.dumps(kb, indent=2), encoding="utf-8")

    from collections import Counter
    c = Counter(r["confidence"] for r in kb["rules"])
    print(f"  knowledge base -> v{kb['version']}")
    print(f"  added as hypothesis: {added}")
    print(f"  rules: {dict(c)}")
    print(f"  check_coverage: {kb['check_coverage']['rules_with_check']} with / "
          f"{kb['check_coverage']['rules_without_check']} without")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
