"""Every check must say what it looked at, so a zero can be read.

WHY THIS EXISTS
    Rounds 82-86 established that a count of zero is ambiguous: it can mean "the check looked and
    found nothing" or "there was nothing for the check to look at". The project learned this the hard
    way twice --

        legend_occlusions: 0 over 139 figures, of which NONE contains a legend   (VACUOUS)
        text_collision:    0 over 139 figures carrying 101-245 glyphs each       (MEANINGFUL)

    -- and the only reason the second could be told apart from the first is that the glyph count was
    measured separately, by hand, in a test.

    A hand measurement is not a mechanism. This module makes the denominator part of every check's
    return value, so the distinction is available to the report without anyone remembering to ask.

WHAT A DENOMINATOR IS, AND IS NOT
    It is the number of OBJECTS THE CHECK EXAMINED, in the check's own units:

        glyph collisions    -> glyphs compared
        legend occlusion    -> legend frames found
        font size           -> text spans found
        text overlap        -> text spans compared

    It is NOT the number of tasks, files or pages. "0 findings over 139 tasks" says nothing about
    whether any task contained an object the check can see -- that is exactly the aggregate defect
    this project has recorded more times than any other.

WHAT THIS DOES NOT DO
    It does not change any check's verdict. It records what was examined beside what was found. A
    check whose denominator is 0 is reported as NOT EXERCISED, and that is a different state from
    PASS.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass

#: The states a check can be in. `not_exercised` exists because a zero without objects is not a pass.
PASS = "pass"
FINDINGS = "findings"
NOT_EXERCISED = "not_exercised"


@dataclass(frozen=True)
class Examined:
    """What one check looked at, and what it found.

    `denominator` is in the check's OWN units -- glyphs for a glyph check, frames for a legend check.
    `unit` names them so a report cannot print a bare number.
    """

    check: str
    denominator: int
    unit: str
    n_findings: int

    @property
    def state(self) -> str:
        """THE DISTINCTION THE PROJECT KEPT GETTING WRONG.

        A check that found nothing because it examined nothing is NOT a pass. Reporting it as one is
        how a vacuous zero gets read as a clean result.
        """
        if self.denominator == 0:
            return NOT_EXERCISED
        return FINDINGS if self.n_findings else PASS

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["state"] = self.state
        return d

    def describe(self) -> str:
        return (f"{self.check}: {self.n_findings} finding(s) over {self.denominator} {self.unit} "
                f"-> {self.state}")


def summarise(examined: list[Examined]) -> dict:
    """Roll several checks up, keeping `not_exercised` separate from `pass`.

    A summary that counts the two together is the aggregate defect in its usual form: "0 problems"
    over a set that includes checks which never ran.
    """
    states = [e.state for e in examined]
    return {
        "checks": [e.to_dict() for e in examined],
        "n_checks": len(examined),
        "n_pass": states.count(PASS),
        "n_findings": states.count(FINDINGS),
        "n_not_exercised": states.count(NOT_EXERCISED),
        "verdict": (
            f"{states.count(NOT_EXERCISED)} of {len(examined)} checks examined NOTHING, so their "
            f"zero is not a pass" if NOT_EXERCISED in states else
            f"all {len(examined)} checks examined something; {states.count(PASS)} passed"),
    }
