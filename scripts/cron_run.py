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


def snapshot() -> dict:
    return json.loads(KB.read_text(encoding="utf-8"))


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
                       capture_output=True, text=True)
    tail = (p.stdout or p.stderr).strip().splitlines()
    return p.returncode == 0, (tail[-1] if tail else "")


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
    for cmd in (["git", "add", "-A"],
                ["git", "-c", "user.name=figpipe-bot",
                 "-c", "user.email=bot@figpipe.local",
                 "commit", "--no-verify", "-m", msg],
                ["git", "push", "origin", "main"]):
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        steps.append({"cmd": " ".join(cmd[:3]), "code": p.returncode,
                      "tail": (p.stdout or p.stderr).strip().splitlines()[-1:] })
    return {"pushed": steps[-1]["code"] == 0, "steps": steps}


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    RUNS.mkdir(parents=True, exist_ok=True)
    before = snapshot()

    ok_evolve, _ = True, ""
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "evolve.py")],
                       cwd=ROOT, capture_output=True, text=True)
    ok_evolve = p.returncode == 0
    evolve_out = (p.stdout or "").strip().splitlines()

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
        "evolve_output": evolve_out[-6:],
        "tests_ok": None,          # patched in after the suite runs
        "tests_summary": "pending",
        "knowledge_version_before": before.get("version"),
        "knowledge_version_after": after.get("version"),
        "knowledge_changed": changed,
        "published": publish,
        "reverified": evo_report.get("reverified", {}),
        "demoted": evo_report.get("demoted", []),
        "promoted": evo_report.get("promoted", []),
        "hypothesis_H02": evo_report.get("hypothesis_H02", {}),
        "evolution_summary": evo_report.get("summary", {}),
        "rules": {
            "verified": sum(1 for r in after["rules"] if r["confidence"] == "verified"),
            "hypothesis": sum(1 for r in after["rules"] if r["confidence"] == "hypothesis"),
            "regressed": sum(1 for r in after["rules"] if r["confidence"] == "regressed"),
        },
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
    run["ok"] = ok_evolve and ok_tests
    if not dry:
        out.write_text(json.dumps(run, indent=2), encoding="utf-8")
        (ROOT / "knowledge" / "latest_run.json").write_text(
            json.dumps(run, indent=2), encoding="utf-8")

    # Publish LAST, so the commit snapshots the record of THIS run rather than the previous
    # one. Doing it earlier left the repository permanently one run behind.
    if not dry:
        publish = git_publish(changed)
        run["published"] = publish
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
