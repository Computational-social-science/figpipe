"""End-to-end evaluation on PlotTwin-Bench (FigMirror), the reference-style benchmark.

WHY THIS SCRIPT
    The user's requirement was an authoritative benchmark, not a self-made one. PlotTwin-Bench
    (FigMirror, arXiv 2608.28814, CC BY-NC 4.0) asks exactly what figpipe does: given a
    REFERENCE figure and a NEW dataset, produce a figure in the reference's style. This script is
    the harness: it fetches tasks from the dataset server (nothing is redistributed), profiles the
    official reference image, maps the task's chart type to one of our skills, renders TWO figures
    (default style vs reference style), and reports deterministic metrics.

WHAT IT DOES AND DOES NOT CLAIM
    * Reference images are raster, so the reference style is profiled with `from_image`:
      palette, aspect and ink density only. Type sizes are NOT available from pixels; the
      comparison renormalises over the shared components and reports which ones were used.
    * The official scorer's combined score needs a VLM component. This script does NOT run or
      imitate it; it reports deterministic style distance and format compliance, and labels them
      as such. Claiming the official score without running the official scorer would be fraud.
    * The dataset (images, target data) is cached under corpus/e2e/ which is gitignored because
      the licence is non-commercial; only the metric report is committed.

USAGE
    python scripts/bench_plottwin.py --limit 8
    python scripts/bench_plottwin.py --limit 12 --types Line,Distribution,Scatter
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import shutil
import sys
import tempfile
import urllib.request

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import decision, select, skills, styleprofile  # noqa: E402

API = ("https://datasets-server.huggingface.co/rows?dataset=figmirror%2FPlotTwin-Bench"
       "&config=bench&split=test&offset={offset}&length=1")
CACHE = ROOT / "corpus" / "e2e" / "cache"
IMAGES = ROOT / "corpus" / "e2e" / "images"
#: The task cache is an INTERMEDIATE (the licence forbids redistributing the data anyway), but it
#: lives in the worktree, which has a size budget. Keeping it bounded is the difference between a
#: cache and a leak: 60 tasks already cost 38 MB.
MAX_CACHE_MB = 40.0


def prune_cache() -> int:
    """Drop the oldest cached tasks when the cache exceeds its budget; return files removed."""
    files = sorted(CACHE.glob("*.json"), key=lambda f: f.stat().st_mtime)
    total = sum(f.stat().st_size for f in files)
    removed = 0
    while total > MAX_CACHE_MB * 1e6 and files:
        victim = files.pop(0)
        size = victim.stat().st_size
        victim.unlink(missing_ok=True)
        (IMAGES / f"{victim.stem}.png").unlink(missing_ok=True)
        total -= size
        removed += 1
    return removed
OUT = ROOT / "corpus" / "e2e" / "plottwin_report.json"


class MappingError(RuntimeError):
    """The task's target data has no supported reading. Recorded, never silently defaulted."""


#: Chart types with NO operator, and why. A task of one of these types is a CLASSIFIED failure:
#: it must not be routed to the decision service, because no choice among our skills could ever
#: be right, and a model asked anyway would be forced to pick a wrong one.
UNSUPPORTED_TYPES = {
    "3D": "no 3D operator; 3D rarely survives Nature print, so this is a deliberate exclusion",
    "Network/Tree": "no graph-layout operator yet (backlog: node-link layout, not a chart "
                    "encoding this library owns)",
}


def classify_failure(chart: str) -> str | None:
    """A reason code when the chart type is deliberately unsupported, else None."""
    return UNSUPPORTED_TYPES.get(chart)


def fetch_row(offset: int) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / f"{offset}.json"
    if cache.is_file():
        return json.loads(cache.read_text(encoding="utf-8"))
    req = urllib.request.Request(API.format(offset=offset),
                                 headers={"User-Agent": "figpipe-bench/0.1"})
    with urllib.request.urlopen(req, timeout=180) as r:
        payload = json.load(r)
    prune_cache()
    row = payload["rows"][0]["row"]
    keep = {"id": row.get("id"), "chart_type_name": row.get("chart_type_name"),
            "panel_mode": row.get("panel_mode"), "target_data": row.get("target_data"),
            "reference_url": (row.get("reference_image") or {}).get("src")}
    cache.write_text(json.dumps(keep), encoding="utf-8")
    return keep


def download_image(row: dict) -> pathlib.Path:
    IMAGES.mkdir(parents=True, exist_ok=True)
    p = IMAGES / f"{row['id']}.png"
    if p.is_file():
        return p
    req = urllib.request.Request(row["reference_url"],
                                 headers={"User-Agent": "figpipe-bench/0.1"})
    with urllib.request.urlopen(req, timeout=180) as r:
        p.write_bytes(r.read())
    return p


def crop_ink(src: pathlib.Path, dst: pathlib.Path) -> pathlib.Path:
    """Trim page-white margins so aspect/ink are compared on the figure, not the canvas."""
    from PIL import Image
    im = Image.open(src).convert("RGB")
    arr = np.asarray(im)
    mask = np.any(arr < 245, axis=2)
    if not mask.any():
        raise MappingError("reference image is blank")
    ys, xs = np.where(mask)
    im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)).save(dst)
    return dst


def _numeric(df: pd.DataFrame) -> list[str]:
    out = []
    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() >= 8 and s.nunique() > 1:
            df[c] = s
            out.append(c)
    return out


def _categorical(df: pd.DataFrame, nums: list[str]) -> list[str]:
    out = []
    for c in df.columns:
        if c in nums:
            continue
        n = df[c].nunique(dropna=True)
        if 2 <= n <= 10:
            out.append(c)
    return out


def _matrix_reading(df, nums, cats):
    usable = [c for c in nums if df[c].notna().mean() >= 0.25][:8]
    sub = df[usable].dropna() if usable else pd.DataFrame()
    if sub.shape[0] >= 2 and sub.shape[1] >= 2:
        return sub.head(40), f"matrix {len(usable)} measures"
    cat_cols = [c for c in cats if df[c].notna().mean() >= 0.5]
    if len(cat_cols) >= 2 and usable:
        piv = df.pivot_table(index=cat_cols[0], columns=cat_cols[1],
                             values=usable[0], aggfunc="mean")
        piv = piv.dropna(how="all").dropna(axis=1, how="all").fillna(0.0)
        if piv.shape[0] >= 2 and piv.shape[1] >= 2:
            return piv, f"pivot {cat_cols[0]} x {cat_cols[1]} of {usable[0]}"
    return None, ""


def _reading_from_skill(skill, df, nums, cats):
    """Build a skill's parameters from column roles. Caller still validates by rendering."""
    pref = next((c for c in cats
                 if any(k in c.lower() for k in ("condition", "group", "model", "category",
                                                 "class", "type", "treatment"))),
                cats[0] if cats else None)
    if skill == "histogram":
        params = {"value": nums[0]}
        if pref and df[pref].nunique() <= 6:
            params["group"] = pref
        return params, df, f"hist {nums[0]}"
    if skill == "faceted_distribution":
        facet = next((c for c in df.columns
                      if any(k in str(c).lower() for k in ("panel_group", "panel", "facet",
                                                           "condition"))
                      and 2 <= df[c].nunique() <= 4), None)
        if not facet:
            raise MappingError("faceted_distribution chosen but no 2-4 level facet column exists")
        return {"value": nums[0], "by": facet, "max_panels": 4}, df, f"faceted by {facet}"
    if skill == "distribution_comparison":
        if not pref:
            raise MappingError("distribution_comparison needs a categorical group")
        return {"group": pref, "value": nums[0]}, df, f"box {nums[0]} by {pref}"
    if skill == "scatter_relationship":
        if len(nums) < 2:
            raise MappingError("scatter needs two numeric measures")
        return {"x": nums[0], "y": nums[1]}, df, f"scatter {nums[0]} vs {nums[1]}"
    if skill == "trend_with_uncertainty":
        x = next((c for c in df.columns
                  if any(k in str(c).lower() for k in ("year", "time", "date", "month"))), nums[0])
        y = next(c for c in nums if c != x)
        return {"x": x, "y": y}, df, f"trend {x}->{y}"
    if skill == "grouped_measures":
        if not pref or len(nums) < 2:
            raise MappingError("grouped_measures needs a category and two measures")
        return {"x": pref, "ycols": nums[:3]}, df, f"bars {nums[:3]} by {pref}"
    if skill == "ranked_composition":
        if not pref:
            raise MappingError("ranked_composition needs a categorical axis")
        return {"label": pref, "value": nums[0]}, df, f"ranked {nums[0]} by {pref}"
    if skill == "error_comparison":
        label = next((c for c in cats if df[c].nunique() <= 20), None)
        if not label:
            raise MappingError("error_comparison needs a categorical axis")
        return {"x": label, "y": nums[0]}, df, f"bars {nums[0]} by {label}"
    if skill == "composite_groups":
        group = next((c for c in df.columns
                      if any(k in str(c).lower() for k in ("panel_group", "panel_block",
                                                           "block_id", "facet"))
                      and 2 <= df[c].nunique() <= 4), None)
        label = next((c for c in cats if c != group and df[c].nunique() <= 12), None)
        if not (group and label):
            raise MappingError("composite_groups needs a 2-4 level panel group and a category")
        return {"by": group, "x": label, "y": nums[0]}, df, f"composite {group} x {label}"
    if skill == "radial_profile":
        cat = next((c for c in cats if df[c].nunique() <= 12), None)
        if not cat:
            raise MappingError("radial_profile needs an angular category (<=12 levels)")
        return {"theta": cat, "value": nums[0]}, df, f"polar {nums[0]} by {cat}"
    if skill == "matrix_plate":
        data, why = _matrix_reading(df, nums, cats)
        if data is None:
            raise MappingError("matrix_plate chosen but no matrix or 2-category pivot exists")
        return {}, data, why
    raise MappingError(f"skill {skill!r} cannot be parameterised from this data")


def choose_reading(df: pd.DataFrame, chart: str, panel_mode: str):
    """Map one benchmark chart type to (skill, params, data, rationale)."""
    df = df.dropna(how="all").copy()
    df.columns = [str(c).strip() for c in df.columns]
    nums = _numeric(df)
    cats = _categorical(df, nums)
    if not nums:
        raise MappingError("no numeric measure in target data")
    pref = next((c for c in cats
                 if any(k in c.lower() for k in ("condition", "group", "model", "category",
                                                 "class", "type", "treatment"))),
                cats[0] if cats else None)

    def pick_x_y():
        x = next((c for c in df.columns
                  if any(k in str(c).lower() for k in ("year", "time", "date", "epoch",
                                                       "month", "day"))), nums[0])
        y = next((c for c in nums if c != x), nums[-1])
        return x, y

    if chart in ("Line", "Std-band"):
        x, y = pick_x_y()
        return "trend_with_uncertainty", {"x": x, "y": y}, df, f"trend {x}->{y}"
    if chart == "Distribution":
        if panel_mode == "multi":
            facet = next((c for c in df.columns
                          if any(k in str(c).lower() for k in ("panel_group", "panel",
                                                               "facet", "condition"))
                          and 2 <= df[c].nunique() <= 4), None)
            if facet:
                return ("faceted_distribution", {"value": nums[0], "by": facet,
                                                 "max_panels": 4}, df,
                        f"faceted hist by {facet}")
        group = pref if pref and df[pref].nunique() <= 6 else None
        params = {"value": nums[0]}
        if group:
            params["group"] = group
        return "histogram", params, df, f"hist {nums[0]}" + (f" by {group}" if group else "")
    if chart in ("Box/Violin",):
        if not pref:
            raise MappingError("box/violin needs a categorical group")
        return "distribution_comparison", {"group": pref, "value": nums[0]}, df, \
            f"box {nums[0]} by {pref}"
    if chart == "Scatter":
        if len(nums) < 2:
            raise MappingError("scatter needs two numeric measures")
        return "scatter_relationship", {"x": nums[0], "y": nums[1]}, df, \
            f"scatter {nums[0]} vs {nums[1]}"
    if chart == "Bar":
        if pref and len(nums) >= 2:
            return "grouped_measures", {"x": pref, "ycols": nums[:3]}, df, \
                f"grouped bars {nums[:3]} by {pref}"
        if pref:
            return "ranked_composition", {"label": pref, "value": nums[0]}, df, \
                f"ranked {nums[0]} by {pref}"
        raise MappingError("bar needs a categorical axis")
    if chart == "Composite":
        group = next((c for c in df.columns
                      if any(k in str(c).lower() for k in ("panel_group", "panel_block",
                                                           "block_id", "facet"))
                      and 2 <= df[c].nunique() <= 4), None)
        label = next((c for c in cats if c != group and df[c].nunique() <= 12), None)
        if group and label and nums:
            err = next((c for c in nums
                        if any(k in c.lower() for k in ("ci95_lower", "lower", "err"))), None)
            hi = next((c for c in nums
                       if any(k in c.lower() for k in ("ci95_upper", "upper"))), None)
            return "composite_groups", {"by": group, "x": label, "y": nums[0]}, df, \
                f"composite {group} x {label}"
        raise MappingError("composite task has no 2-4 level panel group with a categorical axis")
    if chart == "Polar/Radial":
        ang = next((c for c in cats if df[c].nunique() <= 12), None)
        if not ang:
            raise MappingError("polar/radial needs an angular category (<=12 levels)")
        return "radial_profile", {"theta": ang, "value": nums[0]}, df, \
            f"polar {nums[0]} by {ang}"
    if chart in ("Heatmap", "Field 2D"):
        data, why = _matrix_reading(df, nums, cats)
        if data is None:
            raise MappingError("heatmap target data has neither a numeric matrix nor a 2-category pivot")
        return "matrix_plate", {}, data, why
    raise MappingError(f"chart type {chart!r} has no operator yet (see knowledge/benchmark_skill_map.json)")


def run_task(row: dict, out_dir: pathlib.Path) -> dict:
    result = {"id": row["id"], "chart": row["chart_type_name"], "panel_mode": row["panel_mode"]}
    try:
        ref_img = crop_ink(download_image(row), out_dir / f"{row['id']}_ref.png")
        ref_profile = styleprofile.StyleProfile.from_image(ref_img)
        df = pd.read_csv(io.StringIO(row["target_data"]), low_memory=False)
        df.columns = [str(c).strip() for c in df.columns]
        decision_info = None
        try:
            skill, params, data, why = choose_reading(df, row["chart_type_name"], row["panel_mode"])
        except MappingError as map_exc:
            reason = classify_failure(row["chart_type_name"])
            if reason:
                result.update({"status": "unsupported", "error": f"unsupported chart type: "
                                                                  f"{reason}"})
                return result
            nums = _numeric(df)
            cats = _categorical(df, nums)
            try:
                decision_info = decision.choose_skill(
                    row["chart_type_name"], list(df.columns),
                    evidence={"panel_mode": row["panel_mode"],
                              "mapping_error": str(map_exc)})
            except (decision.DecisionUnavailable, decision.DecisionRejected) as dec_exc:
                result.update({"status": "error",
                               "error": f"mapping: {map_exc}; decision: {dec_exc}"})
                return result
            skill = decision_info["choice"]
            params, data, why = _reading_from_skill(skill, df, nums, cats)
        result.update({"skill": skill, "rationale": why, "rows_used": int(len(data))})
        if decision_info:
            result["decision"] = decision_info
        styled = skills.run(skill, data, out_stem=out_dir / f"{row['id']}_styled",
                            profile=ref_profile, **params)
        plain = skills.run(skill, data, out_stem=out_dir / f"{row['id']}_plain", **params)
        cand = styleprofile.StyleProfile.from_image(
            crop_ink(pathlib.Path(styled["png"]), out_dir / f"{row['id']}_styled_crop.png"))
        base = styleprofile.StyleProfile.from_image(
            crop_ink(pathlib.Path(plain["png"]), out_dir / f"{row['id']}_plain_crop.png"))
        d_styled = styleprofile.compare(ref_profile, cand)
        d_plain = styleprofile.compare(ref_profile, base)
        # DECIDE, don't always transfer. The reference is an input, so keeping the closer of
        # the two rendered pages is a legitimate inference-time decision -- and the measured data
        # say transfer hurts a minority of tasks, so always-transferring cannot be optimal.
        #
        # MEASUREMENT BASIS MATTERS: the benchmark's distances are raster-to-raster (the official
        # reference is a PNG, so the candidates are cropped PNGs too). Selecting on PDF profiles
        # while reporting PNG distances compares two different instruments -- the first attempt
        # did exactly that and reported a "shipped" mean 0.158 WORSE than always-styled, which is
        # impossible when the decision is a minimum of the same two numbers. Selection therefore
        # uses the same cropped PNGs the metric uses.
        picked = select.select(ref_profile, {
            "plain": pathlib.Path(plain["png"]),
            "styled": pathlib.Path(styled["png"]),
        })
        chosen_is_styled = picked["choice"] == "styled"
        result.update({
            "status": "ok",
            # the two measured candidates, unchanged, so the decision can be re-derived
            "distance": d_styled["distance"],
            "baseline_distance": d_plain["distance"],
            "delta": round(d_plain["distance"] - d_styled["distance"], 3),
            # what the pipeline would actually ship
            "selected": picked["choice"],
            "selected_distance": picked["distance"],
            "selected_gain": round(d_plain["distance"] - picked["distance"], 3),
            "selection_margin": picked["margin"],
            "components": d_styled["details"],
            "hard_failures": (styled if chosen_is_styled else plain)["hard_failures"],
            "findings": (styled if chosen_is_styled else plain)["findings"][:5],
        })
    except Exception as exc:                       # recorded, not hidden
        result.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return result


#: How many tasks make up the stable anchor metric.
ANCHOR_N = 20

#: The anchor's task ids, FROZEN on first creation. A "first N sorted ids" rule is not stable:
#: as new tasks are measured, ids that sort earlier enter the set and the anchor moves without
#: any capability change (observed: 0.297 -> 0.329 on a run that only added coverage). The list is
#: persisted so the anchor measures the SAME tasks forever.
ANCHOR_FILE = ROOT / "knowledge" / "benchmark_anchor.json"


def _selected_mean(tasks) -> float | None:
    """Mean distance of the pages the pipeline would SHIP (the closer of the two candidates)."""
    vals = [t["selected_distance"] for t in tasks
            if t.get("selected_distance") is not None]
    return round(float(np.mean(vals)), 3) if vals else None


def anchor_ids(tasks) -> list[str]:
    """The frozen anchor task ids, created from the first ANCHOR_N measured tasks if absent."""
    if ANCHOR_FILE.is_file():
        try:
            data = json.loads(ANCHOR_FILE.read_text(encoding="utf-8"))
            if data.get("ids"):
                return list(data["ids"])
        except (OSError, ValueError):
            pass
    ok = sorted((t for t in tasks if t.get("status") == "ok"), key=lambda t: str(t["id"]))
    ids = [t["id"] for t in ok[:ANCHOR_N]]
    if len(ids) >= 5:
        ANCHOR_FILE.parent.mkdir(parents=True, exist_ok=True)
        ANCHOR_FILE.write_text(json.dumps(
            {"ids": ids, "n": len(ids),
             "why": "frozen so the anchor measures the same tasks across runs"},
            indent=2) + "\n", encoding="utf-8")
    return ids


#: The shipped-figure metric needs its OWN frozen subset. The shipped mean is averaged over the
#: tasks that carry a selection decision, and that set GROWS as coverage advances -- so the mean
#: moves whenever a new task is added, which produced a false "regression" of 0.257 -> 0.258 on
#: 2026-10-19 (a 0.001 change with no capability change). Same defect family as the raw mean and
#: the sorted-id anchor; the fix is the same: freeze the ids.
SHIPPED_ANCHOR_FILE = ROOT / "knowledge" / "benchmark_shipped_anchor.json"


def shipped_anchor_ids(tasks) -> list[str]:
    """Frozen task ids for the shipped-figure metric, created once from the first decisions."""
    if SHIPPED_ANCHOR_FILE.is_file():
        try:
            data = json.loads(SHIPPED_ANCHOR_FILE.read_text(encoding="utf-8"))
            if data.get("ids"):
                return list(data["ids"])
        except (OSError, ValueError):
            pass
    ready = sorted((t for t in tasks
                    if t.get("selected_distance") is not None
                    and t.get("status") == "ok"), key=lambda t: str(t["id"]))
    ids = [t["id"] for t in ready[:ANCHOR_N]]
    if len(ids) >= 5:
        SHIPPED_ANCHOR_FILE.parent.mkdir(parents=True, exist_ok=True)
        SHIPPED_ANCHOR_FILE.write_text(json.dumps(
            {"ids": ids, "n": len(ids),
             "why": "frozen so the shipped-figure metric measures the same tasks across runs"},
            indent=2) + "\n", encoding="utf-8")
    return ids


def _shipped_anchor_distance(tasks) -> float | None:
    """Mean shipped distance over the FROZEN shipped subset."""
    ids = set(shipped_anchor_ids(tasks))
    vals = [t["selected_distance"] for t in tasks
            if t.get("id") in ids and t.get("selected_distance") is not None]
    return round(float(np.mean(vals)), 3) if len(vals) >= 5 else None


def _anchor_distance(tasks) -> float | None:
    """Mean style distance over the FROZEN anchor subset -- comparable across runs."""
    ids = set(anchor_ids(tasks))
    ok = [t for t in tasks
          if t.get("status") == "ok" and t.get("distance") is not None
          and t.get("id") in ids]
    if len(ok) < 5:
        return None
    return round(float(np.mean([t["distance"] for t in ok])), 3)


#: The benchmark pool size, used to walk every window before repeating one.
POOL = 150


def covered_offsets(report_path=None) -> set[int]:
    """Offsets whose task ids already appear in the report.

    WHY: the scheduled slice rotated by `(runs * tasks) % 120`, which re-measured windows that
    were already covered (run 43 landed on offset 12, whose tasks were measured hours earlier).
    A loop that keeps re-measuring the same tasks cannot advance coverage toward the full pool --
    it looks busy and grows nothing. Coverage is only honest when the slice walks forward.
    """
    path = pathlib.Path(report_path or OUT)
    if not path.is_file():
        return set()
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    ids = {t.get("id") for t in report.get("tasks", [])}
    covered = set()
    for off in range(POOL):
        cache = CACHE / f"{off}.json"
        if cache.is_file():
            try:
                row = json.loads(cache.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if row.get("id") in ids:
                covered.add(off)
    return covered


def next_uncovered_offset(tasks: int, report_path=None) -> int:
    """The first window that still contains an unmeasured task; wraps to 0 when done."""
    covered = covered_offsets(report_path)
    for off in range(0, POOL, tasks):
        if not all(o in covered for o in range(off, min(off + tasks, POOL))):
            return off
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--merge", action="store_true",
                    help="merge into the existing report instead of replacing it")
    ap.add_argument("--types", default="", help="comma list, e.g. Line,Distribution,Scatter")
    args = ap.parse_args(argv)
    wanted = {t.strip() for t in args.types.split(",") if t.strip()}
    # Rendered candidates are INTERMEDIATES, not artefacts: 30 tasks produce ~600 files and
    # ~60 MB, which alone blew the 150 MB worktree budget. They go to a system temp directory
    # that is removed at the end; the metric report (the actual deliverable) stays in the repo.
    out_dir = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-bench-"))
    tasks = []
    for off in range(args.offset, args.offset + args.limit):
        row = fetch_row(off)
        if wanted and row["chart_type_name"] not in wanted:
            continue
        tasks.append(row)
    print(f"  tasks fetched: {len(tasks)} (offset {args.offset}, limit {args.limit})")
    results = [run_task(row, out_dir) for row in tasks]
    ok = [r for r in results if r["status"] == "ok"]
    unsupported = [r for r in results if r["status"] == "unsupported"]
    errored = [r for r in results if r["status"] == "error"]
    deltas = [r["delta"] for r in ok]
    improved = sum(1 for d in deltas if d > 0.005)
    worse = sum(1 for d in deltas if d < -0.005)
    ties = len(deltas) - improved - worse
    by_type = {}
    for r in results:
        t = by_type.setdefault(r["chart"], {"n": 0, "ok": 0, "d": [], "base": [],
                                            "delta": [], "errors": []})
        t["n"] += 1
        if r["status"] == "ok":
            t["ok"] += 1
            t["d"].append(r["distance"])
            t["base"].append(r["baseline_distance"])
            t["delta"].append(r["delta"])
        else:
            t["errors"].append(r.get("error", "")[:80])
    def _shipped(rows):
        vals = [r["selected_distance"] for r in rows
                if r.get("selected_distance") is not None]
        return round(float(np.mean(vals)), 3) if vals else None

    type_stats = {}
    for chart, t in sorted(by_type.items()):
        type_stats[chart] = {
            "n": t["n"], "ok": t["ok"],
            "mean_distance": round(float(np.mean(t["d"])), 3) if t["d"] else None,
            "mean_baseline": round(float(np.mean(t["base"])), 3) if t["base"] else None,
            "mean_delta": round(float(np.mean(t["delta"])), 3) if t["delta"] else None,
            "mean_shipped": _shipped([r for r in results if r["chart"] == chart]),
            "errors": len(t["errors"]), "error_examples": t["errors"][:3],
        }
    report = {
        "benchmark": {"name": "PlotTwin-Bench", "license": "CC BY-NC 4.0",
                      "source": "figmirror/PlotTwin-Bench", "arxiv": "2608.28814",
                      "note": "deterministic metrics only; official combined score requires the "
                              "benchmark's VLM scorer and is NOT claimed here"},
        "n_tasks": len(results), "n_ok": len(ok),
        "n_unsupported": len(unsupported), "n_error": len(errored),
        "unsupported_types": {r["chart"]: r.get("error") for r in unsupported},
        "mean_distance": round(float(np.mean([r["distance"] for r in ok])), 3) if ok else None,
        "mean_baseline": round(float(np.mean([r["baseline_distance"] for r in ok])), 3) if ok else None,
        "mean_improvement": round(float(np.mean(deltas)), 3) if ok else None,
        "improved": improved, "worse": worse, "ties": ties,
        "mean_best_of_two": round(float(np.mean([min(r["distance"], r["baseline_distance"])
                                                 for r in ok])), 3) if ok else None,
        "decision_service": decision.health(),
        "by_type": type_stats,
        "failures": [{"id": r["id"], "chart": r["chart"], "error": r.get("error")}
                     for r in results if r["status"] != "ok"],
        "tasks": results,
    }
    if args.merge and OUT.is_file():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            old = {}
        seen = {t["id"] for t in report["tasks"]}
        merged = [t for t in old.get("tasks", []) if t.get("id") not in seen] + report["tasks"]
        ok_all = [t for t in merged if t.get("status") == "ok"]
        uns = [t for t in merged if t.get("status") == "unsupported"]
        report["tasks"] = merged
        report["n_tasks"] = len(merged)
        report["n_ok"] = len(ok_all)
        report["n_unsupported"] = len(uns)
        report["n_error"] = len(merged) - len(ok_all) - len(uns)
        if ok_all:
            report["mean_distance"] = round(float(np.mean([t["distance"] for t in ok_all])), 3)
            report["mean_baseline"] = round(float(np.mean([t["baseline_distance"] for t in ok_all])), 3)
            report["mean_improvement"] = round(float(np.mean([t["delta"] for t in ok_all])), 3)
            report["mean_best_of_two"] = round(float(np.mean([
                min(t["distance"], t["baseline_distance"]) for t in ok_all])), 3)
            report["improved"] = sum(1 for t in ok_all if t["delta"] > 0.005)
            report["worse"] = sum(1 for t in ok_all if t["delta"] < -0.005)
            report["ties"] = len(ok_all) - report["improved"] - report["worse"]
        by_type = {}
        for t in merged:
            bucket = by_type.setdefault(t["chart"], {"n": 0, "ok": 0, "d": [], "base": [],
                                                     "delta": [], "ship": [], "errors": 0})
            bucket["n"] += 1
            if t.get("status") == "ok":
                bucket["ok"] += 1
                bucket["d"].append(t["distance"])
                bucket["base"].append(t["baseline_distance"])
                bucket["delta"].append(t["delta"])
                if t.get("selected_distance") is not None:
                    bucket["ship"].append(t["selected_distance"])
            else:
                bucket["errors"] += 1
        report["by_type"] = {
            c: {"n": b["n"], "ok": b["ok"], "errors": b["errors"],
                "mean_distance": round(float(np.mean(b["d"])), 3) if b["d"] else None,
                "mean_baseline": round(float(np.mean(b["base"])), 3) if b["base"] else None,
                "mean_delta": round(float(np.mean(b["delta"])), 3) if b["delta"] else None,
                "mean_shipped": round(float(np.mean(b["ship"])), 3) if b["ship"] else None}
            for c, b in sorted(by_type.items())}
    # ANCHOR METRIC. The mean distance over a growing task set is NOT comparable across runs:
    # adding a harder window moves the mean without any change in capability, which made the
    # loop report a false regression on 2026-10-19 (0.278 over 30 tasks -> 0.302 over 66).
    # The anchor is the mean over the FIRST `ANCHOR_N` task ids in sorted order, which is stable
    # as long as those tasks stay in the report.
    report["benchmark_anchor_distance"] = _anchor_distance(report["tasks"])
    report["benchmark_shipped_anchor_distance"] = _shipped_anchor_distance(report["tasks"])
    # SELECTION IS MEASURED ON ITS OWN SUBSET. Only tasks rendered after the decision existed
    # carry `selected_distance`; averaging those against a mean over ALL tasks compares two
    # different task sets -- the exact defect this project has now fixed three times. Every
    # selection figure below is therefore computed over the SAME subset, and the always-styled /
    # plain means are recomputed on it so the comparison is like-for-like.
    sel_tasks = [t for t in report["tasks"] if t.get("selected_distance") is not None]
    if sel_tasks:
        report["selection"] = {
            "n": len(sel_tasks),
            "shipped_mean": round(float(np.mean([t["selected_distance"] for t in sel_tasks])), 3),
            "always_styled_mean": round(float(np.mean([t["distance"] for t in sel_tasks])), 3),
            "plain_mean": round(float(np.mean([t["baseline_distance"] for t in sel_tasks])), 3),
            "gain_vs_always_styled": round(float(np.mean([
                t["distance"] - t["selected_distance"] for t in sel_tasks])), 3),
            "gain_vs_plain": round(float(np.mean([
                t["baseline_distance"] - t["selected_distance"] for t in sel_tasks])), 3),
            "picked_styled": sum(1 for t in sel_tasks if t.get("selected") == "styled"),
            "picked_plain": sum(1 for t in sel_tasks if t.get("selected") == "plain"),
            "rule": "closer of plain/styled to the reference; the reference is an input",
        }
    else:
        report["selection"] = None
    report.pop("selected_mean_distance", None)
    report.pop("selected_gain", None)
    report.pop("selected_always_styled", None)
    report.pop("selected_always_plain", None)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    from figpipe import sources
    sources.assert_writable(out_dir)
    shutil.rmtree(out_dir, ignore_errors=True)
    print(f"  ok {len(ok)}/{len(results)}  mean distance {report['mean_distance']}  "
          f"baseline {report['mean_baseline']}  delta {report['mean_improvement']}")
    for chart, t in sorted(type_stats.items()):
        print(f"    type {chart:<14} ok {t['ok']}/{t['n']:<3} "
              f"d={t['mean_distance']} base={t['mean_baseline']} "
              f"delta={t['mean_delta']} errors={t['errors']}")
    for r in results:
        if r["status"] != "ok":
            print(f"    FAIL {r['id']:<12} {r['chart']:<12} {str(r.get('error'))[:100]}")
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
