"""Prove a fix was LOAD-BEARING by reverting it and measuring.

WHY THIS EXISTS
    The project has made many fixes. It has never measured whether any of them mattered. A fix that
    changes no metric is either (a) a fix for a defect this benchmark does not exercise, or (b) not
    a fix. Both are worth knowing, and neither can be learned by reading the diff.

    `patchprobe` can revert a declared fix for the duration of one measurement. This script does
    exactly that: measure the anchor with the fix, revert, measure again, restore. The difference is
    the fix's contribution.

WHAT IT REPORTS
    For each declared fix:
      state        fix / revert / stale (see proposals.patch_state)
      with_fix     the anchor measured as the tree stands
      without_fix  the anchor measured with the fix reverted
      delta        without - with, so a POSITIVE delta means the fix improved the metric

    A fix whose delta is ~0 is reported as NOT LOAD-BEARING. That is a result, not a failure: it says
    the benchmark does not exercise the defect, which is itself worth recording.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def _anchor() -> float | None:
    """The styled anchor from the current report, or None."""
    try:
        report = json.loads((ROOT / "corpus" / "e2e" / "plottwin_report.json")
                            .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    block = report.get("benchmark_anchor_single") or {}
    return block.get("mean")


def _hard_findings() -> int | None:
    """Total hard findings across the pool, or None.

    THE ANCHOR IS THE WRONG INSTRUMENT FOR "was this fix load-bearing". A 20-task slice re-measured
    by a different instrument leaves the anchor incomplete BY DESIGN, so it refuses to report a mean
    and `without_fix` came back None on the first run. The question is whether the DEFECT the fix
    addressed comes back -- that is a count of hard findings, which is the signal the fix was
    written against.
    """
    try:
        report = json.loads((ROOT / "corpus" / "e2e" / "plottwin_report.json")
                            .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return sum(int(t.get("hard_failures") or 0) for t in (report.get("tasks") or []))


#: Which skill's tasks a fix must be probed on.
#:
#: A fix that changes a drawer can only show up on tasks that drawer produced. Measuring the first
#: 20 pool rows is a fact about the slice, not about the fix -- and it made the polar label wrap look
#: inert because only one of the 12 radial tasks is in the anchor set.
FIX_SKILL = {
    "polar_label_overflow": "radial_profile",
    "polar_wrap_width": "radial_profile",
    "matrix_label_width": "matrix_plate",
    "matrix_row_budget": "matrix_plate",
    "colorbar_label_room": "field_map",
}


def _tasks_for_skill(skill: str) -> list[str]:
    """Every pool task id whose skill is `skill`."""
    try:
        report = json.loads((ROOT / "corpus" / "e2e" / "plottwin_report.json")
                            .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [str(t.get("id")) for t in (report.get("tasks") or []) if t.get("skill") == skill]


def _measure_slice(n: int = 20, *, skill: str | None = None) -> dict:
    """Re-measure the tasks a fix could affect.

    With `skill`, the slice is EVERY pool task that skill produced, addressed by id. Without it the
    first `n` rows are measured, which is only right for a fix with no particular target.
    """
    import subprocess

    ids = _tasks_for_skill(skill) if skill else []
    if ids:
        cmd = [sys.executable, str(ROOT / "scripts" / "bench_plottwin.py"),
               "--ids", ",".join(ids), "--merge", "--no-lock"]
    else:
        cmd = [sys.executable, str(ROOT / "scripts" / "bench_plottwin.py"),
               "--limit", str(n), "--offset", "0", "--merge", "--no-lock"]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return {"ok": p.returncode == 0, "n_ids": len(ids),
            "tail": ((p.stdout or "") + (p.stderr or ""))[-300:]}


def main(argv=None) -> int:
    from figpipe import patchprobe, proposals

    only = None
    if argv and "--fix" in argv:
        only = argv[argv.index("--fix") + 1]

    catalog = proposals.CODE_PATCHES
    if only:
        catalog = {k: v for k, v in catalog.items() if k == only}
    if not catalog:
        print(f"  no declared fix matches {only!r}")
        return 2

    results = []
    for key, (path, old, new, rationale) in catalog.items():
        entry = {"fix": key, "path": path, "rationale": rationale}
        patch_dict = {"id": key, "path": path, "old": old, "new": new, "rationale": rationale}
        state = proposals.patch_state(ROOT, patch_dict)
        entry["state"] = state["state"]
        if state["state"] != "revert":
            # only a revert can measure a fix that is already in the tree
            entry["measured"] = False
            entry["why"] = (f"state is {state['state']}, so there is no fix in the tree to revert "
                            f"and no contribution to measure")
            results.append(entry)
            continue

        base = _anchor()
        base_hard = _hard_findings()
        entry["with_fix"] = base
        entry["with_fix_hard_findings"] = base_hard

        revert = patchprobe.Patch(**{k: patch_dict[k] for k in
                                     ("id", "path", "old", "new", "rationale")})
        revert = patchprobe.Patch(id=key + "-revert", path=path, old=new, new=old,
                                  rationale="reintroduce the defect")
        try:
            skill = FIX_SKILL.get(key)
            patchprobe.probe_with_patch(
                ROOT, revert, lambda: _measure_slice(20, skill=skill))
        except patchprobe.PatchError as exc:
            entry["measured"] = False
            entry["why"] = f"the revert could not be applied: {exc}"
            results.append(entry)
            continue
        after = _anchor()
        after_hard = _hard_findings()
        entry["without_fix"] = after
        entry["without_fix_hard_findings"] = after_hard
        entry["measured"] = True
        if base_hard is not None and after_hard is not None:
            entry["delta_hard_findings"] = after_hard - base_hard
            # LOAD-BEARING MEANS THE DEFECT COMES BACK. A fix whose revert adds findings was
            # doing something; one whose revert changes nothing is unexercised by this benchmark.
            entry["load_bearing"] = entry["delta_hard_findings"] > 0
        else:
            entry["delta_hard_findings"] = None
            entry["load_bearing"] = None
        if base is not None and after is not None:
            entry["delta_anchor"] = round(after - base, 4)
        # the slice has now been measured with the defect present; re-measure with the fix so the
        # report is left describing the tree as it stands
        _measure_slice(20, skill=skill)
        entry["restored_anchor"] = _anchor()
        entry["probed_skill"] = skill
        entry["probed_tasks"] = len(_tasks_for_skill(skill)) if skill else None
        results.append(entry)

    out = {"fixes": results, "n": len(results),
           "n_measured": sum(1 for r in results if r.get("measured")),
           "n_load_bearing": sum(1 for r in results if r.get("load_bearing") is True)}
    path = ROOT / "corpus" / "e2e" / "fix_contribution.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    for r in results:
        if r.get("measured"):
            print(f"  {r['fix']:<26} with={r['with_fix']} without={r['without_fix']} "
                  f"delta={r.get('delta')} load_bearing={r.get('load_bearing')}")
        else:
            print(f"  {r['fix']:<26} not measured: {r.get('why','')[:70]}")
    print(f"\n  wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
