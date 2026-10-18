"""Program-space search over template variants, with a DETERMINISTIC oracle.

WHY THIS MODULE EXISTS
    The peer systems in this space close the "does it look right" loop with an agent that writes
    code, renders, and asks a vision model to review the render (FigMirror), or with a Monte
    Carlo tree search whose reward is a learned image metric (DeTi*k*Zify, ImageSim). Both work,
    both cost a model, and neither is reproducible: two runs can pick different variants and no
    one can say why.

    figpipe already has the two ingredients for the same loop without a model:
      * a measured STYLE PROFILE of a reference and a distance to it  (figpipe/styleprofile.py)
      * hard, exact checks on the rendered page                      (figpipe/audit.py)
    What it was missing was the SEARCH: someone to try variants and keep the better ones. That is
    what this module adds, using the vendored MIT tree-search library (third_party/mcts) for the
    exploration policy -- the peer project's search engine with our oracle instead of its learned
    metric.

WHAT IS SEARCHED
    A small, discrete space of template/style choices for one panel: type size tier within
    Nature's 5-7 pt band, uncertainty-band alpha, marker size. The reward is
    `1 - style_distance`, reduced by any hard failure (wrong width, sub-5 pt text, text collision).
    Every evaluation is recorded, so the chosen variant can be justified rather than asserted.

WHAT THIS DOES NOT SEARCH YET
    Layout topology (panel arrangement, legends outside, annotation corners) is a larger space;
    the composer already refuses invalid layouts, so it should be searched next, with the same
    reward. Not claiming it is done is part of the design.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "third_party"))          # vendored, MIT (see third_party/mcts)

from mcts.montecarlo import MonteCarlo  # noqa: E402
from mcts.node import Node  # noqa: E402

from figpipe import audit, composite, grammar, layout, styleprofile  # noqa: E402

#: The searched knobs. Values are explicit and bounded: every size is inside the 5-7 pt band, so
#: the search cannot "win" by breaking the specification.
DEFAULT_SPACE = {
    "size": ["5.5", "6.0", "6.5", "7.0"],
    "alpha": ["0.15", "0.25", "0.35"],
    "marker": ["2.2", "2.6", "3.2"],
}

DEFAULT_STATE = {"size": "6.0", "alpha": "0.25", "marker": "2.6"}


def _state_str(params: dict) -> str:
    return ";".join(f"{k}={params[k]}" for k in sorted(params))


def _parse(state: str) -> dict:
    out = {}
    for part in state.split(";"):
        k, _, v = part.partition("=")
        out[k] = v
    return out


def _rc_for(params: dict) -> dict:
    size = float(params.get("size", 6.0))
    return {"font.size": size, "axes.labelsize": size,
            "axes.titlesize": min(size + 0.5, 7.0),
            "xtick.labelsize": max(5.0, size - 0.5),
            "ytick.labelsize": max(5.0, size - 0.5),
            "legend.fontsize": min(size, 6.0)}


class VariantEvaluator:
    """Render one variant, measure its distance to the reference profile, and score it.

    A cache keeps the search honest: a state is rendered once, and the cache is also the trace a
    human reads to see what was tried and what it cost.
    """

    def __init__(self, df: pd.DataFrame, reference: styleprofile.StyleProfile,
                 out_dir: pathlib.Path | None = None, budget_note: str = ""):
        self.df = df
        self.reference = reference
        self.out_dir = pathlib.Path(out_dir) if out_dir else ROOT / "templates" / "search"
        self.cache: dict[str, dict] = {}
        self.budget_note = budget_note

    def evaluate(self, state: str) -> float:
        if state in self.cache:
            return self.cache[state]["reward"]
        params = _parse(state)
        stem = self.out_dir / ("variant_" + state.replace("=", "-").replace(";", "_"))
        self.out_dir.mkdir(parents=True, exist_ok=True)
        panel = grammar.panel(
            "trend_with_uncertainty", self.df, x="Year", y="mean", fit="lm", band="fit",
            connect=True, marker_size=float(params["marker"]),
            band_alpha=float(params["alpha"]), palette=["#1f1f1f"], fit_color="#0072b2",
            xticks=[1995, 2000, 2005, 2010], legend=False)
        fig, _paths = None, None
        try:
            fig = grammar.plate([panel], columns=2.0, height_mm=110.0, rc=_rc_for(params))
            paths = layout.save(fig, stem)
            pdf = pathlib.Path(paths[0])
            profile = styleprofile.StyleProfile.from_pdf(pdf)
            result = styleprofile.compare(self.reference, profile)
            distance = result["distance"]
            a = audit.audit(pdf, expect_width_mm=183.0, check_overlap=False)
            hard = [f for f in a["findings"]
                    if f["check"] in ("font_size", "width", "height", "font_type")]
            collisions = audit.overlapping_glyphs(pdf)
            reward = (1.0 - distance)
            if hard:
                reward -= 0.5 * len(hard)
            if collisions:
                reward -= 0.5
            reward = max(0.0, min(1.0, reward))
            try:
                shown = str(pdf.relative_to(ROOT))
            except ValueError:                       # out_dir may be outside the repository
                shown = str(pdf)
            rec = {"state": state, "params": params, "distance": distance,
                   "details": result["details"], "reward": round(reward, 4),
                   "hard_findings": [f["check"] for f in hard],
                   "collisions": len(collisions), "pdf": shown}
        except Exception as e:                                   # noqa: BLE001
            rec = {"state": state, "params": params, "distance": None, "reward": 0.0,
                   "error": f"{type(e).__name__}: {e}"}
        self.cache[state] = rec
        return rec["reward"]


def search(df: pd.DataFrame, reference: styleprofile.StyleProfile,
           budget: int = 12, seed: int = 0, space: dict | None = None,
           out_dir=None) -> dict:
    """Explore template variants with MCTS and return the trace and the best variant.

    Uses the vendored MIT tree search only as an EXPLORATION POLICY: the reward is ours, exact
    and re-computable, so two runs with the same seed and budget produce the same evaluations.
    """
    space = space or DEFAULT_SPACE
    evaluator = VariantEvaluator(df, reference, out_dir=out_dir)
    root = Node(_state_str(DEFAULT_STATE))

    def child_finder(node, mc):
        current = _parse(node.state)
        for key, values in space.items():
            for value in values:
                if current.get(key) == value:
                    continue
                nxt = dict(current)
                nxt[key] = value
                if all(k in nxt for k in space):
                    node.add_child(Node(_state_str(nxt)))

    def node_evaluator(child, mc):
        return evaluator.evaluate(child.state)

    mc = MonteCarlo(root)
    mc.child_finder = child_finder
    mc.node_evaluator = node_evaluator
    random.seed(seed)
    mc.simulate(expansion_count=budget)
    baseline = evaluator.cache.get(root.state, {})
    best = max(evaluator.cache.values(), key=lambda r: (r["reward"], -len(r.get("error", ""))))
    trace = sorted(evaluator.cache.values(), key=lambda r: -r["reward"])
    return {
        "space": space,
        "budget": budget,
        "seed": seed,
        "baseline": baseline,
        "best": best,
        "improvement": round(best["reward"] - baseline["reward"], 4)
        if baseline else None,
        "trace": trace,
        "note": ("reward = (1 - style distance) - 0.5 per hard audit finding - 0.5 if any "
                 "text collision; every state in the trace was rendered and measured"),
    }


if __name__ == "__main__":
    print(json.dumps({"space": DEFAULT_SPACE, "default": DEFAULT_STATE}, indent=1))
