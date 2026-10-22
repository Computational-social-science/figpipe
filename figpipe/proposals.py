"""Candidates derived from measured findings, instead of from a fixed menu.

WHY THIS EXISTS
    Measured over 152 scheduled runs: 4 knowledge changes, 222 ties, 149 runs that selected
    NOTHING. The loop was not failing to find improvements -- it was structurally unable to
    represent them. Its whole search space was five hard-coded budget integers:

        split-max-bars-24 / -13            layout.split_panels:max_bars
        matrix-max-rows-41 / -42 / -60     encode.matrix:max_rows

    and `mutation_step()` never read the pool report, so it never saw a finding.

    Every real defect this project fixed -- 9 text collisions, the polar label overflow, the colour
    bar falling off the page, the pivot choosing a row index as its measurement -- was found by
    reading a report and was NOT EXPRESSIBLE as one of those five integers. The loop's discovery
    channel was a five-item menu.

WHAT A PROPOSAL IS
    A finding names a defect and the operator that produced it. A proposal is the PARAMETER EDIT
    that would plausibly fix that class of defect, derived mechanically:

        finding check             -> operator              -> parameter
        overlap / text_collision     layout.split_panels     max_rows, max_panels
        font_size                    layout.plate            columns
        height / width               layout.plate            columns
        density                      layout.split_panels     max_rows

    A finding with no scalar fix is REPORTED as unproposable rather than silently dropped, because
    "the loop cannot express this" is the diagnosis, not a gap to hide.

WHAT THIS DOES NOT DO
    It does not invent parameter values. A proposal names a parameter the operator DECLARES and a
    direction the finding implies; the probe harness then measures whether the move helped. A
    proposal that cannot be probed is not made.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass

#: Which operator parameter a finding's shape points at.
#:
#: Keyed by the finding's `check`. A finding whose check is not here is UNPROPOSABLE and is
#: reported as such -- never dropped silently.
FINDING_TO_PARAMETER = {
    "overlap": ("layout.split_panels", ("max_rows", "max_panels")),
    "text_collision": ("layout.split_panels", ("max_rows", "max_panels")),
    "font_size": ("layout.plate", ("columns",)),
    "height": ("layout.plate", ("columns",)),
    "width": ("layout.plate", ("columns",)),
    "density": ("layout.split_panels", ("max_rows",)),
}

#: Findings whose fix is a CODE EDIT, not a scalar. Reported, never dropped.
CODE_ONLY_CHECKS = ("semantics.", "mesh_scale", "axis_range", "font_type")


@dataclass
class Proposal:
    """One candidate derived from a measured finding."""

    finding: str
    task_id: str
    operator: str
    parameter: str
    direction: str
    rationale: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def proposals_from_report(report: dict) -> dict:
    """Every candidate the pool's own findings imply, plus what could not be proposed.

    Returns both lists. The unproposable ones are the interesting half: they are the defects this
    workflow cannot act on, and a report that omits them hides the structural limit.
    """
    tasks = report.get("tasks") or []
    out: list[Proposal] = []
    unproposable: list[dict] = []
    seen: set[tuple] = set()

    for task in tasks:
        for finding in (task.get("findings") or []):
            check = str(finding.get("check") or "")
            if not check:
                continue
            if any(check.startswith(p) for p in CODE_ONLY_CHECKS):
                # A CODE EDIT, not a scalar. This is the honest answer: the loop cannot express it.
                unproposable.append({
                    "task": task.get("id"), "check": check,
                    "why": "the fix is a drawer change, not a parameter value; the loop can only "
                           "propose scalars, so this finding has no candidate",
                })
                continue
            target = FINDING_TO_PARAMETER.get(check)
            if target is None:
                unproposable.append({
                    "task": task.get("id"), "check": check,
                    "why": "no parameter is mapped to this finding shape",
                })
                continue
            operator, params = target
            for parameter in params:
                key = (operator, parameter)
                if key in seen:
                    continue
                seen.add(key)
                out.append(Proposal(
                    finding=check, task_id=str(task.get("id")), operator=operator,
                    parameter=parameter, direction="down",
                    rationale=(f"{check} on {task.get('id')}: a {parameter} budget that admits "
                               f"less is the scalar move this finding implies"),
                ))
    return {"proposals": [p.to_dict() for p in out],
            "n": len(out), "unproposable": unproposable,
            "n_unproposable": len(unproposable),
            "verdict": (f"{len(out)} candidate(s) derived from the pool's own findings"
                        if out else
                        "the pool reports no finding that a scalar edit could address")}


def describe(result: dict) -> str:
    """One line for a run record."""
    return (f"{result['n']} proposal(s) from findings, "
            f"{result['n_unproposable']} unproposable")
