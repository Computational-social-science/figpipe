"""A candidate that is a CODE EDIT, not a scalar.

WHY THIS EXISTS
    The mutation loop's `Candidate` is `(operator, parameter, baseline_value, value)` and
    `run_task` applies it as `params.update({parameter: value})`. That is enough to move a budget
    integer and nothing else.

    Measured over 152 scheduled runs: 4 knowledge changes, 222 ties, 149 runs that selected
    NOTHING. Every real fix this project made -- the polar label overflow, the colour bar falling
    off the page, the pivot choosing a row index as its measurement, the matrix budget that checked
    rows and not columns -- was a DRAWER CHANGE. None of them is expressible as `{param: value}`.
    The loop's discovery channel was five integers, so it could not discover anything else.

WHAT THIS IS
    A `Patch` is a declared textual replacement in one module, applied for the duration of a probe
    and reverted afterwards. It is still DATA -- a (file, old, new, reason) tuple -- so a probe
    records exactly what was changed rather than a diff of generated code.

    Two rules make it safe enough to run unattended:
      * the OLD text must occur EXACTLY ONCE in the file, or the patch refuses (an ambiguous
        replacement would edit the wrong place silently)
      * the NEW text is applied by rewriting the file, importing nothing new, and the ORIGINAL bytes
        are restored in a `finally` -- so a crash mid-probe cannot leave the tree modified

WHAT THIS IS NOT
    It is not a general refactoring engine. A patch that needs to touch two places, add an import or
    change a signature is out of scope and must be reported as unproposable, which is the honest
    answer rather than a silent skip.
"""
from __future__ import annotations

import dataclasses
import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Patch:
    """One declared textual edit, applied for a probe and reverted afterwards."""

    id: str
    path: str
    old: str
    new: str
    rationale: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


class PatchError(RuntimeError):
    """A patch that cannot be applied unambiguously is refused, not approximated."""


def _resolve(root: pathlib.Path, path: str) -> pathlib.Path:
    target = (root / path).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise PatchError(f"patch path escapes the repository: {path}")
    if not target.is_file():
        raise PatchError(f"no such file: {path}")
    return target


def check(root, patch: Patch) -> tuple[bool, str]:
    """Can this patch be applied unambiguously? Returns (ok, why).

    THE OLD TEXT MUST OCCUR EXACTLY ONCE. A replacement that matches twice would edit whichever
    place `str.replace` reaches first, and the probe would then measure a change nobody declared.
    """
    try:
        target = _resolve(pathlib.Path(root), patch.path)
    except PatchError as exc:
        return False, str(exc)
    text = target.read_text(encoding="utf-8")
    n = text.count(patch.old)
    if n == 1:
        return True, "applies"
    if n == 0:
        return False, f"the old text is not present in {patch.path}"
    return False, f"the old text occurs {n} times in {patch.path}; an ambiguous patch is refused"


def apply(root, patch: Patch) -> str:
    """Apply the patch and return the ORIGINAL text, which the caller must restore."""
    ok, why = check(root, patch)
    if not ok:
        raise PatchError(why)
    target = _resolve(pathlib.Path(root), patch.path)
    original = target.read_text(encoding="utf-8")
    target.write_text(original.replace(patch.old, patch.new, 1), encoding="utf-8")
    return original


def revert(root, patch: Patch, original: str) -> None:
    """Restore the file to its pre-patch bytes."""
    target = _resolve(pathlib.Path(root), patch.path)
    target.write_text(original, encoding="utf-8")


def probe_with_patch(root, patch: Patch, fn):
    """Run `fn()` with the patch applied, restoring the file whatever happens.

    THE `finally` IS THE POINT. An unattended loop that crashes mid-probe must not leave a source
    file edited -- the next run would then measure a tree nobody chose.
    """
    original = apply(root, patch)
    try:
        return fn()
    finally:
        revert(root, patch, original)


def describe(patch: Patch) -> str:
    """One line for a run record."""
    return f"{patch.path}: {patch.id} ({patch.rationale[:60]})"
