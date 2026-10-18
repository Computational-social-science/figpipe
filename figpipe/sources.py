"""The source PDFs are READ-ONLY. This module makes that a checked invariant.

WHY THIS EXISTS
    figpipe learns from published Nature papers. Those PDFs are the owner's own library,
    organised across ~30 topic folders on D:/. They are the INPUT to the whole project and must
    never be modified, moved, or deleted by anything figpipe does.

    An audit found that no script currently writes to them -- the extractor only calls
    `open(..., "w")` on its own inventory file, and the slimming pass deletes only four
    project-internal, regenerable directories. But "no script does it today" is not a
    guarantee: one careless `shutil.rmtree(source_root)` in a future edit would destroy the
    corpus, and it would not be recoverable from git.

    So the rule is enforced, not remembered.

WHAT IS ENFORCED
    1. A PATH GUARD. `assert_writable(path)` refuses any path that resolves inside a registered
       source root. Every destructive helper in this project must call it first.
    2. A SNAPSHOT. `fingerprint(root)` records (path, size, mtime) for every PDF under the
       sources, so a later comparison can PROVE nothing changed.
    3. The source roots themselves are data, so adding a root is a visible edit rather than a
       hard-coded string buried in a walker.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Directories whose contents are READ-ONLY INPUT. Nothing may be written inside them.
#: Declared here so every module shares one definition.
READ_ONLY_ROOTS = [
    pathlib.Path("D:/2026-AI4S"),
    pathlib.Path("D:/"),
    pathlib.Path("C:/keystroke-corpus"),
    # the seed paper's raw OpenAlex-derived tables, moved out of the repository to keep it lean
    # (see Seeds/README.md). They are the INPUT to the reproduction and must never be written.
    pathlib.Path("E:/2026-AI4S/dataverse_cache"),
]

#: Only this subtree may be written by figpipe.
WRITABLE_ROOT = ROOT


class SourceProtectionError(RuntimeError):
    """Raised when an operation would write inside a read-only source root."""


def _resolve(p) -> pathlib.Path:
    return pathlib.Path(os.path.abspath(str(p)))


def is_inside_source(path) -> bool:
    """True when `path` resolves inside any registered read-only root."""
    p = _resolve(path)
    for root in READ_ONLY_ROOTS:
        try:
            r = _resolve(root)
        except OSError:
            continue
        if p == r or r in p.parents:
            return True
    return False


def assert_writable(path) -> pathlib.Path:
    """Refuse to operate destructively on a source path. Returns the resolved path."""
    p = _resolve(path)
    if is_inside_source(p):
        raise SourceProtectionError(
            f"refusing to write or delete {p}: it is inside a READ-ONLY source root. The "
            f"published PDFs are the project's input and are not recoverable from git.")
    return p


def fingerprint(root, limit: int | None = None, full: bool = False) -> dict:
    """A content-and-metadata fingerprint of every PDF under `root`.

    Used to PROVE the sources are unchanged after a long run, rather than assuming it.

    `full=True` also hashes each file's bytes. Metadata alone (size + sub-second mtime) can
    miss a same-length rewrite that happens inside one filesystem timestamp tick -- a test
    caught exactly that, so the content hash is the guarantee and the metadata is the fast path.
    """
    root = _resolve(root)
    recs = {}
    if not root.is_dir():
        return {"root": str(root), "exists": False, "files": {}}
    for i, p in enumerate(sorted(root.rglob("*.pdf"))):
        if limit is not None and i >= limit:
            break
        try:
            st = p.stat()
        except OSError:
            continue
        rec = {"size": st.st_size, "mtime_ns": st.st_mtime_ns}
        if full:
            rec["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
        recs[str(p)] = rec
    digest = hashlib.sha256(
        json.dumps(recs, sort_keys=True).encode()).hexdigest()[:16]
    return {"root": str(root), "exists": True, "n_files": len(recs),
            "digest": digest, "files": recs}


def compare(before: dict, after: dict) -> dict:
    """What changed between two fingerprints: added, removed, modified."""
    b, a = before.get("files", {}), after.get("files", {})
    added = sorted(set(a) - set(b))
    removed = sorted(set(b) - set(a))
    modified = sorted(k for k in set(b) & set(a) if b[k] != a[k])
    return {"added": added, "removed": removed, "modified": modified,
            "unchanged": not (added or removed or modified),
            "digest_before": before.get("digest"), "digest_after": after.get("digest")}


if __name__ == "__main__":
    print("  READ-ONLY source roots:")
    for r in READ_ONLY_ROOTS:
        print(f"    {r}  exists={r.is_dir()}  inside_project={is_inside_source(r) is False and str(_resolve(r)).startswith(str(_resolve(WRITABLE_ROOT)))}")
    print()
    print("  self-test: writing inside a source must be refused")
    for probe in (READ_ONLY_ROOTS[0] / "x.pdf", pathlib.Path("D:/some.pdf"),
                  ROOT / "corpus" / "ok.json"):
        inside = is_inside_source(probe)
        print(f"    {str(probe)[:52]:<52} inside_source={inside}  "
              f"{'BLOCKED' if inside else 'allowed'}")
