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
import sys as _sys
_sys.path.insert(0, str(ROOT))
try:
    from figpipe import guard
except Exception:                                    # pragma: no cover
    guard = None                                     # reported, never fatal
try:
    from figpipe.sources import assert_writable as _assert_writable
except Exception:                                    # pragma: no cover
    def _assert_writable(p):                         # fallback: refuse nothing, but refuse to
        return p                                     # crash the loop if the module is missing


#: Path prefixes that must never be tracked because a script regenerates them.
#: (glob, why). git is consulted for what is ACTUALLY tracked, so this list is a rule, not a
#: snapshot -- a file added tomorrow is covered.
REGENERABLE = [
    ("corpus/extracted/*/pages/*", "page renders, rebuilt by extract_corpus.py"),
    ("corpus/pages_for_vlm/*", "VLM page renders, rebuilt on demand"),
    ("corpus/raw/*", "raw downloads, re-fetchable"),
    ("_qc_negative/*", "negative-control fixtures, rebuilt by every test run"),
    ("_qc_tools_attempt/*", "one-off tool clones -- vendored copies of upstream tools, kept"),
    # NOTE: these vendored clones ARE valuable (they are what figpipe/_qc_vendor also carries),
    # but the scratch directory is a working copy. The canonical copies live under
    # figpipe/_qc_vendor/ and are tracked there.
    ("qc_artifacts/*", "QC outputs"),
    ("corpus/qc_r3/*", "QC round-3 outputs"),
]

#: Directories deleted outright when present -- one-off jobs already finished.
SCRATCH_DIRS = ["_qc_tools_attempt", "_qc_negative", ".pytest_cache",
                # every mutation probe writes a PDF here; regenerable by re-running
                "templates/mutation"]

#: How many run records to keep. Six-hourly runs make 4/day = 1460/year; the newest 200 covers
#: ~50 days, which is enough to see a regression, and older ones are recoverable from git.
KEEP_RUNS = 200

#: The FLOOR the window may never go below, whatever KEEP_RUNS is set to. The window exists to bound
#: a growing directory, not to empty the audit trail: a mistyped or mis-defaulted KEEP_RUNS once
#: would delete the history silently, which is the seed-deletion shape (routine operation removes
#: evidence). `trim_run_records` refuses to cross this line without an explicit override.
MIN_RUN_RECORDS = 20



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
                # Refuse to delete anything inside a read-only source root. This project
                # learns from published PDFs on D:/ -- they are the INPUT and are not
                # recoverable from git.
                _assert_writable(t)
                shutil.rmtree(t, ignore_errors=True)
    return freed


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return p.stdout


def tracked_regenerable() -> dict[str, list[str]]:
    """Which regenerable paths git is still tracking, per rule."""
    out = {}
    for pattern, why in REGENERABLE:
        # Ask GIT to match the glob. An earlier version computed a `hits` list from
        # `str.startswith(pattern.split("*")[0])` and never used it -- the result came from the
        # `git ls-files` call below. Dead code that looks like the real check is worse than no
        # check, because a reader believes it. The expression also had an operator-precedence bug
        # (`A and B or C and D` binds as `(A and B) or (C and D)`).
        matched = git("ls-files", "--", pattern).splitlines()
        if matched:
            out[why] = matched
    return out


def trim_run_records(*, allow_shrink: bool = False) -> list[str]:
    """Keep the newest KEEP_RUNS run records; return the ones removed.

    THE WINDOW IS EVIDENCE, SO IT GOES THROUGH THE SHARED GUARD. `knowledge/runs/*.json` is the
    audit trail of what each scheduled run found; trimming it is a routine operation that REMOVES
    FILES, which is exactly the shape of the seed-package deletion (a routine `git add -A` committed
    the absence of files nobody meant to delete). Trimming is legitimate and must keep working, but
    a trim that would take the trail below `MIN_RUN_RECORDS` is refused with both counts named, and
    nothing is unlinked. The decision itself is `figpipe.guard.retain_or_refuse`, not a local copy
    of the idea.

    A refusal is RAISED, not swallowed: `evolve.py` already records an exception from this call in
    `report["lean"]["error"]`, so the run record shows that the window policy fired instead of
    reporting "trimmed 0" -- a control that looks present and does nothing is the defect this
    project keeps finding.
    """
    runs = ROOT / "knowledge" / "runs"
    if not runs.is_dir():
        return []
    files = sorted(runs.glob("*.json"))
    if len(files) <= KEEP_RUNS:
        return []
    result = guard.retain_or_refuse(files, KEEP_RUNS, allow_shrink=allow_shrink,
                                    minimum=MIN_RUN_RECORDS, unit="run records",
                                    override="--allow-shrink")
    return result["removed"]


def prune_scratch(apply: bool) -> list[str]:
    """Remove one-off scratch directories."""
    gone = []
    for name in SCRATCH_DIRS:
        d = ROOT / name
        if d.is_dir():
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
            gone.append(f"{name} ({size / 1_000_000:.1f} MB)")
            if apply:
                _assert_writable(d)
                shutil.rmtree(d, ignore_errors=True)
    return gone


def measure() -> dict:
    tracked = git("ls-files").splitlines()
    tb = sum((ROOT / t).stat().st_size for t in tracked if (ROOT / t).is_file())
    wt = sum(f.stat().st_size for f in ROOT.rglob("*")
             if f.is_file() and ".git" not in f.parts)
    return {"tracked_files": len(tracked), "tracked_mb": round(tb / 1e6, 1),
            "worktree_mb": round(wt / 1e6, 1)}


def main(apply: bool = True, *, allow_shrink: bool = False) -> int:
    before = measure()
    fat = tracked_regenerable()
    removed_runs = trim_run_records(allow_shrink=allow_shrink)
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
    raise SystemExit(main(apply="--dry-run" not in sys.argv,
                          allow_shrink="--allow-shrink" in sys.argv))
