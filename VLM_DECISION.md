# Whether to introduce a local VLM, and what the measurement says

Asked: **"如果必要引入VLM，就引入本地化VLM"** (if a VLM is necessary, introduce a localised VLM).

The honest answer is **not necessary, and here is the measurement that says so** -- followed by what
IS worth taking from the idea. This note exists because "no" without evidence is an opinion, and
"yes" without evidence would undo work this project already did.

---

## What is already in the repository

The corpus labelling pass was **already local**: `corpus/vlm_report.json` records
`models: ["gemma3:12b"]`, 40 figures, 840 field slots, JSON parse rate 1.0. It ran on this machine.

So the question is not "local or cloud" -- it was never cloud. The question is **whether the
labels can be trusted**, and that was tested.

## The control experiment

`corpus/vlm_controls.json` fed the model three images that contain **no figure at all**:

| control image | what it is | fields asserted | **fabricated** |
|---|---|---|---|
| `control_blank.png` | a blank page | 7 | **2** |
| `control_noise.png` | random strokes | 15 | **9** |
| `control_textonly.png` | text, no figure | 12 | **9** |

**20 fabricated values across 3 controls.**

The specific fabrications are the damning part, because they are the fields the corpus most wanted:

    control_blank.png   ->  "column_width": "single"
    control_noise.png   ->  "high_contrast": true

A model that reports `column_width: single` about a **blank page** cannot be the ground truth for
column width. A model that reports `high_contrast: true` about **random strokes** cannot be the
ground truth for contrast. These are not near-misses on hard cases; they are confident answers about
images that contain nothing to answer about.

That is why `CLAIM.md` excludes the official benchmark's 0.65 vision channel, and why the 75.41
official score is reported as *image-inferred* rather than vision-scored.

## What the fields decompose into

The VLM was asked for ten fields. Measured against what figpipe can determine without a model:

| field | deterministic replacement | status |
|---|---|---|
| `column_width` | `audit.width` | **already measured** |
| `font_uniform` | `audit.font_type` | **already measured** |
| `min_font_legible` | `audit.font_size` | **already measured** |
| `panel_count` | `result.panels` | **already measured** |
| `high_contrast` | `colourcheck` | **already measured** |
| `frame_restrained` | `styleprofile` | **already measured** |
| `figure_type` | `structure.figure_type` | **NEW this round** |
| `panel_labels_present` | `structure.panel_labels_from_sizes` | **NEW this round** |
| `arrow_style` | -- | genuinely unmeasured |
| `panel_layout` | -- | partly inferable, not done |

**Eight of ten are now deterministic.** Two remain, and neither is worth a model that fabricates on
blank pages.

## The two new measurements, and how they were found

`figpipe/structure.py` reads the PDF's own text layer. The non-obvious part, found by measurement:

> **Panel letters are drawn at a larger font size than every axis label and tick.**

Matching on text alone reported the panel letters of a 4-facet histogram as `['v', 'a']` -- `v` was
the **y-axis label**. Font size separates them exactly:

    multi-panel  -> ['a', 'b']     (8.0 pt, above the 7.0 pt axis labels and 6.0 pt ticks)
    single-panel -> []             (no letter above the axis-label size)

And the figure-type classifier had the same kind of error: the word `density` is an **axis label** on
a histogram, and the first version called every such figure a `heatmap`. A heatmap's distinguishing
feature is a colour bar, which a text-only reader cannot see -- so the honest answer for a matrix
figure is `other`, not a confident wrong guess.

## When a VLM WOULD be worth it

Not never. A local VLM would be justified for a field that is:

1. **visually decidable** -- a reader can answer it by looking, and
2. **not expressible as a deterministic check**, and
3. **verified against controls before being trusted**

`arrow_style` meets (1) and (2). It does not yet meet (3) -- nothing has shown that any local model
here answers it reliably, and the model on this machine failed the controls it was given.

The path to using one honestly is therefore:

* build a control set specific to the field (blank, noise, text-only, and a figure whose true value
  is known by construction)
* require the model to answer the controls correctly before its labels count
* use the labels as a **second opinion that is checked** (`structure.compare_to_vlm`), never as an
  answer key

That is a measurement project, not a feature. It is worth doing when a field is genuinely needed and
no deterministic route exists -- not before.

## What was NOT done, and why

No model was wired into the judging path this round. Adding one would have changed the official
score from "deterministic, reproducible, 75.41" to "model-dependent, unreproducible", and the
control experiment says the model on this machine is not accurate enough to justify that trade.

## 2026-10-23 update: the field-level control set was built, and the model failed it

`scripts/vlm_field_controls.py` is the measurement this document asked for. One field
(`panel_count`), four controls whose answers were fixed before the model saw them, and a pass
requiring all four.

    [FAIL] blank        expect=0  got=1
    [OK  ] noise        expect=0  got=0
    [OK  ] one-panel    expect=1  got=1
    [OK  ] three-panel  expect=3  got=3

**gemma3:12b answered 3 of 4.** The failure is the one that matters: a **pure white page** --
verified at one unique grey level and 0.0000 fraction non-white -- was reported as having **one
panel**. That is a fabrication, not a near miss, and it is the same failure mode the earlier
ten-field experiment recorded.

### Why this is the right test and a real result

Three of four is not "close". A model that invents a panel where the image has no ink at all cannot
be trusted on a figure where the ink is ambiguous, and the fields this project would want from a VLM
(arrow style, legend presence, layout intent) are strictly harder than counting four subplots.

It also settles the question this document left open: the model on this machine is **not** accurate
enough to justify moving the official score from "deterministic, reproducible, 75.41" to
"model-dependent, unreproducible".

### What would change the answer

A different local model that passes all four controls. The harness is now one command:

    python scripts/vlm_field_controls.py --model <name>

and it exits non-zero on any control failure, so a candidate can be screened without touching the
judging path. 59 models are installed; the screening is cheap and the bar is exact.

### What this does not change

The vision channel of the benchmark remains unrun, and the 0.65 share of the combined score remains
unmeasured. That is the honest state, and it is now backed by a measurement rather than by an
impression.

## 2026-10-23 (later): two models passed the controls, and it was overfitting

The screen was extended to all **nine** vision-capable local models, and two passed the four
synthetic controls:

    translategemma:4b      4/4  [OOOO]
    translategemma:latest  4/4  [OOOO]

A fifth control was then added -- a REAL figpipe figure, rendered through the project's own drawer,
where the panel count is the INPUT to the layout rather than read back from the image. Both models
passed that too, at counts 1, 2, 3, 4 and 6. **9 of 9.**

That looked like the answer to the 0.65 question. It was not.

### The held-out test

The counts 1, 2, 3, 4 and 6 were chosen while designing the control. Counts 8 and 9 were not:

    [FAIL] translategemma:4b      expect=8 got=6
    [FAIL] translategemma:4b      expect=9 got=7
    [FAIL] translategemma:latest  expect=8 got=6
    [FAIL] translategemma:latest  expect=9 got=7

Both models **systematically undercount by two** above six panels. The perfect score was not a
measurement of counting; it was a model that had learned to answer within the range the controls
covered.

### Why this matters more than the result

A control set whose values are all used in DESIGNING the control cannot detect overfitting. This is
the same defect class this project has recorded repeatedly -- an aggregate that describes a different
set than the one beside it -- applied to model screening: "9 of 9 controls" was true and it described
a model that cannot count.

**The rule, from now on:** a field screen must reserve at least one value that no other control uses,
and a model that fails the held-out value fails the screen regardless of its score on the rest.

`scripts/vlm_real_control.py` now spans 1, 2, 3, 4, 6, 8 and 9 panels, with the grid passed
explicitly for counts that do not fill figpipe's default (the drawer correctly refuses a plate with
an empty cell: "5 panels do not fill a 2x3 grid, leaving 1 empty cell(s)").

### The state of the VLM question

**No local model has passed.** The best available answer to "is a local VLM good enough" is still no,
and it is now a stronger no than before: the one candidate that looked perfect was overfitting.

