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
| The answer key stays out of the input | The target could be reachable from the style source | **Found and now GUARDED**: the 100.0 ceiling came from copying `reference_code`. `figpipe/tripwire.py` refuses a path whose name or content carries the target, with an explicit `allow=` where reading it IS the measurement. Harness² (google-research) reached the same rule independently |
| Freshness is a binary | "Unknown" could be reported as "stale" | **Found and fixed**: three-valued freshness |
| A style metric is valid | It could be blind, or rank a wrong transfer above a right one, and nobody would know | **Measured**: a discrimination experiment on 30 real corpus figures scores **0.933 (95 % CI 0.787–0.982)**, inverted control 0.033, official scorer agrees 27/27 decisive. See below |

**Residual risk (narrowed, not closed):** the style-distance weights are still hand-set, and
the discrimination experiment tests **ordering, not preference**. Two limits are measured and
stated rather than assumed away:

1. **The result is concentrated in one component.** Leave-one-out shows that withholding
   `aspect` alone drops accuracy from 0.933 to **0.700**; withholding any other single component
   leaves it at 0.933. Most of the discrimination therefore comes from figure aspect — the
   easiest property to reproduce — not from palette or typography. A metric whose accuracy is
   carried by one cheap dimension is weaker than its aggregate suggests, and `CLAIM.md` says so.
2. **No human judgement was collected.** The experiment can refute a blind or inverted metric
   (that is what the inverted control is for); it cannot establish that the closer figure is the
   figure an expert would prefer. That remains open, and remains listed in `CLAIM.md`.

What changed is that the residual risk is now **bounded by a measurement** instead of being an
untested assertion. This section previously named "nothing validates that a smaller distance
corresponds to a figure an expert prefers" as a genuine open question; the ordering half of that
question is now answered, and the preference half is stated as the remaining limit.

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
| The VERIFIERS catch planted defects | A verifier tested only on correct input has not been tested | **Swept**: `scripts/audit_verifiers.py` plants sub-5 pt text, a wrong width, Type-3 fonts and a real glyph collision; all four are caught. A correct figure passes, and rotated tick labels are NOT reported as collisions. 13/13 cases ok |
| `composite` refuses invalid geometry | Overlapping cells, negative positions, span collisions, impossible colour bars could slip through | **Swept**: all six invalid geometries are refused with a message naming the problem; a correct plate still passes |

**Residual risk:** the *checks themselves* are validated by negative controls written by the same
author who wrote the checks. `scripts/audit_verifiers.py` now plants each defect the project exists
to catch (13 cases, all caught) and confirms no false positives, which closes the mechanical gap —
but an independent adversarial review remains the only real mitigation for shared blind spots, and
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
