"""figpipe must evolve AND stay lean. These tests make "lean" a checked property.

THE RULE
    The owner's instruction: figpipe 必须一边自进化，一边维持瘦身状态，遵循最小化原则，避免自身
    不断无节制地体积增长.

    Measured when this file was written: 527.8 MB worktree and 187.8 MB tracked, of which
    120.9 MB was regenerable page renders. The repo had grown monotonically because every
    extraction added crops, every VLM run added labels and every test run left fixtures -- and
    nothing ever removed anything.

WHY BUDGETS RATHER THAN A CLEANUP SCRIPT
    A cleanup script that runs when someone remembers is not a guarantee. These tests state the
    budget, so exceeding it fails the suite and blocks the commit. The numbers are deliberately
    loose enough to allow a normal extraction and tight enough that the old 527 MB state fails.

WHAT EACH TEST PROTECTS
    * tracked size ceiling      -- catches assets creeping back into version control
    * no regenerable path tracked -- catches the specific mistake that caused the bloat
    * worktree ceiling          -- catches intermediates piling up on disk
    * run-record window         -- catches unbounded growth of the audit trail
    * the corpus itself is still tracked -- the opposite failure: slimming something vital
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

slim = pytest.importorskip("slim", reason="slim module absent")

#: Budgets. Tracked bytes are the version-control footprint; worktree is disk.
MAX_TRACKED_MB = 80.0       # the corpus structure + crops is ~42 MB; room for growth, not bloat
MAX_WORKTREE_MB = 150.0     # intermediates allowed transiently, but not 500 MB of them
#: The audit trail is evidence, not state: a window is enough to see a regression.
MAX_RUN_RECORDS = 260


def _tracked_files() -> list[str]:
    p = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.splitlines()


def test_tracked_size_is_within_budget():
    files = _tracked_files()
    total = sum((ROOT / f).stat().st_size for f in files if (ROOT / f).is_file())
    mb = total / 1e6
    assert mb <= MAX_TRACKED_MB, (
        f"git tracks {mb:.1f} MB across {len(files)} files, over the {MAX_TRACKED_MB} MB "
        f"budget. Before the first slimming pass this stood at 187.8 MB, 64 % of it "
        f"regenerable page renders. Find the large additions and untrack them.")


def test_no_regenerable_path_is_tracked():
    """THE SPECIFIC MISTAKE THAT CAUSED THE BLOAT, made un-repeatable.

    `corpus/extracted/*/pages/` was in .gitignore and `git check-ignore` matched it -- yet the
    files were tracked anyway, because a .gitignore rule does not apply to a path git already
    tracks. A control that looks present and does nothing.
    """
    fat = slim.tracked_regenerable()
    assert not fat, (
        "these regenerable paths are still tracked: "
        + "; ".join(f"{n} x {why}" for why, n in ((len(v), k) for k, v in fat.items())))


#: Paths excluded from the worktree budget. Each is an INPUT cache that its owning script bounds
#: itself; counting them makes a correct concurrent run look like a leak.
WORKTREE_EXEMPT = ("corpus/e2e/images", "corpus/e2e/cache")


def test_worktree_is_within_budget():
    exempt = tuple((ROOT / p).resolve() for p in WORKTREE_EXEMPT)

    def _counted(path: pathlib.Path) -> bool:
        resolved = path.resolve()
        return not any(str(resolved).startswith(str(e)) for e in exempt)

    total = sum(f.stat().st_size for f in ROOT.rglob("*")
                if f.is_file() and ".git" not in f.parts and _counted(f))
    mb = total / 1e6
    assert mb <= MAX_WORKTREE_MB, (
        f"the worktree is {mb:.1f} MB, over the {MAX_WORKTREE_MB} MB budget. Regenerable "
        f"intermediates (page renders, VLM renders) are the usual cause -- run "
        f"`python scripts/slim.py`.")


def test_run_records_are_windowed():
    runs = ROOT / "knowledge" / "runs"
    if not runs.is_dir():
        pytest.skip("no run records yet")
    n = len(list(runs.glob("*.json")))
    assert n <= MAX_RUN_RECORDS, (
        f"{n} run records kept, over the window of {MAX_RUN_RECORDS}. Six-hourly runs make "
        f"~1460 a year; the audit trail is evidence, not state, and old entries are "
        f"recoverable from git.")


def test_the_corpus_itself_is_still_tracked():
    """The opposite failure: a slimmer that deletes something vital.

    The figure crops are kept deliberately -- they are what a human inspects to verify the
    extraction -- and the structure (figures_meta.json / layout.json) is the corpus itself,
    not reproducible without re-running docling over every PDF.
    """
    files = _tracked_files()
    meta = [f for f in files if f.endswith("figures_meta.json")]
    crop = [f for f in files if "/figures/" in f and f.endswith(".png")]
    assert len(meta) >= 30, f"only {len(meta)} figures_meta.json tracked; the corpus is lost"
    assert len(crop) >= 150, f"only {len(crop)} figure crops tracked; verification is crippled"


def test_publisher_refuses_to_stage_a_bloated_addition(tmp_path):
    """THE DEFECT THAT GOT PAST THE BUDGET: `git add -A` in the scheduled publisher.

    On 2026-10-18 a scheduled run staged 1567.5 MB of dataverse CSVs that were sitting in the
    worktree and committed them, taking the tracked footprint from ~70 MB to 1717.6 MB. The
    budget test above noticed -- but only after the commit existed. The publisher now measures
    the index before committing. This proves the measurement fires, on a real repository.
    """
    import subprocess

    cron = pytest.importorskip("cron_run")
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / "small.txt").write_text("ok", encoding="utf-8")
    with (repo / "big.csv").open("wb") as fh:
        fh.write(b"0" * 9_000_000)
    git("add", "small.txt", "big.csv")

    problems = cron.staged_problems(cwd=repo)
    flagged = {p["path"] for p in problems}
    assert "big.csv" in flagged, (
        f"a 9 MB addition was not flagged by the publish guard: {problems}")
    assert "small.txt" not in flagged, problems
    git("reset", "-q", "--", "big.csv")
    assert cron.staged_problems(cwd=repo) == [], (
        "the guard still flags the index after the oversized file was unstaged; it would "
        "block every routine commit")


def test_slim_measures_and_reports_consistently():
    m = slim.measure()
    assert m["tracked_files"] == len(_tracked_files())
    assert m["tracked_mb"] >= 0 and m["worktree_mb"] >= m["tracked_mb"]
