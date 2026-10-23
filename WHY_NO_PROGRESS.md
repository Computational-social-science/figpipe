# Why there is no substantive progress: the honest answer

Asked directly, again. This time the answer is in the project's own numbers, and it is uncomfortable.

## The measurement

Across 115 run records, only FOUR distinct official scores exist:

    2026-10-19 06:43   92.68
    2026-10-19 07:32   93.53
    2026-10-19 08:13   70.59     <- the drop
    2026-10-19 09:23   75.41     <- and then nothing, for four days

**The score has not moved since 2026-10-19 09:23.** Every commit since then -- and there are 43 of
them -- changed something, but not the number that matters.

The styled anchor DID move: 0.359 -> 0.335 over the same period. So the project improved on its own
proxy while the official metric stayed flat.

## What the 92.68 -> 70.59 drop actually was

It is recorded in `KNOWN_CORRECTIONS`:

> 93.53 -> 70.59. The earlier number came from the in-harness aggregate, which scores only tasks
> whose cache entry carried `reference_code` and copied the reference's own code features -- a
> tautology.

So the drop was a CORRECTION, not a regression: the earlier number was measuring the wrong thing.
**75.41 is the first honest score this project ever produced.** Everything after it has been work
that did not move an honest score.

## The three reasons, in order of how much they cost

### 1. The remaining 25 points are not reachable by the work being done

`75.41` is the CODE channel only. The benchmark's combined score is `0.35*S_code + 0.65*S_vision`,
and the vision channel is NOT RUN. So:

* the ceiling on everything this project can measure is 35 % of the official score
* rounds 44-76 improved code-channel-adjacent things -- label wrapping, colour bars, axis checks,
  pivot roles, coverage bookkeeping -- and the code channel went from 75.41 to 75.41

The last twenty rounds produced **zero movement on the only scored channel**, because they were
about the FIGURE's correctness, and the code channel scores the CODE that would reproduce it.

### 2. The work has been on the instrument, not the output

Count the commits since the score last moved:

    coverage bookkeeping      unverifiable 29 -> 0, five states, partial verification
    the checks themselves     colour scale, axis range, mesh data, planted truth
    the workflow              freshness, membership, instrument, coupling
    the catalogue             patch probing, contribution measurement
    detectors                 name collisions, tautology, tripwire

Every one of those makes the project **better at knowing whether it is right**. None of them makes
a figure that scores higher. That is real work and it is not progress toward SOTA, and I have been
reporting it as progress.

### 3. The loop still cannot propose anything that would help

Three rounds of diagnosis established that the mutation loop's search space is five budget integers
and `compose` could only judge scalars. Both are now fixed -- patches can be proposed and judged --
but the catalogue has FIVE entries, all of them fixes this project already made. **A catalogue of
fixes already applied cannot discover a new one.** The loop can now measure its own history; it
still cannot generate a hypothesis.

## What would actually move the score

Not more checks. The three things, in order:

1. **Run the vision channel.** 65 % of the score is unmeasured. Every figure this project draws is
   judged by a code proxy while the benchmark would judge it by a VLM. A local VLM is installed
   (59 ollama models, `gemma3:12b` was tested and failed a control -- but that was ONE model and
   the controls are now written). Until the vision channel runs, no amount of figure work can be
   shown to help.

2. **Improve the CODE channel directly.** It is 35 % and it is at 75.41. The gap is in the generated
   code's deviation from the reference's, which is a different problem from label wrapping.

3. **Let the loop generate, not just measure.** A catalogue of past fixes is memory. A hypothesis
   generator -- even a weak one that proposes a patch and lets the probe reject it -- is the only
   thing that turns this from a very well-instrumented static pipeline into a learning one.

## The sentence I should have written twenty rounds ago

**The project has been getting better at measuring itself while the thing being measured has not
changed.** Every round I reported a defect count, a coverage number, a check added. None of those is
the score, and I let the first three substitute for the fourth.

That is the answer to "why no substantive progress": the work was real, and it was aimed at the
instrument.
