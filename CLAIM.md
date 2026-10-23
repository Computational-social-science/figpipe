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
| baseline — matplotlib defaults + this project's compliance floor | **37.36** | 148 |
| **figpipe** — style inferred from the reference **image** | **79.02** | 148 |
| ceiling — style copied from the reference **code** | 99.19 | 148 |

**Improvement over baseline: +41.66 points, 111.5 % relative.**

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

**What this does NOT invalidate.** The official benchmark score (78.95 over 148 tasks, baseline
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


## Update 2026-10-21 (third): the "aspect-only" reading was too strong, and here is why

The previous update said the metric is "very nearly an aspect-only check". That was too strong, and
the way it was wrong is worth recording.

**WHY aspect dominates.** `transfer_style` applies EVERY dimension it measures -- including setting
the candidate's height from the reference's width/height. So the `aspect` component is testing
whether the transfer RAN. It never gets a pair wrong (26 right, 0 wrong, 4 ties), which is the
signature of a PLUMBING check, not a measurement of style fidelity.

**BUT removing aspect does not collapse the metric:**

    all 30 pairs, aspect removed            0.800
    26 pairs where aspect differs, removed  0.808
     4 pairs where aspect is equal, removed 0.750

The other components are weak and noisy but not zero (palette 16 right / 6 wrong; sizes 12 right /
4 wrong with 14 ties). So the correct statement is:

> **aspect supplies most of the MARGIN but not all of the SIGNAL.**

The earlier phrasing would have led a reader to discard five components that do carry real signal,
and to conclude the metric is worthless when it is merely weak. Both errors matter.

**What is still NOT established** is unchanged: nothing shows the metric tracks what a READER cares
about. That remains the one claim only human validation can settle, and the question is now precise:
does a reader prefer the figure the metric calls closer when the difference is NOT mainly aspect?


## Update 2026-10-21 (fourth): the ablation run -- 0.933 with aspect, 0.733 without

The previous update said the other five components "carry a real but weak signal", measured by
removing aspect from the WEIGHTS. That analysis re-weights the same numbers and cannot tell you what
a different TREATMENT would produce. So the treatment itself was changed: `transfer_style(...,
apply_aspect=False)` renders the candidate at a fixed height, and the experiment was re-run.

    with aspect applied    0.9333   95% CI [0.787, 0.982]   p = 4.3e-07
    aspect withheld        0.7333   95% CI [0.556, 0.858]   p = 0.008

**+0.20 of the headline accuracy was the plumbing check.** And **0.733 is the metric's real ability
on style dimensions** -- weak, but statistically above chance (p = 0.008, CI lower bound 0.556).

Both halves matter:

* a reader who saw only "aspect is a plumbing check" would conclude the metric is worthless. It is
  not: it discriminates at p < 0.01 without aspect.
* a reader who saw only "0.933 accuracy" would believe the metric measures style broadly. It does
  not: a fifth of that is a check that the transfer ran.

**The diagnostic is not a shipping mode.** The shipped pipeline still applies the reference's aspect,
because a figure at the wrong aspect is the wrong figure. `--no-aspect` exists to make the ablation
runnable, and the run records a warning when a dimension the transfer should have moved did not.

Reproduce: `python scripts/validate_style_metric.py --no-aspect --contrast same --seed 20261021`.


## Update 2026-10-21 (fifth): my "below chance" component readings were a scoring artefact

The earlier updates reported per-component accuracies like `letters 0.033`, `lines 0.333`,
`sizes 0.400` and concluded those components were "at or below chance". **That was a measurement
error in my analysis, not a property of the metric.**

A component's gap is a weighted distance in [0,1]. When the gap between the two candidates is below
the measurement's resolution (~0.05), the component has NO OPINION -- and the all-pairs table counted
that as a wrong answer, dragging every row toward zero. Scored only where the gap is resolvable:

    dimension   n    acc
    letters     1   1.000
    aspect     25   1.000
    palette    15   0.867
    lines      13   0.769
    sizes      15   0.733
    rules      21   0.714

**Every component is 0.71 to 1.00 accurate where it has a resolvable opinion.** None is broken. The
metric is WEAK because most pairs do not separate on most dimensions, not because its components are
wrong.

This is the same defect the project keeps finding in the pipeline -- **an absence of information
reported as a violation** -- appearing in the analysis of the metric rather than in the metric. The
earlier claim that five components "contribute nothing" should be read as "contribute nothing ON
MOST PAIRS, because most pairs do not differ on them".

The validator now prints both tables, with a warning on the all-pairs one, and a test asserts the
two disagree sharply so the distinction cannot be silently dropped.


## Update 2026-10-21 (sixth): the ablation was confounded, and the real effect is 0.133

The previous update reported "0.933 with aspect, 0.733 without, so ~0.20 of the headline accuracy is
the plumbing check". **The 0.20 was wrong, and the ablation was not an ablation.**

The ablation run used seed 20261021 while the main run used 20261019. Only **2 of 30 pairs** were
shared. So the comparison mixed two changes at once -- withholding aspect AND a different sample --
which is exactly what an ablation must not do.

Re-run with the SAME seed (30 of 30 pairs shared):

    main, aspect applied   (seed 20261019)   0.9333
    TRUE ablation          (seed 20261019)   0.8000   <- the only valid number
    first attempt          (seed 20261021)   0.7333   <- confounded, overstated by 0.067

**The real effect of withholding aspect is 0.133, not 0.200.** The confounded run overstated it by
half again as much as the true value's own uncertainty.

Both runs are kept on disk and the validator reports both, with the pair overlap printed next to each
number. The lesson is in the artefact, not only in a changelog: a reader can see that the confounded
run shared 2 of 30 pairs and drew a different conclusion from the same metric.

**What survives unchanged:** aspect is a plumbing check (it never gets a pair wrong because the
transfer applies it), and the metric is weak but real on style dimensions. **What changes:** the
plumbing check is worth ~13 points of the headline accuracy, not 20, and the metric without aspect
scores 0.80 -- better than the 0.733 previously reported.


## Update 2026-10-21 (seventh): two dimensions are tested on a figure that cannot express them

Asked to improve `palette` (the load-bearing component after the ablation), I found the component is
not the problem -- the EXPERIMENT is.

THE MEASUREMENT THAT FOUND IT: `palette_from_profile` truncates at 4 colours, and the corpus's
references have 12 to 99 usable colours. Raising the truncation to 6 was a plausible fix. It changed
**0 of 30 pairs.** Not one distance moved.

THE REASON: the validation draws a **single-series trend panel**. One series uses one colour, so a
longer palette cannot appear in the figure at all. Reverting the change, and the number stays at 4
until there is a multi-series panel to measure it against.

THE GENERALISATION -- tie rate per dimension on the ablation run:

    letters  28/30    one panel  -> no panel letters can appear
    lines    17/30    one line   -> little stroke variety
    sizes    14/30    font tiers DO vary
    rules     9/30    grid and spines DO vary
    palette   8/30    one series -> one colour

The two highest tie rates are exactly the two dimensions a single-series single-panel figure cannot
express. **A dimension the figure cannot express ties on almost every pair, and a tie is a limit of
the EXPERIMENT, not a weakness of the metric.**

So "palette scores 0.727" reads as "the component is weak" when the truth is "the panel gave it
nothing to see". The actionable next step is a multi-series, multi-panel validation figure -- not a
change to the metric.

The validator now prints the tie rate with the reason next to each dimension, and tests assert that
`letters` still ties almost always (so the panel has not silently changed) and that widening the
palette still moves nothing (so the limitation stays attributed to the panel).


## Update 2026-10-21 (eighth): the figure those two dimensions needed, and a mechanical check

Round 48 diagnosed that `palette` and `letters` are tested on a figure that cannot express them. This
round built the figure that can, and verified the diagnosis mechanically rather than by argument.

`scripts/check_panel_expressibility.py` renders both panels, re-profiles the OUTPUT, and counts how
many of a supplied palette's colours and how many panel letters actually arrived:

    single-series panel (what the validation used)    palette 1/3    letters 1
    multi-series multi-panel figure                   palette 3/3    letters 2

**Both directions are checked.** If only the second were, a figure that showed colour for an
unrelated reason would pass. The single-series panel carrying 1 of 3 supplied colours is the
positive evidence that the limitation is real, not folklore.

`validate_style_metric._multi_panel()` now builds that figure: three series coloured from the
reference's own palette, across two lettered panels. It is not yet wired into the headline
experiment -- the run cost is real and the ordering should be deliberate -- but the instrument now
exists and is tested, which is the prerequisite for measuring those two dimensions at all.

**What this changes about the reported numbers.** `palette 0.727` and `letters 1.000` are not
measurements of those components; they are measurements of what a one-series one-panel figure could
show of them. They should be read as "untested", not as "weak" and certainly not as "strong".
