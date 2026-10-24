# Why there is no breakthrough: the reward is saturated, not the pipeline

Asked directly: **"是PIPELINE链路不科学，还是缺少关键链路，如REWARD机制？梯度收敛？"**

The question names three possibilities. Measured, the answer is the second one, and it is worse than
"missing" -- the reward exists, it is wired in, and **it is constant**.

## The measurement that settles it

The mutation loop scores every probe with:

```python
def _render_score(hard_failures: int) -> float:
    """`1 - n/(n+1)`: 0 hard findings -> 1.0, 1 -> 0.5, 2 -> 0.667, 19 -> 0.05."""
    n = max(0, int(hard_failures))
    return round(1.0 - n / (n + 1), 6)
```

Across all 139 pool tasks:

    hard_failures = 0 : 139 tasks
    reward = 1.0      : 139 tasks
    distinct values   : [1.0]

**The reward is 1.0 everywhere. The gradient is identically zero.** A loop climbing this surface is a
ball on a perfectly flat table: it moves, it measures, and no direction is better than any other.

That is not "a missing reward channel". It is **a saturated one** -- which is harder to notice,
because the number looks healthy.

## Is the pipeline unscientific? No, and that is the problem

The pipeline is the best-understood part of this project. Measured this session:

    correctness        709 -> 863 tests, negative controls for every check
    measurement        139/139 coverage, every zero has a denominator
    provenance         artefacts recorded, instrument fingerprints, membership reported
    premise            honest vs ceiling modes kept apart (round 100 fixed a violation)
    reproducibility    every claim re-derivable from a run record

The score moved **7 times in five days**, and **6 of those moves were mine**, not the loop's:

    147 commits since 2026-10-19
     44 written by the scheduled loop   (all of them "run: record ...")
    103 written by me

The loop's own contribution to the official score across its whole life is **zero**. Not because it
measured wrong -- because there was nothing to climb.

## The three things the question asks about

**REWARD机制** -- present, wired into `mutation.probe` and `mutation.compose`, and **saturated**. The
loop cannot distinguish a candidate that would raise the official score by 9 points from one that
changes nothing, because both leave `hard_failures` at 0.

**梯度收敛** -- there is no gradient. `_render_score` maps every task in the pool to the same value, so
every candidate's mean score is 1.0 and every contrast is 0.0. The 222 ties and 149 empty selections
recorded over 152 runs are the arithmetic consequence: **a tie is what a zero gradient looks like in a
comparison.**

**PIPELINE链路** -- not unscientific. It is a well-instrumented pipeline whose optimisation target is
disconnected from the number it reports. That is a different defect from a bad pipeline: a bad pipeline
gives wrong answers, this one gives right answers about the wrong objective.

## Why this took a hundred rounds to see

Because the two numbers never had to meet. The pool reports `hard_findings: 0` and
`official_code_score: 82.02` side by side, and both are correct. Nothing in the system compares them,
so nothing notices that one is the loop's reward and the other is the claim.

The loop optimises what it can see (hard findings). The claim reports what the benchmark measures
(official score). **They are not the same quantity, and no link in the workflow requires them to be.**

## What a working reward would look like

Not a new pipeline. One connection:

    probe(candidate) -> official.score_code_deviation(reference, candidate)

The scorer is already vendored, already called by the scoring pass, and already returns a per-dimension
breakdown. A candidate that changes `linewidth` from 0.8 to the reference's value moves that number by
50 points on one task. **The loop has never been told that.**

The measurement that would justify the change is small: run the existing five candidates through the
official scorer instead of `_render_score`, and see whether the ranking changes. If it does, the reward
was the defect. If it does not, the search space is.

## The honest summary

**The pipeline is not unscientific. It is scientific about the wrong thing.**

Every instrument this project built is correct, and the objective those instruments feed is flat. Rounds
82-100 produced real gains (+7 points on the official channel) -- **all of them by a human reading
dimension tables, none of them by the loop**, because the loop's reward cannot tell those gains apart
from noise.

That is the answer to "why no breakthrough": the breakthrough mechanism has no signal to amplify.


## Correction, round 101: the proposal in the section above does not work

I wrote that the fix is one connection --

    probe(candidate) -> official.score_code_deviation(reference, candidate)

**Measured, that connection produces no gradient either**, because the search space does not contain
anything the official scorer can see.

### What the loop actually searches

    split-max-bars-24     layout.split_panels.max_bars:  12 -> 24
    split-max-bars-13     layout.split_panels.max_bars:  12 -> 13
    matrix-max-rows-41    encode.matrix.max_rows:        40 -> 41
    matrix-max-rows-42    encode.matrix.max_rows:        40 -> 42
    matrix-max-rows-60    encode.matrix.max_rows:        40 -> 60

### What the loop actually measures

    7 tasks, every one of them `expect: refused` or `expect: clean`

**The whole loop is a refusal classifier.** It asks "should this input be rejected", and its reward is
1.0 when the answer is right. That question has no style content at all.

### The measurement that closes the door on my own proposal

Emitting the same figure with one panel and with two panels -- which is exactly what a layout candidate
changes -- and running the official extractor on both:

    background       #ffffff        same
    figure_aspect    2.0333         same
    grid             True           same
    legend_frame     False          same
    linewidth        0.8            same
    palette          [#0072b2, ...] same
    serif            False          same
    spines_removed   [right, top]   same
    tick_direction   out            same

**Every scored dimension is identical.** Wiring the official scorer into `probe` would replace one
constant reward with another constant reward, and cost 149 scoring passes to learn it.

### So which is it: missing reward, or wrong search space?

**Both, and the second one comes first.** A reward can only rank what the search produces. This search
produces layout budgets; the benchmark scores style. No reward function over this space can point at
the style improvements that were worth +7 points, because none of them are in the space.

### The correct fix, in order

1. **Put style in the search space.** `skills.run` already accepts `profile=<StyleProfile>` and routes
   it through `op_style_profile`; the emitter already has `style_from_image_profile`. A candidate like
   `linewidth: 0.8 -> 2.25` is expressible today -- the `Candidate` dataclass holds
   `(operator, parameter, baseline_value, value)` and nothing in it requires a layout parameter.
2. **Then** point the reward at `official.score_code_deviation`, which now has something to rank.
3. Keep the refusal classifier -- it is a real capability, it is just not the one the benchmark scores.

**The lesson is about the order of the two questions.** "Is there a reward?" and "is there anything to
reward?" are different, and I answered the first one loudly and the second one not at all.
