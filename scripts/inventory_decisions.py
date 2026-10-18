"""Inventory the places where figpipe makes a JUDGEMENT rather than a measurement.

WHY THIS COMES BEFORE INTEGRATING ANY DECISION MODEL
    The owner proposes StartLux-Decision 4B as "a unified logical-decision base operator" and
    notes it must be shared, deployed outside this project, usable by every other project.

    That is a good fit for SOME of what figpipe does and a bad fit for the rest. Measured
    against the actual code, the decisions fall into two groups:

      A. DETERMINISTIC. "Is pdf.fonttype 42?" "Is the width 183 mm?" These have one right
         answer that a two-line check settles. Routing them through a language model would add
         latency, cost and a new failure mode in exchange for nothing.

      B. GENUINELY JUDGEMENTAL. "Is this caption a summary or a panel walk?" "Is this region a
         figure or body text?" "Does this caption belong to this figure?" These are
         ambiguous, context-dependent, and currently decided by regexes whose accuracy is
         unmeasured.

    A decision model belongs in group B only. This script enumerates both so the boundary is
    explicit and reviewable, rather than decided by enthusiasm.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "decision_inventory.json"

#: Judgements currently made by CODE, with the mechanism and whether its accuracy is known.
CODE_JUDGEMENTS = [
    {"id": "J01", "where": "archive/figdetect.py (superseded by docling)",
     "question": "Which page region is a figure?",
     "mechanism": "caption-anchored: find 'Fig. N |' then take the contiguous ink block above",
     "deterministic": False,
     "accuracy_known": "partially -- 5/5 visually verified on one paper; 2 known mis-pairs "
                       "enumerated in tests/test_extraction.py",
     "candidate_for_model": True},
    {"id": "J02", "where": "scripts/extract_corpus.py",
     "question": "Which caption belongs to which figure?",
     "mechanism": "nearest caption below with horizontal overlap, plus a gap bound per kind",
     "deterministic": False,
     "accuracy_known": "no -- 196/196 paired but only spot-checked; 2 known mis-pairs",
     "candidate_for_model": True},
    {"id": "J03", "where": "scripts/caption_features.py",
     "question": "Is the opening sentence an overview or the start of a panel walk?",
     "mechanism": "regex: not-a-panel-marker AND not-a-statistic",
     "deterministic": False,
     "accuracy_known": "no -- rules pinned by tests, accuracy against human labels unmeasured",
     "candidate_for_model": True},
    {"id": "J04", "where": "figpipe/figuretypes.py",
     "question": "What TYPE of figure is this?",
     "mechanism": "ordered regex rules over the caption, then aspect ratio",
     "deterministic": False,
     "accuracy_known": "no -- 105/275 (38 %) land in 'unclassified'",
     "candidate_for_model": True},
    {"id": "J05", "where": "scripts/derive_rules.py",
     "question": "Is this measured value physically impossible?",
     "mechanism": "hard bounds: width <= page width, font >= 2 pt",
     "deterministic": True,
     "accuracy_known": "exact -- it is a physical constraint",
     "candidate_for_model": False},
    {"id": "J06", "where": "figpipe/qc.py",
     "question": "Is a truncated axis a FAIL or a WARN?",
     "mechanism": "categorical (barh + explicit ticks) -> WARN, else FAIL",
     "deterministic": True,
     "accuracy_known": "exact -- structural test on the source",
     "candidate_for_model": False},
    {"id": "J07", "where": "figpipe/colourcheck.py",
     "question": "Is this colour map a rainbow?",
     "mechanism": "hue bins plus lightness direction reversals from the rendered pixels",
     "deterministic": True,
     "accuracy_known": "measured -- jet=True, viridis/cividis=False, pinned by test",
     "candidate_for_model": False},
    {"id": "J08", "where": "figpipe/style.py",
     "question": "Are the rcParams compliant?",
     "mechanism": "equality against the specification",
     "deterministic": True,
     "accuracy_known": "exact",
     "candidate_for_model": False},
    {"id": "J09", "where": "scripts/slim.py",
     "question": "Is this path regenerable?",
     "mechanism": "explicit allow-list of paths, guarded by figpipe/sources.py",
     "deterministic": True,
     "accuracy_known": "exact -- a path either matches the list or does not",
     "candidate_for_model": False},
    {"id": "J10", "where": "knowledge/layout_rules.json",
     "question": "Should this rule be enforced, or only observed?",
     "mechanism": "human classification: specification vs observed practice",
     "deterministic": False,
     "accuracy_known": "no -- this is a scientific judgement about what a rule MEANS",
     "candidate_for_model": False,
     "why_not": "A model must not decide which of its own findings counts as a requirement. "
                "That is the H02 mistake with extra steps."},
]


def main() -> int:
    model_cands = [j for j in CODE_JUDGEMENTS if j["candidate_for_model"]]
    det = [j for j in CODE_JUDGEMENTS if j["deterministic"]]
    out = {
        "about": ("Which figpipe decisions are genuinely judgemental, and which are exact. "
                  "Only the judgemental ones are candidates for a decision model."),
        "n_total": len(CODE_JUDGEMENTS),
        "n_deterministic": len(det),
        "n_candidate_for_model": len(model_cands),
        "judgements": CODE_JUDGEMENTS,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  judgements audited : {len(CODE_JUDGEMENTS)}")
    print(f"  deterministic       : {len(det)}  (a model would add cost and failure modes)")
    print(f"  need judgement      : {len(model_cands)}")
    print()
    print("  %-5s %-34s %-9s %s" % ("id", "question", "det?", "accuracy known?"))
    print("  " + "-" * 88)
    for j in CODE_JUDGEMENTS:
        print("  %-5s %-34s %-9s %s" % (
            j["id"], j["question"][:34], "yes" if j["deterministic"] else "NO",
            j["accuracy_known"][:34]))
    print(f"\n  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
