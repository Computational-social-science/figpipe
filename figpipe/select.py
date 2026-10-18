"""Choose between candidate figures using the reference alone -- never the target.

WHY THIS MODULE EXISTS
    The benchmark showed that style transfer helps most tasks and HURTS a minority: on 78 measured
    tasks it improved 49, worsened 15 and tied 6. A pipeline that always transfers therefore
    cannot beat one that transfers only when transfer helps. The question is how to decide.

    The decision must be legitimate: at inference time there is no "correct answer" to compare
    against, only the reference the caller supplied. So the rule is simple and honest --
    render both candidates, measure each against the REFERENCE, and keep the closer one. That is
    not cheating; the reference is the input.

    This module is deliberately separate from the benchmark harness. It is a general capability
    ("given several candidates and a target style, pick one"), the harness is one consumer, and a
    second consumer (an author with two drafts) must not have to import the benchmark.

WHAT IT IS NOT
    * Not a learned ranker: the weights are the ones `styleprofile.compare` already uses, and the
      decision is a single comparison of two numbers.
    * Not a claim that the closer figure is the better figure. It is the figure closer to the
      style the caller asked for. Semantic correctness stays with the audit and the author.
"""
from __future__ import annotations

import pathlib

from figpipe import styleprofile


def distance_to(reference: styleprofile.StyleProfile, pdf_or_png) -> dict:
    """Style distance from one rendered candidate to the reference."""
    path = pathlib.Path(pdf_or_png)
    if not path.is_file():
        raise FileNotFoundError(f"candidate not found: {path}")
    if path.suffix.lower() == ".pdf":
        cand = styleprofile.StyleProfile.from_pdf(path)
    else:
        cand = styleprofile.StyleProfile.from_image(path)
    return styleprofile.compare(reference, cand)


def select(reference: styleprofile.StyleProfile, candidates: dict, *,
           tie_break: str = "first") -> dict:
    """Pick the candidate closest to the reference; report every distance and the margin.

    `candidates` maps a name to a rendered path (PDF or PNG). The return value names the winner,
    every measured distance, the margin over the runner-up, and the rule that produced it, so the
    decision can be re-derived from the artefact.
    """
    if not candidates:
        raise ValueError("select() needs at least one candidate")
    measured = {}
    for name, path in candidates.items():
        measured[name] = distance_to(reference, path)
    order = sorted(measured.items(), key=lambda kv: kv[1]["distance"])
    winner, best = order[0]
    runner_up = order[1][1]["distance"] if len(order) > 1 else None
    margin = round(runner_up - best["distance"], 3) if runner_up is not None else None
    return {
        "choice": winner,
        "distance": best["distance"],
        "details": best["details"],
        "distances": {name: d["distance"] for name, d in measured.items()},
        "margin": margin,
        "rule": ("keep the candidate whose rendered page is closest to the reference profile; "
                 "the reference is an input, not ground truth about the data"),
        "tie_break": tie_break if margin == 0 else None,
    }


def should_transfer(reference: styleprofile.StyleProfile, plain_pdf, styled_pdf, *,
                    min_margin: float = 0.005) -> dict:
    """Decide whether to ship the styled figure or the plain one.

    `min_margin` prevents flip-flopping on differences smaller than the measurement's own
    resolution: below it, the plain figure is kept, because a change that cannot be measured is
    not an improvement.
    """
    picked = select(reference, {"plain": plain_pdf, "styled": styled_pdf})
    margin = picked["margin"] or 0.0
    transfer = picked["choice"] == "styled" and margin >= min_margin
    return {"transfer": transfer, "choice": picked["choice"],
            "margin": margin, "min_margin": min_margin,
            "distance": picked["distance"], "distances": picked["distances"],
            "rule": f"transfer only when the styled page is at least {min_margin} closer"}
