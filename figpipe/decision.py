"""Boundary to the shared StartLux-Decision 4B operator (one deployment, many projects).

WHY THIS IS A THIN BRIDGE AND NOT AN IMPORT
    The owner's rule is explicit: the decision model is 共用，而非私用. It is deployed once,
    outside figpipe, as its own project (`E:\\2026-AI4S\\decision-service`) and every project
    talks to it over HTTP through that project's client. figpipe therefore does not vendor the
    model, the llama.cpp launch line, or a copy of the client: it imports the client (from the
    sibling checkout, or `DECISION_SERVICE_PATH`) and wraps it with the one policy this project
    needs.

THE POLICY
    1. NO SILENT FALLBACK. If the service is down, callers get `DecisionUnavailable`; if the
       model says no listed option fits (none_probability >= its measured 0.2 threshold), callers
       get `DecisionRejected`. They may choose a heuristic, but they must do so explicitly.
    2. A CHOICE MUST BE ONE OF THE OFFERED OPTIONS. Anything else is `DecisionUnavailable`, not
       a parse of prose.
    3. THE MODEL NEVER SCORES. It may propose a skill or a column mapping; the deterministic
       skills contract, audit and style distance still decide whether the figure passes.

USED BY
    `scripts/bench_plottwin.py` as the fallback when the rule-based benchmark mapper cannot read
    a task. That is the honest use: the model resolves ambiguity, the deterministic layer keeps
    the veto.
"""
from __future__ import annotations

import pathlib
import sys

DEFAULT_PATH = r"E:\2026-AI4S\decision-service"

_DEFAULT_NONE_THRESHOLD = 0.2


class DecisionUnavailable(RuntimeError):
    """The shared service is not reachable, or returned something unusable."""


class DecisionRejected(RuntimeError):
    """The model reports that none of the offered options is likely correct."""


def _client():
    """Import the shared client from the decision-service checkout (no vendoring)."""
    try:
        import decision_service as ds
        return ds
    except ImportError:
        pass
    path = pathlib.Path(__import__("os").environ.get("DECISION_SERVICE_PATH", DEFAULT_PATH))
    if path.is_dir() and str(path) not in sys.path:
        sys.path.insert(0, str(path))
    try:
        import decision_service as ds
        return ds
    except ImportError as exc:          # pragma: no cover - depends on the host
        raise DecisionUnavailable(
            f"decision_service client not importable (looked in {path}). "
            "Start the shared service with decision-service/scripts/serve.ps1 or set "
            "DECISION_SERVICE_PATH.") from exc


def health(timeout: float = 5.0) -> dict:
    """Structured service status; empty dict only if the client itself is missing."""
    try:
        return _client().health(timeout=timeout)
    except DecisionUnavailable as exc:
        return {"up": False, "detail": str(exc)}


def choose(instructions: str, options: dict, evidence, *,
           none_threshold: float | None = None, **controls) -> dict:
    """One calibrated choice over named options.

    Returns `{"choice", "confidence", "none_probability", "probabilities", "model"}`.
    Raises `DecisionRejected` when the model's own none-probability clears the measured
    threshold, and `DecisionUnavailable` when the answer is not one of the options.
    """
    if not options:
        raise ValueError("choose() needs at least one option")
    ds = _client()
    result = ds.choose(instructions, options, evidence, **controls)
    threshold = (_DEFAULT_NONE_THRESHOLD if none_threshold is None
                 else float(none_threshold))
    none_p = result.none_probability
    if none_p is not None and none_p >= threshold:
        raise DecisionRejected(
            f"none_probability={none_p:.2f} >= {threshold:.2f}: no listed option is likely "
            f"correct (options={sorted(options)})")
    choice = result.get("choice")
    if choice not in options:
        raise DecisionUnavailable(
            f"model returned choice={choice!r}, which is not one of {sorted(options)}")
    return {"choice": choice, "confidence": result.get("confidence"),
            "none_probability": none_p, "probabilities": result.get("probabilities"),
            "model": result.get("_model")}


#: The skills the benchmark mapper may offer the model; descriptions are the criteria text.
SKILL_OPTIONS = {
    "trend_with_uncertainty": "an ordered x (time/year) and a measured y, optionally with an interval",
    "histogram": "the distribution of one measured column",
    "faceted_distribution": "the distribution of one measured column repeated over a facet column",
    "distribution_comparison": "box plots comparing a measured column across categories",
    "scatter_relationship": "the relationship between two continuous measures",
    "grouped_measures": "parallel measured columns compared across categories",
    "ranked_composition": "categories ranked by one measured share/value",
    "matrix_plate": "a numeric matrix, or a long table pivoted into one",
}


def choose_skill(chart_type: str, columns: list[str], *,
                 evidence: dict | None = None, **controls) -> dict:
    """Propose one skill for a benchmark task; the caller still validates by rendering it.

    The model sees the chart-type label and the target data's column names, not the figure. It
    chooses among OUR skills -- the output is a figpipe contract name, not free text.
    """
    state = {"chart_type": chart_type, "columns": list(columns)}
    if evidence:
        state.update(evidence)
    return choose(
        f"The benchmark task is chart type {chart_type!r} with these data columns: "
        f"{list(columns)}. Which figure recipe should be used to draw it? Choose exactly one.",
        SKILL_OPTIONS, state, **controls)
