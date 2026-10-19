# NOTICE — vendored `harness2/core/ledger.py`

## Origin

- Repository: **google-research/harness2** <https://github.com/google-research/harness2>
- Local read-only clone: `E:\2026-AI4S\peer-repos\harness2`
- Upstream commit (exact): **`1cfe254e8d25b15f37048c3730134686abe60335`**
  (`git -C E:\2026-AI4S\peer-repos\harness2 rev-parse HEAD`, dated 2026-10-13, subject
  "Fix arXiv link"; the clone had a clean working tree when the file was copied)
- Source path upstream: `harness2/core/ledger.py`
- Vendored path here: `third_party/harness2_ledger/ledger.py`

## Licence

Apache License, Version 2.0 (the upstream `LICENSE` at the repository root). The upstream
copyright header is retained verbatim inside `ledger.py`; a copy of the licence text is kept
beside the vendored file as `LICENSE` in this directory.

## Modification status

`ledger.py` is **byte-identical** to upstream. Proven, not asserted — sha256 of both copies:

    fc34c75a7ec67ab0c541bd97faca6c2313e54f5f4182b2c9bdbfedd3bf7856f7

`tests/test_mutation.py::test_the_vendored_ledger_is_byte_identical_to_upstream` re-computes
both hashes and fails if either the bytes here or the upstream checkout move.

The only file authored by figpipe in this directory is `__init__.py`, which re-exports the
public names so callers do not import a third-party module path directly. It contains no
ledger logic.

## What figpipe uses it for, and what it does NOT do

`figpipe/mutation.py` uses `Ledger` as the **recording instrument** for the
Propose–Probe–Compose loop: one rollout per probe execution, one session per proposal stage.
Upstream's identity check (`assert_identity`, R = 4k / P = 3k) is used unchanged where the
loop's shape matches it.

The vendored ledger is a **recorder**, not an admission controller: it counts entries that
were already made and raises `BudgetError` when a *completed* run does not land on the expected
identity. It cannot stop a rollout before it happens. The refusal this project needs ("never
spend the 13th rollout of a 12-rollout budget") is therefore implemented in
`figpipe/mutation.py::_charge`, which checks the remaining budget *before* delegating to
`Ledger.rollout`. That split is stated here because a reader could otherwise assume the
vendored file enforces the budget by itself.

## What was NOT vendored

- `harness2/core/proposer.py`, `selection.py`, `recursion.py` — these drive model sessions
  through the Claude CLI or OpenCode. figpipe's loop is **deterministic**: no LLM, no network,
  no API key. Only the *idea* (Propose → Probe → Compose by behavioural contrast) is reused,
  re-implemented over figpipe's own operators.
- The rest of `harness2/core/` (context, judge, library, prompts, report, runmark, schedule,
  spec, tree). Not needed for budget accounting.
