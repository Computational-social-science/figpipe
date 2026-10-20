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
