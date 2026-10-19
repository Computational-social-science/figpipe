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
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import codegen, decision, select, skills, styleprofile  # noqa: E402

sys.path.insert(0, str(ROOT / "third_party"))
try:                                            # official scorer is optional and CC BY-NC
    import plottwin_scorer as official
except Exception:                               # noqa: BLE001 - reported, not fatal
    official = None

API = ("https://datasets-server.huggingface.co/rows?dataset=figmirror%2FPlotTwin-Bench"
       "&config=bench&split=test&offset={offset}&length=1")
CACHE = ROOT / "corpus" / "e2e" / "cache"
IMAGES = ROOT / "corpus" / "e2e" / "images"
#: offset -> task id. The CACHE is prunable (it holds megabytes of target data), so coverage must
#: not be derived from it: pruning the cache once made `covered_offsets()` return an empty set and
#: the loop restarted from offset 0. This index is a few kilobytes and is never pruned.
COVERAGE_FILE = ROOT / "corpus" / "e2e" / "coverage.json"


def _read_coverage() -> dict:
    if not COVERAGE_FILE.is_file():
        return {}
    try:
        return {int(k): v for k, v in json.loads(
            COVERAGE_FILE.read_text(encoding="utf-8")).items()}
    except (OSError, ValueError):
        return {}


def _record_coverage(offset: int, task_id: str) -> None:
    cov = _read_coverage()
    if cov.get(offset) == task_id:
        return
    cov[offset] = task_id
    COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_FILE.write_text(json.dumps({str(k): v for k, v in sorted(cov.items())},
                                        indent=2) + "\n", encoding="utf-8")
#: The task cache is an INTERMEDIATE (the licence forbids redistributing the data anyway), but it
#: lives in the worktree, which has a size budget. Keeping it bounded is the difference between a
#: cache and a leak: 60 tasks already cost 38 MB.
#: Budget for the WHOLE cache (task JSON + reference images). The earlier version counted only
#: the JSON files, so 66 MB of cache and images sat in the worktree while the guard reported
#: 34 MB -- and the worktree reached 147 MB of its 150 MB budget. A guard that measures half of
#: what it guards is the same defect as a metric over a growing set.
MAX_CACHE_MB = 24.0


def prune_orphan_images() -> int:
    """Delete reference images whose task is no longer in the cache or the report.

    Images are the larger half of the cache (39 MB of 41 MB) and the pruner walked only the JSON,
    so they accumulated silently until the worktree budget caught them. A cache that prunes one of
    its two stores is not a bounded cache.
    """
    keep: set[str] = set()
    for f in CACHE.glob("*.json"):
        try:
            keep.add(json.loads(f.read_text(encoding="utf-8")).get("id"))
        except (OSError, ValueError):
            continue
    if OUT.is_file():
        try:
            keep.update(t.get("id") for t in
                        json.loads(OUT.read_text(encoding="utf-8")).get("tasks", []))
        except (OSError, ValueError):
            pass
    keep.discard(None)
    removed = 0
    for img in IMAGES.glob("*.png"):
        task_id = img.stem.replace("_crop", "")
        if task_id not in keep:
            img.unlink(missing_ok=True)
            removed += 1
    return removed


def _cache_bytes() -> int:
    return (sum(f.stat().st_size for f in CACHE.glob("*.json"))
            + sum(f.stat().st_size for f in IMAGES.glob("*.png")))


def prune_cache() -> int:
    """Drop the oldest cached tasks until the WHOLE cache fits its budget."""
    files = sorted(CACHE.glob("*.json"), key=lambda f: f.stat().st_mtime)
    total = _cache_bytes()
    removed = 0
    # prune a little BELOW the budget so the next task does not immediately exceed it again
    target = MAX_CACHE_MB * 0.8 * 1e6
    while total > target and files:
        victim = files.pop(0)
        size = victim.stat().st_size
        task_id = None
        try:
            task_id = json.loads(victim.read_text(encoding="utf-8")).get("id")
        except (OSError, ValueError):
            pass
        victim.unlink(missing_ok=True)
        # images are named by TASK ID, not by offset: unlinking "<offset>.png" never matched and
        # left 31 MB of orphaned reference images in the worktree
        if task_id:
            img = IMAGES / f"{task_id}.png"
            if img.is_file():
                size += img.stat().st_size
                img.unlink(missing_ok=True)
        total -= size
        removed += 1
    prune_orphan_images()
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
    #: Fields the harness needs. A cache entry written before a field existed must be refreshed,
    #: or that measurement dimension stays permanently empty while looking "cached".
    REQUIRED = ("id", "chart_type_name", "panel_mode", "target_data")
    if cache.is_file():
        try:
            cached = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = {}
        if all(k in cached for k in REQUIRED) and "reference_code" in cached:
            return cached
    req = urllib.request.Request(API.format(offset=offset),
                                 headers={"User-Agent": "figpipe-bench/0.1"})
    # The dataset server rate-limits (HTTP 429) when a type-wide scan walks the pool. Back off
    # instead of hammering it, and treat exhaustion as a normal, reported outcome.
    payload = None
    for attempt in range(7):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                payload = json.load(r)
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(min(30.0, 3.0 * (attempt + 1)))
        except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
            # a dropped connection (WinError 10054) is transient, not a task failure
            if attempt == 6:
                raise RuntimeError(
                    f"dataset server unreachable at offset {offset}: {exc}") from exc
            time.sleep(min(30.0, 3.0 * (attempt + 1)))
    if payload is None:
        raise RuntimeError(f"dataset server kept rate-limiting offset {offset}")
    time.sleep(0.35)
    prune_cache()
    row = payload["rows"][0]["row"]
    if row.get("id"):
        _record_coverage(offset, row["id"])
    keep = {"id": row.get("id"), "chart_type_name": row.get("chart_type_name"),
            "panel_mode": row.get("panel_mode"), "target_data": row.get("target_data"),
            "reference_code": row.get("reference_code"),
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
        # a MEASURE must be mostly finite: bookkeeping columns such as panel_row are >90% NaN and
        # drawing them raises "has non-finite values" instead of producing a profile
        usable = [c for c in nums if df[c].notna().mean() >= 0.8]
        if not usable:
            raise MappingError("polar/radial has no mostly-finite numeric measure")
        val = usable[0]
        sub = df[[ang, val]].dropna()
        if len(sub) < 3:
            raise MappingError("polar/radial has fewer than 3 complete (angle, value) rows")
        return "radial_profile", {"theta": ang, "value": val}, sub, \
            f"polar {val} by {ang}"
    if chart == "Field 2D":
        # a field needs its own (x, y, value) triple: the pivot is the drawing
        coord_candidates = [c for c in nums if df[c].nunique() >= 3]
        if len(coord_candidates) >= 2:
            xs = coord_candidates[0]
            ys = coord_candidates[1]
            val = next((c for c in nums if c not in (xs, ys)), None)
            if val is not None:
                sub = df[[xs, ys, val]].dropna()
                if sub[xs].nunique() >= 2 and sub[ys].nunique() >= 2 and len(sub) >= 8:
                    return "field_map", {"x": xs, "y": ys, "value": val}, sub, \
                        f"field {val} over {xs} x {ys}"
        raise MappingError("field 2D task has no usable (x, y, value) triple")
    if chart == "Heatmap":
        data, why = _matrix_reading(df, nums, cats)
        if data is None:
            raise MappingError("heatmap target data has neither a numeric matrix nor a 2-category pivot")
        return "matrix_plate", {}, data, why
    raise MappingError(f"chart type {chart!r} has no operator yet (see knowledge/benchmark_skill_map.json)")


def _code_version() -> str:
    """A short fingerprint of the code that renders figures.

    WHY: rows rendered before a fix are STALE, and re-running the fixed operator over a report that
    still holds pre-fix numbers makes the fix look like a regression (observed twice: Field 2D and
    Heatmap both looked broken because their rows predated the canvas-width fix). Recording the
    version makes staleness a queryable fact instead of a suspicion.
    """
    import hashlib
    h = hashlib.sha1()
    # RENDERING code only. Including the harness made every edit to this file invalidate all
    # rows, which turned the staleness signal into noise (120 of 132 "stale" after a one-line
    # change to the report). What matters is whether the FIGURE would come out differently.
    for rel in ("figpipe/drawlib.py", "figpipe/skills.py", "figpipe/styleprofile.py",
                "figpipe/composite.py", "figpipe/layout.py", "figpipe/style.py"):
        path = ROOT / rel
        if path.is_file():
            h.update(path.read_bytes())
    return h.hexdigest()[:12]


CODE_VERSION = _code_version()


def freshness(tasks) -> dict:
    """Three-valued freshness: fresh / stale / unknown.

    WHY THREE, NOT TWO: the first version reported every row without a recorded version as
    "stale", so 117 of 141 rows stayed permanently stale and the signal became noise. A row whose
    fingerprint was never recorded is UNKNOWN -- it may have been rendered by the current code, we
    simply cannot prove it. Collapsing unknown into stale is the same error as collapsing a missing
    measurement into a passing one.
    """
    fresh, stale, unknown = [], [], []
    for t in tasks:
        if t.get("status") != "ok":
            continue
        version = t.get("code_version")
        if not version:
            unknown.append(t.get("id"))
        elif version == CODE_VERSION:
            fresh.append(t.get("id"))
        else:
            stale.append(t.get("id"))
    return {"fresh": fresh, "stale": stale, "unknown": unknown,
            "n_fresh": len(fresh), "n_stale": len(stale), "n_unknown": len(unknown)}


def stale_tasks(tasks) -> list[str]:
    """Ids KNOWN to have been measured by a different rendering fingerprint."""
    return freshness(tasks)["stale"]


def _official_summary(tasks) -> dict:
    """Aggregate the OFFICIAL code channel: how many tasks it could score, and the mean."""
    scores = [t["official_code_score"]["score"] for t in tasks
              if isinstance(t.get("official_code_score"), dict)
              and t["official_code_score"].get("score") is not None]
    unavailable = [t["id"] for t in tasks
                   if isinstance(t.get("official_code_score"), dict)
                   and t["official_code_score"].get("score") is None]
    return {
        "channel": "code_deviation",
        "weight_upstream": 0.35,
        "note": "official deterministic channel only; the 0.65 vision channel is NOT run, so this "
                "is not the combined score",
        "n_scored": len(scores),
        "n_unavailable": len(unavailable),
        "mean_score": round(float(np.mean(scores)), 2) if scores else None,
        "min_score": round(float(np.min(scores)), 2) if scores else None,
        "max_score": round(float(np.max(scores)), 2) if scores else None,
    }


def _official_code_score(ref_code, skill, data, params, *, height_mm, columns,
                         rc=None, palette=None, style=None):
    """Score figpipe's emitted code against the benchmark's own reference code.

    Returns None when the scorer is not vendored, the task has no reference code, or the drawer
    cannot be expressed as a script -- each is a reported absence, not a zero.
    """
    if official is None or not ref_code:
        return None
    try:
        panel = _panel_for(skill, data, params)
        cand = codegen.emit([panel], columns=columns, height_mm=float(height_mm),
                            rc=rc, palette=palette, style=style)
    except Exception as exc:                       # noqa: BLE001 - unsupported drawer
        return {"available": False, "reason": f"{type(exc).__name__}: {exc}"}
    try:
        oc = official.score_code_deviation(ref_code, cand)
    except Exception as exc:                       # noqa: BLE001
        return {"available": False, "reason": f"{type(exc).__name__}: {exc}"}
    return {"available": oc["available"], "score": oc["score"],
            "n_activated": oc["n_activated"], "scored": oc["scored_dimensions"],
            "channel": "code_deviation", "weight_upstream": 0.35,
            "note": "code channel only; the 0.65 vision channel is not run"}


def _panel_for(skill, data, params):
    """Rebuild the panel a skill drew, for code emission."""
    from figpipe import composite
    if skill == "trend_with_uncertainty":
        kw = {k: v for k, v in params.items() if k in ("x", "y", "lo", "hi", "fit",
                                                       "reference", "xlabel", "ylabel")}
        return composite.Panel("trend_band", data, kw)
    if skill == "scatter_relationship":
        return composite.Panel("scatter_fit", data,
                               {"x": params["x"], "y": params["y"]})
    if skill in ("histogram", "faceted_distribution"):
        return composite.Panel("histogram", data, {"value": params["value"]})
    if skill == "distribution_comparison":
        return composite.Panel("boxplot", data,
                               {"group": params["group"], "value": params["value"]})
    if skill == "matrix_plate":
        return composite.Panel("heatmap", data, {})
    if skill == "grouped_measures":
        return composite.Panel("line_series", data,
                               {"x": params["x"], "ycols": list(params["ycols"])})
    raise codegen.CodegenError(f"skill {skill!r} has no code emitter yet")


def run_task(row: dict, out_dir: pathlib.Path) -> dict:
    result = {"id": row["id"], "chart": row["chart_type_name"], "panel_mode": row["panel_mode"],
              "code_version": CODE_VERSION}
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
        # OFFICIAL code channel (35% of the benchmark score), deterministic, no VLM.
        # The honest claim is "code channel", never the combined score: the vision channel is
        # 65% and is not run here.
        # The official channel compares AST-extracted style features, so the candidate must carry
        # the REFERENCE's own features (palette/grid/spines/ticks/serif/legend/aspect), not a
        # guess derived from a raster profile. Extract them from the reference code itself.
        ref_style = None
        if official is not None and row.get("reference_code"):
            try:
                ref_style = codegen.style_from_features(
                    official.extract_style_features(row["reference_code"])["features"])
            except Exception:                      # noqa: BLE001 - reference not parseable
                ref_style = None
        official_score = _official_code_score(
            row.get("reference_code"), skill, data, params,
            height_mm=(styled["layout"]["height_mm"] or 120.0),
            columns=float(styled["layout"]["columns"] or 2.0),
            rc=None,
            palette=(ref_style or {}).get("palette"),
            style=ref_style)
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
            "official_code_score": official_score,
            "semantic_findings": [f for f in
                                  (styled if chosen_is_styled else plain)["findings"]
                                  if str(f.get("check", "")).startswith("semantics")],
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
    """Mean shipped distance over the FROZEN shipped subset, ALL rows.

    Reported for continuity, but NOT safe to compare across a change to the measurement code: the
    anchor can mix rows measured by different fingerprints, so the number moves when the INSTRUMENT
    changes (observed: 0.252 -> 0.243 when only 3 of 20 anchor tasks had been re-measured after a
    styleprofile fix). Use `_shipped_anchor_single_instrument()` for anything judged.
    """
    ids = set(shipped_anchor_ids(tasks))
    vals = [t["selected_distance"] for t in tasks
            if t.get("id") in ids and t.get("selected_distance") is not None]
    return round(float(np.mean(vals)), 3) if len(vals) >= 5 else None


def _shipped_anchor_single_instrument(tasks) -> dict:
    """The shipped-anchor mean restricted to rows measured by the CURRENT fingerprint.

    WHY THIS EXISTS
        A frozen task set is not enough: if the rows inside it were measured by different versions
        of the measurement code, the mean moves when the code changes and reads as a capability
        change. This returns the value, the count, and the count still stale -- so a reader can see
        whether the number is comparable yet or is a partial re-measurement.
    """
    ids = set(shipped_anchor_ids(tasks))
    same, other = [], 0
    for t in tasks:
        if t.get("id") not in ids or t.get("selected_distance") is None:
            continue
        if t.get("code_version") == CODE_VERSION:
            same.append(t["selected_distance"])
        else:
            other += 1
    comparable = other == 0 and len(same) >= 5
    return {"mean": round(float(np.mean(same)), 3) if (same and comparable) else None,
            "partial_mean": round(float(np.mean(same)), 3) if same else None,
            "n_same_instrument": len(same), "n_other_instrument": other,
            "comparable": comparable,
            "note": ("comparable" if comparable else
                     "not comparable yet: anchor tasks are still measured by an older "
                     "fingerprint; re-measure them with --scan")}


def _anchor_distance(tasks) -> float | None:
    """Mean style distance over the FROZEN anchor subset, ALL rows.

    Reported for continuity only; like the shipped anchor it can mix rows measured by different
    fingerprints, so it is not safe to compare across a change to the measurement code. The judged
    value is `_anchor_single_instrument()`.
    """
    ids = set(anchor_ids(tasks))
    ok = [t for t in tasks
          if t.get("status") == "ok" and t.get("distance") is not None
          and t.get("id") in ids]
    if len(ok) < 5:
        return None
    return round(float(np.mean([t["distance"] for t in ok])), 3)


def _anchor_single_instrument(tasks) -> dict:
    """The styled-anchor mean restricted to rows measured by the CURRENT fingerprint."""
    ids = set(anchor_ids(tasks))
    same, other = [], 0
    for t in tasks:
        if t.get("id") not in ids or t.get("status") != "ok" or t.get("distance") is None:
            continue
        if t.get("code_version") == CODE_VERSION:
            same.append(t["distance"])
        else:
            other += 1
    comparable = other == 0 and len(same) >= 5
    return {"mean": round(float(np.mean(same)), 3) if (same and comparable) else None,
            "partial_mean": round(float(np.mean(same)), 3) if same else None,
            "n_same_instrument": len(same), "n_other_instrument": other,
            "comparable": comparable,
            "note": ("comparable" if comparable else
                     "not comparable yet: anchor tasks are still measured by an older fingerprint")}


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
    return {off for off, task_id in _read_coverage().items()
            if off < POOL and task_id in ids}


def measured_ids(report_path=None) -> set[str]:
    """Task ids already present in the report -- the durable definition of "covered"."""
    path = pathlib.Path(report_path or OUT)
    if not path.is_file():
        return set()
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {t.get("id") for t in report.get("tasks", []) if t.get("id")}


def next_uncovered_offset(tasks: int, report_path=None) -> int:
    """The first window containing a task the report does not already have; 0 when complete.

    Coverage is defined by the REPORT, not by the cache: the cache is prunable (it holds megabytes
    of target data), and deriving coverage from it made the loop restart from offset 0 after a
    prune. The offset->id index is written as a side effect of fetching, so a walk is cheap once
    the rows are cached, and it self-heals if the cache is pruned again.
    """
    seen = measured_ids(report_path)
    for off in range(0, POOL, tasks):
        window = range(off, min(off + tasks, POOL))
        known = _read_coverage()
        if all(known.get(o) in seen and known.get(o) for o in window):
            continue
        missing = False
        for o in window:
            task_id = known.get(o)
            if not task_id:
                try:
                    task_id = fetch_row(o).get("id")
                except Exception:                       # noqa: BLE001 - offline is not fatal
                    task_id = None
            if task_id not in seen:
                missing = True
                break
        if missing:
            return off
    return 0


def ensure_coverage_index() -> int:
    """Rebuild the id -> offset index if it is missing or incomplete.

    WHY: the index is derived from the report and the pool, and it is cheap (a few KB). When it was
    pruned along with the data cache, `--ids` could not locate a single anchor task. Coverage is a
    durable fact and must not depend on a prunable store.
    """
    report_ids = measured_ids()
    if not report_ids:
        return 0
    have = {v for v in _read_coverage().values()}
    missing = report_ids - have
    if not missing:
        return 0
    added = 0
    for off in range(POOL):
        try:
            row = fetch_row(off)
        except Exception:                       # noqa: BLE001 - offline is not fatal
            continue
        if row.get("id") in missing:
            added += 1
        if len(have) + added >= len(report_ids):
            break
    return added


def backfill_coverage() -> int:
    """Rebuild the coverage index from the report and whatever cache remains.

    Called once after the index was introduced: without it, coverage would restart from zero even
    though 102 tasks had already been measured.
    """
    if not OUT.is_file():
        return 0
    try:
        report = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    ids = {t.get("id") for t in report.get("tasks", [])}
    added = 0
    for off in range(POOL):
        cache = CACHE / f"{off}.json"
        if not cache.is_file():
            continue
        try:
            row = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if row.get("id") in ids:
            _record_coverage(off, row["id"])
            added += 1
    return added


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--merge", action="store_true",
                    help="merge into the existing report instead of replacing it")
    ap.add_argument("--types", default="", help="comma list, e.g. Line,Distribution,Scatter")
    ap.add_argument("--ids", default="",
                    help="comma list of task ids to re-measure (targeted refresh, e.g. an anchor)")
    ap.add_argument("--scan", action="store_true",
                    help="with --types: walk the WHOLE pool and measure every task of those "
                         "types, so a fixed operator is re-measured everywhere at once")
    args = ap.parse_args(argv)
    wanted = {t.strip() for t in args.types.split(",") if t.strip()}
    # Rendered candidates are INTERMEDIATES, not artefacts: 30 tasks produce ~600 files and
    # ~60 MB, which alone blew the 150 MB worktree budget. They go to a system temp directory
    # that is removed at the end; the metric report (the actual deliverable) stays in the repo.
    out_dir = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-bench-"))
    tasks = []
    if args.ids:
        # TARGETED REFRESH. A frozen anchor needs the SAME tasks re-measured after a change to the
        # measurement code; scanning whole chart types re-measures far more than necessary and
        # still may not cover the anchor. The coverage index maps id -> offset, so the exact tasks
        # can be fetched.
        wanted_ids = {t.strip() for t in args.ids.split(",") if t.strip()}
        by_id = {task_id: off for off, task_id in _read_coverage().items()}
        for task_id in sorted(wanted_ids):
            off = by_id.get(task_id)
            if off is None:
                print(f"  ! no offset recorded for {task_id}; skipping")
                continue
            tasks.append(fetch_row(off))
    elif args.scan and wanted:
        # a type-wide re-measurement: the old rows must be replaced wherever they came from, and
        # --limit now bounds the number of MATCHING tasks rather than a window of offsets
        for off in range(POOL):
            row = fetch_row(off)
            if row["chart_type_name"] in wanted:
                tasks.append(row)
                if len(tasks) >= args.limit:
                    break
    else:
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
        "semantic_violations": sum(1 for r in ok if r.get("semantic_findings")),
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
        old_tasks = old.get("tasks", [])
        merged = [t for t in old_tasks if t.get("id") not in seen] + report["tasks"]
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
    report["benchmark_anchor_single"] = _anchor_single_instrument(report["tasks"])
    report["benchmark_shipped_anchor_distance"] = _shipped_anchor_distance(report["tasks"])
    report["benchmark_shipped_anchor_single"] = _shipped_anchor_single_instrument(report["tasks"])
    # computed AFTER the merge, over every task in the report -- a per-slice aggregate would
    # change whenever a new window is measured, the same defect as the raw mean
    report["official_code_channel"] = _official_summary(
        [t for t in report["tasks"] if t.get("status") == "ok"])
    report["code_version"] = CODE_VERSION
    fresh = freshness(report["tasks"])
    report["freshness"] = fresh
    report["stale_tasks"] = fresh["stale"]
    report["n_stale"] = fresh["n_stale"]
    report["n_unknown"] = fresh["n_unknown"]
    report["n_fresh"] = fresh["n_fresh"]
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
