"""What Nature captions actually do -- measured, and compared against the guidance.

WHY THIS EXISTS
    The task asked to learn "why a figure is clear and professional", including the caption
    structure: does it open with a summary, then walk the panels, then state the statistics?
    That was previously left to the VLM, which the audit proved fabricates. These four
    properties are measurable from the caption string exactly.

    So this script reports what the corpus does, splits it by figure kind (main text vs
    Extended Data -- different conventions), and states the sample size behind every number.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "corpus" / "caption_features.jsonl"
OUT = ROOT / "corpus" / "caption_analysis.json"

FEATURES = [
    "caption_overview_first",
    "caption_panel_by_panel",
    "caption_has_stats",
    "caption_stats_last",
    "caption_defines_error",
]


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0}
    out = {"n": n}
    for k in FEATURES:
        c = sum(1 for r in rows if r.get(k))
        out[k] = {"count": c, "share": round(c / n, 4)}
    lens = [r["caption_chars"] for r in rows]
    out["caption_chars"] = {"median": int(np.median(lens)), "p25": int(np.percentile(lens, 25)),
                            "p75": int(np.percentile(lens, 75)), "max": max(lens)}
    panels = [r["n_panel_markers"] for r in rows]
    out["panel_markers"] = {"median": int(np.median(panels)),
                            "p90": int(np.percentile(panels, 90)),
                            "max": max(panels),
                            "share_with_2_or_more": round(
                                sum(1 for p in panels if p >= 2) / n, 4)}
    return out


def main() -> int:
    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_kind: dict[str, list[dict]] = {}
    for r in rows:
        by_kind.setdefault(str(r.get("kind") or "figure"), []).append(r)

    result = {"source": "corpus/caption_features.jsonl", "overall": summarise(rows),
              "by_kind": {k: summarise(v) for k, v in sorted(by_kind.items())}}
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    o = result["overall"]
    print(f"  captions: {o['n']}")
    print()
    print("  %-26s %8s %8s" % ("feature", "count", "share"))
    print("  " + "-" * 46)
    for k in FEATURES:
        print("  %-26s %8d %7.1f%%" % (k, o[k]["count"], 100 * o[k]["share"]))
    print()
    print("  caption length (chars): median %d  p25 %d  p75 %d  max %d" % (
        o["caption_chars"]["median"], o["caption_chars"]["p25"],
        o["caption_chars"]["p75"], o["caption_chars"]["max"]))
    print("  panel markers         : median %d  p90 %d  max %d  (>=2: %.1f%%)" % (
        o["panel_markers"]["median"], o["panel_markers"]["p90"], o["panel_markers"]["max"],
        100 * o["panel_markers"]["share_with_2_or_more"]))
    print()
    print("  BY KIND")
    print("  %-26s %6s %10s %10s %10s" % ("kind", "n", "overview", "panelwalk", "stats"))
    print("  " + "-" * 66)
    for k, v in sorted(result["by_kind"].items(), key=lambda kv: -kv[1]["n"]):
        if not v["n"]:
            continue
        print("  %-26s %6d %9.1f%% %9.1f%% %9.1f%%" % (
            k[:26], v["n"], 100 * v["caption_overview_first"]["share"],
            100 * v["caption_panel_by_panel"]["share"],
            100 * v["caption_has_stats"]["share"]))
    print(f"\n  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
