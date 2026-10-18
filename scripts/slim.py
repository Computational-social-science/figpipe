"""Keep figpipe lean. Runs as part of every evolution cycle.

THE RULE
    figpipe must evolve AND stay small. Left alone it grows monotonically: every extraction
    adds crops, every VLM run adds labels, every test run leaves fixtures. Measured once at
    527.8 MB worktree / 187.8 MB tracked, of which 120.9 MB was regenerable page renders.

WHAT IS CONSIDERED FAT
    1. Anything git TRACKS that a script can regenerate
       -- page renders, test fixtures, __pycache__, .pytest_cache.
    2. Growable ARTEFACTS that live in the worktree
       -- run records (one per 6 h, forever), raw corpora, tool clones.
    3. The knowledge base itself, if it starts accumulating rules that were never re-checked.

    Each category has a different correct treatment:
       tracked-regenerable -> untrack (keep on disk, or delete; the script rebuilds it)
       run records        -> keep a rolling window; they are evidence, not state
       tool clones        -> delete after use; they are inputs to a one-off decision

WHAT IT DOES NOT DO
    It never deletes SOURCE, never deletes the knowledge base, and never deletes anything it
    cannot prove is regenerable. A slimmer that deletes the wrong file is worse than a fat
    repo.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Path prefixes that must never be tracked because a script regenerates them.
#: (glob, why). git is consulted for what is ACTUALLY tracked, so this list is a rule, not a
#: snapshot -- a file added tomorrow is covered.
REGENERABLE = [
    ("corpus/extracted/*/pages/*", "page renders, rebuilt by extract_corpus.py"),
    ("corpus/pages_for_vlm/*", "VLM page renders, rebuilt on demand"),
    ("corpus/raw/*", "raw downloads, re-fetchable"),
    ("_qc_negative/*", "negative-control fixtures, rebuilt by every test run"),
    ("_qc_tools_attempt/*", "one-off tool clones"),
    ("qc_artifacts/*", "QC outputs"),
    ("corpus/qc_r3/*", "QC round-3 outputs"),
]

#: Directories deleted outright when present -- one-off jobs already finished.
SCRATCH_DIRS = ["_qc_tools_attempt", "_qc_negative", ".pytest_cache"]

#: How many run records to keep. Six-hourly runs make 4/day = 1460/year; the newest 200 covers
#: ~50 days, which is enough to see a regression, and older ones are recoverable from git.
KEEP_RUNS = 200



#: Regenerable directories to DELETE from the filesystem, not merely untrack.
#:
#: Untracking the page renders removed them from git but left ~480 MB on disk, because the
#: extractor writes them beside the structure it produces. The repo became slimmer in version
#: control and stayed fat on the filesystem.
#:
#: What is KEPT on disk, and why:
#:   corpus/extracted/*/figures/*.png   the crops -- 27 MB, and they are what a human inspects
#:                                      to verify the extraction
#:   corpus/extracted/*/*.json / *.md   THE CORPUS. Not reproducible without re-running docling
#:                                      over 34 PDFs, so never deleted
REGENERABLE_ON_DISK = [
    ("corpus/extracted/*/pages", "page renders"),
    ("corpus/pages_for_vlm", "VLM page renders"),
    ("corpus/rendered", "verification renders"),
    ("corpus/vlm_controls", "control images"),
]


def purge_disk(apply: bool) -> list[str]:
    """Delete regenerable directories from the filesystem; report what was freed."""
    freed = []
    for pattern, why in REGENERABLE_ON_DISK:
        targets = list(ROOT.glob(pattern))
        if not targets:
            continue
        files = [f for t in targets for f in t.rglob("*") if f.is_file()]
        if not files:
            continue
        size = sum(f.stat().st_size for f in files)
        freed.append(f"{why}: {len(files)} files, {size / 1_000_000:.1f} MB")
        if apply:
            for t in targets:
                shutil.rmtree(t, ignore_errors=True)
    return freed


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return p.stdout


def tracked_regenerable() -> dict[str, list[str]]:
    """Which regenerable paths git is still tracking, per rule."""
    tracked = set(git("ls-files").splitlines())
    out = {}
    for pattern, why in REGENERABLE:
        prefix_globs = pattern.split("*")[0]
        hits = [t for t in tracked if t.startswith(prefix_globs) and "pages/" in t
                or (t.startswith(prefix_globs) and pattern.endswith("/*") and "/" in t)]
        # simpler and exact: ask git to match the glob for us
        matched = git("ls-files", "--", pattern).splitlines()
        if matched:
            out[why] = matched
    return out


def trim_run_records() -> list[str]:
    """Keep the newest KEEP_RUNS run records; return the ones removed."""
    runs = ROOT / "knowledge" / "runs"
    if not runs.is_dir():
        return []
    files = sorted(runs.glob("*.json"))
    if len(files) <= KEEP_RUNS:
        return []
    removed = []
    for f in files[: len(files) - KEEP_RUNS]:
        f.unlink()
        removed.append(f.name)
    return removed


def prune_scratch(apply: bool) -> list[str]:
    """Remove one-off scratch directories."""
    gone = []
    for name in SCRATCH_DIRS:
        d = ROOT / name
        if d.is_dir():
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
            gone.append(f"{name} ({size / 1_000_000:.1f} MB)")
            if apply:
                shutil.rmtree(d, ignore_errors=True)
    return gone


def measure() -> dict:
    tracked = git("ls-files").splitlines()
    tb = sum((ROOT / t).stat().st_size for t in tracked if (ROOT / t).is_file())
    wt = sum(f.stat().st_size for f in ROOT.rglob("*")
             if f.is_file() and ".git" not in f.parts)
    return {"tracked_files": len(tracked), "tracked_mb": round(tb / 1e6, 1),
            "worktree_mb": round(wt / 1e6, 1)}


def main(apply: bool = True) -> int:
    before = measure()
    fat = tracked_regenerable()
    removed_runs = trim_run_records()
    gone = prune_scratch(apply)
    freed = purge_disk(apply)

    print(f"  tracked : {before['tracked_files']} files, {before['tracked_mb']} MB")
    print(f"  worktree: {before['worktree_mb']} MB")
    if fat:
        print("  TRACKED BUT REGENERABLE (should be untracked):")
        for why, files in fat.items():
            print(f"    {len(files):4d}  {why}")
            if apply:
                git("rm", "-r", "--cached", "-q", "--ignore-unmatch", "--", *files[:500])
    else:
        print("  no regenerable path is tracked -- clean")
    if removed_runs:
        print(f"  trimmed {len(removed_runs)} old run records (kept newest {KEEP_RUNS})")
    if gone:
        print(f"  scratch dirs {'removed' if apply else 'found'}: {', '.join(gone)}")
    if freed:
        print(f"  disk {'freed' if apply else 'purgeable'}:")
        for line in freed:
            print(f"    {line}")

    after = measure()
    print(f"  after   : {after['tracked_files']} files, {after['tracked_mb']} MB")
    return 0 if not fat or apply else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main(apply="--dry-run" not in sys.argv))
