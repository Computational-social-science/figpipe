"""The scheduled re-check: generic, complete, and able to fail.

WHAT THE AUDIT CHANGED HERE
    The previous version had three defects (CRITICAL_AUDIT.md):

    1. It hard-coded checks for only 3 of 8 rules and still printed "3/3 hold" -- a healthy
       number over the wrong denominator. Now every rule carries a machine-executable `check`
       in the knowledge base, and this loop executes them generically. Coverage is 8/8 by
       construction, and a rule without a check is reported UNCHECKED rather than assumed
       passing.

    2. It could not fail. Any measurement error was swallowed into a dict and the process
       still exited 0. Now an unexecutable check, a failed assertion, or an unwritable
       knowledge base produces a non-zero exit, so the scheduler can see it.

    3. It called itself "autonomous evolution" while only ever measuring one hard-coded
       hypothesis. It is renamed to what it is: a scheduled compliance re-check. It re-verifies
       mechanisms and re-measures empirical rules; it does not discover new rules, and the
       README says so.

WHAT THIS DOES
    For each rule in the knowledge base:
      * run its `check` (rcparams / rcparams_range / symbol_exists / ink_density_band)
      * a rule whose check fails is DEMOTED to `regressed`
      * a rule whose check passes keeps its confidence
      * a rule with no check is recorded as UNCHECKED

    Demotion is sticky and visible: once a rule regresses, the next run reports it again until
    a human fixes it, rather than silently passing.
"""
from __future__ import annotations

import datetime
import importlib
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

KB = ROOT / "knowledge" / "layout_rules.json"
REPORT = ROOT / "knowledge" / "evolution_report.json"
FIGS = ROOT.parent / "keystroke-observatory" / "docs"


def _atomic_write(path: pathlib.Path, text: str) -> None:
    """Write via a temp file and os.replace, so a killed process cannot truncate it."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------- check runners

def _check_rcparams(spec: dict) -> tuple[bool, str]:
    import matplotlib.pyplot as plt
    bad = []
    for key, want in spec["assert"].items():
        got = plt.rcParams.get(key)
        if got != want:
            bad.append(f"{key}={got!r} (expected {want!r})")
    return (not bad), ("; ".join(bad) if bad else "all rcParams match")


def _check_rcparams_range(spec: dict) -> tuple[bool, str]:
    import matplotlib.pyplot as plt
    bad = []
    for key in spec["keys"]:
        raw = plt.rcParams.get(key)
        try:
            v = float(raw)
        except (TypeError, ValueError):
            bad.append(f"{key}={raw!r} is not an explicit number")
            continue
        if not (spec["min"] <= v <= spec["max"]):
            bad.append(f"{key}={v} outside [{spec['min']},{spec['max']}]")
    return (not bad), ("; ".join(bad) if bad else "all sizes in band")


def _check_symbol_exists(spec: dict) -> tuple[bool, str]:
    mod = importlib.import_module(spec["module"])
    ok = hasattr(mod, spec["symbol"])
    return ok, (f"{spec['module']}.{spec['symbol']} present" if ok
                else f"{spec['module']}.{spec['symbol']} MISSING")


def _check_ink_density_band(spec: dict) -> tuple[bool, str]:
    import numpy as np
    from PIL import Image
    figs = sorted(FIGS.glob("fig*.png")) if FIGS.is_dir() else []
    if not figs:
        return False, "no figures to measure (cannot confirm the band)"
    vals = {}
    for p in figs:
        a = np.array(Image.open(p).convert("L"), dtype=np.uint8)
        vals[p.name] = round(100 * float((a < 200).mean()), 2)
    outside = {k: v for k, v in vals.items()
               if not (spec["min_pct"] <= v <= spec["max_pct"])}
    if outside:
        return False, f"outside [{spec['min_pct']},{spec['max_pct']}]%: {outside}"
    lo, hi = min(vals.values()), max(vals.values())
    return True, f"all {len(vals)} figures within band (measured {lo}-{hi}%)"


def _check_composite_plate(spec: dict) -> tuple[bool, str]:
    """Compose a real four-panel plate and verify the properties the rule claims.

    A rule about multi-panel figures that is "verified" by `hasattr(composite, "composite")`
    would still pass with a composer that placed every panel on top of the others. This runs
    the mechanism and reads the finished figure back: the letters, the gutters, the page size.
    """
    import numpy as np
    import pandas as pd
    from figpipe import composite
    df = pd.DataFrame({"g": list("abcde"), "v": np.linspace(5, 25, 5),
                       "w": np.linspace(9, 30, 5)})
    panels = [
        composite.Panel("grouped_bars", df, {"x": "g", "ycols": ["v"], "legend": False}),
        composite.Panel("grouped_bars", df, {"x": "g", "ycols": ["w"], "legend": False}),
        composite.Panel("bar_with_errors", df, {"x": "g", "y": "v"}),
        composite.Panel("line_series", df, {"x": "g", "ycols": ["v", "w"], "legend": False}),
    ]
    f = composite.composite(panels, columns=2.0, height_mm=140.0)
    r = composite.inspect(f)
    problems = composite.check(f, r)
    if problems:
        return False, "; ".join(problems)
    return True, (f"{r['n_panels']} panels, letters "
                  f"{[lt['letter'] for lt in r['letters']]}, gaps x={r['gaps_x_mm']} "
                  f"y={r['gaps_y_mm']} mm, page {r['width_mm']}x{r['height_mm']} mm")


RUNNERS = {
    "rcparams": _check_rcparams,
    "rcparams_range": _check_rcparams_range,
    "symbol_exists": _check_symbol_exists,
    "ink_density_band": _check_ink_density_band,
    "composite_plate": _check_composite_plate,
}


def run_check(spec) -> tuple[bool, str]:
    if not spec:
        return None, "UNCHECKED: no machine-executable check defined for this rule"
    fn = RUNNERS.get(spec.get("kind"))
    if fn is None:
        return False, f"unknown check kind {spec.get('kind')!r}"
    return fn(spec)


# ---------------------------------------------------------------- main

def main() -> int:
    from figpipe import style
    style.apply()

    kb = json.loads(KB.read_text(encoding="utf-8"))
    results, demoted, hard_errors = {}, [], []

    for rule in kb["rules"]:
        rid = rule["id"]
        try:
            ok, detail = run_check(rule.get("check"))
        except Exception as e:                                   # noqa: BLE001
            ok, detail = False, f"check raised {type(e).__name__}: {e}"
            hard_errors.append(f"{rid}: {detail}")

        results[rid] = {"ok": ok, "detail": detail,
                        "confidence_before": rule["confidence"]}

        if ok is False:
            # Demote. Sticky: the next run reports it again until a human fixes it.
            if rule["confidence"] != "regressed":
                rule["confidence"] = "regressed"
                rule["regressed_on"] = datetime.date.today().isoformat()
            demoted.append(rid)

    checked = [r for r in results.values() if r["ok"] is not None]
    unchecked = [k for k, v in results.items() if v["ok"] is None]
    failed = [k for k, v in results.items() if v["ok"] is False]

    summary = {
        "rules_total": len(kb["rules"]),
        "checked": len(checked),
        "passed": sum(1 for v in checked if v["ok"]),
        "failed": len(failed),
        "unchecked": len(unchecked),
        "unchecked_ids": unchecked,
    }

    # DERIVE check_coverage FROM THE RULES, EVERY RUN.
    # It was previously written once by a one-shot migration and drifted: it claimed 8 rules
    # with a check while only 7 had one, in the same JSON whose last_check block said
    # unchecked: 4. Recomputed here so it cannot go stale again.
    from refresh_coverage import compute as _compute_coverage
    kb["check_coverage"] = _compute_coverage(kb["rules"])

    kb["version"] += 1 if demoted else 0
    if demoted:
        kb["updated"] = datetime.date.today().isoformat()
    kb["last_check"] = {
        "at": datetime.datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
    }
    _atomic_write(KB, json.dumps(kb, indent=2))

    report = {
        "run_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "knowledge_base_version": kb["version"],
        "results": results,
        "demoted": demoted,
        "summary": summary,
        "hard_errors": hard_errors,
        "ok": not failed and not hard_errors,
        "note": ("A rule with ok=null has no machine check and is NOT counted as passing. "
                 "The loop re-verifies and re-measures; it does not discover new rules."),
    }
    _atomic_write(REPORT, json.dumps(report, indent=2))

    print(f"  knowledge base -> v{kb['version']}")
    print(f"  checked {summary['checked']}/{summary['rules_total']} rules "
          f"({summary['unchecked']} unchecked)")
    print(f"  passed {summary['passed']}, failed {summary['failed']}")
    if unchecked:
        print(f"  UNCHECKED (not counted as passing): {unchecked}")
    if failed:
        print(f"  !! REGRESSED: {failed}")
        for rid in failed:
            print(f"     {rid}: {results[rid]['detail'][:110]}")
    if hard_errors:
        print(f"  !! HARD ERRORS: {hard_errors}")
    print(f"  wrote {REPORT.relative_to(ROOT)}")

    # ---- LEAN PASS ----------------------------------------------------------------
    # Runs after the verdict so slimming can never hide a regression.
    try:
        import slim as _slim
        before = _slim.measure()
        fat = _slim.tracked_regenerable()
        trimmed = _slim.trim_run_records()
        _slim.prune_scratch(apply=True)
        freed = _slim.purge_disk(apply=True)
        after = _slim.measure()
        report["lean"] = {
            "tracked_files_before": before["tracked_files"],
            "tracked_files_after": after["tracked_files"],
            "tracked_mb_before": before["tracked_mb"],
            "tracked_mb_after": after["tracked_mb"],
            "worktree_mb_before": before["worktree_mb"],
            "worktree_mb_after": after["worktree_mb"],
            "regenerable_still_tracked": {k: len(v) for k, v in fat.items()},
            "run_records_trimmed": len(trimmed),
            "disk_purged": freed,
        }
        _atomic_write(REPORT, json.dumps(report, indent=2))
        print(f"  lean: tracked {before['tracked_mb']} -> {after['tracked_mb']} MB, "
              f"worktree {before['worktree_mb']} -> {after['worktree_mb']} MB")
        if fat:
            print(f"  !! still tracking regenerable files: "
                  f"{ {k: len(v) for k, v in fat.items()} }")
        for line in freed:
            print(f"     freed {line}")
    except Exception as e:                                       # noqa: BLE001
        # Recorded, not raised: a slimming failure must not look like a rule regression.
        report["lean"] = {"error": f"{type(e).__name__}: {e}"}
        _atomic_write(REPORT, json.dumps(report, indent=2))
        print(f"  lean pass failed (recorded, not fatal): {type(e).__name__}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
