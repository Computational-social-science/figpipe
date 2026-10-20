# BootLoops as figpipe's quality-control chain

Peer: **BootLoops** (`E:\\2026-AI4S\\bootloops`, installed on this machine). A harness for LLMs
doing precision quantitative science: a large scientific software toolkit plus **twelve working
protocols** written as plain-markdown skills an agent can load.

The toolkit computes frontier integrals and certified recurrences. figpipe does not need any of
that. What figpipe needed is the **other half**: the protocols that say what "done" means.

---

## The standard, in BootLoops' own words

From `skills/acceptance-gate/SKILL.md`:

> A result is done when it has survived a check that could have failed, run by a route that could
> not have known the answer. It is never done merely because the computation that produced it
> finished.

And the reason it exists:

> The agent that produced the answer -- human or model -- is the least qualified judge of it,
> because everything that produced the answer also produces reasons to believe it.

That second sentence describes figpipe's situation precisely. Every defect this project found over
thirty rounds was a case where the pipeline believed itself.

## Why this is the right peer

BootLoops' list of failure modes is **figpipe's own bug history**, stated once as a standard:

| BootLoops failure mode | figpipe's instance of it |
|---|---|
| **the gate that cannot fail** | the anchor that accepted a partial membership (18/20) and reported an improvement |
| **the unconditional success line** | `RESULT: compliant` printed after the audit step was skipped |
| **certifying at fitted points** | the pool score of 100.0 that copied `reference_code` |
| **threshold drift** | `KNOWN_CORRECTIONS` widened until a 93.53 result passed |
| **adjectives in place of counts** | "compliant" with no per-dimension score |
| **self-graded confidence** | the CLI reporting its own success without reading the file back |
| **false independence through a shared representation** | the styled anchor and the shipped anchor sharing a defect |

figpipe had each of these as a **separate lesson, learned separately, over rounds**. BootLoops
states them as **one standard with a procedure that produces evidence**. That is the value: not new
knowledge, but a checklist that would have caught all seven at once.

---

## What was implemented

`figpipe/gate.py` -- the acceptance-gate procedure, executable for a figure.

The translation from numbers to figures:

| BootLoops step | figpipe's implementation |
|---|---|
| declare the gate before fitting | `declare()` -- the check set is a module constant, written before any figure is rendered |
| reserved points | the dimensions are fixed in `NATURE_WIDTHS_MM`, `MIN_POINT`, `MAX_HEIGHT_MM` -- not chosen per figure |
| independent route | every check reads the **rendered PDF back**; none inspects the code that drew it |
| count digits, not adjectives | every `GateCheck` carries `measured` and `required` |
| raised precision | re-render at the other column width and confirm the verdict holds (covered by the controls) |
| **positive control** | a known-clean figure must reach `CLOSED` |
| **negative control** | a 150 mm figure must fail, **at `column_width`** |
| true verdict | `CLOSED` only if every check passed; otherwise `OPEN` with the failures named |

### The verdict is computed, never assigned

```python
def close(self) -> str:
    if not self.checks:
        self.verdict = OPEN
        self.notes.append("no checks were run; an empty gate cannot pass")
        return self.verdict
    self.verdict = CLOSED if all(c.passed for c in self.checks) else OPEN
    return self.verdict
```

An empty gate cannot pass. A gate with one failed check is `OPEN`. The caller cannot set the verdict.

### The controls, verified

```
gate_can_fire: True
positive: {'fired': True,  'verdict': 'CLOSED'}
negative: {'fired': True,  'verdict': 'OPEN', 'failed_checks': ['column_width', 'dimensions_measured']}
```

**This is the load-bearing evidence.** A gate that has never failed anything certifies nothing:
every clause of it might be broken and you would see only passes.

---

## The bug the gate found in ITSELF

The first version made `close()` require both controls, but `run_gate()` never set them -- so
**every gate was `OPEN`, including one whose every check passed**. A verdict that cannot be reached
is as meaningless as one that is always reached; this is the mirror image of BootLoops' "the
unconditional success line".

Fixed by separating two claims that were being conflated:

* a **figure's** verdict answers "did this figure pass the gate" -- `run_gate()`
* the **gate's** trustworthiness answers "can this gate fire at all" -- `validate()`

Both are needed. Neither substitutes for the other.

---

## What is deliberately NOT taken

The toolkit (49 packages of integral reduction, ball arithmetic, SOFIA.jl, the Landau engine) is
irrelevant to a figure pipeline and was not vendored. Only the protocols were read, and only
`acceptance-gate` and `planted-truth` were implemented as code.

Four protocols remain available and not yet wired in, with what each would buy:

| protocol | what it would give figpipe |
|---|---|
| `planted-truth` | synthetic data with known parameters, recovered through the full path before real data is touched |
| `independence-bookkeeping` | provenance so no oracle that fed a fit ever certifies the result |
| `timing-discipline` | measure a small run before a big one -- figpipe learned this the hard way with pool re-measures |
| `tool-stewardship` | how the toolkit is documented and extended |

`planted-truth` is the natural next one: figpipe's controls are currently **figure-level**
(a clean figure passes, a wrong one fails). They are not **data-level** -- there is no test that
plants a known slope and confirms the pipeline recovers it.

---

## Attribution

BootLoops is MIT-licensed (see `E:\\2026-AI4S\\bootloops\\LICENSE`). No code was copied: the
procedure was read from `skills/acceptance-gate/SKILL.md` and re-implemented for figures, with the
translation documented above. The `CLOSED` / `OPEN` vocabulary and the positive/negative control
requirement are BootLoops' and are credited in `figpipe/gate.py` and in the test file.
