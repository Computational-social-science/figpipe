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


#: Findings whose fix is a DECLARED CODE EDIT, with the patch that would address it.
#:
#: Each entry is (path, old, new, rationale). The old text must occur exactly once -- `patchprobe`
#: refuses anything ambiguous, so a wrong entry fails loudly rather than editing the wrong place.
#:
#: These are the fixes this project actually made by hand, written down as data so a probe can
#: measure them. That is the difference between "the loop found it" and "the loop could not express
#: it", and it is the whole point of this module.
#: THE CONVENTION, stated once: `old` is the DEFECT text, `new` is the FIXED text.
#:
#: A tree holding the fix reports state `revert` -- applying the patch puts the defect back -- which
#: is what a contribution measurement needs. Getting this backwards made two fixes report `fix`
#: while the tree plainly held the repaired value, and made the run install the defect and then
#: measure the fix.
CODE_PATCHES = {
    "polar_label_overflow": (
        "figpipe/drawlib.py",
        "            ax.set_xticklabels(labels, fontsize=6)",
        "            ax.set_xticklabels([_wrap_spoke(v) for v in labels], fontsize=6)",
        "long polar spoke labels overflow the page edge and are cut by the PDF boundary",
    ),
    # THE MATRIX LABEL-WIDTH BUDGET. Before it, a matrix axis carried whatever labels the frame had,
    # and twelve 30-character names overlapped on a 90 mm panel.
    "matrix_label_width": (
        "figpipe/drawlib.py",
        "    MAX_LABEL_CHARS = 10**9",
        "    MAX_LABEL_CHARS = 18",
        "a matrix axis with long column names draws them all and they overlap",
    ),
    # THE POLAR WRAP WIDTH. 10 is the value that fits the panel; reverting to a huge width puts the
    # labels back outside the page.
    "polar_wrap_width": (
        "figpipe/drawlib.py",
        "POLAR_LABEL_WRAP = 10**6",
        "POLAR_LABEL_WRAP = 10",
        "without a wrap width the polar labels run past the page edge",
    ),
    # THE MATRIX ROW BUDGET. A 40-row matrix on a 90 mm panel is 2.25 mm per row and cannot be
    # labelled; the budget refuses past that rather than drawing an unreadable figure.
    "matrix_row_budget": (
        "figpipe/skills.py",
        "MAX_MATRIX_ROWS = 10**6",
        "MAX_MATRIX_ROWS = 40",
        "without a row budget a long table is drawn as an unreadable matrix",
    ),
    # THE COLOUR-BAR LABEL ROOM. The bar and its pad were reserved; the tick labels were not, so a
    # colour scale printed NO numbers because its labels fell off the page.
    "colorbar_label_room": (
        "figpipe/composite.py",
        "CBAR_LABEL_MM = 0.0",
        "CBAR_LABEL_MM = 4.2",
        "without room for the labels a colour bar prints no scale at all",
    ),
}


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


def patch_state(root, patch: dict) -> dict:
    """Is this patch a FIX (the defect is present) or a REVERT (the fix is already in)?

    THE TWO DIRECTIONS ARE BOTH USEFUL and must not be confused:
      fix     the defect text is present, so applying the patch repairs it
      revert  the fixed text is present, so applying the patch reintroduces the defect -- which is
              how a probe demonstrates that a fix was load-bearing
      stale   neither is present, so the catalogue entry no longer describes this tree
    """
    import pathlib as _pathlib

    from . import patchprobe

    forward = patchprobe.Patch(id=patch["id"], path=patch["path"],
                               old=patch["old"], new=patch["new"],
                               rationale=patch["rationale"])
    backward = patchprobe.Patch(id=patch["id"] + "-revert", path=patch["path"],
                                old=patch["new"], new=patch["old"],
                                rationale="reintroduce the defect to measure the fix")
    ok_forward, _ = patchprobe.patch_applies(_pathlib.Path(root), forward)
    ok_backward, _ = patchprobe.patch_applies(_pathlib.Path(root), backward)
    # `old` IS THE DEFECT TEXT and `new` is the FIXED text, so the mapping is direct:
    #   forward applies  -> the tree holds the DEFECT -> this patch is a FIX
    #   backward applies -> the tree holds the FIX    -> this patch is a REVERT
    if ok_forward and not ok_backward:
        return {"state": "fix", "patch": forward.to_dict(),
                "why": "the defect is present; applying this repairs it"}
    if ok_backward and not ok_forward:
        return {"state": "revert", "patch": backward.to_dict(),
                "why": "the fix is present; applying this reintroduces the defect"}
    return {"state": "stale", "patch": forward.to_dict(),
            "why": "neither the defect nor the fix text is present; the catalogue entry no longer "
                   "describes this tree"}


def patches_for(findings: list[dict]) -> dict:
    """Declared code patches that would address these findings, plus what has none.

    A finding's `check` names the defect class; `CODE_PATCHES` maps the classes this project has
    already learned to fix to the edit that fixes them. A class with no patch is reported -- the loop
    cannot express it, and saying so is the honest answer.
    """
    out = []
    missing = []
    seen: set[str] = set()
    for finding in findings:
        check = str(finding.get("check") or "")
        if not check:
            continue
        key = next((k for k in CODE_PATCHES if k in check), None)
        if key is None:
            missing.append({"check": check,
                            "why": "no declared code patch exists for this defect class"})
            continue
        if key in seen:
            continue
        seen.add(key)
        path, old, new, rationale = CODE_PATCHES[key]
        out.append({"id": key, "path": path, "old": old, "new": new, "rationale": rationale})
    return {"patches": out, "n": len(out), "missing": missing, "n_missing": len(missing)}


def describe(result: dict) -> str:
    """One line for a run record."""
    return (f"{result['n']} proposal(s) from findings, "
            f"{result['n_unproposable']} unproposable")
