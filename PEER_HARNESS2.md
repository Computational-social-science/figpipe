# What figpipe took from Harness², and what it did not

Peer project: **Harness²: Recursive Agent Harnessing for an Open World**
(google-research/harness2, arXiv 2610.14224, **Apache 2.0**).
Read-only clone: `E:\2026-AI4S\peer-repos\harness2`.

This note records what was absorbed, what was deliberately not absorbed, and why. It is written in
the same spirit as `third_party/*/NOTICE.md`: an absorption that cannot be stated precisely is
usually not an absorption.

---

## The one idea that mattered: Propose–Probe–Compose

Harness²'s task-level recursion is a contrastive loop with **no ground-truth feedback**:

1. **Propose** — an editor proposes candidate edits to the harness.
2. **Probe** — each candidate is executed on the *same* task.
3. **Compose** — the refined harness is assembled from the *behavioural contrasts* between
   executions, not from a score.

figpipe's evolution loop before this integration was **not** a mutation loop. It re-verified rules,
measured artefacts, and recorded deltas — but it never proposed a candidate change, probed it, and
kept it on evidence. It could report that a number moved; it could not *choose* an edit.

`figpipe/mutation.py` implements the same three stages over figpipe's own operators, deterministically
(no LLM, no network, no API key). The refusals the project already produced — the bar category
budget, the unpivotable matrix — become the first mutation candidates, because each refusal names a
gap an operator could close.

## The second idea: budget accounting that cannot be gamed

`harness2/core/ledger.py` is 130 lines of pure stdlib that records what a run spent and then asserts
an **identity**: R = 4k rollouts, P = 3k sessions. Two details are worth more than the code:

- **Duplicate labels are checked BEFORE the counts**, because a duplicate can satisfy them. A
  repeated label means two stages wrote the same run id and one silently overwrote the other, so a
  candidate the ledger counts was never actually produced.
- **`BudgetError` subclasses `AssertionError`** — a budget violation is a programming error, not a
  runtime condition to be handled.

Vendored unmodified at `third_party/harness2_ledger/` (Apache 2.0, see its NOTICE.md).

## The third idea, arrived at independently: the answer-key tripwire

Harness² refuses to serve any harness file whose name or body carries a **grader verdict**, because
such a file "cannot be served as evidence to later tasks":

```python
GRADER_VERDICT_MARKERS = (
    "deterministic_eval_summary", "deterministic_eval_result",
    "judge_scope_and_deterministic_status", "Judge findings on the rendered result",
    '"passed_count"', '"pass_rate"', '"test_pass_rate"',
)
```

figpipe reached the same rule from the opposite direction: it once reported an official score of
**100.0** that came entirely from copying the reference figure's own code. The answer key was in the
input, and the number looked like a triumph.

Two projects, independent methods, the same conclusion — which is the strongest evidence either
could have that the rule is real. `figpipe/tripwire.py` is the figpipe-side equivalent, expressed
for figures: `assert_no_answer_key()` refuses a path whose name or content carries the target, with
an explicit `allow=(...)` for the one case where reading the answer key *is* the measurement (the
tautological ceiling).

## What was NOT absorbed, and why

| Harness² component | why not |
|---|---|
| `core/proposer.py` (OpenCode / Claude CLI sessions) | Requires an LLM CLI and an API key. figpipe's mutation loop must be deterministic and reproducible offline; a proposal step whose output varies run to run cannot be validated by this project's own rules. The *interface* was adopted; the LLM was not. |
| `core/recursion.py` parallel/sequential modes | Depends on the proposer, `config`, `prompts`, and benchmark adapters (`jobbench`, `lab`, `workbuddy`). Vendoring it would drag in a dependency tree for a scheduling choice figpipe does not need: its mutation space is small enough to probe exhaustively. |
| `benchmarks/*` | JobBench / LAB / WorkBuddy-Bench are agentic coding benchmarks. figpipe's authoritative benchmark is PlotTwin-Bench, already integrated with its own official scorer. |
| `core/library.py` (experience library) | Requires `context` and `tree` modules; the retrieval model (per-domain experience directories) presumes many tasks per domain. figpipe has 16 skills over one domain. |
| `dependencies/`, `third_party/` | Third-party code with its own licences; not needed for the ideas adopted. |

## Licence position

- Harness² is **Apache 2.0**. The one file vendored (`ledger.py`) is copied **unmodified**, with its
  Apache header intact, and `third_party/harness2_ledger/NOTICE.md` records provenance, the upstream
  commit sha, and the licence.
- The *ideas* (Propose–Probe–Compose, budget identity, answer-key tripwire) are re-implemented in
  figpipe's own code, not copied. Ideas are not copyrightable; the expression is, which is why the
  one file taken is taken verbatim with its notice.
- Harness² is not redistributed, not packaged into figpipe's wheel, and not required at runtime.

## What this absorption demonstrates, and what it does not

**Demonstrates:** figpipe can read a peer's architecture, identify the one mechanism it actually
lacked (a mutation loop), adopt it in a form that fits its own constraints (deterministic, offline,
verifiable), and independently confirm a second idea (the tripwire) it had already learned the hard
way.

**Does not demonstrate:** that figpipe is now better than Harness² at anything. They solve different
problems. Harness² optimises an agent's harness for open-world tasks with an LLM in the loop;
figpipe produces publication-compliant figures from data and measures style transfer against an
official benchmark. No head-to-head comparison was run, and none is implied — the same limit stated
in `CLAIM.md` for every other peer.
