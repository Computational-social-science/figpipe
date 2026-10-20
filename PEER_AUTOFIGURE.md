# What figpipe can take from AutoFigure, and what it cannot

Peer: **AutoFigure: Generating and Refining Publication-Ready Scientific Illustrations**
(ResearAI/AutoFigure, **ICLR 2026**, MIT, ~1,930 stars, ~8,000 lines of Python).
Read-only clone: `E:\2026-AI4S\peer-repos\AutoFigure`.

This note exists because the honest answer is more useful than admiration. AutoFigure is a mature
system and figpipe should learn from it -- but three of its central mechanisms are ones figpipe has
**deliberately ruled out**, and copying them would undo work this project spent rounds proving.

---

## What AutoFigure does, in its own terms

    Generate  ->  Evaluate  ->  Refine   (the "Review-Refine loop")

* **Generate** an SVG or mxGraph XML figure from a text description or a paper's methodology.
* **Evaluate** with a VLM-as-Judge (`judge.py`, 1,539 lines) that scores 0-10 on eleven dimensions
  and returns specific feedback.
* **Refine** until the score clears a threshold (default 9.0), up to `max_iterations` (default 5).
* Output is **editable vector**: SVG or draw.io XML, not a raster.

Its eleven rubric dimensions:

    1. Aesthetic & Design Quality (ADQ)     7. Content Fidelity (CF)
    2. Visual Expressiveness (VE)           8. Appropriateness to Audience
    3. Professional Polish (PP)             9. Information Sophistication
    4. Clarity                             10. Logical Flow
    5. Accuracy                            11. Modern Visual Excellence
    6. Completeness

---

## The three mechanisms figpipe CANNOT copy, and why

### 1. VLM-as-Judge

AutoFigure's scoring loop is a vision-language model rating the figure. figpipe **measured** what
that is worth on its own corpus: `vlm_report.json` recorded **20 fabrications** in VLM descriptions
of figures. A judge that invents content it is looking at cannot be the ground truth for a pipeline
whose entire value is that its checks can be re-run and disagree with it.

This is not a preference. It is a recorded measurement in this repository, and `CLAIM.md` states
that the official benchmark's 0.65 vision channel is out of scope for the same reason.

### 2. Text-to-figure generation from prose

AutoFigure turns a description into a diagram. figpipe turns a **data table** into a **chart**, and
verifies the chart against the data (`semantics.py` re-derives every printed number). Those are
different products with different failure modes. A text-to-diagram system cannot tell you that your
error bar is wrong; a data-to-chart system cannot draw your architecture diagram.

### 3. LLM-generated code with an LLM quality gate

AutoFigure's figure is produced by a model and judged by a model. figpipe's mutation loop
(`figpipe/mutation.py`) is deliberately **deterministic and offline** -- no LLM, no network, no API
key -- because a proposal step whose output varies run to run cannot be validated by this project's
own rules. That constraint was chosen, not inherited.

---

## The four things figpipe SHOULD take

### 1. The output format: editable vector, not raster

AutoFigure outputs **SVG / draw.io XML**. figpipe outputs PDF (Nature submission) and PNG (preview).
The PDF is already vector, so figpipe is not behind here -- but AutoFigure's *insistence on
editability* is the right instinct and worth stating: **a figure a researcher cannot edit is a
figure they cannot fix at 2 a.m. before a deadline.** figpipe's `codegen.emit()` already produces
runnable matplotlib source for exactly this reason; the two projects agree.

### 2. A rubric with NAMED dimensions, scored separately

This is the transferable idea. figpipe's audit reports findings by `check` name
(`font_size`, `font_type`, `width`, `height`, `overlap`, `exists`) but has **no named quality
dimensions** and no per-dimension score. AutoFigure's eleven dimensions are too many and too
subjective, but the STRUCTURE -- name the dimension, score it, report it separately -- is better than
a flat list of findings, because it tells a user **what to fix first**.

figpipe can adopt this deterministically, for the dimensions it can actually measure:

| dimension | figpipe's deterministic check | status |
|---|---|---|
| typography | `font_size`, `font_type` | exists |
| geometry | `width`, `height` | exists |
| legibility | `overlap` (glyph collisions) | exists |
| information density | axis label budgets (12) | exists, not scored |
| colour | palette contrast / rainbow rejection | exists in `colourcheck.py`, not in the score |
| semantic fidelity | `semantics.py` number re-derivation | exists, not in the score |

**The gap is that these are separate reports, not one score with named parts.** AutoFigure's
contribution is the presentation, and figpipe should adopt it.

### 3. A quality threshold with a bounded loop

AutoFigure refines until `score >= quality_threshold` or `max_iterations`, whichever comes first.
figpipe's mutation loop already has a budget and a margin, but it has **no target**: it selects the
best available edit even when every edit is a tie. A threshold would let it say "nothing here is good
enough, stop" -- which is a different and more honest outcome than "selected the least-bad".

### 4. An explicit content-type context

AutoFigure parameterises its judge by content type (`paper` / `survey` / `textbook` / `blog`) and
changes the evaluation focus accordingly. figpipe has the equivalent idea in its **chart types**
(Bar / Line / Heatmap / Polar / ...) and already reports per-type scores. The lesson is that
**the same figure can be right for one audience and wrong for another**, and the evaluation should
say which standard it is applying.

---

## What figpipe does better, stated plainly

Not to be defensive, but because a one-sided comparison is not a comparison:

| | AutoFigure | figpipe |
|---|---|---|
| Ground truth | a VLM judge | the benchmark's official deterministic scorer, with a baseline and a ceiling |
| Reproducibility | model-dependent; the same prompt can score differently | every judged number is a function of a fixed task set, complete membership, one instrument version |
| Failure detection | the judge notices | 15 documented defect classes with tests, plus a mutation loop that must reject a regression |
| Audit trail | per-run output folder | 197 run records, git history where a diff means a change |
| Editability | SVG / draw.io XML | PDF vector + emitted matplotlib source |
| Scope | text or paper -> diagram | data table -> chart, with number re-derivation |

AutoFigure is a **generation** system with a model in the loop. figpipe is a **verification** system
with the model removed. The two are complementary, and the honest claim is not that one beats the
other.

---

## The one thing figpipe should be embarrassed about

AutoFigure has a **web interface** (`frontend/`, Next.js) and a **Flask API** (`backend/`). A
researcher can use it without a terminal.

figpipe has `scripts/make_figure.py`, a command line. Its README leads with a CSV and a shell
command. For a tool whose objective is "reusable in research scenarios", **a command line is a
barrier that AutoFigure decided was worth removing and figpipe has not**.

That is the most valuable thing in this comparison, and it is not a modelling idea -- it is a
product decision.
