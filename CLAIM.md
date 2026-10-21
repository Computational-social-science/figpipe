# The claim, stated precisely

This document exists because a number without referents supports no claim, and a claim without
limits is marketing. Everything below is measured by scripts in this repository and can be
re-run.

---

## What is claimed

On **PlotTwin-Bench** (FigMirror, arXiv 2608.28814), using the benchmark's **own scorer**
`plottwin_scorer` version `deviation-defect-v1`, on its **deterministic code channel**:

| configuration | mean / 100 | tasks |
|---|---|---|
| baseline — matplotlib defaults + this project's compliance floor | **38.16** | 149 |
| **figpipe** — style inferred from the reference **image** | **75.41** | 149 |
| ceiling — style copied from the reference **code** | 100.00 | 149 |

**Improvement over baseline: +37.25 points, 97.6 % relative.**

The code channel is 35 % of the benchmark's combined score (`S = 0.35·S_code + 0.65·S_vision`).
The vision channel is **not run** by this project, so **no combined-score claim is made**.

## Why the pipeline number is legitimate

The benchmark's premise is *reference image + new data → a figure in the reference's style*.
`figpipe` infers the style from the reference **image** — the input a real user has — and emits
matplotlib code that the official scorer reads. Nothing in that path reads the target figure.

The **ceiling** row is shown because the task record also ships `reference_code`. Extracting the
style from that code and emitting the same style reproduces every scored dimension *by
construction*, and scores 100. That is a tautology, not a capability, and it is reported only as a
ceiling so the remaining gap is visible.

## What is NOT claimed

- **Not** a combined-score or leaderboard result: the 0.65 vision channel is out of scope.
- **Not** a claim about semantic correctness of the data analysis. The pipeline verifies that a
  figure is compliant and that its printed claims match its input data
  (`figpipe/semantics.py`); it does not verify that the analysis was the right analysis.
- **Not** a claim of beating any named paper. No head-to-head run against FigMirror,
  NaturePanelForge or DeTi*k*Zify was performed, and none is implied. The comparison here is
  against a **baseline configuration of this same pipeline**, not against another system.
- **Human preference is still unmeasured — but the metric is no longer untested.** A
  discrimination experiment (`scripts/validate_style_metric.py`, artefact
  `corpus/e2e/style_validation.json`) measured whether the style distance ranks a transfer from
  the **matched** reference above a transfer from a **sibling figure in the same paper**:
  **28 of 30 pairs correct, accuracy 0.933, 95 % CI 0.787–0.982**, one-sided binomial
  p = 4.3 × 10⁻⁷ against chance. The deliberately inverted ranking scored 0.033, so the harness
  can fail. The official scorer agreed on **27 of 27 decisive pairs** (3 ties). This is a
  **proxy for ordering, not a reader study**: it shows the metric is not blind or inverted, and
  says nothing about whether an expert would prefer the closer figure. See "The measurement that
  replaced 'pending'" below.

## The measurement that replaced "pending"

`CLAIM.md` used to say that whether the style metric tracks expert preference "has not been
measured yet", and `LOGICAL_AUDIT.md` §1 named the same sentence as the project's residual risk.
A reader study is still not possible here. A **discrimination experiment** is, and it closes the
part of that gap that can be closed deterministically.

**Design.** For each of 30 real published figures in `corpus/extracted/` (vector PDF regions, so
the profile is measured from the PDF's own objects rather than guessed from pixels), figpipe
renders two candidates from **identical data** and the **same grammar**:

| | style source |
|---|---|
| **A** | a MISMATCHED figure — another figure **in the same paper**, so the house style is held constant |
| **B** | the MATCHED reference itself |

The only difference between A and B is the style source, so the question is exactly the one the
metric claims to answer: does `styleprofile.compare` put B closer to the reference than A?

**Result.**

| quantity | measured |
|---|---|
| pairs | 30 |
| B ranked closer (hard, same-paper contrast) | **28 / 30** |
| **discrimination accuracy** | **0.933** (95 % CI 0.787–0.982) |
| one-sided binomial p vs chance (0.5) | 4.3 × 10⁻⁷ |
| negative control — inverted ranking | 0.033 (passes: a harness that cannot fail proves nothing) |
| easy contrast (different paper), for reference | 30 / 30 = 1.000 |
| official scorer (`deviation-defect-v1`) agreement | 27 / 27 decisive (3 ties) |

**What this does and does not establish.**

- It **does** establish that the metric is not blind and not inverted: every one of the six
  components ranks the matched transfer closer more often than not
  (`aspect` 1.00, `letters` 1.00, `lines` 0.77, `sizes` 0.75, `palette` 0.73, `rules` 0.71),
  and the aggregate is 28/30.
- It **does not** establish that the closer figure is the better figure. A metric can
  discriminate perfectly and still disagree with an expert about which of two close candidates
  is preferable. No human judgement was collected, and none is implied.
- **It is substantially an aspect check.** Leave-one-out: withholding `aspect` alone drops
  accuracy to **0.700** (Δ −0.233); withholding any other single component leaves it at 0.933.
  Most of the discrimination therefore comes from **figure aspect** — the easiest property to
  reproduce — not from palette or typography. `letters` is decisive on only 1 of 30 pairs, so
  its 1.00 is not evidence of anything. A metric whose accuracy is carried by one cheap
  dimension is weaker than its aggregate suggests, and that is the honest reading here.
- The **easy** contrast (mismatch from a different paper) is 30/30, which is a ceiling rather
  than a sensitivity result: two unrelated papers differ in palette, type and layout at once.
  The headline above is deliberately the **hard** arm.

**Why the official scorer is run on the same pairs.** Two independent deterministic instruments
agreeing is evidence about which is measuring style. The official channel is a *deviation*
score (100 = the candidate's style calls match the reference's), run on code emitted from the
**rendered** candidates' own measured profiles — so it describes what actually came out rather
than what the transfer intended, and it is not true by construction. It agreed on every pair
where it expressed a preference.

## The dimensions that cap the number

The official channel averages the reference-activated dimensions. Per-dimension means
(baseline → figpipe):

| dimension | baseline | figpipe | note |
|---|---|---|---|
| palette | 0.002 | **0.648** | dominant gain |
| grid | 0.000 | **0.829** | dominant gain |
| figure_aspect | 0.480 | 0.869 | |
| spines_removed | 0.874 | 0.965 | |
| linewidth | 0.574 | 0.574 | **not recoverable from a raster** |
| legend_frame | 1.000 | 1.000 | |
| tick_direction / serif / background | 0.000 | 0.000 | **code constructs; a picture cannot show them** |

The last four are 0 or unchanged because a raster image does not contain them. That ceiling is a
property of the **input modality**, not of the pipeline, and is stated rather than hidden.

## How to reproduce

```bash
python scripts/score_official.py --limit 150 --source naive    # baseline
python scripts/score_official.py --limit 150 --source image    # pipeline
python scripts/score_official.py --limit 150 --source code     # ceiling
python -c "import sys; sys.path.insert(0,'scripts'); import score_official as s; print(s.comparison())"
```

The three runs write to **separate files** (`official_scores_naive.json`,
`official_scores.json`, `official_scores_code.json`) because two modes writing to one path
silently destroyed the honest result once.

## Provenance and licence

- Scorer: `third_party/plottwin_scorer/`, copied **unmodified** from the benchmark repository.
  Licence **CC BY-NC 4.0** — local evaluation only, not packaged, not redistributed.
  See `third_party/plottwin_scorer/NOTICE.md`.
- Benchmark data: cached locally and gitignored; never redistributed.
- Every number above is regenerated by `scripts/build_report.py` from those artefacts.


## Update 2026-10-21: what the style metric actually measures

The style metric was validated at 0.9333 discrimination accuracy with a recorded caveat that
withholding `aspect` drops it to 0.700. Re-deriving each component ALONE from the same 30 pairs
(`scripts/validate_metric_claims.py`) gives:

    aspect 0.867 | palette 0.533 | rules 0.500 | sizes 0.400 | lines 0.333 | letters 0.033

So on its own validation corpus the metric is **very nearly an aspect-only check**: one component
carries the discrimination and the other five are at or below chance. This is NOT overfitting -- a
leave-one-out weight search scores the same 0.867 -- but it does mean the metric should not be
described as measuring style broadly. It measures aspect, reliably, and almost nothing else.

**What this does NOT invalidate.** The official benchmark score (75.41 over 149 tasks, baseline
38.16) uses the benchmark's own deterministic scorer, not this metric. The style metric is used for
the reference-transfer arm, where its job is to order two candidates, and at that job it is above
chance on every arm measured.

**What it does change.** Human validation is now the only way to establish that the metric tracks
anything a reader cares about. The question is sharper than "is the metric good": it is "does a
reader prefer the figure the metric calls closer, when the difference is NOT mainly aspect".


## Update 2026-10-21 (second): the aspect finding replicates, and the weight claim does not

The aspect-only finding was made on 30 pairs. A claim that holds only on its own sample is a claim
about the sample, so a SECOND pair set was built with a different seed (20261021, same corpus, same
floors). Results:

    dimension     main   holdout   delta
    aspect        0.867   0.900    +0.033
    palette       0.533   0.467    -0.066
    rules         0.500   0.467    -0.033
    sizes         0.400   0.467    +0.067
    lines         0.333   0.200    -0.133
    letters       0.033   0.067    +0.034

**The aspect finding REPLICATES**: aspect is the leading component on both sets, and every other
component is at or below 0.533 on both.

**The equal-weight claim does NOT replicate.** The main set said equal weights score 0.967 against
the declared 0.900. On the independent set BOTH score 0.933. So the equal-weight advantage was
tuning noise, and the declared weights are not measurably worse. This is recorded because the
previous update reported 0.967 with a caveat that it "proves nothing" -- the holdout now turns that
caveat into a measured result rather than an open question.

The whole comparison is reproducible: `python scripts/validate_metric_claims.py`.
