"""Answer-key tripwire: refuse to let the target figure enter the pipeline's own input.

WHY THIS EXISTS
    This project discovered the tautology rule the hard way: an "official score" of 100.0 that came
    from copying the reference figure's own code is not a capability, it is the answer key in the
    input. That was caught by reading the numbers, not by any control.

    Harness^2 (google-research/harness2, Apache 2.0) reached the same conclusion independently and
    built a mechanical guard for it: `context.assert_tree_has_no_grader_verdicts` refuses any
    harness file whose NAME or BODY contains a grader-verdict marker, because "files carrying these
    strings cannot be served as evidence to later tasks". Two projects arriving at the same rule is
    evidence the rule is real.

    This module is the figpipe-side equivalent, expressed for figures rather than harness trees.

THE RULE
    A measurement is tautological when the answer key is reachable from the input. For this project
    that means: when a candidate's style is being derived from a reference, the TARGET figure (the
    one being scored) must not be readable from that same code path. `assert_no_answer_key()` is
    called at the points where that could happen.

WHAT IT IS NOT
    Not a sandbox and not a security boundary. It is a tripwire against the specific mistake of
    letting a scored artefact leak into the inputs that produce it -- the mistake this project
    already made once, in `--source code`.
"""
from __future__ import annotations

import pathlib
import re

#: Filename fragments that mark a file as containing the ANSWER rather than an input.
#: Kept deliberately narrow: a false positive blocks legitimate work, so each entry names a
#: concrete artefact that really does carry the target.
ANSWER_KEY_PATTERNS: tuple[str, ...] = (
    "reference_code",        # the benchmark ships the target's own source
    "target_figure",         # the figure being scored
    "answer_key",
    "ground_truth_style",
)

#: Content markers that mean "this file states the verdict we are trying to measure".
VERDICT_MARKERS: tuple[str, ...] = (
    "official_code_channel",
    "deviation_defect_score",
    "score_code_deviation(",
)


class AnswerKeyLeak(RuntimeError):
    """The target artefact is reachable from the inputs that produce it."""


def _scan_text(text: str) -> str | None:
    for marker in VERDICT_MARKERS:
        if marker in text:
            return marker
    return None


def assert_no_answer_key(*paths: pathlib.Path | str, allow: tuple[str, ...] = ()) -> None:
    """Raise if any given path (or its directory contents) carries the answer key.

    `allow` names patterns that are legitimate for this particular call -- for example the scoring
    pass legitimately reads the reference IMAGE, and the ceiling run legitimately reads
    `reference_code` because that is precisely what it is measuring. Making the exception explicit
    is the point: an unstated exception is how the original tautology survived.
    """
    for raw in paths:
        path = pathlib.Path(raw)
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else [
            p for p in path.rglob("*") if p.is_file()]
        for p in candidates:
            name = p.name.lower()
            for pattern in ANSWER_KEY_PATTERNS:
                if pattern in name and not any(a in name for a in allow):
                    raise AnswerKeyLeak(
                        f"answer key reachable: {p} matches {pattern!r}. A measurement whose "
                        f"target is readable from its input is tautological -- that is how this "
                        f"project once scored 100.0 by copying the reference code. Pass "
                        f"allow=(...) only when the leak IS the thing being measured.")
            # content scan only for small text files; a PDF or PNG cannot be scanned this way
            if p.suffix.lower() in {".py", ".json", ".md", ".txt", ".csv", ".yaml", ".yml"}:
                try:
                    if p.stat().st_size > 2_000_000:
                        continue
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                marker = _scan_text(text)
                if marker and not any(a in name for a in allow):
                    raise AnswerKeyLeak(
                        f"answer key reachable: {p} contains verdict marker {marker!r}. The "
                        f"scored value must not be readable from the inputs that produce it.")


def assert_style_source_is_honest(source: str, *, target_path=None) -> None:
    """`image` is honest; `code` is the tautological ceiling and must say so.

    This encodes the distinction the project paid for: style inferred from the reference PICTURE is
    a capability; style copied from the reference CODE reproduces every scored dimension by
    construction. Anything else must be named.
    """
    if source not in ("image", "code", "naive", "ceiling"):
        raise AnswerKeyLeak(
            f"unknown style source {source!r}; expected 'image' (honest), 'naive' (baseline) or "
            f"'code'/'ceiling' (tautological, reported only as a ceiling)")
    if source in ("code", "ceiling") and target_path is not None:
        # the ceiling run is allowed to read the code -- but never to be reported as the pipeline
        pass


def audit_measurement_sources() -> dict:
    """Report which measured artefacts declare a tautological source.

    Used by the report so a ceiling can never be quoted without its label.
    """
    import json

    root = pathlib.Path(__file__).resolve().parents[1]
    out: dict[str, str] = {}
    for name in ("official_scores.json", "official_scores_code.json",
                 "official_scores_naive.json"):
        path = root / "corpus" / "e2e" / name
        if not path.is_file():
            continue
        try:
            summary = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
        except (OSError, ValueError):
            continue
        out[name] = str(summary.get("style_source", "undeclared"))
    return out
