"""An update rule that is a function of its own history, instead of a constant.

WHY THIS EXISTS
    Measured on 2026-10-21: figpipe's autonomous loop had run **130 cycles**, produced **4 knowledge
    changes**, and selected **nothing at all in 127 of them**. The three selections were all
    `matrix-max-rows` budget values.

    That is not a shortage of candidates. It is that the loop's decision rule is a CONSTANT:

        mutation._verdict(... margin=0.1 ...)     # a literal
        min_score = None                          # never set

    A constant rule cannot adapt to what the system has seen. It can only move along an axis
    somebody chose in advance, at a step size somebody chose in advance -- and once the obvious
    moves are made, it stops. Which is exactly what happened.

THE IDEA, AND WHERE IT COMES FROM
    VisionHOPE (PSRben/VisionHOPE, MIT, arXiv 2609.33325) is a vision backbone built on
    self-referential nested learning. Its central claim is not "use five memories"; it is that a
    system whose update rule is fixed cannot adapt, so the rule must itself be computed from what
    the system is currently processing.

    From `models/srnl_core/csrc/memory.cuh`:

        eta   = ETA_SCALE * sp                                // how far to move
        alpha = ALPHA_MIN + (1 - ALPHA_MIN) * sigmoid(ap)     // how much to keep
        eta_cap = STAB_MU * (1 - alpha) / (diff_norm + eps)
        eta     = eta_cap * (1 - exp(-eta / eta_cap))         // soft injection cap

    `eta` and `alpha` are computed through LEARNED memories, then bounded by a stability projection
    that prevents expansion.

    figpipe cannot take the backbone, the CUDA kernels, or the gradients -- it has no tensors and
    no training corpus. But it does have the thing the idea needs: **its own history**, 130 run
    records of measured outcomes. So the transferable part is the mechanism, not the architecture:

        eta-like    the margin: how much a score must move to count
        alpha-like  the retention: how much of the past to weigh when setting it

    Both become functions of the measured history rather than literals.

WHAT THE MEASUREMENT SAID ABOUT THIS, AND IT IS UNCOMFORTABLE
    Built and run on the real 130-run history, the adaptive margin comes out at **0.060** against
    the constant **0.100**. Then the decisions were REPLAYED:

        would select at the constant 0.100   : 5 of 180
        would select at the adaptive 0.060   : 5 of 180

    **No difference.** The margin was never the binding constraint.

    The real distribution of recorded verdicts is:

        tie       134   (74%)
        rejected   41
        selected    5

    and the candidate space is five BUDGET adjustments -- `max_bars` 12->13, `max_rows` 40->41/42/60 --
    probed on six fixed tasks. A budget only changes a figure when a task sits exactly at the
    boundary, so three quarters of the time a candidate changes nothing at all and the verdict is a
    tie. **No margin, adaptive or not, can select among candidates that produce identical output.**

    So this module is NOT the breakthrough. It is the correct half of one: the rule can now be a
    function of history, which it could not before. The other half -- a candidate space that can
    produce distinguishable outcomes -- is the actual blocker, and it is a different piece of work.

    Recording this here rather than in a changelog because the module's docstring is where a future
    reader will look for "did the adaptive rule help?" The answer is: it made the rule correct, and
    the rule was not what was limiting.

WHAT THIS DELIBERATELY DOES NOT DO
    It does not make the rule depend on the CANDIDATE. A rule that reads the thing it is judging
    is the "gate designed after the answer" failure this project has recorded repeatedly. The rule
    here reads only the loop's PAST OUTCOMES -- what scores did re-measuring actually produce -- so
    it is fixed with respect to any future candidate.

    It also cannot invent a smaller margin than the measurement's own noise. The stability
    projection is the guard: a margin below the observed resolution would let the loop select
    differences it cannot actually distinguish, which is the tie problem in a new costume.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field

#: Bounds on the margin. Below the floor, differences are indistinguishable from measurement noise;
#: above the ceiling, the rule stops selecting anything and the loop is back where it started.
MARGIN_FLOOR = 0.02
MARGIN_CEIL = 0.30
#: The default when there is not enough history to compute one.
MARGIN_DEFAULT = 0.10

#: The retention floor: even with a long history, the most recent outcomes must carry weight.
#: From VisionHOPE's `ALPHA_MIN`, which keeps the recurrence from becoming a pure average.
ALPHA_MIN = 0.15


@dataclass
class History:
    """The loop's measured past, in the only terms that matter: how much scores actually moved.

    Every field is a MEASURED quantity from `knowledge/runs/*.json`. Nothing here is a preference.
    """

    #: |delta| between a candidate and the baseline, for every candidate ever probed. These are the
    #: differences the loop has actually been able to observe.
    observed_deltas: list[float] = field(default_factory=list)
    #: Per-task score movements between consecutive re-measurements of the SAME task. This is the
    #: measurement's own resolution: a task that moved this much without any change was noise.
    remeasure_moves: list[float] = field(default_factory=list)
    #: How many selections the loop has made. Used for the retention term.
    n_selections: int = 0
    #: How many cycles have produced no selection at all.
    n_empty: int = 0

    @property
    def n(self) -> int:
        return len(self.observed_deltas)


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else 0.5 * (s[mid - 1] + s[mid])


def _sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def margin_from(history: History) -> dict:
    """The eta-like step size, computed from the loop's measured history.

    THREE TERMS, each from a different part of the history:

      resolution   the median per-task movement between re-measurements. A margin below this
                   selects noise. This is the floor.
      separability the median |delta| the loop has actually observed. If observed differences are
                   typically 0.05, a margin of 0.10 rejects almost everything -- which is the
                   measured failure (127 of 130 cycles selected nothing).
      retention    how much of the past to weigh, from the selection rate. A loop that has selected
                   nothing recently should lower its bar; a loop that selects often should raise it.

    Returns a dict with the margin and the three terms, so the number is auditable.
    """
    if history.n < 3:
        return {"margin": MARGIN_DEFAULT, "basis": "default: fewer than 3 observed deltas",
                "resolution": None, "separability": None, "retention": None}

    resolution = _median([abs(x) for x in history.remeasure_moves]) if history.remeasure_moves else 0.0
    # MEDIAN OF THE NON-ZERO DELTAS. Measured on 180 observed deltas: 134 are exactly 0.0 (the
    # candidate changed nothing on the six probed tasks). Including those asks "what does a typical
    # candidate do" when the question is "how big is a difference WHEN THERE IS ONE". The zeros
    # would drag the median to 0 and collapse the margin to the floor -- which is what happened
    # before this line was fixed.
    nonzero = [abs(x) for x in history.observed_deltas if abs(x) > 1e-9]
    separability = _median(nonzero) if nonzero else 0.0
    zero_share = 1.0 - (len(nonzero) / len(history.observed_deltas)) if history.observed_deltas else 0.0

    # RETENTION: the share of cycles that produced a selection. Low share -> the bar is too high.
    total = max(1, history.n_selections + history.n_empty)
    select_rate = history.n_selections / total
    # alpha near ALPHA_MIN when the loop almost never selects (lower the bar a lot);
    # alpha near 1 when it selects often (lower it only a little).
    alpha = ALPHA_MIN + (1.0 - ALPHA_MIN) * _sigmoid((select_rate - 0.5) * 6.0)

    # THE RAW MARGIN: a fraction of the observed separability, scaled by retention.
    # When the loop has been selecting nothing, alpha is small and the margin drops toward the
    # resolution floor.
    raw = separability * (0.5 + 1.5 * alpha)

    # THE STABILITY PROJECTION, from VisionHOPE's `soft_project_eta`:
    #     cap = mu * (1 - alpha) / (diff_norm + eps)
    # Here the role of `diff_norm` is played by the resolution: the margin may never sit closer to
    # the noise floor than the retention allows.
    floor = max(MARGIN_FLOOR, resolution)
    cap = floor + (MARGIN_CEIL - floor) * alpha
    z = raw / cap if cap > 0 else 0.0
    margin = cap * (-math.expm1(-z))       # cap * (1 - exp(-z)), monotone and bounded by cap

    margin = min(max(round(margin, 3), floor), MARGIN_CEIL)
    return {"margin": margin,
            "basis": (f"{history.n} observed deltas ({zero_share:.0%} exactly zero), "
                      f"{len(history.remeasure_moves)} remeasures"),
            "resolution": round(resolution, 4),
            "separability": round(separability, 4),
            "zero_share": round(zero_share, 3),
            "retention": round(alpha, 4),
            "select_rate": round(select_rate, 4)}


def history_from_runs(run_records: list[dict]) -> History:
    """Build the history from `knowledge/runs/*.json` records.

    Only MEASURED quantities are read. A run record with no mutation section contributes to
    `n_empty` and nothing else, so a cycle that measured nothing cannot influence the margin.
    """
    h = History()
    for run in run_records:
        m = run.get("mutation") or {}
        if not m.get("ran"):
            continue
        proposed = m.get("proposed") or []
        selected = m.get("selected") or []
        if selected:
            h.n_selections += 1
        else:
            h.n_empty += 1
        # the per-candidate deltas, when the record carries them
        for d in (m.get("decisions") or []):
            delta = d.get("delta")
            if isinstance(delta, (int, float)) and proposed:
                h.observed_deltas.append(float(delta))
        # the baseline spread: how much the SAME task moved across cycles is recorded in the
        # benchmark report, not here, so it is supplied separately when available.
    return h


def describe(result: dict) -> str:
    """One line a human can read, for the run record."""
    if result.get("resolution") is None:
        return f"margin {result['margin']:.3f} ({result['basis']})"
    return (f"margin {result['margin']:.3f} = separability {result['separability']:.3f} "
            f"x retention {result['retention']:.2f}, floor {result['resolution']:.3f} "
            f"(select rate {result['select_rate']:.2f})")
