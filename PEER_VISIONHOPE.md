# What figpipe can take from VisionHOPE, and the diagnosis that prompted it

Peer: **VisionHOPE: Visual Backbones as Self-Modifying Learning Systems** (PSRben/VisionHOPE, MIT,
arXiv 2609.33325, ~1,300 stars). A PyTorch vision backbone built on **self-referential nested
learning (SRNL)**: while processing one image, the model adapts both its memory AND the rule that
updates it.

The request was direct: *"we are not breaking through; study VisionHOPE and adopt it."* This note
records what the study found, including the part that is uncomfortable.

---

## First, the diagnosis: why there is no breakthrough

Before reading the paper I measured what figpipe's autonomous loop has actually changed:

    130 run records
      4 runs with a knowledge change
    127 runs whose mutation step selected NOTHING
      3 runs that selected, all of them `matrix-max-rows` budget values

So the loop has spent 130 cycles performing **parameter search against a fixed threshold**. It has
never changed the rule that decides what counts as an improvement. `mutation._verdict` has
`min_margin = 0.1` written as a literal; `min_score` is `None`.

That is the thing VisionHOPE's thesis is about. Its whole architecture exists because a system whose
learning rule is fixed cannot adapt to what it is looking at -- it can only move along an axis
somebody chose in advance. figpipe's loop moves along `max_rows` and `max_bars`, and stops.

**So the "no breakthrough" is not a shortage of features. It is that the loop was never a learning
system: it is a fixed comparison applied repeatedly.**

---

## What VisionHOPE actually does

`models/srnl.py` (190 lines) plus `models/srnl_core/csrc/` (CUDA). Five learned memories per head:

    M_m, M_v, M_k       content / value / key memories  (head_dim x head_dim matrices)
    M_eta               the LEARNING RATE memory        (head_dim vector)
    M_alpha             the RETENTION memory            (head_dim vector)

And the update rule, from `csrc/memory.cuh`:

    eta   = ETA_SCALE * sp                        // how far to move
    alpha = ALPHA_MIN + (1 - ALPHA_MIN) * sigmoid(ap)   // how much of the old memory to keep

Both `eta` and `alpha` are **computed from the input** through learned memories, then stabilised:

    eta_cap = STAB_MU * (1 - alpha) / (diff_norm + eps)
    eta     = eta_cap * (1 - exp(-eta / eta_cap))     // soft injection cap
    eta     = min(eta, nextafterf(ETA2ALPHA_FACTOR * alpha / key_norm_sq, 0))

So the step size and the retention are **functions of the data**, bounded by a stability projection
that prevents expansion. That is the mechanism.

---

## What figpipe CANNOT take, and why

**1. The backbone itself.** A vision backbone maps pixels to logits. figpipe maps a data table to a
vector PDF. There is no shared tensor shape, no gradient, no training corpus. Porting `SRNL` into
figpipe would be a category error, not an integration.

**2. The CUDA kernels.** `csrc/` is ~2,000 lines of templated CUDA with hand-written memory layouts
and head-dimension dispatch tables. They compute a chunkwise recurrence over `[B, directions, heads,
N, head_dim]`. figpipe has no such tensor and no GPU work to do.

**3. Gradient-based adaptation.** SRNL's memories are `nn.Parameter`s updated by backprop across a
training corpus. figpipe's "training corpus" is 139 benchmark tasks with a deterministic score, and
its loop is explicitly **offline and LLM-free** -- a design choice recorded in CLAIM.md, made so
that a proposal whose output varies run to run cannot enter the pipeline.

## What figpipe CAN take, and did

**The thesis, applied at the level figpipe actually operates on.**

VisionHOPE's claim is not "use five memories". It is:

> A system whose update rule is a constant cannot adapt; the rule must itself be a function of what
> the system has seen.

figpipe's mutation loop has a constant rule. It can be given a rule that **is a function of its own
history** without any GPU, any gradient, or any model -- because figpipe's "memories" are already
there, in `knowledge/`:

    the run records       130 of them, each with a measured outcome
    the decision history  which candidates were selected, rejected, tied
    the resolution        how much a score actually moved when a task was re-measured

`figpipe/adaptiverule.py` implements the transferable part: an `eta`-like **margin** and an
`alpha`-like **retention**, both computed from the loop's own measured history instead of written as
literals, with a stability projection borrowed from `soft_project_eta` so the margin cannot run away.

This is a real transfer, and it is small: the mechanism is one idea, not an architecture.

---

## The honest summary

| | VisionHOPE | figpipe |
|---|---|---|
| what adapts | memories and the update rule, per image | the update rule, per N runs |
| mechanism | learned `eta`/`alpha` via backprop | measured `margin`/`retention` via history |
| needs GPU | yes (CUDA extensions) | no |
| needs a model | yes (PyTorch weights) | no (deterministic) |
| what it produces | logits | a vector PDF |

The two systems share one sentence and nothing else. Adopting the sentence is the integration.
Adopting the code would be a mistake that looks like progress.

---

## Attribution

VisionHOPE is MIT-licensed. No code was copied. The mechanism was read from
`models/srnl_core/csrc/memory.cuh` (`soft_project_eta`, the `eta`/`alpha` computation) and
re-expressed in `figpipe/adaptiverule.py` for a system with no tensors. The citation is in that
module's docstring.
