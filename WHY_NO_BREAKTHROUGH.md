# Why there has been no breakthrough: the workflow has a structural defect

Asked directly: **"为什么始终没有突破？是WORKFLOW链路存在逻辑缺陷？"** This is the answer, from the
project's own records rather than from opinion.

## The measurement

Every scheduled run writes `knowledge/runs/*.json`. Across **152 runs**:

    knowledge changes        4
    mutation verdicts        222 tie / 63 rejected / 5 selected
    selections               149 runs selected NOTHING
    what was selected        `matrix-max-rows` 41 and 42, three times

Meanwhile the styled anchor moved **0.357 -> 0.335** over rounds 50-63, and **every one of those
improvements came from a commit written by hand, not from the loop.**

So the loop is not failing to find improvements. It is **structurally unable to represent them**.

## The defect, stated precisely

The loop's proposal stage is `figpipe/mutation.py`, whose entire search space is five candidates:

    split-max-bars-24     layout.split_panels:max_bars  12 -> 24
    split-max-bars-13     layout.split_panels:max_bars  12 -> 13
    matrix-max-rows-41    encode.matrix:max_rows        40 -> 41
    matrix-max-rows-42    encode.matrix:max_rows        40 -> 42
    matrix-max-rows-60    encode.matrix:max_rows        40 -> 60

probed on seven synthetic tasks (`split-many-bars`, `matrix-real-40x10`, ...).

`mutation_step()` in `scripts/cron_run.py` **does not read `corpus/e2e/plottwin_report.json`**. It
never sees the pool's findings. So:

* every real defect this project has fixed -- the 9 text collisions, the polar label overflow, the
  colour bar falling off the page, the pivot choosing a row index as its measurement -- was found by
  a human reading a report, and **none of them was expressible as a candidate** the loop could
  propose.
* the loop can only move five budget integers by +1 or +2. Four of the five do not change any figure
  at all on the probed tasks, which is where the **222 ties** come from.

**The workflow is a closed loop around a fixed five-item menu.** It measures, it proposes from that
menu, it selects almost nothing, and it reports honestly that nothing changed. Every part of that is
working. The menu is the defect.

## Why "no breakthrough" follows from this

A breakthrough requires the system to *discover* something it was not told to look for. This
workflow's discovery channel is exactly five hard-coded integers. It cannot discover anything else,
and it has not.

Rounds 44-63 improved the project substantially -- hard findings 9 -> 0, coverage 110/139 -> 139/139,
anchor 0.357 -> 0.335. **Every one of those was me, using the loop's measurements as a dashboard.**
The dashboard works. The driver is not connected.

## The second structural defect: the loop cannot fail a figure

`capability_delta` compares snapshots, and the benchmark reports `n_ok`, distances and anchors. None
of those can express "this figure is wrong in a way a reader would notice". The loop optimises
proxies -- style distance, task success -- and a proxy can improve while the thing it proxies gets
worse. That is why `human validation` has sat on the board as "Next step" for sixty rounds: **there
is no channel from a human judgement back into the loop.**

## What would actually change this

Not more checks. The three that would matter:

1. **Generate candidates from findings.** The pool already records `semantics.*`, `overlap`,
   `font_size` findings with task ids. A candidate is `(operator, parameter, direction)` derived from
   a finding's shape. This is the missing link and it is mechanical -- the data is on disk.

2. **Let a proposal be a CODE EDIT, not a scalar.** The five candidates are integers because the
   probe harness can only re-run a scalar. A drawer change (the label wrap, the pivot role rules)
   cannot be expressed. Until a proposal can be a patch, the loop is confined to tuning.

3. **A human-judgement channel.** One boolean per figure from a reader, recorded, is enough to make
   the proxy falsifiable. Without it the project can only report that its own metric improved.

## The honest summary

The loop is **correct and useless**: it does exactly what it is built to do, and what it is built to
do cannot produce a breakthrough. The defect is not in the measuring, the gating, the locking or the
publishing -- all of which I have audited for sixty rounds and fixed repeatedly. It is in the one
place I never changed: **what the loop is allowed to propose.**

That is the next piece of work, and it is the only one that addresses the question asked.
