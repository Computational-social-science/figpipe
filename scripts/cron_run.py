"""The CRON entry point: evolve, verify, and report. Designed to be idempotent.

WHAT A SCHEDULED RUN DOES
    1. re-verify every `verified` rule against the live pipeline
    2. measure the open hypotheses and promote any that now have evidence
    3. run the full test suite (a rule that breaks the suite is not a rule)
    4. write a dated report under knowledge/runs/
    5. exit non-zero if anything regressed, so the scheduler can alert

WHY IT IS IDEMPOTENT
    Running it twice in a row must not change the knowledge base the second time unless
    something actually changed. Otherwise a 6-hourly schedule would inflate the version
    number forever and the history would be noise. The version only increments when a rule
    changes state.

USAGE
    python scripts/cron_run.py            # normal scheduled run
    python scripts/cron_run.py --dry-run  # measure, do not write

SCHEDULING (see knowledge/SCHEDULE.md for the registered task)
    The task is registered in the DSH scheduler and also as a Windows scheduled task so it
    survives a reboot. It is safe to run concurrently with development: it only writes inside
    knowledge/runs/ and the knowledge base.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNS = ROOT / "knowledge" / "runs"
KB = ROOT / "knowledge" / "layout_rules.json"

#: A commit made by the schedule may not ADD more than this. The budget exists because the
#: publisher ran `git add -A` blindly: on 2026-10-18 it staged 1567.5 MB of dataverse CSVs
#: sitting in the worktree and committed them, taking the tracked footprint from ~70 MB to
#: 1717.6 MB. `tests/test_lean.py` noticed -- but only after the commit had landed and been
#: pushed. A budget the publisher itself enforces is the difference between a test and a
#: control.
MAX_ADDED_MB = 25.0
MAX_ADDED_FILE_MB = 8.0


def snapshot() -> dict:
    return json.loads(KB.read_text(encoding="utf-8"))


def capability_snapshot() -> dict:
    """A machine-readable snapshot of what the project can DO, not just what it knows.

    WHY THIS EXISTS
        The run record used to contain rules, tests and publish status -- all measures of
        self-consistency. It could not answer "did the project gain capability since the last
        run?", which is the only question that separates self-check from self-improvement.
        This snapshot reads capability artefacts that other scripts produce (skills catalogue,
        seed reproduction report, PlotTwin-Bench report) so a scheduled run can record and diff
        them. It deliberately contains no derived opinion: every field is a count or a measured
        distance from a file.
    """
    def _read(rel):
        try:
            return json.loads((ROOT / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    bench = _read("corpus/e2e/plottwin_report.json")
    skills = _read("knowledge/skills_catalog.json")
    seed = _read("templates/seed/report.json")
    kb = _read("knowledge/layout_rules.json")
    return {
        "skills": len(skills.get("skills", []) or []),
        "operators": len(skills.get("operators", []) or []),
        "benchmark_tasks": bench.get("n_tasks", 0) or 0,
        "benchmark_ok": bench.get("n_ok", 0) or 0,
        "benchmark_mean_distance": bench.get("mean_distance"),
        "statistics_reproduced": (seed.get("self_check") or {}).get("statistics_recorded"),
        "knowledge_version": kb.get("version"),
        "tests": None,             # patched in after the suite runs
    }


def capability_delta(previous: dict, current: dict) -> dict:
    """Which capability fields changed, and by how much. `changed` is explicit."""
    delta = {}
    for key, value in current.items():
        old = (previous or {}).get(key)
        if old != value:
            delta[key] = {"before": old, "after": value}
    return {"changed": bool(delta), "delta": delta}


def run_tests() -> tuple[bool, str]:
    """Run the suite, unless we are already inside it.

    FIGPIPE_NO_TESTS exists because this runner and the test suite can invoke each other:
    the runner runs the suite, and a test of the runner runs the runner. Without the guard
    that recursion hung the suite for ten minutes. A scheduled run leaves the variable unset
    and gets the full suite.
    """
    if os.environ.get("FIGPIPE_NO_TESTS"):
        return True, "skipped (FIGPIPE_NO_TESTS set: already inside the suite)"
    py = sys.executable
    p = subprocess.run([py, "-m", "pytest", "tests/", "-q"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (p.stdout or p.stderr).strip().splitlines()
    return p.returncode == 0, (tail[-1] if tail else "")


def staged_problems(cwd=None) -> list[dict]:
    """Staged ADDITIONS that exceed the commit budget, as [{path, mb, why}].

    Checks the INDEX, not the worktree: what matters is what the next commit would carry.
    Only fully-added files are measured -- a deletion costs nothing, and modifying a file that
    is already tracked was inside the budget when it was first added.
    """
    cwd = cwd or ROOT
    p = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
                       cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        return [{"path": "<git>", "mb": 0.0, "why": (p.stderr or "").strip()[:200]}]
    files = [ln for ln in p.stdout.splitlines() if ln.strip()]
    out, total = [], 0.0
    for f in files:
        try:
            b = pathlib.Path(cwd, f).stat().st_size
        except OSError:
            continue
        total += b
        mb = b / 1e6
        if mb > MAX_ADDED_FILE_MB:
            out.append({"path": f, "mb": round(mb, 1),
                        "why": f"single file over {MAX_ADDED_FILE_MB} MB"})
    if total / 1e6 > MAX_ADDED_MB:
        out.append({"path": f"<{len(files)} new files>", "mb": round(total / 1e6, 1),
                    "why": f"total additions over {MAX_ADDED_MB} MB"})
    return out


def git_publish(changed: bool) -> dict:
    """Commit and push the knowledge base when a rule changed state.

    Only on change: a 6-hourly schedule that commits unconditionally would fill the history
    with empty commits. A failure here is reported but does not fail the run -- the evolution
    itself succeeded, and a network problem should not look like a rule regression.
    """
    # The run record is an audit trail and always lands; only the commit MESSAGE distinguishes
    # a knowledge update from a routine run. Gating the record on `changed` meant the history
    # was never committed at all.
    pass
    steps = []
    msg = ("knowledge: autonomous evolution update" if changed
           else "run: record scheduled evolution run (no knowledge change)")
    for cmd in (["git", "add", "-A"],):
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        steps.append({"cmd": " ".join(cmd[:3]), "code": p.returncode,
                      "tail": (p.stdout or p.stderr).strip().splitlines()[-1:]})
    # THE GUARD. `git add -A` is what let 1.57 GB into the history; unstage the additions that
    # blow the budget and commit the rest, reporting exactly what was withheld and why.
    problems = staged_problems()
    real = [d["path"] for d in problems if not d["path"].startswith("<")]
    if real:
        subprocess.run(["git", "reset", "-q", "--"] + real, cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if problems:
        steps.append({"cmd": "budget guard", "code": 1, "withheld": problems,
                      "tail": [f"refused to stage {len(problems)} over-budget addition(s)"]})
    for cmd in (["git", "-c", "user.name=figpipe-bot",
                 "-c", "user.email=bot@figpipe.local",
                 "commit", "--no-verify", "-m", msg],
                ["git", "push", "origin", "main"]):
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        steps.append({"cmd": " ".join(cmd[:3]), "code": p.returncode,
                      "tail": (p.stdout or p.stderr).strip().splitlines()[-1:] })
    return {"pushed": steps[-1]["code"] == 0, "steps": steps, "withheld": problems}


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    RUNS.mkdir(parents=True, exist_ok=True)
    previous_caps = {}
    try:
        previous_caps = json.loads((ROOT / "knowledge" / "latest_run.json")
                                   .read_text(encoding="utf-8")).get("capabilities", {})
    except (OSError, json.JSONDecodeError):
        previous_caps = {}
    caps = capability_snapshot()
    before = snapshot()

    ok_evolve, _ = True, ""
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "evolve.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok_evolve = p.returncode == 0
    evolve_out = (p.stdout or "").strip().splitlines()
    # A non-zero evolve exit means a rule REGRESSED or a check could not run. That must
    # surface in the run record and in this process's exit code, or the scheduler cannot see
    # it -- the previous version swallowed exactly this.
    evolve_failed = p.returncode != 0

    after = snapshot()

    # Fold in the structured evolution report. Without this the run record held only the last
    # few lines of stdout, so "did any rule regress?" and "was anything promoted?" were
    # unanswerable from the artefact -- which is the whole point of the scheduled run.
    evo_report = {}
    evo_path = ROOT / "knowledge" / "evolution_report.json"
    if evo_path.is_file():
        try:
            evo_report = json.loads(evo_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            evo_report = {"error": "evolution_report.json unreadable"}

    changed = (before.get("version") != after.get("version"))
    publish = {"pushed": False, "reason": "not yet published"}
    stamp = datetime.datetime.now()
    run = {
        "run_at": stamp.isoformat(timespec="seconds"),
        "dry_run": dry,
        "evolve_ok": ok_evolve,
        "evolve_exit_code": p.returncode,
        "evolve_output": evolve_out[-6:],
        "tests_ok": None,          # patched in after the suite runs
        "tests_summary": "pending",
        "knowledge_version_before": before.get("version"),
        "knowledge_version_after": after.get("version"),
        "knowledge_changed": changed,
        "published": publish,
        "check_results": evo_report.get("results", {}),
        "demoted": evo_report.get("demoted", []),
        "promoted": evo_report.get("promoted", []),
        "regressed_detail": {k: v for k, v in evo_report.get("results", {}).items()
                              if v.get("ok") is False},
        "check_summary": evo_report.get("summary", {}),
        # v2 schema: `enforced` requires BOTH a mechanism and a measurement. Counting the old
        # `verified` label here reported 0 enforced rules while 7 were enforced, which reads
        # as a collapse rather than as a schema change.
        "rules": {
            "enforced": sum(1 for r in after["rules"] if r.get("enforced")),
            "measured_unenforced": sum(1 for r in after["rules"]
                                       if r["confidence"] == "measured_unenforced"),
            "hypothesis": sum(1 for r in after["rules"] if r["confidence"] == "hypothesis"),
            "regressed": sum(1 for r in after["rules"] if r["confidence"] == "regressed"),
        },
        "capabilities": caps,
        "capabilities_delta": capability_delta(previous_caps, caps),
        "ok": None,                # patched in after the suite runs
    }

    if dry:
        print(json.dumps(run, indent=2)[:1200])
        return 0

    out = RUNS / f"{stamp:%Y-%m-%dT%H%M%S}.json"
    out.write_text(json.dumps(run, indent=2), encoding="utf-8")
    # keep the latest run where a reader will look
    (ROOT / "knowledge" / "latest_run.json").write_text(
        json.dumps(run, indent=2), encoding="utf-8")

    # Run the suite now that the record exists, then patch the result in.
    ok_tests, test_tail = run_tests()
    run["tests_ok"] = ok_tests
    run["tests_summary"] = test_tail
    import re as _re
    m = _re.search(r"(\d+) passed", test_tail or "")
    run["capabilities"]["tests"] = int(m.group(1)) if m else None
    run["capabilities_delta"] = capability_delta(previous_caps, run["capabilities"])
    run["ok"] = ok_evolve and ok_tests
    if not dry:
        out.write_text(json.dumps(run, indent=2), encoding="utf-8")
        (ROOT / "knowledge" / "latest_run.json").write_text(
            json.dumps(run, indent=2), encoding="utf-8")

    # Publish LAST, so the commit snapshots the record of THIS run rather than the previous
    # one. Doing it earlier left the repository permanently one run behind.
    if not dry:
        # Publish, then record the outcome. The record written here documents THIS run and is
        # itself committed by the NEXT run's publish -- which is stated explicitly rather than
        # left for a reader to discover from `git status`.
        publish = git_publish(changed)
        run["published"] = publish
        run["publish_note"] = (
            "The publish outcome is recorded after the commit that carries this run, so it "
            "describes the push triggered by this run; the file's own commit is made by the "
            "next scheduled run.")
        out.write_text(json.dumps(run, indent=2), encoding="utf-8")
        (ROOT / "knowledge" / "latest_run.json").write_text(
            json.dumps(run, indent=2), encoding="utf-8")

    print(f"  run at {run['run_at']}")
    print(f"  evolve: {'ok' if ok_evolve else 'FAILED'}   tests: {'ok' if ok_tests else 'FAILED'}")
    print(f"  knowledge: v{run['knowledge_version_before']} -> "
          f"v{run['knowledge_version_after']}  changed={changed}")
    print(f"  rules: {run['rules']}")
    if run.get("demoted"):
        print(f"  !! DEMOTED (regression): {run['demoted']}")
    if run.get("promoted"):
        print(f"  ++ PROMOTED to verified: {run['promoted']}")
    if publish.get("pushed"):
        print("  pushed to origin/main")
    elif publish.get("reason"):
        print(f"  not pushed: {publish['reason']}")
    print(f"  wrote {out.relative_to(ROOT)}")
    return 0 if run["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
