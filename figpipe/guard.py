"""Never lose accumulated evidence to a routine write: one shrink guard for every writer.

WHY THIS EXISTS
    On 2026-10-19 a two-task diagnostic run of the benchmark harness destroyed 106 accumulated rows
    of `corpus/e2e/plottwin_report.json`, because the harness wrote its report unconditionally and a
    small run simply replaced the pool. The fix at the time was a shrink guard inside that ONE
    script. It worked, and it was in the wrong place: the same shape exists in every writer that
    owns an accumulated collection -- the official scores, the coverage index, the run-record
    window. A guard that lives in one script protects one file.

    The general rule is the one the seed-package deletion taught: **a routine operation must not
    remove evidence as a side effect.** Shrinking accumulated data has to be a deliberate act with a
    flag attached, not a consequence of running the tool on a small input.

WHAT `write_or_refuse` GUARANTEES
    1. It READS the existing file and compares the size of the payload's declared collection with
       the existing one.
    2. A shrink RAISES `ShrinkRefused`, naming the path, BOTH counts and the override flag. The
       file on disk is untouched: the check happens before the write, and the write itself is
       atomic, so a refusal cannot leave a half-written file.
    3. A missing, unreadable or corrupt existing file counts as EMPTY. The guard must never be the
       reason a scheduled run crashes.
    4. The same size or larger is written without comment.
    5. The DEFAULT is to refuse. No code path in this module shrinks a file on its own: a caller
       that has a user-facing flag must pass `allow_shrink` explicitly.

WHAT IT IS NOT
    Not a schema validator and not a merge. It compares the COUNT of one declared collection, so a
    payload that keeps the count while losing content passes -- stated rather than implied. It
    guards the failure that actually happened (a small run replacing a large collection), not every
    conceivable one. A caller that needs merge semantics (`bench_plottwin --merge`) still implements
    them itself; the guard only decides whether the result may be written.

TWO SHAPES, ONE DECISION
    * `write_or_refuse` -- one file holding one collection ("tasks", "records", "rules").
    * `retain_or_refuse` -- a WINDOW over many files (`knowledge/runs/*.json`), where the collection
      is the file set and the "shrink" is the deletion of the oldest members.
    Both build the refusal from the same message formatter and the same tolerant reader, so there is
    one implementation of the concept in the project rather than one per script.
"""
from __future__ import annotations

import json
import os
import pathlib
from typing import Any, Callable, Iterable

__all__ = ["ShrinkRefused", "GuardMisuse", "write_or_refuse", "retain_or_refuse", "read_json"]

#: Collection types whose LENGTH is what the guard compares. A writer that serialises something
#: else has no accumulated rows and must not pretend it does.
_SIZED = (list, tuple, dict, set, frozenset)


class ShrinkRefused(RuntimeError):
    """A write would have reduced an accumulated collection; refused unless overridden."""


class GuardMisuse(ValueError):
    """The caller asked the guard to compare something that is not a sized collection.

    Raised for a PROGRAMMING error (a payload with no such key, or a scalar where a list belongs),
    never for a data condition: a malformed file on disk is tolerated, a malformed payload is not.
    """


def _default_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _size(value: Any, *, what: str) -> int:
    if not isinstance(value, _SIZED):
        raise GuardMisuse(
            f"{what} is a {type(value).__name__}, not a collection with a length, so the shrink "
            f"guard cannot compare it. Pass the list or mapping the writer serialises, or the key "
            f"that holds it.")
    return len(value)


def _load(path: pathlib.Path) -> tuple[Any, str]:
    """(parsed, state). Never raises: a file the guard cannot read counts as EMPTY.

    The states are reported to the caller rather than hidden, because "the existing file was
    corrupt" is a fact a scheduled run should be able to record. Collapsing it into "empty" without
    saying so would be the same defect as collapsing an unknown measurement into a passing one.
    """
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None, "missing"
    except OSError:
        return None, "unreadable"
    try:
        return json.loads(raw.decode("utf-8")), "ok"
    except (UnicodeDecodeError, ValueError):
        return None, "corrupt"


def read_json(path) -> tuple[Any, str]:
    """The parsed existing file and its state ('ok' / 'missing' / 'unreadable' / 'corrupt').

    Exposed so a caller that must MERGE (rather than replace) can read the old payload through the
    same tolerant reader the guard uses, instead of a second `json.loads` with its own opinions.
    """
    return _load(pathlib.Path(path))


def _existing_size(path: pathlib.Path, key: str | None) -> tuple[int, str]:
    """How large the collection already on disk is, and in what state it was found."""
    data, state = _load(path)
    if state != "ok":
        return 0, state
    if key is None:
        collection = data
    elif isinstance(data, dict):
        collection = data.get(key)
    else:
        collection = None
    if not isinstance(collection, _SIZED):
        # the file does not carry the collection the payload declares (a different schema, or a
        # scalar where a list belongs). Treat as empty so the writer is never blocked by an
        # unreadable shape, but report `no-collection` so the caller can see why.
        return 0, "no-collection"
    return len(collection), "ok"


def _refusal(what, existing: int, new: int, unit: str, override: str,
             floor: int | None = None) -> str:
    detail = f"{unit} would drop {existing} -> {new}"
    if floor is not None:
        detail += f", below the floor of {floor}"
    return f"refusing to shrink {what}: {detail}. Pass {override} to do it deliberately."


def write_or_refuse(path, payload, *, allow_shrink: bool = False, key: str | None = None,
                    unit: str = "rows", override: str = "allow_shrink=True",
                    dumps: Callable[[Any], str] | None = None,
                    atomic: bool = True) -> dict:
    """Write `payload` to `path`, REFUSING if its collection shrank.

    `key` names the field that holds the accumulated collection (`"tasks"`, `"records"`, `"rules"`).
    With `key=None` the payload IS the collection (a list of rows, or a mapping such as the
    offset -> task id coverage index).

    `override` is the flag a human must pass; it is quoted in the refusal so the message names its
    own escape hatch (`--fresh`, `--allow-shrink`, ...). It defaults to the Python keyword.

    Returns a small dict describing the decision, so a caller can record it:
        {"path", "existing", "new", "unit", "existing_state", "shrank", "allowed"}
    """
    path = pathlib.Path(path)
    if key is None:
        new = _size(payload, what="payload")
    else:
        if not isinstance(payload, dict):
            raise GuardMisuse(
                f"a payload with key={key!r} must be a mapping, not a {type(payload).__name__}")
        if key not in payload:
            raise GuardMisuse(
                f"payload has no {key!r} collection; the guard cannot compare what the writer "
                f"would accumulate. Declared keys: {sorted(payload)[:8]}")
        new = _size(payload[key], what=f"payload[{key!r}]")
    existing, state = _existing_size(path, key)
    shrank = new < existing
    if shrank and not allow_shrink:
        raise ShrinkRefused(_refusal(path, existing, new, unit, override))
    text = (dumps or _default_dumps)(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    if atomic:
        # Write beside the target and replace, so a killed process cannot leave a truncated
        # report -- the same failure the guard exists to prevent, one layer down.
        tmp = path.with_name(path.name + ".tmp")
        try:
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, path)
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
    else:
        path.write_text(text, encoding="utf-8")
    return {"path": str(path), "existing": existing, "new": new, "unit": unit,
            "existing_state": state, "shrank": shrank, "allowed": bool(allow_shrink)}


def retain_or_refuse(paths: Iterable, keep: int, *, allow_shrink: bool = False,
                     minimum: int = 1, unit: str = "records",
                     override: str = "allow_shrink=True") -> dict:
    """Keep the newest `keep` members of a file WINDOW; refuse to drop below `minimum`.

    WHY A SECOND SHAPE: the run-record window (`knowledge/runs/*.json`) is not one file with a list
    in it, it is a directory of evidence trimmed to a rolling window. Trimming it is SUPPOSED to
    remove files, so "any shrink is refused" would forbid the feature. What must be refused is a
    window that takes the audit trail below the floor it is supposed to keep -- the shape of the
    seed deletion: a routine operation removing evidence nobody meant to remove.

    `paths` must be ordered OLDEST FIRST; the newest `keep` are retained. Files are unlinked here so
    that a refusal provably deletes nothing.

    Returns {"existing", "new", "shrink", "removed", "kept", "allowed"}.
    """
    files = [pathlib.Path(p) for p in paths]
    existing = len(files)
    keep = max(0, int(keep))
    retained = files[existing - keep:] if keep else []
    new = len(retained)
    shrank = new < existing
    if shrank and new < max(0, int(minimum)) and not allow_shrink:
        raise ShrinkRefused(_refusal(f"the {unit} window", existing, new, unit, override,
                                     floor=minimum))
    removed: list[str] = []
    for victim in files[: existing - new]:
        try:
            victim.unlink()
            removed.append(victim.name)
        except FileNotFoundError:
            continue
        except OSError:
            # a file we cannot remove must not crash the lean pass; it stays in the window
            continue
    return {"existing": existing, "new": new, "shrink": shrank, "removed": removed,
            "kept": [f.name for f in retained], "allowed": bool(allow_shrink)}
