# What was actually learned, whether it generalises, and what did not advance

Measured 2026-10-25 from the artefacts, not from memory.

## 1. What skills were acquired

    code capabilities    16 skills, 21 operators
    knowledge base       16 rules, 8 with a machine check
    lessons              179 entries: 42 a defect found, 10 a limit measured, 127 other
    test suite           914 passed, 7 skipped (from 709 at the start)
    commits              273 total: 97 by the scheduled loop, 176 by the agent
                         120 of the agent's are fix/feat

**The skills are of one kind.** Reading the 179 titles: the project learned to build INSTRUMENTS --
guards, negative controls, reason codes, re-derivation steps -- far more than it learned about figures.
That is the honest characterisation: **the capability that grew is measurement discipline, not drawing.**

## 2. Does it generalise

### The rendering layer generalises

Tested every skill with synthetic data it was never tuned on:

    rendered: 14/16

The two failures are DATA mismatches, not capability gaps -- `density_relationship` needs positive values
for a log axis, `field_map` needs a 2-D grid. Both refuse with a message naming the reason, which is the
behaviour this project demands.

### The measurement layer generalises, and this is measurable

A lesson applied in ONE place is a fix; applied in SEVERAL places it is a generalisation. Measured by
searching the source:

    "a None must say why"            in 34 files
    "a guard needs a negative control" in 34 files
    "print the failure"              in  5 files
    "re-derive the claim"            in  3 files

**The first two are the generalised ones**: 34 files each. They stopped being lessons and became habits.

### The claim layer generalises least

`claim_rederivation` exists in 3 files. It is the newest and it has run successfully exactly ONCE.

## 3. What did NOT advance

### The official score is flat since 2026-10-25 05:37

    2026-10-24 01:18   75.41 -> 75.44
    2026-10-24 02:33   75.44 -> 78.95
    2026-10-24 03:04   78.95 -> 79.02
    2026-10-24 06:22   79.02 -> 82.02
    2026-10-25 02:49   82.02 -> 83.69
    2026-10-25 05:37   83.69 -> 84.33
    2026-10-25 08:50   84.33 -> 84.08   <- the count fix cost 0.25
    2026-10-25 11:59   84.08            <- flat

**Every one of those moves was made by the agent reading a dimension table. The scheduled loop has never
moved this number.** The loop's contributions are 97 commits of `run: record ...`.

### The loop selects, but rarely and never profitably

    200 runs
    knowledge changes:        0
    hypotheses promoted:      0
    mutation selections:      matrix-max-rows-41 x3, matrix-max-rows-42 x2, sizes-plus-half x2

Two of those three selections were later shown to be artefacts: `sizes-plus-half` was cancelling a
font-tier bug the agent then fixed, and after the fix it is correctly rejected.

### Three sub-tasks were declared unwinnable, with measurements

    linewidth      +9.01 pts   one pixel is the whole decision at ~150 dpi
    figure_aspect  +2.53 pts   bbox_inches="tight" destroys the canvas aspect
    serif          +0.92 pts   serif footings are sub-pixel at 5-7 pt

Together 12.5 of the 16.3 points that remained. **These are not "not yet done"; they are bounded by the
benchmark's construction.**

### The one sub-task that never advanced at all

**Human validation.** It has been the "next step" in every round for a hundred rounds. It is the only
claim no script can settle, and it is the only one still open.

## 4. The honest summary

**What was learned:** how to build instruments that cannot lie to themselves. 42 defects found, each with
a guard, each guard verified with a negative control.

**Whether it generalises:** the two strongest lessons reached 34 files and stopped being lessons. The
weakest reached 3 files and has run once.

**What did not advance:** the score is flat because the image channel is exhausted, the loop cannot select
because its reward is saturated or its space is empty, and human validation has never been attempted.

**The uncomfortable measurement:** the loop wrote 97 commits and moved the score zero times. The
self-evolution that happened was the agent's, using the loop's RECORDS as evidence. **The loop is a
camera, not an engine** -- and knowing that is worth more than the 8.7 points it did not produce.
