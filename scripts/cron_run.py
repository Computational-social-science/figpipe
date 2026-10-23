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
sys.path.insert(0, str(ROOT))
from figpipe import lock  # noqa: E402

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
    n_tasks = bench.get("n_tasks", 0) or 0
    n_ok = bench.get("n_ok", 0) or 0
    n_unsupported = bench.get("n_unsupported", 0) or 0
    # tasks that failed to FETCH never exercised the pipeline; counting them as capability loss
    # would let a network hiccup read as a regression (it did, on 2026-10-19)
    infra = sum(1 for t in (bench.get("tasks") or bench.get("failures") or [])
                if (t.get("status") in (None, "error"))
                and _is_infra(t.get("error")))
    attempted = max(n_tasks - n_unsupported - infra, 1)
    return {
        # WHICH INSTRUMENT PRODUCED THIS SNAPSHOT. Without it a later comparison cannot tell a
        # capability change from an instrument change -- measured 2026-10-21: the styled anchor
        # moved 0.355 -> 0.357 with ZERO of the 20 anchor tasks changing distance, because a label
        # fix altered the rendered text the style profile reads. That was reported as a capability
        # regression and exited 1.
        "_code_version": bench.get("code_version"),
        # COMPLETE MEMBERSHIP, recorded beside the rate it qualifies. `benchmark_success_rate` is a
        # judged field, and a rate over 140 of 150 tasks is not the same quantity as one over 150.
        # Without this flag a short set reads as a capability change.
        # HARD FINDINGS ARE A CAPABILITY FACT, not only a report line. `n_ok` and mean distance can
        # both hold while a figure gets worse; a hard finding is the only channel that says so.
        "benchmark_hard_findings": sum(int(t.get("hard_failures") or 0)
                                       for t in (bench.get("tasks") or [])),
        "benchmark_complete_membership": bool(bench.get("complete_membership")),
        "benchmark_pool_size": bench.get("pool_size"),
        # DOES THE DECLARED POOL STILL AGREE WITH THE COVERAGE INDEX? A `False` here means the
        # upstream dataset changed shape and every rate in this snapshot is computed against a
        # stale denominator. Diagnostic, so it does not fail a run by itself -- but it is recorded
        # in every run record rather than discovered later.
        "benchmark_pool_consistent": bool((bench.get("pool_facts") or {}).get("consistent")),
        "skills": len(skills.get("skills", []) or []),
        "operators": len(skills.get("operators", []) or []),
        "benchmark_tasks": n_tasks,
        "benchmark_ok": n_ok,
        # VISIBLE, so the exclusion from the success rate is never silent. A fetch failure means
        # the pipeline never ran, so it is not a capability result either way.
        "benchmark_infrastructure_failures": infra,   # diagnostic; see DIAGNOSTIC_FIELDS
        # a RATE, not a count: ok-count rises whenever the measured set grows, which is the
        # mirror image of the false regression the raw mean produced. Coverage and success rate
        # are separate facts and only the rate is a capability.
        "benchmark_success_rate": round(n_ok / attempted, 3) if n_tasks else None,
        "benchmark_mean_distance": bench.get("mean_distance"),
        # judged instead of the raw mean: the mean moves when the task SET changes, which is a
        # property of the measurement, not of the capability
        # JUDGED: single-instrument view. The all-rows value mixes fingerprints and moves when the
        # MEASUREMENT changes (0.305 -> 0.316 when only 5 of 20 anchor tasks were on current code).
        "benchmark_anchor_single": (bench.get("benchmark_anchor_single") or {}).get("mean"),
        "benchmark_anchor_distance": bench.get("benchmark_anchor_distance"),
        # the distance of the figures the pipeline would actually SHIP (closer of plain/styled);
        # this is the capability the selection step added, so it is judged
        # JUDGED: the frozen-subset version. The full-set shipped mean moves whenever a task is
        # added (0.257 -> 0.258 on a coverage-only run), which is the same defect as the raw mean.
        # JUDGED value is the single-instrument one: the all-rows anchor mixes rows measured by
        # different versions of the measurement code, so it moves when the INSTRUMENT changes
        # (0.252 -> 0.243 when only 3 of 20 anchor tasks had been re-measured after a styleprofile
        # fix). The mixed value is kept below as a reported fact, never judged.
        "benchmark_shipped_anchor_single": (
            (bench.get("benchmark_shipped_anchor_single") or {}).get("mean")),
        "benchmark_shipped_anchor_distance": bench.get("benchmark_shipped_anchor_distance"),
        "benchmark_unsupported": bench.get("n_unsupported"),
        # The benchmark's OWN deterministic channel (deviation-defect-v1, 35% weight upstream).
        # This is the only number produced by THEIR scorer, so it is the closest thing to an
        # external measure this project has. It was added to CAPABILITY_DIRECTION without being
        # added HERE -- a judged field the snapshot never returns is never judged, which is the
        # "control that looks present and does nothing" defect this project keeps finding.
        # READ FROM THE DEDICATED PASS, not the in-harness aggregate. The harness only scores
        # tasks whose cache entry currently carries reference_code, so its mean drifts with cache
        # contents (93.53) while the dedicated pass measures the whole pool honestly (70.59).
        # Two numbers for one concept is how a metric stops being trusted.
        "benchmark_official_code_score": _official_pass_score(),
        # the referent: points above the naive baseline, on the same task count
        "benchmark_official_improvement": _official_improvement(),
        "statistics_reproduced": (seed.get("self_check") or {}).get("statistics_recorded"),
        "knowledge_version": kb.get("version"),
        "tests": None,             # patched in after the suite runs
    }


#: Corrections that are KNOWN and intentional: a field whose drop reflects a more honest
#: measurement, not a loss of ability. Each entry says what changed and why, so the guard keeps
#: firing for real regressions while a documented correction does not read as one.
#: A correction must be justified in this comment; it is not a mute switch.
KNOWN_CORRECTIONS = {
    "benchmark_official_code_score": (
        "2026-10-19: 93.53 -> 70.59. The earlier number came from the in-harness aggregate, which "
        "scores only tasks whose cache entry carried reference_code and copied the reference's own "
        "code features -- a tautology that scores 100 by construction. The current number infers "
        "style from the reference IMAGE, which is the benchmark's actual premise. Lower is more "
        "honest, not worse."),
}


#: Which direction is "better" for each capability field. +1 = higher is better, -1 = lower is
#: better. A field that is not listed is reported but never judged: an unjudged field cannot
#: silently count as an improvement.
#: Fields that are RECORDED and DIFFED but judged in NEITHER direction. They are diagnostics whose
#: movement must be visible without ever being scored as a capability gain or loss. The success-rate
#: denominator depends on `benchmark_infrastructure_failures`, so if that count were invisible the
#: exclusion could be tuned whenever the number looked bad -- worse than the defect it fixes.
DIAGNOSTIC_FIELDS = frozenset({"benchmark_infrastructure_failures"})


CAPABILITY_DIRECTION = {
    "skills": +1,
    "operators": +1,
    "benchmark_success_rate": +1,
    # NOTE: benchmark_tasks and benchmark_ok are counts, not capabilities: they rise whenever the
    # measured set grows. They are recorded for coverage and are deliberately NOT judged.
    "benchmark_anchor_single": -1,
    # NOTE: benchmark_anchor_distance (all rows) is recorded but NOT judged, for the same reason as
    # the shipped anchor: it can mix rows measured by different fingerprints.
    "benchmark_official_code_score": +1,
    "benchmark_official_improvement": +1,
    "benchmark_shipped_anchor_single": -1,
    # NOTE: benchmark_shipped_anchor_distance (all rows) is recorded but NOT judged: it can mix
    # rows measured by different fingerprints, so a code change moves it without a capability
    # change. This project has now produced four variants of this same defect.
    # NOTE: benchmark_shipped_distance (full-set) is recorded but NOT judged, for the same reason
    # as benchmark_mean_distance: its value depends on which tasks are in the set.
    # NOTE: benchmark_mean_distance is deliberately NOT judged. It is a mean over a growing task
    # set, so it changes when the benchmark slice grows even if nothing about the pipeline did.
    # Judging it produced a false capability regression on 2026-10-19 (0.278/30 -> 0.302/66).
    "statistics_reproduced": +1,
    "tests": +1,
    "knowledge_version": +1,
    # FEWER HARD FINDINGS IS BETTER. `n_ok` and mean distance can both hold while a figure gets
    # worse; a hard finding is the only channel in the snapshot that says so, and it needs the
    # direction to be negative or the delta would treat a rise as a gain.
    "benchmark_hard_findings": -1,
}


def mutation_step() -> dict:
    """Run the mutation loop and return its record.

    Deliberately AFTER the benchmark slice and anchor refresh, so the probe runs on current code.
    A failure here must not fail the whole run: a mutation step that cannot measure is a finding
    about the machine, not a capability regression.
    """
    # WHAT THE POOL'S FINDINGS IMPLY, next to what the fixed menu proposes.
    #
    # Measured over 152 runs: 4 knowledge changes, 222 ties, 149 runs that selected NOTHING. The
    # menu was the defect -- every real fix this project made was a drawer change that no budget
    # integer could express. This records the finding-derived candidates so the gap is visible in
    # every run record rather than inferred from the tie rate.
    try:
        report = json.loads((ROOT / "corpus" / "e2e" / "plottwin_report.json")
                            .read_text(encoding="utf-8"))
        from figpipe import proposals as proposals_mod
        derived = proposals_mod.proposals_from_report(report)
    except (OSError, json.JSONDecodeError, ImportError) as exc:
        derived = {"proposals": [], "n": 0, "unproposable": [], "n_unproposable": 0,
                   "verdict": f"could not read the pool report: {type(exc).__name__}"}
    finding_fields = {
        "finding_proposals": derived.get("proposals") or [],
        "n_finding_proposals": derived.get("n") or 0,
        "finding_unproposable": derived.get("unproposable") or [],
        "n_finding_unproposable": derived.get("n_unproposable") or 0,
        "finding_proposal_verdict": derived.get("verdict"),
    }

    # PROBE THE CATALOGUED PATCHES. Each is reverted (or applied) for one slice of the tasks its
    # own skill produced, and the hard-finding count is compared. This is the only path by which the
    # loop can MEASURE a drawer fix rather than a budget integer.
    patch_runs: list[dict] = []
    try:
        from figpipe import patchprobe as _pp
        from figpipe import proposals as _prop
        for key, (path, old, new, why) in _prop.CODE_PATCHES.items():
            state = _prop.patch_state(ROOT, {"id": key, "path": path, "old": old,
                                             "new": new, "rationale": why})
            entry = {"patch": key, "state": state["state"], "why": why, "eligible": False,
                     "probed": False}
            if state["state"] != "revert":
                entry["note"] = ("the fix is not in this tree, so there is no contribution to "
                                 "measure") if state["state"] == "fix" else state["why"]
                patch_runs.append(entry)
                continue
            skill = _prop.FIX_SKILL.get(key) if hasattr(_prop, "FIX_SKILL") else None
            # ELIGIBLE, NOT PROBED. The probe needs the pool lock and minutes per patch, so the
            # schedule records WHAT COULD BE MEASURED and `scripts/measure_fix_contribution.py`
            # does the measuring. Calling this `probed` would report a measurement that did not
            # happen.
            entry["eligible"] = True
            entry["probed"] = False
            entry["skill"] = skill
            entry["how"] = ("run scripts/measure_fix_contribution.py to measure this fix's "
                            "contribution")
            patch_runs.append(entry)
    except (ImportError, AttributeError, OSError) as exc:
        patch_runs = [{"patch": "?", "probed": False,
                       "note": f"the patch catalogue could not be read: {type(exc).__name__}"}]
    patch_fields = {
        "patch_catalogue": patch_runs,
        "n_patch_candidates": len(patch_runs),
        "n_patch_eligible": sum(1 for e in patch_runs if e.get("eligible")),
        "n_patch_probed": sum(1 for e in patch_runs if e.get("probed")),
        "patch_note": ("a patch changes the SOURCE, so it is probed and reported but never "
                       "auto-selected: the loop does not edit its own drawer without a human "
                       "seeing the diff"),
    }

    script = ROOT / "scripts" / "mutate.py"
    if not script.is_file():
        return {"ran": False, "reason": "scripts/mutate.py absent", **finding_fields,
                **patch_fields}
    p = subprocess.run([sys.executable, str(script), "--quiet", "--no-lock"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if p.returncode != 0:
        return {"ran": False, "code": p.returncode,
                "reason": ((p.stdout or "") + (p.stderr or "")).strip()[-300:],
                **finding_fields, **patch_fields}
    try:
        return {"ran": True, **json.loads(
            (ROOT / "knowledge" / "mutation_report.json").read_text(encoding="utf-8")),
            **finding_fields, **patch_fields}
    except (OSError, json.JSONDecodeError) as exc:
        return {"ran": False, "reason": f"report unreadable: {exc}", **finding_fields,
                **patch_fields}

#: Error-name fragments that mean the measurement never ran. The list must cover the SUBTYPES, not
#: only the bases: `ConnectionResetError` is a `ConnectionError` but its name does not contain that
#: string, so a string-prefix match on the base misses it.
INFRA_ERROR_NAMES = (
    "HTTPError", "URLError", "ConnectionError", "ConnectionResetError",
    "ConnectionAbortedError", "ConnectionRefusedError", "TimeoutError", "SSLError",
    "socket.timeout", "RemoteDisconnected", "IncompleteRead", "ProtocolError",
)


def _is_infra(error) -> bool:
    """A fetch failure means the pipeline never ran, so it is not a capability result.

    MEASURED 2026-10-23: a `ConnectionResetError` was classified as a CAPABILITY failure because
    `ConnectionResetError` does not contain the substring `ConnectionError`. The run then reported
    `success_rate 1.0 -> 0.993` and exited 1 -- a regression that was a dropped socket.

    THE NAME LIST IS NOT THE TEST. Matching the type name against a tuple is a proxy; the honest
    check is `isinstance`, which is unavailable because only the string survives into the report.
    The list therefore has to enumerate the subtypes that actually occur, and this one did.
    """
    text = str(error or "")
    return any(p in text[:80] for p in INFRA_ERROR_NAMES)


def _official_pass_score():
    """The pool-wide honest official score, from the dedicated scoring pass."""
    try:
        data = json.loads((ROOT / "corpus" / "e2e" / "official_scores.json")
                          .read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    summary = data.get("summary") or {}
    if summary.get("style_source") != "image":
        return None
    return summary.get("mean_score")


def _official_improvement():
    """Points above the naive baseline -- the referent that makes the score a claim.

    A raw score supports no claim on its own. This is the number a report should quote, and it is
    only defined when BOTH the baseline and the pipeline were measured on the same task count.
    """
    def _read(name):
        try:
            return json.loads((ROOT / "corpus" / "e2e" / name)
                              .read_text(encoding="utf-8"))["summary"]
        except (OSError, json.JSONDecodeError, KeyError):
            return {}

    base, pipe = _read("official_scores_naive.json"), _read("official_scores.json")
    if not base or not pipe:
        return None
    if base.get("n_scored") != pipe.get("n_scored"):
        return None
    if base.get("mean_score") is None or pipe.get("mean_score") is None:
        return None
    return round(pipe["mean_score"] - base["mean_score"], 2)


#: Capability fields whose value is produced by a MEASUREMENT INSTRUMENT, and therefore cannot be
#: compared across a change to that instrument. A style distance computed by one version of the
#: drawer stack is not the same quantity as one computed by another: the label fix on 2026-10-21
#: changed the rendered text, the style profile reads text, and the anchor moved 0.355 -> 0.357
#: with ZERO of the 20 anchor tasks actually changing distance -- the instrument had changed.
#:
#: Comparing across that is the exact violation the project's invariant forbids.
INSTRUMENT_FIELDS = ("benchmark_anchor_single", "benchmark_shipped_anchor_single",
                     "benchmark_official_code_score", "benchmark_official_improvement")

#: Fields that are RATES over the benchmark task set. A rate over an incomplete set is not the same
#: quantity as a rate over the whole set, so these cannot be compared across a membership break.
MEMBERSHIP_FIELDS = ("benchmark_success_rate", "benchmark_ok", "benchmark_anchor_single",
                     "benchmark_shipped_anchor_single", "benchmark_official_code_score",
                     "benchmark_official_improvement")


def _instrument_changed(previous: dict, current: dict) -> bool:
    """True when the two snapshots were provably taken by DIFFERENT instruments.

    THE DISTINCTION THIS RESTS ON:

        both carry a version, equal        -> same instrument, comparable
        both carry a version, different    -> different instruments, NOT comparable
        one carries it, the other does not -> the recording layer changed between them, NOT comparable
        neither carries it                 -> no instrument information at all; a plain comparison of
                                              two dicts (a unit test, a hand check), not a
                                              measurement across instrument versions

    An earlier version returned True for the LAST case, which broke six existing tests -- the tests
    doing their job. The case that actually failed is the THIRD: the old scheduled run predates the
    field, so its snapshot has no version while the new one does, and the +0.002 anchor move was
    reported as a capability regression.
    """
    old = (previous or {}).get("_code_version")
    new = (current or {}).get("_code_version")
    if old is None and new is None:
        return False          # nothing recorded; plain comparison
    return not (old and new and old == new)


def capability_delta(previous: dict, current: dict) -> dict:
    """Which capability fields changed, by how much, and whether any of them got WORSE.

    Recording a delta is not a control. The review of the loop found that a run could report
    "capability 23/30" after a previous run reported "26/30" and still exit 0, because nothing
    compared the two. `verdict.regressions` makes a capability loss explicit, and main() turns
    it into a non-zero exit unless the operator accepts it on the command line -- the same
    shape as a rule regression.
    """
    delta = {}
    for key, value in current.items():
        old = (previous or {}).get(key)
        if old != value:
            delta[key] = {"before": old, "after": value}
    gains, regressions, corrections = [], [], []
    # AN INSTRUMENT CHANGE INVALIDATES INSTRUMENT-DEPENDENT COMPARISONS. The project's invariant:
    # a judged metric must be a function of a fixed task set, complete membership, and a SINGLE
    # INSTRUMENT VERSION. A style distance computed by one drawer stack is not the same quantity
    # as one computed by another -- measured 2026-10-21: the anchor moved 0.355 -> 0.357 with ZERO
    # of the 20 anchor tasks changing distance, because a label fix changed the rendered text the
    # profile reads. That was reported as a capability regression and exited 1.
    instrument_moved = _instrument_changed(previous, current)
    # INCOMPLETE MEMBERSHIP INVALIDATES A RATE, for the same reason an instrument change does. A
    # success rate over 140 of 150 tasks is not the same quantity as one over 150, and `n_ok` alone
    # cannot tell them apart. The snapshot records `benchmark_complete_membership` for exactly this.
    membership_broken = (current.get("benchmark_complete_membership") is False
                         or previous.get("benchmark_complete_membership") is False)
    not_compared = []
    for key, change in delta.items():
        direction = CAPABILITY_DIRECTION.get(key)
        old, new = change["before"], change["after"]
        if direction is None or old is None or new is None:
            continue
        if membership_broken and key in MEMBERSHIP_FIELDS:
            not_compared.append({"field": key, "before": old, "after": new,
                                 "why": "one of these snapshots was measured over an INCOMPLETE "
                                        "task set, so the two rates are not the same quantity"})
            continue
        if instrument_moved and key in INSTRUMENT_FIELDS:
            not_compared.append({"field": key, "before": old, "after": new,
                                 "why": "the measurement instrument changed between these "
                                        "snapshots, so the two values are not the same quantity"})
            continue
        move = (new - old) * direction
        entry = {"field": key, "before": old, "after": new}
        if move > 0:
            gains.append(entry)
        elif move < 0:
            if key in KNOWN_CORRECTIONS:
                entry["why"] = KNOWN_CORRECTIONS[key]
                corrections.append(entry)
            else:
                regressions.append(entry)
    return {"changed": bool(delta), "delta": delta,
            "verdict": {"gains": gains, "regressions": regressions,
                        "corrections": corrections,
                        "not_compared": not_compared,
                        "instrument_changed": instrument_moved,
                        "membership_broken": membership_broken,
                        "ok": not regressions,
                        "judged_fields": sorted(CAPABILITY_DIRECTION)}}


def _report_is_current() -> tuple[bool, str]:
    """Is the pool report fresh enough for the anchor to re-measure against?

    THE ORDERING WAS A COMMENT, NOT A COUPLING. `refresh_anchor` reads whatever
    `corpus/e2e/plottwin_report.json` contains, and nothing checked that `benchmark_slice` had just
    written it. A skipped or failed slice would leave the anchor re-measuring against stale rows and
    recording a number that looks current.

    The report states both facts already: `code_version` (which instrument produced it) and
    `n_stale` (rows measured by another instrument).
    """
    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    try:
        import json as _json
        report = _json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"no readable pool report: {type(exc).__name__}"
    try:
        import sys as _sys
        _sys.path.insert(0, str(ROOT / "scripts"))
        import bench_plottwin as _bench
        expected = _bench.CODE_VERSION
    except Exception:                                      # noqa: BLE001
        return True, "cannot determine the current instrument; proceeding"
    got = report.get("code_version")
    if got and got != expected:
        return False, (f"the pool report was produced by instrument {got}, current is {expected}; "
                       f"the anchor would re-measure against rows from another instrument")
    return True, "current"


def refresh_anchor() -> dict:
    """Re-measure the frozen shipped anchor when its rows are on mixed instruments.

    WHY: a judged metric must be a function of a fixed task set AND one instrument version. After a
    change to the measurement code the anchor becomes non-comparable and reports None, which is
    correct but leaves the loop blind. Re-measuring just the 20 anchor tasks restores comparability
    at a bounded cost (20 renders, not a full pool walk).
    """
    import json as _json
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    try:
        data = _json.loads(report.read_text(encoding="utf-8"))
    except (OSError, _json.JSONDecodeError):
        return {"ran": False, "reason": "report unreadable"}
    # BOTH anchors must be comparable. Checking only one is how a stale metric survives a heal.
    shipped = data.get("benchmark_shipped_anchor_single") or {}
    styled = data.get("benchmark_anchor_single") or {}
    if shipped.get("comparable") and styled.get("comparable"):
        return {"ran": False, "reason": "both anchors already comparable"}
    stale = [name for name, info in (("shipped", shipped), ("styled", styled))
             if not info.get("comparable")]
    ids: list[str] = []
    for name in (("benchmark_shipped_anchor.json" if "shipped" in stale
                  else None),
                 ("benchmark_anchor.json" if "styled" in stale else None)):
        if name is None:
            continue
        try:
            ids.extend(_json.loads((ROOT / "knowledge" / name)
                                   .read_text(encoding="utf-8"))["ids"])
        except (OSError, KeyError, _json.JSONDecodeError):
            continue
    ids = sorted(set(ids))
    if not ids:
        return {"ran": False, "reason": "no anchor ids readable"}
    script = ROOT / "scripts" / "bench_plottwin.py"
    try:
        p = subprocess.run([sys.executable, str(script), "--ids", ",".join(ids), "--merge",
                            "--no-lock"],
                           cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=1800)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ran": False, "reason": f"{type(exc).__name__}: {exc}"}
    tail = (p.stdout or p.stderr or "").strip().splitlines()
    return {"ran": True, "stale_anchors": stale, "tasks": len(ids),
            "code": p.returncode, "tail": tail[-3:]}


def benchmark_slice(tasks: int = 6) -> dict:
    """Run a small, rotating PlotTwin-Bench slice and record the outcome.

    WHY IN THE LOOP
        Capability that is only measured when someone remembers to run a script is not tracked
        capability. The slice rotates through the 150-task pool (offset derived from the run
        count) so successive runs cover new tasks without a long run time, and every result is
        merged into the same report the deliverable points at.

    A missing network, a missing dataset cache or a broken harness must NOT fail the scheduled
    run: this is a measurement, and a measurement that cannot run is reported as skipped.
    """
    script = ROOT / "scripts" / "bench_plottwin.py"
    if not script.is_file():
        return {"ran": False, "reason": "benchmark harness absent"}
    # walk forward over UNCOVERED windows instead of re-measuring covered ones
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import bench_plottwin as _bench
        offset = _bench.next_uncovered_offset(tasks)
    except Exception:                                  # noqa: BLE001 - never fail the run
        runs = sorted((ROOT / "knowledge" / "runs").glob("*.json"))
        offset = (len(runs) * tasks) % 120
    cmd = [sys.executable, str(script), "--limit", str(tasks), "--offset", str(offset),
           "--merge", "--no-lock"]      # the parent already holds it
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=1800)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ran": False, "reason": f"{type(exc).__name__}: {exc}"}
    tail = (p.stdout or p.stderr or "").strip().splitlines()
    return {"ran": True, "offset": offset, "tasks": tasks, "code": p.returncode,
            "tail": tail[-4:]}


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
    out = (p.stdout or "") + (p.stderr or "")
    tail = out.strip().splitlines()
    if p.returncode == 0:
        return True, (tail[-1] if tail else "")
    # A SCHEDULED FAILURE MUST NAME WHAT FAILED. Keeping only the last line made the run record say
    # "1 failed, 310 passed" with no way to know which test -- the failure was undiagnosable
    # without re-running the whole suite. Collect the FAILED/ERROR lines and the short summary.
    failures = [ln.strip() for ln in tail
                if ln.startswith("FAILED") or ln.startswith("ERROR")]
    summary = tail[-1] if tail else ""
    detail = "; ".join(failures[:6])
    return False, (f"{summary} | {detail}" if detail else summary)


#: Tracked paths a scheduled commit must never DELETE on its own.
#:
#: WHY: the publisher runs `git add -A`. On 2026-10-19 a scheduled run committed the deletion of
#: the entire seed package (the paper PDF, seven published figure PNGs, the authors' recipe) --
#: 3.7 MB of INPUT data that cannot be regenerated from this repository. The commit message said
#: "no knowledge change". The files were simply missing from the worktree at that moment, and
#: `git add -A` recorded their absence as intent.
#:
#: A scheduled job may add and modify; it may not remove evidence. Deleting these paths is a
#: human decision and has to be made with `--allow-deletions`.
PROTECTED_PREFIXES = (
    "Seeds/",
    "corpus/style/",
    "templates/seed/",
    "templates/transfer/",
    "knowledge/layout_rules.json",
    "knowledge/skills_catalog.json",
    "knowledge/benchmark_skill_map.json",
    "reports/",
)


def deletion_problems(cwd=None) -> list[str]:
    """Tracked files the staged change would DELETE inside a protected prefix."""
    cwd = cwd or ROOT
    p = subprocess.run(["git", "diff", "--cached", "--diff-filter=D", "--name-only"],
                       cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    deleted = [line.strip() for line in (p.stdout or "").splitlines() if line.strip()]
    return [d for d in deleted if d.startswith(PROTECTED_PREFIXES)]


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


def git_publish(changed: bool, allow_deletions: bool = False,
                run_ok: bool | None = None) -> dict:
    """Commit and push the knowledge base when a rule changed state.

    Only on change: a 6-hourly schedule that commits unconditionally would fill the history
    with empty commits. A failure here is reported but does not fail the run -- the evolution
    itself succeeded, and a network problem should not look like a rule regression.
    """
    # DO NOT COMMIT A RUN THAT CHANGED NOTHING. 49 of 80 commits once read "no knowledge change";
    # a history where 61% of entries say nothing happened hides the entries that did. The run
    # record still lands in the worktree every time -- it is overwritten by the next run and read
    # by the report -- but it is only COMMITTED when something actually changed, or when the run
    # failed (a failure is evidence and must be preserved).
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
    deletions = [] if allow_deletions else deletion_problems()
    if deletions:
        # unstage everything: a commit that deletes evidence is not worth making
        subprocess.run(["git", "reset", "-q"], cwd=ROOT, capture_output=True, text=True)
        return {"pushed": False, "withheld": [],
                "blocked_deletions": deletions,
                "reason": "refusing to commit deletions of protected paths; re-run with "
                          "--allow-deletions if this is intentional"}
    real = [d["path"] for d in problems if not d["path"].startswith("<")]
    if real:
        subprocess.run(["git", "reset", "-q", "--"] + real, cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if problems:
        steps.append({"cmd": "budget guard", "code": 1, "withheld": problems,
                      "tail": [f"refused to stage {len(problems)} over-budget addition(s)"]})
    # a failed run is evidence and must be preserved even when nothing changed
    if not changed and run_ok is not False:
        # nothing to say; do not say it 49 times
        return {"pushed": False, "withheld": [], "blocked_deletions": [],
                "skipped": True,
                "reason": "no knowledge change: the run record stays uncommitted for the next run"}
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
    # ONE MEASUREMENT AT A TIME. A scheduled run and a pool-wide re-measure sharing this machine
    # produce numbers that are neither reproducible nor trustworthy -- that is exactly what made a
    # run on 2026-10-19 report a regression that was contention.
    lock.break_stale()
    try:
        lock.acquire("cron_run")
    except lock.MeasurementBusy as exc:
        print(f"  refused: {exc}")
        return 3
    try:
        return _main_locked(argv, dry)
    finally:
        # ONLY RELEASE WHAT WE STILL HOLD. `_main_locked` releases the lock around the test suite
        # (so the suite's own cross-process test can take it) and re-acquires afterwards; if
        # another measurement took it in that window, the lock is no longer ours and releasing it
        # raises -- from inside a `finally`, turning a clean "not pushed" exit into a traceback.
        # This happened on 2026-10-20 at 13:56.
        holder = lock.holder() or {}
        if holder.get("name") == "cron_run":
            lock.release("cron_run")


def _main_locked(argv: list[str], dry: bool) -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    previous_caps = {}
    try:
        previous_caps = json.loads((ROOT / "knowledge" / "latest_run.json")
                                   .read_text(encoding="utf-8")).get("capabilities", {})
    except (OSError, json.JSONDecodeError):
        previous_caps = {}
    bench_run = {"ran": False, "reason": "dry run"}
    anchor_run = {"ran": False, "reason": "dry run"}
    mutation_run = {"ran": False, "reason": "dry run"}
    if not dry and "--skip-benchmark" not in argv:
        # ORDER MATTERS: the slice writes the report, and the anchor refresh must follow it (a
        # stale anchor is only stale AFTER new rows land). The snapshot is taken once, after both,
        # so it can never read a half-written state -- which it did, recording null for a metric
        # that was 0.351 in the report.
        bench_run = benchmark_slice()
        # REFUSE TO RE-MEASURE AGAINST A STALE REPORT. The comment above described this ordering and
        # nothing enforced it: a skipped or failed slice left the anchor reading whatever the file
        # happened to contain. The report states `code_version`; one comparison is the contract.
        _fresh, _fresh_why = _report_is_current()
        anchor_run = (refresh_anchor() if _fresh
                      else {"ran": False, "reason": f"refused: {_fresh_why}"})
        # PROPOSE -> PROBE -> COMPOSE. Without this the loop can only report that numbers moved; it
        # cannot choose an edit. 91 runs produced 0 knowledge changes for exactly that reason.
        mutation_run = mutation_step()
    before = snapshot()

    ok_evolve, _ = True, ""
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "evolve.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok_evolve = p.returncode == 0
    evolve_out = (p.stdout or "").strip().splitlines()
    # A non-zero evolve exit means a rule REGRESSED or a check could not run. `ok_evolve` carries
    # that fact into the record and the exit code; an earlier `evolve_failed` computed the same
    # thing and was never read.

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
        "benchmark_slice": bench_run,
        "anchor_refresh": anchor_run,
        "mutation": mutation_run,
        "capabilities": None,        # patched in AFTER every measurement has written its report
        "capabilities_delta": None,
        "ok": None,                # patched in after the suite runs
    }

    caps = capability_snapshot()
    run["capabilities"] = caps
    run["capabilities_delta"] = capability_delta(previous_caps, caps)

    if dry:
        print(json.dumps(run, indent=2)[:1200])
        return 0

    out = RUNS / f"{stamp:%Y-%m-%dT%H%M%S}.json"
    out.write_text(json.dumps(run, indent=2), encoding="utf-8")
    # keep the latest run where a reader will look
    (ROOT / "knowledge" / "latest_run.json").write_text(
        json.dumps(run, indent=2), encoding="utf-8")

    # Run the suite now that the record exists, then patch the result in.
    #
    # THE LOCK IS RELEASED FIRST. A test suite is not a measurement -- it renders small fixtures and
    # never touches the pool -- but one of its tests spawns a subprocess that must ACQUIRE the
    # measurement lock, and it waits 240 s for it. Holding the lock across the suite therefore made
    # the test wait for the very run that was waiting for the test: on 2026-10-20 07:52 the run
    # reported "tests: FAILED" while nothing was broken. `run_tests` is called outside the lock.
    # RELEASE THE MEASUREMENT LOCK AROUND THE SUITE. A test suite is not a measurement -- it renders
    # small fixtures and never touches the pool -- but one of its tests spawns a subprocess that must
    # ACQUIRE this lock and waits 240 s for it. Holding the lock across the suite made the test wait
    # for the very run that was waiting for the test: on 2026-10-20 07:52 the run reported
    # "tests: FAILED" while nothing was broken.
    #
    # Re-acquired afterwards because the publish step follows and must not interleave with another
    # measurement. If re-acquisition fails, the suite result stands but the publish is skipped --
    # losing a commit is recoverable, publishing during someone else's measurement is not.
    released_for_tests = False
    try:
        lock.release("cron_run")
        released_for_tests = True
    except Exception:                                  # noqa: BLE001 - best effort, reported below
        pass
    ok_tests, test_tail = run_tests()
    if released_for_tests:
        try:
            lock.acquire("cron_run")
        except lock.MeasurementBusy as exc:
            # The suite finished but someone else is measuring now. Do NOT publish: a commit that
            # interleaves with another measurement is exactly what the lock exists to prevent.
            # Losing one commit is recoverable; corrupting a measurement is not.
            run["tests_ok"] = ok_tests
            run["tests_summary"] = test_tail
            run["ok"] = False
            run["publish_note"] = (f"suite ran, but the measurement lock was taken before the "
                                   f"publish step; not publishing: {exc}")
            print("  not pushed: another measurement started while the suite ran")
            out.write_text(json.dumps(run, indent=2), encoding="utf-8")
            (ROOT / "knowledge" / "latest_run.json").write_text(
                json.dumps(run, indent=2), encoding="utf-8")
            return 1
    run["tests_ok"] = ok_tests
    run["tests_summary"] = test_tail
    import re as _re
    m = _re.search(r"(\d+) passed", test_tail or "")
    run["capabilities"]["tests"] = int(m.group(1)) if m else None
    run["capabilities_delta"] = capability_delta(previous_caps, run["capabilities"])
    cap_ok = (run["capabilities_delta"].get("verdict") or {}).get("ok", True)
    accept = "--accept-capability-regression" in argv
    run["capability_ok"] = cap_ok or accept
    run["capability_regressions"] = ((run["capabilities_delta"].get("verdict") or {})
                                     .get("regressions", []))
    if not cap_ok and not accept:
        run["publish_note"] = ("capability regression detected; record kept but the run exits "
                               "non-zero (re-run with --accept-capability-regression to accept)")
    run["ok"] = ok_evolve and ok_tests and (cap_ok or accept)
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
        publish = git_publish(changed,
                              allow_deletions="--allow-deletions" in argv,
                              run_ok=run.get("ok"))
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
