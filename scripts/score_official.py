"""Score the WHOLE benchmark pool through PlotTwin-Bench's own deterministic channel.

WHY A SEPARATE PASS
    The benchmark harness measures style distance on every task, but the OFFICIAL code channel needs
    three things the harness only has for tasks whose cache entry is current: the reference code, a
    panel the emitter can express, and the reference's extracted style features. Cached rows are
    pruned for disk budget, so the harness ends up with an official score for a fraction of the pool.

    This script does the one job properly: walk the pool, extract the reference style features,
    emit a candidate script that reproduces them, score the pair with the benchmark's own scorer,
    and write a report that states exactly what was and was not scored.

WHAT THIS NUMBER IS AND IS NOT
    * It is `score_code_deviation` from `third_party/plottwin_scorer`, i.e. the benchmark's own
      `deviation-defect-v1` code channel, worth 35 % of the official combined score.
    * It is NOT the combined score: the 65 % vision channel needs a model this project does not run.
    * A task whose drawer has no emitter is reported as `unscored` with the reason, never as zero.

USAGE
    python scripts/score_official.py --limit 150
    python scripts/score_official.py --limit 20 --types Line,Scatter
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "third_party"))

from figpipe import codegen  # noqa: E402

try:
    import plottwin_scorer as official
except Exception:                                   # noqa: BLE001 - optional, CC BY-NC
    official = None

import bench_plottwin as bench                       # noqa: E402

OUT = ROOT / "corpus" / "e2e" / "official_scores.json"


def score_one(row: dict, *, source: str = "image") -> dict:
    """Extract the reference style, emit a matching candidate, score the pair."""
    rec = {"id": row.get("id"), "chart": row.get("chart_type_name")}
    if official is None:
        rec.update({"status": "unavailable", "reason": "official scorer not vendored"})
        return rec
    ref_code = row.get("reference_code")
    if not ref_code:
        rec.update({"status": "unscored", "reason": "task carries no reference_code"})
        return rec
    if source == "code":
        # TAUTOLOGY MODE. The reference code is part of the task record, so reading its style and
        # emitting the same style is legal -- but it measures "can the emitter copy a spec", not
        # "can the pipeline infer a style". Kept only as a ceiling/upper bound.
        try:
            features = official.extract_style_features(ref_code)["features"]
            style = codegen.style_from_features(features)
        except Exception as exc:                    # noqa: BLE001
            rec.update({"status": "unscored",
                        "reason": f"reference features not extractable: {type(exc).__name__}"})
            return rec
    else:
        # HONEST MODE: style inferred from the reference IMAGE only -- what a real user has.
        img = pathlib.Path(row.get("reference_url") or "")
        if not img.is_file():
            img = bench.IMAGES / f"{row.get('id')}.png"
        if not img.is_file():
            try:
                img = bench.download_image(row)
            except Exception as exc:                # noqa: BLE001
                rec.update({"status": "unscored",
                            "reason": f"reference image unavailable: {type(exc).__name__}"})
                return rec
        try:
            from figpipe import styleprofile
            cropped = bench.crop_ink(img, img.with_name(img.stem + "_crop.png"))
            prof = styleprofile.StyleProfile.from_image_detailed(cropped)
            style = codegen.style_from_image_profile(prof)
        except Exception as exc:                    # noqa: BLE001
            rec.update({"status": "unscored",
                        "reason": f"image style not inferable: {type(exc).__name__}"})
            return rec
    # a minimal panel is enough: the code channel scores STYLE, not data content
    import pandas as pd
    df = pd.DataFrame({"x": np.arange(20.0), "y": np.linspace(0.1, 0.9, 20)})
    from figpipe import composite
    panel = composite.Panel("trend_band", df, {"x": "x", "y": "y", "fit": "lm"})
    try:
        candidate = codegen.emit([panel], columns=2.0, height_mm=100.0, style=style,
                                 palette=style.get("palette"))
    except Exception as exc:                        # noqa: BLE001
        rec.update({"status": "unscored",
                    "reason": f"emitter cannot express this style: {type(exc).__name__}"})
        return rec
    try:
        res = official.score_code_deviation(ref_code, candidate)
    except Exception as exc:                        # noqa: BLE001
        rec.update({"status": "unscored", "reason": f"scorer failed: {type(exc).__name__}"})
        return rec
    rec.update({
        "status": "scored" if res["available"] else "unavailable",
        "score": res["score"],
        "n_activated": res["n_activated"],
        "scored_dimensions": res["scored_dimensions"],
        "unavailable_dimensions": res["unavailable_dimensions"],
    })
    if not res["available"]:
        rec["reason"] = res["status"]
    return rec


def summarise(records: list[dict], source: str = "image") -> dict:
    scored = [r for r in records if r["status"] == "scored" and r.get("score") is not None]
    by_type: dict[str, list[float]] = {}
    for r in scored:
        by_type.setdefault(r["chart"], []).append(float(r["score"]))
    return {
        "channel": "code_deviation",
        "scorer": "plottwin_scorer deviation-defect-v1 (vendored, unmodified)",
        "weight_upstream": 0.35,
        "note": ("OFFICIAL deterministic channel only. The 0.65 vision channel is not run, so this "
                 "is NOT the combined score."),
        "style_source": source,
        "n_tasks": len(records),
        "n_scored": len(scored),
        "n_unscored": sum(1 for r in records if r["status"] == "unscored"),
        "n_unavailable": sum(1 for r in records if r["status"] == "unavailable"),
        "mean_score": round(float(np.mean([r["score"] for r in scored])), 2) if scored else None,
        "min_score": round(float(np.min([r["score"] for r in scored])), 2) if scored else None,
        "max_score": round(float(np.max([r["score"] for r in scored])), 2) if scored else None,
        "by_type": {k: {"n": len(v), "mean": round(float(np.mean(v)), 2)}
                    for k, v in sorted(by_type.items())},
        "unscored_reasons": _reasons(records),
    }


def _reasons(records: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for r in records:
        if r["status"] != "scored":
            key = str(r.get("reason", "unknown"))[:70]
            counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--types", default="")
    ap.add_argument("--source", choices=["image", "code"], default="image",
                    help="where the candidate's style comes from: 'image' (honest, the benchmark "
                         "premise) or 'code' (tautological ceiling, kept for comparison)")
    args = ap.parse_args(argv)
    wanted = {t.strip() for t in args.types.split(",") if t.strip()}

    records: list[dict] = []
    for off in range(args.offset, min(args.offset + args.limit, bench.POOL)):
        try:
            row = bench.fetch_row(off)
        except Exception as exc:                    # noqa: BLE001 - network is not a score
            records.append({"id": f"offset-{off}", "chart": "?", "status": "unscored",
                            "reason": f"fetch failed: {type(exc).__name__}"})
            continue
        if wanted and row.get("chart_type_name") not in wanted:
            continue
        records.append(score_one(row, source=args.source))
        if len(records) % 10 == 0:
            print(f"  ... {len(records)} tasks processed")

    summary = summarise(records, args.source)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"summary": summary, "records": records},
                              indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print()
    print(f"  scored {summary['n_scored']}/{summary['n_tasks']} tasks")
    print(f"  official code-channel mean: {summary['mean_score']} "
          f"(min {summary['min_score']}, max {summary['max_score']})")
    for name, st in summary["by_type"].items():
        print(f"    {name:<14} n={st['n']:<3} mean={st['mean']}")
    if summary["unscored_reasons"]:
        print("  not scored:")
        for reason, n in summary["unscored_reasons"].items():
            print(f"    {n:>3} x {reason}")
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
