# figpipe — a reusable pipeline for publication figures

A small, dependency-light package that makes journal-figure compliance a property of an
import rather than of the author's memory. Extracted from a real project where six figures
were produced, all six passed the author's own checks, and **four of them turned out to carry
text below the journal's minimum size**.

---

## Why this exists

The defects that get a figure rejected are **not visible in the source code**. They appear in
the rendered file:

| defect | how it looked in the source | how it looked in the PDF |
|---|---|---|
| text at 4.0–4.8 pt | `fontsize=4.8` on an annotation — plausible | below the 5 pt floor |
| log-axis exponents at 3.15 pt | `ax.set_yscale("log")` — nothing wrong | exponent span measured at 3.15 pt |
| 198.8 mm wide | `figsize=(...)` — looked fine | 15.8 mm outside the column |
| Type-3 fonts | `pdf.fonttype` never set | outlined, uneditable text |

A source linter cannot catch any of them. **The audit therefore reads the PDF back and
measures the spans**, which is the only check that would have caught all four.

---

## Install

    pip install matplotlib pymupdf
    pip install scienceplots          # optional; the package degrades gracefully without it

No packaging step needed — put the directory on `sys.path`, or `pip install -e .`.

---

## Use

```python
from figpipe import style, layout, audit

style.apply()                                  # compliant rcParams
fig, w, h = layout.figure(columns=2, height_mm=55)
gs = layout.gridspec(fig, 1, 2)

ax = fig.add_subplot(gs[0, 0])
ax.plot(x, y, "o-", color=style.OKABE_ITO["blue"], ms=2.5, lw=1)
ax.set_xlabel("sentence position")
ax.set_ylabel("mean error rate (%)")           # unit in parentheses
style.panel_letter(ax, "a")

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_yscale("log")                          # handled: exponents replaced by plain numbers
style.panel_letter(ax2, "b")

layout.save(fig, "docs/fig3_session_dynamics")  # .pdf (submission) + .png (preview)

report = audit.audit("docs/fig3_session_dynamics.pdf", expect_width_mm=183)
assert report["ok"], report["findings"]
```

---

## The five things it fixes that a hand-rolled style gets wrong

### 1. `pdf.fonttype` — the invisible rejection

SciencePlots' `nature` style sets **`pdf.fonttype = 3`**, which converts text to Type-3
outlines. Nature's guide says: *"Do not outline text; embed fonts (True Type 2 or 42)"*. The
rendered figure looks correct; it is rejected on submission. `style.apply()` sets 42.

### 2. `savefig.bbox` — the third mechanism that moves the width

Passing no `bbox_inches` to `savefig` is **not enough**. The style sets `savefig.bbox =
"tight"`, so matplotlib pads the output regardless. Measured: a figure created at exactly
183.00 mm was written to a **185.54 mm** page. Pinning the rcParam is what holds the size.

### 3. `10^n` log labels are arithmetically unsolvable

matplotlib draws `10^n` as a base span at the configured size and an exponent at ~0.7× that.
Measured:

| base size | exponent size | verdict |
|---:|---:|---|
| 5.0 pt | 3.50 pt | below floor |
| 6.0 pt | 4.20 pt | below floor |
| 7.0 pt | 4.90 pt | below floor |

The allowed band is 5–7 pt, so **no admissible base produces a compliant exponent**. The only
fix is to stop using `10^n`: `style.suppress_log_exponents(fig)` prints plain numbers
(100, 1000, 10000), which puts every glyph at the configured size.

### 4. `text.usetex` — a silent hard dependency

The plain `science` style sets `text.usetex=True`. On a machine without TeX **every text call
fails** and the figure cannot be produced at all. The package applies `no-latex` and forces
`text.usetex=False`.

### 5. Size is not a free parameter

`layout.figure(columns=1|2)` is the only way to size a figure: 89 mm or 183 mm, nothing else.
A height above 170 mm raises, because the limit exists so the legend fits beneath the figure.
`figsize=(7.3, 2.4)` is not expressible.

---

## What the audit checks

| check | method | hard failure |
|---|---|---|
| font sizes | every text span in the PDF via PyMuPDF | yes |
| width | against {89, 183} mm ±0.6 | yes |
| height | against 170 mm | yes |
| font type | embedded fonts, Type-3 rejected | yes |
| text overlap | bounding-box IoU ≥ 0.30 | reported, not failing |

**Panel letters at 8 pt are exempt from the 7 pt ceiling** — the guide specifies 8 pt for
them, above the body-text maximum.

---

## What it does NOT check, stated plainly

**Whether the figure is well designed.** Panel balance, visual hierarchy, whether the eye is
led to the finding, whether a caption collides with a title — none of that is measurable.
A passing audit means the mechanical requirements are met. It is not a claim of quality, and
this README says so rather than letting a green check imply more.

The honest position: a text-only agent can enforce the measurable half. The other half needs
eyes.

---

## Tests

    python -m pytest tests/ -q     # 18 passed

Each test is written from a **real failure**, not from the implementation, so a refactor
cannot quietly reintroduce one. Notable ones:

- `test_audit_catches_sub_5pt_text` — builds a figure with 4 pt text and asserts the audit
  fails it
- `test_audit_catches_log_exponents` — builds a log axis **without** the fix and asserts the
  audit catches the 3.15 pt exponent
- `test_savefig_bbox_is_not_tight` — pins the rcParam that silently padded the output
- `test_violations_reports_a_deliberately_broken_style` — the checker must detect a
  deliberately broken style, or it is not a checker

---

## Dependencies

| package | required | why |
|---|---|---|
| matplotlib | yes | drawing |
| pymupdf | yes | the audit reads the PDF back |
| scienceplots | optional | base style; the package works without it |

---

## Provenance

Extracted from `keystroke-observatory`, where the specification work lives in the journal
guide (sources below) and the per-figure design critique informed `LEARNINGS.md`.

Specification sources:
- <https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/>
- <https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/>


---

## Five entry points

The package exports fifteen modules; these five cover the whole workflow, in increasing order of
ambition. Each is verified by the pipeline itself, not merely documented.

```python
# 1. draw one compliant panel
from figpipe import grammar
panel = grammar.panel("trend_with_uncertainty", df, x="year", y="mean", fit="lm")

# 2. compose a plate and verify the RENDERED file
from figpipe import grammar, layout, audit
fig = grammar.plate([panel_a, panel_b], columns=2.0, height_mm=140.0)
pdf = layout.save(fig, "fig2")[0]
report = audit.audit(pdf, expect_width_mm=183.0)
assert report["ok"], report["findings"]

# 3. declare the figure from the data instead of by hand (refuses rather than guessing)
from figpipe import spec
figure = spec.infer_spec(df)

# 4. run a named recipe over classic operators, with the global verification floor
from figpipe import skills
result = skills.run("trend_with_uncertainty", df, x="year", y="mean")

# 5. measure a reference's style, transfer it, ship the closer candidate
from figpipe import styleprofile, select
ref = styleprofile.StyleProfile.from_pdf("published.pdf", page=3)
picked = select.select(ref, {"plain": a_pdf, "styled": b_pdf})
```

A complete, runnable demonstration on invented data:

    python examples/worked_example.py

It runs spec -> recipe -> render -> audit -> semantics -> codegen -> select and exits non-zero
unless every claim it prints was verified.

## Repository map

| file | what it is |
|---|---|
| `ARCHITECTURE.md` | the current implementation, layer by layer |
| `PIPELINE_V3.md` | the forward plan (entry layer, benchmark route, SOTA definition) |
| `SKILLS.md` | global skill floor + classic operators + named recipes |
| `LEARNINGS.md` | append-only lessons, including corrected mistakes |
| `CRITICAL_AUDIT.md` | adversarial audit of the pipeline (canonical record) |
| `SEED_REPRODUCTION.md` | the seed paper's reproduction record |
| `PEER_LANDSCAPE.md` | peer projects, licences, and what was absorbed |
| `REPRODUCTION_GAP_ANALYSIS.md` | what a figure reproduction does and does not prove |
| `knowledge/benchmark_skill_map.json` | benchmark chart types -> our skills/coverage |
| `reports/figpipe_report.html` | generated progress / deliverables report (HTML only) |

## Language policy

Research outputs of this project -- reports, README, commit messages and new documentation -- are
written in English. The HTML report is the only report format: DOCX and PDF reports are not
produced; figures themselves remain PDF/PNG deliverables.
