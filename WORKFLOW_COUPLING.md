# Is the workflow tightly coupled? An audit of every link

Asked: **"仔细检查WORKFLOW各链路是否紧耦合"** (check carefully whether the workflow's links are
tightly coupled). This is the answer from the code, not from opinion.

## The pipeline as built

`scripts/cron_run.py::_main_locked` runs six things per cycle:

    bench_run    = benchmark_slice()      # re-measure a 6-task slice of the pool
    anchor_run   = refresh_anchor()       # re-measure the frozen 20-task anchor
    mutation_run = mutation_step()        # propose -> probe -> compose
    before       = snapshot()
    after        = snapshot()
    caps         = capability_snapshot()

## The measurement: they share no data

I checked every ordered pair for a data dependency (does step A receive step B's return value?):

    benchmark_slice <- refresh_anchor   no
    benchmark_slice <- mutation_step    no
    refresh_anchor  <- benchmark_slice  no
    refresh_anchor  <- mutation_step    no
    mutation_step   <- benchmark_slice  no
    mutation_step   <- refresh_anchor   no

**Zero.** Each step's return value is written into the run record and consumed by nothing:

    "benchmark_slice": bench_run,
    "anchor_refresh":  anchor_run,
    "mutation":        mutation_run,

That is the whole of their usage. They are three parallel measurements reported side by side, not a
chain.

## What actually couples them: the filesystem, and only the filesystem

    benchmark_slice   -> corpus/e2e/plottwin_report.json   (via scripts/bench_plottwin.py)
    refresh_anchor    -> reads plottwin_report.json
                         writes benchmark_anchor.json, benchmark_shipped_anchor.json
    mutation_step     -> reads plottwin_report.json
                         reads knowledge/mutation_report.json
    snapshot          -> reads all of the above

So the coupling is **temporal through a shared file**, not structural through a value. `refresh_anchor`
reads whatever `plottwin_report.json` happens to contain, which is correct only because the step ran
first. Nothing in the code enforces that ordering; the comment does:

    # ORDER MATTERS: the slice writes the report, and the anchor refresh must follow it

A comment is not a coupling. This project has spent sixty rounds learning that a control which is
documented but not enforced is not a control; the same is true of an ordering.

## The three defects this exposes

### 1. The ordering is asserted in prose and enforced nowhere

`refresh_anchor` would silently read a STALE report if the slice failed or was skipped with
`--skip-benchmark`. There is no freshness check. The anchor would then be re-measured against old
rows and the run would record a number that looks current.

### 2. `mutation_step` reads the report but cannot act on it

This round's previous work added `proposals_from_report`, and the audit confirms the old behaviour:
the step reads `plottwin_report.json` but its candidates come from `mutation.default_space()` -- five
hard-coded integers. **It has the findings in hand and proposes from a menu instead.** That is not
loose coupling; it is a step that ignores its own input.

### 3. The capability snapshot is downstream of everything and gates nothing

`capability_delta(before, after)` compares two snapshots and can FAIL THE RUN. But it compares
AGGREGATES -- task counts, distances, anchors. It cannot see a finding. So a cycle can add a real
defect to a figure, keep the same task count, and the snapshot reports `ok: true`.

## Is that "loosely coupled" or "not coupled"?

Neither word is right. The steps are:

* **not coupled by data** -- no step consumes another's return value
* **coupled by a mutable shared file, in an order nothing enforces**
* **decoupled from the thing they are supposed to serve** -- the findings

That is worse than loose coupling. Loose coupling is a design choice with a contract. This is a
sequence of independent measurements over a shared file, and the only reason it appears to be a
pipeline is that it runs in a fixed order in one function.

## What tight coupling would look like, and whether it is wanted

Not "everything calls everything". Three specific links are missing:

1. **A freshness contract.** `refresh_anchor` must REFUSE to run on a report whose
   `code_version` is not the current one, rather than reading it silently. The report already
   carries `code_version` and `n_fresh`; the check is one comparison.

2. **`mutation_step` must propose from what it read.** The data is in hand. A candidate derived from
   a finding needs a task that reproduces that finding, and the mapping from finding to task already
   exists -- the finding carries `task_id`.

3. **The capability snapshot must be able to see a finding.** Right now `n_ok` and mean distance are
   the only channels, and both can hold while a figure gets worse. A count of hard findings belongs
   in the snapshot, so `capability_delta` can fail a run that introduced one.

## The honest summary

The workflow is **a fixed sequence of independent measurements**, presented as a pipeline by
ordering and a shared JSON file. Every link that matters -- findings to candidates, report to anchor,
snapshot to findings -- is missing, and each one is a small, mechanical addition rather than a
redesign.

That is also the answer to "why no breakthrough": a chain whose links do not carry the signal cannot
propagate an improvement, only record that several measurements were taken.
