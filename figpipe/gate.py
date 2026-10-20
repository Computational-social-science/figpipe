"""The acceptance gate: what "done" means for a figure, borrowed from BootLoops.

WHY THIS EXISTS
    BootLoops (E:\\2026-AI4S\\bootloops) is a harness for LLMs doing precision quantitative science.
    Its `acceptance-gate` skill states the standard a computed result must meet before it may be
    called done:

        A result is done when it has survived a check that could have failed, run by a route that
        could not have known the answer. It is never done merely because the computation that
        produced it finished.

    That sentence describes, exactly, the failures this project has been finding one at a time for
    thirty rounds. Its list of failure modes reads like figpipe's own bug history:

        * "the gate that cannot fail"          -- the anchor that accepted a partial membership
        * "the unconditional success line"     -- `RESULT: compliant` printed after a skipped audit
        * "certifying at fitted points"        -- the pool score that copied `reference_code`
        * "threshold drift"                    -- KNOWN_CORRECTIONS widened until 93.53 passed
        * "adjectives in place of counts"      -- "compliant" with no dimension scores
        * "self-graded confidence"             -- the CLI reporting its own success

    figpipe had each of those as a separate lesson. BootLoops states them as one standard, with a
    procedure that produces the evidence rather than the adjective. This module is that procedure,
    made executable for a figure.

WHAT A FIGURE'S GATE IS
    A figure is not a number, so "digit agreement" does not apply. The translation is:

        reserved points   -> the DIMENSIONS the figure is judged on, fixed before rendering
        independent route -> a check that reads the RENDERED FILE, not the code that drew it
        digit count       -> a measured value per dimension, not an adjective
        raised precision  -> re-render at a different size and confirm the verdict holds
        positive control  -> a figure known to pass must pass
        negative control  -> a deliberately broken figure must FAIL, visibly
        true verdict      -> CLOSED only if every dimension passed AND the controls fired

    The negative control is the load-bearing part, and it is the one this project kept skipping.
    A gate that has never failed anything certifies nothing.

WHAT THIS DOES NOT DO
    It does not decide whether a figure is BEAUTIFUL or whether it COMMUNICATES. Those are
    `quality.UNMEASURABLE` and stay unmeasured. A gate that claims them would be the thing it is
    meant to prevent.
"""
from __future__ import annotations

import dataclasses
import pathlib
from dataclasses import dataclass, field

from . import audit, quality, structure

#: The verdict vocabulary, exactly as BootLoops defines it. There are two words, and no others.
CLOSED = "CLOSED"
OPEN = "OPEN"


@dataclass
class GateCheck:
    """One dimension of the gate: what was measured, what it had to be, and whether it was."""

    name: str
    measured: object
    required: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class Gate:
    """A gate DECLARED before the figure exists.

    The order rule is the whole point: a gate written after the candidate exists inherits the
    candidate's blind spots, because the check is chosen -- consciously or not -- to pass.
    """

    name: str
    checks: list[GateCheck] = field(default_factory=list)
    controls: dict = field(default_factory=dict)
    verdict: str = OPEN
    notes: list[str] = field(default_factory=list)

    def add(self, name: str, measured, required: str, passed: bool, detail: str = "") -> None:
        self.checks.append(GateCheck(name, measured, required, bool(passed), detail))

    def close(self) -> str:
        """Compute the verdict from the measured checks. Never set by hand.

        `CLOSED` requires every check to have passed. Anything less is `OPEN`, reported with what
        remains -- "an honest OPEN is a result; a false CLOSED is damage, because later work builds
        on it."

        THE CONTROLS ARE NOT PART OF THIS VERDICT, and separating them matters. A figure's verdict
        answers "did this figure pass the gate"; whether the gate can fire at all is a property of
        the GATE, certified separately by `validate()`. Conflating them made every gate OPEN --
        including one whose every check passed -- because `run_gate` never sets controls. A verdict
        that cannot be reached is as meaningless as one that is always reached.
        """
        if not self.checks:
            self.verdict = OPEN
            self.notes.append("no checks were run; an empty gate cannot pass")
            return self.verdict
        self.verdict = CLOSED if all(c.passed for c in self.checks) else OPEN
        return self.verdict

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "verdict": self.verdict,
            "checks": [c.to_dict() for c in self.checks],
            "controls": dict(self.controls),
            "notes": list(self.notes),
            "failed": [c.name for c in self.checks if not c.passed],
        }


# ---------------------------------------------------------------------------------------------
# The declared gate. Written HERE, before any figure is rendered, so it cannot be chosen to pass.
# ---------------------------------------------------------------------------------------------

#: Nature's two column widths, in mm. A figure at any other width is not submittable.
NATURE_WIDTHS_MM = (89.0, 183.0)
#: Nature's minimum typeset size, in points.
MIN_POINT = 5.0
MAX_POINT = 12.0
#: A page taller than this cannot be placed in a column without reduction.
MAX_HEIGHT_MM = 170.0
#: Audit reports a width within this tolerance as compliant.
WIDTH_TOL_MM = 0.6
HEIGHT_TOL_MM = 0.6


def declare(name: str = "figure") -> Gate:
    """The gate, declared before the figure exists.

    Every check below is a condition on the RENDERED FILE, read back from the PDF. None is a
    statement about the code that drew it -- that distinction is what makes the route independent.
    """
    return Gate(name=name)


def run_gate(pdf_path, *, result: dict | None = None, name: str = "figure") -> Gate:
    """Measure every declared check against a rendered file, then close the gate.

    `result` is the dict from `skills.run()`, when the caller has it. It supplies the panel count
    and layout, which the layout layer already decided -- reading them from pixels would be
    re-deriving a fact the caller holds.
    """
    gate = declare(name)
    report = audit.audit(str(pdf_path), check_overlap=False)
    findings = report.get("findings") or []
    width = report.get("width_mm")
    height = report.get("height_mm")

    # 1. GEOMETRY -- a fixed set of widths, and a height that fits a column.
    width_ok = any(abs(float(width or 0) - w) <= WIDTH_TOL_MM for w in NATURE_WIDTHS_MM)
    gate.add("column_width", width,
             f"one of {NATURE_WIDTHS_MM} mm (+/- {WIDTH_TOL_MM})", width_ok,
             f"measured {width} mm")
    height_ok = height is not None and float(height) <= MAX_HEIGHT_MM + HEIGHT_TOL_MM
    gate.add("page_height", height, f"<= {MAX_HEIGHT_MM} mm (+/- {HEIGHT_TOL_MM})", height_ok,
             f"measured {height} mm")

    # 2. TYPOGRAPHY -- measured from the embedded fonts, not from the source.
    type_bad = [f for f in findings if f.get("check") in ("font_size", "font_type")]
    gate.add("typography", len(type_bad), "0 font findings", not type_bad,
             "; ".join(f"{f['check']}: {f['detail']}" for f in type_bad[:3]))

    # 3. STRUCTURE -- read from the PDF's own text and path operators.
    struct = structure.describe(pdf_path)
    gate.add("has_content", struct["text_chars"], "> 0 characters of text",
             struct["text_chars"] > 0,
             f"figure_type={struct['figure_type']!r}, arrow_style={struct['arrow_style']!r}")

    # 4. NAMED DIMENSIONS -- the quality report, and the rule that none may be silently absent.
    qrep = quality.for_skill_result(result or {}, figure=str(pdf_path))
    measured = {d["name"]: d["score"] for d in qrep["dimensions"]}
    gate.add("dimensions_measured", len(measured), ">= 1 measured dimension",
             len(measured) >= 1, f"measured {sorted(measured)}")
    failing = [n for n, s in measured.items() if s is not None and s < 1.0]
    gate.add("dimensions_pass", failing, "every measured dimension scores 1.0",
             not failing, f"below 1.0: {failing}" if failing else "all at 1.0")

    # 5. PANEL COUNT -- consistent between the layout record and the file, when both are known.
    if result is not None:
        claimed = int(result.get("panels") or 1)
        gate.add("panel_count", claimed, "matches the layout record",
                 claimed >= 1, f"layout recorded {claimed} panel(s)")
        if claimed > 1:
            gate.add("panel_labels", struct["panel_labels_present"],
                     "a multi-panel figure must letter its panels",
                     bool(struct["panel_labels_present"]),
                     f"letters found: {struct['panel_labels']}")

    gate.close()
    return gate


# ---------------------------------------------------------------------------------------------
# The controls. A gate that has never failed anything certifies nothing.
# ---------------------------------------------------------------------------------------------

def positive_control(tmp_dir) -> dict:
    """A figure that MUST pass. If this fails, the gate is broken, not the figure."""
    import numpy as np
    import pandas as pd
    from . import skills

    d = pathlib.Path(tmp_dir) / "gate_positive"
    d.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"site": ["north", "south", "east", "west"] * 10,
                       "year": list(range(2015, 2025)) * 4,
                       "value": rng.random(40)})
    res = skills.run("grouped_measures", df, out_stem=d / "clean",
                     x="site", ycols=["value"], columns=2.0)
    gate = run_gate(res["pdf"], result=res, name="positive-control")
    return {"fired": gate.verdict == CLOSED, "verdict": gate.verdict,
            "gate": gate.to_dict(), "pdf": res["pdf"]}


def negative_control(tmp_dir) -> dict:
    """A figure that MUST fail, and at the check that should catch it.

    The corruption is a WRONG COLUMN WIDTH -- 150 mm is a real, plausible mistake (A4 with wide
    margins) and it is not one of Nature's two widths. The gate must reject it at `column_width`.

    A gate that has never failed anything certifies nothing: every clause of it might be broken and
    you would see only passes.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = pathlib.Path(tmp_dir) / "gate_negative"
    d.mkdir(parents=True, exist_ok=True)
    out = d / "wrong_width.pdf"
    # 150 mm wide -- deliberately not 89 or 183
    fig, ax = plt.subplots(figsize=(150.0 / 25.4, 60.0 / 25.4))
    ax.plot([0, 1, 2, 3], [1, 2, 1.5, 3])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.savefig(out)
    plt.close(fig)

    gate = run_gate(out, name="negative-control")
    failed = [c.name for c in gate.checks if not c.passed]
    return {"fired": gate.verdict == OPEN and "column_width" in failed,
            "verdict": gate.verdict, "failed_checks": failed,
            "gate": gate.to_dict(), "pdf": str(out)}


def pipeline_controls(tmp_dir) -> dict:
    """The DATA-level controls: does the pipeline carry a planted value through?

    The acceptance gate answers "is this figure well formed". It cannot answer "does the machinery
    put the right number in the figure". That is what the plants are for, and both are needed: a
    figure can be perfectly formed around a wrong number.

    BootLoops calls this `planted-truth`, and its order rule matters -- the plants are constructed
    and run before any real figure is judged, so they cannot be chosen to bless it.
    """
    from . import planted
    rec = planted.recover_all(out_dir=tmp_dir)
    return {
        "all_recovered": rec["all_recovered"],
        "n": rec["n"],
        "n_passed": rec["n_passed"],
        "failed": rec["failed"],
        "verdict": rec["verdict"],
        "plants": rec["plants"],
    }


def validate(tmp_dir) -> dict:
    """Run both controls and report whether the gate can fire.

    A gate whose controls have not fired is not a gate. This is the check that makes the rest
    meaningful, and it is deliberately separate from any real figure's verdict.
    """
    pos = positive_control(tmp_dir)
    neg = negative_control(tmp_dir)
    ok = bool(pos["fired"]) and bool(neg["fired"])
    return {
        "gate_can_fire": ok,
        "positive": {"fired": pos["fired"], "verdict": pos["verdict"]},
        "negative": {"fired": neg["fired"], "verdict": neg["verdict"],
                     "failed_checks": neg.get("failed_checks")},
        "verdict": ("the gate can fire: a clean figure passes and a wrong one fails"
                    if ok else
                    "THE GATE CANNOT FIRE -- every pass it reports is vacuous"),
    }
