"""Named quality dimensions, scored separately -- a deterministic answer to a VLM rubric.

WHY THIS EXISTS
    AutoFigure (ResearAI/AutoFigure, ICLR 2026) scores a generated figure 0-10 on eleven named
    dimensions and reports each separately, so a user learns WHAT to fix rather than just that
    something is wrong. figpipe's audit reports findings by `check` name but has no named
    dimensions and no per-dimension score -- a flat list, which tells a user that five things
    failed and not which one matters.

    AutoFigure's mechanism is a VLM-as-Judge. This project measured that approach and rejected it:
    `vlm_report.json` recorded 20 fabrications in VLM descriptions of figures. So the STRUCTURE is
    adopted and the JUDGE is not.

WHAT IS TRANSFERABLE, EXACTLY
    * name the dimension
    * score it separately on a fixed scale
    * report the worst dimension first, so the list has an order
    * state which dimensions could NOT be measured, rather than omitting them

    A dimension that cannot be measured deterministically is reported as UNMEASURED with the
    reason. Omitting it would let a reader believe the figure is good on it.

WHAT IS NOT TRANSFERABLE
    AutoFigure's rubric includes Visual Expressiveness, Logical Flow, Information Sophistication
    and Appropriateness to Audience. None of those can be decided by a deterministic check -- they
    need a reader. They are listed as unmeasured here, with that reason, rather than being faked
    with a heuristic that would be wrong in ways nobody could audit.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

#: Every dimension this module can score, worst-first ordering is applied at report time.
DIMENSIONS = (
    "typography",       # font size band and embedded Type-42 fonts
    "geometry",         # exact column width and height limits
    "legibility",       # overlapping glyphs, axis label budgets
    "density",          # marks per axis (bars, spokes, matrix cells)
    "colour",           # palette validity, rainbow maps, contrast
    "semantics",        # printed numbers re-derived from the data
)

#: Dimensions a deterministic check cannot decide. Reported, never silently dropped.
UNMEASURABLE = {
    "visual_expressiveness": "needs a reader: does the figure communicate through visual metaphor",
    "logical_flow": "needs the source argument, not the figure",
    "information_sophistication": "needs the field's conventions, not the pixels",
    "audience_appropriateness": "depends on who reads it",
    "completeness": "needs to know what the figure was supposed to show",
}


@dataclass
class DimensionScore:
    """One named dimension: what was checked, what it scored, and what to do about it."""

    name: str
    score: float | None          # 0..1, or None when the dimension could not be measured
    detail: str = ""
    findings: list[str] = field(default_factory=list)

    @property
    def measured(self) -> bool:
        return self.score is not None

    @property
    def band(self) -> str:
        """A word, because '0.83' does not tell a user whether to act."""
        if self.score is None:
            return "unmeasured"
        if self.score >= 0.99:
            return "pass"
        if self.score >= 0.8:
            return "minor"
        if self.score >= 0.5:
            return "needs work"
        return "fails"


def _band_score(n_bad: int, n_checked: int) -> float | None:
    """Fraction of checks that passed. None when nothing was checked."""
    if n_checked <= 0:
        return None
    return round(max(0.0, (n_checked - n_bad) / n_checked), 3)


def score_audit(report: dict) -> DimensionScore:
    """Typography and geometry from an `audit.audit()` report.

    Split into two dimensions because they have different fixes: a sub-5 pt label is a typography
    problem, a 198 mm page is a layout problem, and a user who is told "audit failed" does not know
    which one they have.
    """
    findings = report.get("findings") or []
    type_bad = [f for f in findings if f.get("check") in ("font_size", "font_type")]
    # audit checks typography and geometry separately; each has 2 possible checks. The geometry
    # findings belong to `score_geometry`, not here -- an earlier version computed them twice.
    return DimensionScore(
        name="typography",
        score=_band_score(len(type_bad), 2),
        detail="font size band and embedded Type-42 fonts",
        findings=[f"{f['check']}: {f['detail']}" for f in type_bad[:5]],
    )


def score_geometry(report: dict) -> DimensionScore:
    findings = report.get("findings") or []
    geom_bad = [f for f in findings if f.get("check") in ("width", "height")]
    return DimensionScore(
        name="geometry",
        score=_band_score(len(geom_bad), 2),
        detail="Nature column width and page height limits",
        findings=[f"{f['check']}: {f['detail']}" for f in geom_bad[:5]],
    )


def _ran(trace: list[str], needle: str) -> bool:
    """Did a given verification step actually execute?

    "findings is empty" is ambiguous: it can mean the check RAN and found nothing (a PASS) or that
    no check ran (UNMEASURED). The trace records which steps executed, so it is the right signal --
    without it, a perfect figure and an unverified one look identical.
    """
    return any(needle in step for step in (trace or []))


def score_legibility(findings: list[dict], trace: list[str] | None = None) -> DimensionScore:
    """Overlapping glyphs from a rendering pass (`verify.collisions`)."""
    hard = [f for f in findings
            if f.get("severity") == "hard" and f.get("check") == "text_collision"]
    # no collision is perfect; each collision is a defect. 5+ is a broken figure.
    if not _ran(trace or [], "verify.collisions"):
        return DimensionScore("legibility", None, "the collision check did not run")
    score = max(0.0, 1.0 - len(hard) / 5.0)
    return DimensionScore(
        name="legibility",
        score=round(score, 3),
        detail="overlapping glyphs in the rendered file",
        findings=[f.get("detail", "") for f in hard[:5]],
    )


def score_semantics(findings: list[dict], trace: list[str] | None = None) -> DimensionScore:
    """Printed numbers re-derived from the data (`figpipe/semantics.py`)."""
    sem = [f for f in findings if str(f.get("check", "")).startswith("semantic")]
    if not _ran(trace or [], "verify.semantics"):
        return DimensionScore("semantics", None, "the semantic check did not run")
    return DimensionScore(
        name="semantics",
        score=_band_score(len(sem), max(1, len(sem) + 1)),
        detail="every printed number re-derived from the input data",
        findings=[f.get("detail", "") for f in sem[:5]],
    )


def score_colour(findings: list[dict], trace: list[str] | None = None) -> DimensionScore:
    """Rainbow maps and contrast problems from `colourcheck`."""
    col = [f for f in findings
           if str(f.get("check", "")).startswith("colour")
           or str(f.get("check", "")).startswith("color")]
    if not _ran(trace or [], "colour"):
        return DimensionScore("colour", None, "the colour check did not run")
    return DimensionScore(
        name="colour",
        score=_band_score(len(col), max(1, len(col) + 2)),
        detail="perceptually uniform maps, no rainbow, adequate contrast",
        findings=[f.get("detail", "") for f in col[:5]],
    )


def report(dimensions: list[DimensionScore], *, figure: str = "") -> dict:
    """Assemble the named dimensions into one ordered report.

    ORDER IS THE POINT. AutoFigure reports dimensions separately so a user knows what to fix
    first; a flat list of findings does not. Measured dimensions are sorted worst-first and the
    unmeasured ones are listed after them WITH their reason, never omitted.
    """
    measured = [d for d in dimensions if d.measured]
    unmeasured = [d for d in dimensions if not d.measured]
    measured.sort(key=lambda d: (d.score if d.score is not None else 1.0))

    worst = measured[0] if measured else None
    return {
        "figure": figure,
        "dimensions": [
            {"name": d.name, "score": d.score, "band": d.band,
             "detail": d.detail, "findings": d.findings}
            for d in measured
        ],
        "unmeasured": [
            {"name": d.name, "why": d.detail or "no check available"} for d in unmeasured
        ],
        "worst": worst.name if worst else None,
        "worst_band": worst.band if worst else None,
        "mean": round(sum(d.score for d in measured) / len(measured), 3) if measured else None,
        "verdict": ("no dimension could be measured" if not measured else
                    f"worst dimension: {worst.name} ({worst.band})"),
    }


def for_skill_result(result: dict, *, figure: str = "") -> dict:
    """Build the report from a `skills.run()` result, which is what a caller actually has."""
    findings = result.get("findings") or []
    trace = result.get("trace") or []
    dims = [
        score_legibility(findings, trace),
        score_semantics(findings, trace),
        score_colour(findings, trace),
    ]
    return report(dims, figure=figure or str(result.get("pdf", "")))
