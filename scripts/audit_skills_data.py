"""Run every skill against REAL long-format data shapes, and report what breaks.

WHY THIS EXISTS
    The worked example found a defect that thirteen rounds of internal tests missed: `encode.bars`
    drew ONE BAR PER ROW, so a long table with 40 rows over 2 categories stacked 40 overlapping
    bars and produced three hard text collisions. Every internal test used already-aggregated data,
    so the path "long table -> grouped bars" was never exercised.

    That is a class of defect, not an incident. This script is the systematic version: it feeds
    every registered skill the data shapes a real researcher actually has -- many rows per category,
    repeated measures, missing values, single observations per level -- and reports what each one
    does. A skill that silently draws the wrong thing is worse than one that refuses.

WHAT IT REPORTS
    ok            rendered, passed the global floor
    refused       raised a SkillError with a reason (a valid, correct outcome)
    BROKEN        rendered but produced hard findings (the silent-wrong case)
    CRASHED       raised something that is not a SkillError (a defect in the operator)

USAGE
    python scripts/audit_skills_data.py
    python scripts/audit_skills_data.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import traceback

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import skills  # noqa: E402


def shapes(seed: int = 11) -> dict[str, pd.DataFrame]:
    """The data shapes a researcher actually has, not the ones that make tests pass."""
    rng = np.random.default_rng(seed)
    n_years, n_groups = 20, 3
    # LONG: many rows per category -- the shape that broke grouped bars
    long_rows = []
    for g in ("control", "treated", "placebo")[:n_groups]:
        for i in range(n_years):
            long_rows.append({
                "year": 2005 + i,
                "group": g,
                "response": round(float(0.3 + 0.01 * i + rng.normal(0, 0.01)), 4),
                "se": round(float(abs(rng.normal(0.01, 0.002))), 4),
            })
    long = pd.DataFrame(long_rows)

    # WIDE-ONE: one row per category (the shape internal tests used)
    wide_one = long.groupby("group", as_index=False)[["response", "se"]].mean()

    # TIME-SERIES: one row per year, two measures
    ts = (long.groupby("year", as_index=False)[["response", "se"]].mean()
          .assign(year=lambda d: d["year"].astype(int)))

    # REPLICATES: several observations per level with no time axis
    repl = pd.DataFrame({
        "condition": ["a"] * 12 + ["b"] * 12 + ["c"] * 12,
        "score": rng.normal(0.5, 0.1, 36),
        "err": abs(rng.normal(0.02, 0.005, 36)),
    })

    # SPARSE: missing values scattered through a real measure
    sparse = long.copy()
    sparse.loc[sparse.sample(frac=0.15, random_state=seed).index, "response"] = np.nan

    # SINGLE: one observation per level (no spread to show)
    single = pd.DataFrame({"level": list("abc"), "value": [0.2, 0.5, 0.8]})

    # GRID: a genuine 2-D field
    xs = np.repeat(np.arange(8.0), 6)
    ys = np.tile(np.arange(6.0), 8)
    grid = pd.DataFrame({"x": xs, "y": ys,
                         "v": np.exp(-((xs - 4) ** 2) / 8) * (1 + ys / 6)})

    return {"long": long, "wide_one": wide_one, "time_series": ts, "replicates": repl,
            "sparse": sparse, "single": single, "grid": grid}


#: Per-skill parameters that make sense for each shape. A skill is only tested where the caller
#: could plausibly supply the columns it needs -- testing it elsewhere would report noise.
CASES = [
    ("trend_with_uncertainty", "time_series", {"x": "year", "y": "response", "fit": "lm"}),
    ("trend_with_uncertainty", "sparse", {"x": "year", "y": "response", "fit": "lm"}),
    ("trend_with_uncertainty", "long", {"x": "year", "y": "response", "fit": "lm"}),
    ("ranked_composition", "wide_one", {"label": "group", "value": "response"}),
    ("ranked_composition", "single", {"label": "level", "value": "value"}),
    ("ranked_composition", "long", {"label": "group", "value": "response"}),
    ("distribution_comparison", "replicates", {"group": "condition", "value": "score"}),
    ("distribution_comparison", "long", {"group": "group", "value": "response"}),
    ("grouped_measures", "long", {"x": "group", "ycols": ["response", "se"]}),
    ("grouped_measures", "wide_one", {"x": "group", "ycols": ["response", "se"]}),
    ("grouped_measures", "time_series", {"x": "year", "ycols": ["response", "se"]}),
    ("histogram", "long", {"value": "response"}),
    ("histogram", "replicates", {"value": "score", "group": "condition"}),
    ("density_relationship", "long", {"x": "year", "y": "response"}),
    ("scatter_relationship", "long", {"x": "year", "y": "response"}),
    ("matrix_plate", "grid", {}),
    ("field_map", "grid", {"x": "x", "y": "y", "value": "v"}),
    ("composite_groups", "long", {"by": "group", "x": "year", "y": "response"}),
    ("radial_profile", "wide_one", {"theta": "group", "value": "response"}),
]


def run_case(name: str, data: pd.DataFrame, params: dict, out_dir: pathlib.Path) -> dict:
    rec = {"skill": name, "rows": int(len(data)), "params": params}
    try:
        res = skills.run(name, data, out_stem=out_dir / f"{name}_{len(data)}", **params)
    except skills.SkillError as exc:
        rec.update({"status": "refused", "detail": str(exc)[:140]})
        return rec
    except Exception as exc:                       # noqa: BLE001 - that is the finding
        rec.update({"status": "CRASHED", "detail": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc()[-600:]})
        return rec
    hard = [f for f in res["findings"] if f.get("severity") == "hard"]
    rec.update({"status": "BROKEN" if hard else "ok",
                "panels": res["panels"],
                "findings": [f"{f['check']}: {f['detail']}" for f in hard][:4],
                "trace": res["trace"][:3]})
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    data = shapes()
    out_dir = ROOT / "examples" / "output" / "skill_audit"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  {len(CASES)} cases over {len(data)} data shapes")
    print(f"  {'skill':<26} {'rows':>5}  {'status':<9} detail")
    results = []
    for name, shape, params in CASES:
        rec = run_case(name, data[shape], params, out_dir)
        rec["shape"] = shape
        results.append(rec)
        detail = rec.get("detail") or (rec.get("findings") or [""])[0]
        print(f"  {name:<26} {rec['rows']:>5}  {rec['status']:<9} {detail[:88]}")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print()
    print("  summary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    bad = [r for r in results if r["status"] in ("BROKEN", "CRASHED")]
    if bad:
        print(f"\n  {len(bad)} DEFECT(S) FOUND:")
        for r in bad:
            print(f"    {r['skill']} on {r['shape']} ({r['rows']} rows): {r['status']}")
            for f in r.get("findings", []) or [r.get("detail", "")]:
                print(f"      {f[:120]}")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(results, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
