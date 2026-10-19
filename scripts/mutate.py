"""Run the mutation loop as a standalone step, and record what it decided.

WHY THIS FILE EXISTS
    `figpipe/mutation.py` implements Propose-Probe-Compose, but nothing called it. It was an orphan
    library: verified by tests, described in the report, and never executed by the evolution loop.
    A capability that is not wired in is not a capability of the SYSTEM -- it is a capability of a
    test suite. That distinction is the whole point of this project, so it gets its own entry point.

WHAT IT DOES
    1. propose  -- the declared mutation space (candidate operator-budget edits)
    2. probe    -- run the baseline and every candidate on the FIXED task set, under the measurement
                   lock, charging each rollout to the vendored ledger
    3. compose  -- select by behavioural contrast, rejecting on any per-task regression

    It writes `knowledge/mutation_report.json` so the loop, the report and a human can all see what
    was proposed, what was measured, what was selected, and what was rejected and why.

WHAT IT DELIBERATELY DOES NOT DO
    It does NOT apply the selected edit. Applying a budget change measured on six tasks is the
    "a fix is a change, a change needs the same evidence" defect this project recorded at ##47.
    The selection is a FINDING, routed to a human or to a round that can re-measure the pool.

USAGE
    python scripts/mutate.py                 # propose, probe, compose, write the report
    python scripts/mutate.py --dry-run       # propose and compose only, no probing
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import lock, mutation  # noqa: E402

OUT = ROOT / "knowledge" / "mutation_report.json"


def run(*, dry: bool = False, budget: int | None = None,
        lock_held: bool = False) -> dict:
    """Execute the loop once and return the record."""
    space = mutation.default_space()
    record: dict = {
        "proposed": [{"id": c.id, "skill": c.skill, "parameter": c.parameter,
                      "value": c.value, "rationale": getattr(c, "rationale", "")}
                     for c in space.candidates],
        "tasks": [t.id for t in space.tasks],
        "min_margin": space.min_margin,
    }
    if dry:
        record.update({"probed": False, "selected": [], "rejected": [], "ties": [],
                       "note": "dry run: nothing was executed"})
        return record

    probed = mutation.probe(space, budget=budget, lock_held=lock_held)
    composed = mutation.compose(probed, space)
    record.update({
        "probed": True,
        "baseline_mean": (probed.get("mean_score") or {}).get("baseline"),
        "mean_score": probed.get("mean_score"),
        "ledger": probed.get("ledger"),
        "budget": probed.get("budget"),
        "selected": composed.get("selected", []),
        "rejected": composed.get("rejected", []),
        "ties": composed.get("ties", []),
        "decisions": composed.get("decisions", []),
        "verdict": composed.get("verdict"),
        # the honest limit, carried with the result so it cannot be quoted without it
        "applied": False,
        "why_not_applied": ("a selected edit measured on six tasks is a finding, not a change; "
                            "applying it requires a pool re-measure (LEARNINGS ##47)"),
    })
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--no-lock", action="store_true",
                    help="skip the measurement lock (only when the parent already holds it)")
    args = ap.parse_args(argv)
    if args.no_lock:
        rec = run(dry=args.dry_run, budget=args.budget, lock_held=True)
    else:
        try:
            rec = run(dry=args.dry_run, budget=args.budget)
        except lock.MeasurementBusy as exc:
            print(f"  refused: {exc}")
            return 3
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not args.quiet:
        print(f"  proposed {len(rec['proposed'])} candidates over {len(rec['tasks'])} tasks")
        if rec.get("probed"):
            for d in rec.get("decisions", []):
                print(f"    {d['id']:<24} {d['verdict']:<10} delta={d.get('delta')}")
            print(f"  selected: {rec.get('selected') or '(none)'}")
            print(f"  ties    : {rec.get('ties') or '(none)'}")
            print(f"  applied : {rec.get('applied')} -- {rec.get('why_not_applied')}")
        print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
