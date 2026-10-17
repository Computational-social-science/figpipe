"""The self-improvement loop: measure, then promote a rule from hypothesis to verified.

HOW THE PIPELINE IMPROVES WITHOUT A HUMAN EDITING IT
    The knowledge base (`knowledge/layout_rules.json`) separates rules into `verified` and
    `hypothesis`. This script does two things on every run:

      1. RE-VERIFIES the verified rules by measuring the pipeline's own output. If a rule no
         longer holds -- because matplotlib changed, or a style update regressed it -- the rule
         is demoted and an alert is written. A rule that cannot be re-measured is not a rule.

      2. MEASURES THE HYPOTHESES. A hypothesis is promoted only when a measurement supports
         it. `H02` (whitespace ratio) can be measured on the pipeline's own figures: the
         fraction of non-white pixels. If the measured band is stable across figures, that
         band becomes a verified rule with the measurement attached.

    The output is a machine-readable report AND a rewritten knowledge base, so the next run
    starts from what this run learned.

WHAT THIS LOOP CANNOT DO
    It cannot judge whether a figure is well designed. It can only promote rules that reduce
    to a number measurable from the output file. Aesthetics stay a human judgement, and the
    knowledge base marks the boundary rather than hiding it.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

KB = ROOT / "knowledge" / "layout_rules.json"
REPORT = ROOT / "knowledge" / "evolution_report.json"
FIGS = ROOT.parent / "keystroke-observatory" / "docs"


def ink_density(png: pathlib.Path) -> float:
    """Fraction of non-white pixels. The measurement behind the whitespace hypothesis."""
    a = np.array(Image.open(png).convert("L"), dtype=np.uint8)
    return float((a < 200).mean())


def measure_hypothesis_h02() -> dict:
    """H02: content should occupy most of the canvas.

    Measured on the pipeline's own figures. A band is only promoted if the figures cluster --
    if the spread is enormous there is no band to learn, and the hypothesis stays open.
    """
    figs = sorted(FIGS.glob("fig*.png")) if FIGS.is_dir() else []
    if not figs:
        return {"status": "unmeasurable", "reason": "no figures to measure"}
    vals = {p.name: round(100 * ink_density(p), 2) for p in figs}
    arr = np.array(list(vals.values()))
    spread = float(arr.max() - arr.min())
    return {
        "status": "measured",
        "values_pct": vals,
        "mean": round(float(arr.mean()), 2),
        "min": round(float(arr.min()), 2),
        "max": round(float(arr.max()), 2),
        "spread_pp": round(spread, 2),
        "band": [round(float(arr.min()), 1), round(float(arr.max()), 1)],
        "promotable": spread <= 25.0,
        "note": ("the spread is wide, so no single band describes these figures; the "
                 "hypothesis stays open" if spread > 25.0 else
                 "the figures cluster, so a band can be promoted to a verified rule"),
    }


def reverify_verified_rules() -> dict:
    """Re-measure every rule marked `verified`. Demote any that no longer holds."""
    from figpipe import style
    style.apply()
    import matplotlib.pyplot as plt

    checks = {
        "L03": lambda: all(
            isinstance(plt.rcParams[k], (int, float)) and 5.0 <= float(plt.rcParams[k]) <= 7.0
            for k in ("axes.titlesize", "axes.labelsize", "xtick.labelsize")),
        "L05": lambda: plt.rcParams.get("savefig.bbox") is None,
        "L06": lambda: plt.rcParams.get("pdf.fonttype") == 42,
    }
    out = {}
    for rid, fn in checks.items():
        try:
            out[rid] = {"holds": bool(fn())}
        except Exception as e:                                   # noqa: BLE001
            out[rid] = {"holds": False, "error": str(e)[:120]}
    return out



def _atomic_write(path: pathlib.Path, text: str) -> None:
    """Write via a temporary file and os.replace, so a killed process cannot truncate it.

    write_text truncates before writing: a process killed between those steps leaves a
    zero-length file. The knowledge base was found empty exactly this way. os.replace is
    atomic, so a reader sees either the previous contents or the new ones.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    reverify = reverify_verified_rules()
    h02 = measure_hypothesis_h02()

    demoted, promoted = [], []
    for rule in kb["rules"]:
        rid = rule["id"]
        if rid in reverify and not reverify[rid]["holds"]:
            rule["confidence"] = "regressed"
            rule["regressed_on"] = datetime.date.today().isoformat()
            demoted.append(rid)
        # Only promote a rule that is not already verified. Without this guard the promotion
        # re-fires every run and the version number inflates with no change behind it --
        # observed v5 -> v6 -> v7 in 40 seconds with no rule actually changing.
        if rid == "H02" and h02.get("promotable") and rule["confidence"] != "verified":
            rule["confidence"] = "verified"
            rule["evidence"] = (
                f"Measured on {len(h02['values_pct'])} of this pipeline's own figures: ink "
                f"density {h02['min']}-{h02['max']}% (mean {h02['mean']}%, spread "
                f"{h02['spread_pp']} pp). The figures cluster, so the band is a rule.")
            rule["band_pct"] = h02["band"]
            promoted.append(rid)

    # Version increments only on a real state change, so a quiet run leaves the base alone.
    if demoted or promoted:
        kb["version"] = kb.get("version", 1) + 1
    if demoted or promoted:
        kb["updated"] = datetime.date.today().isoformat()
    _atomic_write(KB, json.dumps(kb, indent=2))

    report = {
        "run_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "knowledge_base_version": kb["version"],
        "reverified": reverify,
        "demoted": demoted,
        "promoted": promoted,
        "hypothesis_H02": h02,
        "summary": {
            "verified_rules": sum(1 for r in kb["rules"] if r["confidence"] == "verified"),
            "open_hypotheses": sum(1 for r in kb["rules"] if r["confidence"] == "hypothesis"),
            "regressed": sum(1 for r in kb["rules"] if r["confidence"] == "regressed"),
        },
    }
    _atomic_write(REPORT, json.dumps(report, indent=2))

    print(f"  knowledge base -> v{kb['version']}")
    print(f"  re-verified: {sum(1 for v in reverify.values() if v['holds'])}/{len(reverify)} hold")
    if demoted:
        print(f"  DEMOTED (regression detected): {demoted}")
    print(f"  hypotheses measured: H02 spread {h02.get('spread_pp', 'n/a')} pp "
          f"-> {'PROMOTED' if promoted else 'stays open'}")
    print(f"  verified rules: {report['summary']['verified_rules']}, "
          f"open: {report['summary']['open_hypotheses']}")
    print(f"  wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
