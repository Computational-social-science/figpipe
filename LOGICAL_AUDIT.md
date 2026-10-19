# Logical audit: does the pipeline's reasoning hold?

The objective asks the project to reflect on whether the pipeline has theoretical or logical
defects. This document answers that by **type of argument**, not by list of bugs. Each entry names
the claim the code makes, the way that claim could be wrong, and the evidence of what was done.

The distinction that matters: a **bug** is a wrong answer; a **logical defect** is a way the
pipeline could be systematically wrong while looking right. Only the second kind is audited here.

---

## 1. Measurement validity — does the number mean what it says?

| claim | how it could be wrong | status |
|---|---|---|
| Style distance orders figures by similarity | The metric could be blind to a change it should see | **Found and fixed**: a 1-pt size histogram could not see 6.0 → 6.5. Replaced with Wasserstein-1 on the CDF |
| A mean measures capability | The mean could move with the measurement SET rather than the capability | **Found and fixed 3×**: raw mean, task count, shipped mean — all moved when coverage grew. All judged metrics now use frozen task subsets |
| A frozen subset is enough | The rows inside it could come from different code versions | **Found and fixed 2×**: both anchors now use a single-instrument view |
| The official score is comparable | It could be a tautology | **Found**: copying style from the shipped `reference_code` scores 100 by construction. Reported only as a ceiling; the claim uses image-inferred style |
| A score supports a claim | It could have no referent | **Found and fixed**: 75.41 meant nothing until measured against a 38.16 baseline |
| Freshness is a binary | "Unknown" could be reported as "stale" | **Found and fixed**: three-valued freshness |

**Residual risk:** the style-distance weights are hand-set. Nothing validates that a smaller
distance corresponds to a figure an expert prefers. This is a genuine open question, not a bug —
it is listed in `CLAIM.md` as unvalidated.

---

## 2. Reference class — is the pipeline being compared to the right thing?

| claim | how it could be wrong | status |
|---|---|---|
| The pipeline beats a baseline | The baseline could be a straw man | The baseline is **this pipeline's own** default style (matplotlib defaults + the compliance floor), not a competitor. Stated explicitly |
| The pipeline is competitive | No head-to-head was run | **Stated as not claimed** in `CLAIM.md`. No comparison to FigMirror / NaturePanelForge / DeTi*k*Zify is implied |
| Style transfer helps | It could help some chart types and hurt others | **Measured**: it hurt 11 of 70 tasks at one point. The pipeline now decides per task instead of always transferring, and no chart type is negative |

**Residual risk:** the benchmark is CC BY-NC 4.0 and cannot be redistributed, so a third party
must re-download it to reproduce the numbers. The reproduction commands are in `CLAIM.md`.

---

## 3. Input assumptions — what does the code silently assume?

| assumption | where it could bite | status |
|---|---|---|
| A table with >24 rows is a matrix | A long field table was drawn as a 48-row matrix whose labels collided | **Fixed**: pivot onto varying columns, or refuse |
| A bar axis can carry any number of categories | 20 year-bars on one axis produced 19 collisions | **Fixed**: category budget of 12, refuse past it with the better encoding named |
| A raster has structure | A blank/noise image reported four spines (edge artefact of `np.convolve`) | **Fixed**: edge-corrected local contrast |
| An aspect ratio is a positive finite number | `figsize=(7.2, nan)` was emitted as a success | **Fixed**: refused |
| Column roles are unambiguous | `spec.infer_spec` could guess | **Refuses** with `SpecError` listing the roles |
| A measure is mostly finite | `panel_row` (95 % NaN) was chosen as the plotted value | **Fixed**: ≥80 % finite required |

**Residual risk:** the data-shape audit covers 7 shapes and the robustness audit 26 adversarial
cases. Shapes neither sweep imagines remain untested. The sweeps are the mitigation, not a proof.

---

## 4. Verification completeness — can the checks fail?

| check | could it be vacuous? | status |
|---|---|---|
| `audit` finds format violations | It might not read the PDF back | It does; negative controls exist in the tests |
| Text-collision detection | Rotated tick labels might be false positives | Per-character geometry; the rotation case is tested |
| `semantics` re-derives printed claims | It might accept any annotation | Negative controls: a false `r`, a clipped outlier, a wrong label all fail |
| A test cannot silently disappear | A test could become a skip | **Fixed**: collected count asserted ≥ 300 |
| The report matches the evidence | Prose could contradict artefacts | **Found and fixed**: the report said "not an SOTA claim" for rounds after that became false. `tests/test_claim.py` now pins it |

**Residual risk:** the *checks themselves* are validated by negative controls written by the same
author who wrote the checks. An independent adversarial review is the only real mitigation, and
this project has had two (the earlier `CRITICAL_AUDIT` rounds).

---

## 5. State and timing — is anything read at the wrong moment?

| claim | how it could be wrong | status |
|---|---|---|
| The snapshot describes this run | It could be read before the measurement writes | **Found and fixed**: `refresh_anchor` runs after the slice; the snapshot is taken at record-write time |
| Coverage advances | The slice could re-measure covered tasks | **Found and fixed**: walks uncovered windows |
| A scheduled commit is safe | `git add -A` could delete evidence | **Found and fixed**: protected-prefix deletion guard (it had already deleted the seed package once) |
| A cache is bounded | Only half of it could be measured | **Found and fixed**: images counted, orphans pruned |
| Coverage survives pruning | It could be derived from the prunable cache | **Found and fixed**: derived from the report |

---

## 6. What is NOT audited, and why

- **Scientific correctness of a user's analysis.** The pipeline verifies that a figure is compliant
  and that its printed claims match its input data. It cannot know whether the right test was run.
- **Aesthetic quality.** Style distance measures similarity to a reference, not quality.
- **Generality beyond the measured shapes.** Two sweeps cover what their authors imagined.
- **The vision channel of the official benchmark.** Not run, by scope decision.

---

## Verdict

The pipeline has **no known logical defect in the claims it makes**. It has, repeatedly, had
logical defects in **how it decided whether its claims were true** — and every one found so far was
found by asking the question in this document's shape: *what would have to be true for this number
to be wrong, and has that been tested?*

The honest summary is therefore not "no defects" but: **the defect rate in the verification layer
is higher than in the drawing layer, and the verification layer is where the remaining risk lives.**
That is stated in `CLAIM.md` and in `LEARNINGS.md`, and the sweeps that exist are the mitigation.
