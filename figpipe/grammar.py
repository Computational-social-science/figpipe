"""The figure grammar: a panel is described by what it MEANS, not by how one paper drew it.

WHY THIS LAYER EXISTS
    `figpipe.drawlib` answers "which pixels" -- `bar_with_errors(df, x, y, err, ...)` etc. That
    is still a pile of plotting arguments per figure: a new paper means a new pile, and the
    knowledge of *when* to use a band, a reference line or a ranked bar stays in the author's
    head. The seed paper (NHB 2026, "The growing concentration of national influence") makes
    the missing layer concrete: seven figures, five recurring visual sentences.

INTENTS, WITH THE EVIDENCE
    Measured by reading the seed's seven figures and its own R recipe:

      intent                  parts of a figure it covers       what it encodes
      ----------------------  --------------------------------- -------------------------------
      trend_with_uncertainty  Figs 2, 3c, 4, 5, 7 (5 of 7)     a quantity over time whose
                                                               uncertainty must be visible:
                                                               points, band, fit, reference,
                                                               correlation in the corner
      ranked_composition      Fig 1a                           what share each entity holds,
                                                               ordered, value printed
      density_relationship    Fig 1b                           many points, two quantities,
                                                               log scales, density not scatter
      signed_matrix           Fig 6b                           a matrix of signed values with
                                                               missing cells
      comparison_with_error   (no seed instance)               a few entities + uncertainty
      distribution            (no seed instance)               the spread of a measure

    The two last intents were already drawers; they are registered here so a figure can be
    described entirely in intents. Three of the seed's panels are NOT in this grammar on
    purpose: the QAP regression series (Fig 2's data is not in the package), and the arc
    diagram and the region matrix (Fig 6) both need a country-to-region mapping the seed does
    not include. They are recorded as gaps, not imitated.

WHAT AN INTENT ADDS OVER A DRAWER
    1. A CONTRACT: required columns/parameters, checked before drawing; a missing one raises a
       KeyError that names the contract instead of a matplotlib error three calls later.
    2. CONVENTIONS MEASURED FROM THE SEED: band alpha, marker size, fit method, reference-line
       style, where the correlation goes. A paper that wants different values can override
       them, but the default is the studied one rather than a guess.
    3. COMPOSITION: `plate()` builds a multi-panel figure out of intents with
       `figpipe.composite`, which owns the geometry.

WHAT IS DELIBERATELY NOT HERE
    A grammar of "journal style". These are the seed paper's encodings, not Nature's rules.
    The format rules live in `figpipe.style` and the knowledge base; the difference matters.
    Nothing in this module enforces a size, a font or a page width -- that is `audit`'s job.
"""
from __future__ import annotations

import pandas as pd

from figpipe import composite


class IntentContractError(KeyError):
    """A panel does not satisfy its intent's data contract."""


#: Conventions read off the seed's published figures and its R recipe. Each carries the
#: provenance that justifies it, because a default that cannot be traced is a guess.
SEED_CONVENTIONS = {
    "band_alpha": {"value": 0.25, "why": "geom_ribbon(alpha=0.25) in the seed's R recipe"},
    "marker_size": {"value": 2.6, "why": "geom_point(size=4) at the seed's print size"},
    "reference_style": {"value": "dashed", "why": "geom_hline(linetype='dashed') for parity 0/1"},
    "fit_centrality": {"value": "lm", "why": "geom_smooth(method='lm') on centrality panels"},
    "fit_gini": {"value": "poly3", "why": "y ~ poly(x,3) on the Gini panels"},
    "fit_dyads": {"value": "loess", "why": "geom_smooth default (loess) on the dyad panels"},
    "annotation_position": {"value": (0.03, 0.97), "why": "stat_cor at label.x/y.npc left/top"},
}


class Intent:
    """One semantic panel role: a drawer, a contract, and its measured conventions."""

    def __init__(self, name: str, drawer: str, requires: tuple[str, ...],
                 defaults: dict | None = None, doc: str = "", evidence: str = ""):
        self.name = name
        self.drawer = drawer
        self.requires = requires
        self.defaults = dict(defaults or {})
        self.doc = doc
        self.evidence = evidence

    def __repr__(self) -> str:
        return f"Intent({self.name!r}, drawer={self.drawer!r})"


INTENTS: dict[str, Intent] = {
    "trend_with_uncertainty": Intent(
        "trend_with_uncertainty", "trend_band", requires=("x", "y"),
        defaults={"fit": None, "reference": None,
                  "band_alpha": SEED_CONVENTIONS["band_alpha"]["value"],
                  "marker_size": SEED_CONVENTIONS["marker_size"]["value"],
                  "annotate_xy": SEED_CONVENTIONS["annotation_position"]["value"]},
        doc="A quantity over time with its uncertainty: points, band (lo/hi), optional fit, "
            "explicit reference line, correlation in the corner.",
        evidence="Seed Figs 2, 3c, 4, 5, 7"),
    "ranked_composition": Intent(
        "ranked_composition", "ranked_share", requires=("label", "value"),
        defaults={"top": 20, "percent": False},
        doc="What share each entity holds, ordered, with the value printed on each bar.",
        evidence="Seed Fig 1a"),
    "density_relationship": Intent(
        "density_relationship", "hexbin_corr", requires=("x", "y"),
        defaults={"gridsize": 30, "xscale": "log", "yscale": "log"},
        doc="Many points, two quantities, log scales: density as a hexbin, correlation stated.",
        evidence="Seed Fig 1b"),
    "signed_matrix": Intent(
        "signed_matrix", "tile_diverging", requires=(),
        defaults={"annotate": True},
        doc="A matrix of signed values with missing cells: diverging tiles, grey for no data.",
        evidence="Seed Fig 6b"),
    "comparison_with_error": Intent(
        "comparison_with_error", "bar_with_errors", requires=("x", "y"),
        defaults={},
        doc="A few entities compared with their uncertainty, as bars.",
        evidence="legacy template"),
    "distribution": Intent(
        "distribution", "boxplot", requires=("group", "value"),
        defaults={},
        doc="The spread of a measure across groups.",
        evidence="legacy template"),
}


def intent(name: str) -> Intent:
    """Look up an intent by name; an unknown name lists what exists."""
    if name not in INTENTS:
        raise KeyError(f"unknown panel intent {name!r}; available: {sorted(INTENTS)}")
    return INTENTS[name]


def panel(name: str, data: pd.DataFrame, *, colorbar: bool = False,
          cbar_label: str = "", at: tuple | None = None, letter: str | None = None,
          letter_dx_pt: float | None = None, letter_dy_pt: float | None = None,
          **kwargs) -> composite.Panel:
    """Build one composite panel from an intent and tidy data.

    THE CONTRACT IS CHECKED, NOT ASSUMED
        `trend_with_uncertainty` without an `x` column, or a `ranked_composition` without a
        `label`, raises `IntentContractError` naming the contract. The alternative -- letting
        matplotlib fail on a missing key, or worse letting pandas silently plot the index --
        is how a figure ends up encoding something other than the claim.

    `colorbar`, `cbar_label`, `at` and `letter` are placement properties of the panel, not of
    the drawing, so they are keyword-only here rather than being smuggled into the drawer's
    kwargs (a drawer that received `colorbar=` would have to ignore it, which is the same
    failure shape as a control that does nothing).
    """
    spec = intent(name)
    if not isinstance(data, pd.DataFrame):
        raise IntentContractError(f"{name}: data must be a DataFrame")
    for key in spec.requires:
        if key not in kwargs:
            raise IntentContractError(
                f"{name} requires the parameter {key!r}; required: {spec.requires}")
        col = kwargs[key]
        if col not in data.columns:
            raise IntentContractError(
                f"{name}: {key}={col!r} is not a column of the data; has {list(data.columns)}")
    if name == "trend_with_uncertainty":
        if ("lo" in kwargs) != ("hi" in kwargs):
            raise IntentContractError(
                "trend_with_uncertainty: lo and hi describe the band together")
        for key in ("lo", "hi"):
            if key in kwargs and kwargs[key] not in data.columns:
                raise IntentContractError(f"{name}: {key}={kwargs[key]!r} is not a column")
    merged = {**spec.defaults, **kwargs}
    return composite.Panel(spec.drawer, data, merged, at=at, letter=letter,
                           colorbar=colorbar, cbar_label=cbar_label,
                           letter_dx_pt=letter_dx_pt, letter_dy_pt=letter_dy_pt)


def plate(panels: list[composite.Panel], **kwargs):
    """Compose intent-built panels into one figure with the measured plate geometry."""
    return composite.composite(panels, **kwargs)


def catalogue() -> list[dict]:
    """The grammar as data: name, drawer, contract, evidence. Used by docs and tests."""
    return [{"intent": s.name, "drawer": s.drawer, "requires": list(s.requires),
             "defaults": s.defaults, "evidence": s.evidence} for s in INTENTS.values()]


if __name__ == "__main__":
    import json
    print(json.dumps(catalogue(), indent=2, ensure_ascii=False))
