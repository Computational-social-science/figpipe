"""Specification layer: from TIDY DATA to a reproducible figure SPEC, without a model.

WHY THIS MODULE EXISTS (the structural gap the benchmark work exposed)
    Until now the pipeline could draw a panel once somebody had decided, by hand, which intent it
    was and which column was x, which was y, which carried the uncertainty. That is why it could
    reproduce the seed paper (where the recipe is known) but could not enter an authoritative
    benchmark: PlotTwin-Bench hands over a reference figure plus a CSV and asks for a figure;
    NaturePanelForge hands over a panel image and asks for code. Both begin one step BEFORE our
    old entry point. The missing layer is the one that turns data into a declared SPEC.

    `infer_spec()` is that layer. It reads column roles, applies an explicit, ordered rule set,
    and returns a `FigureSpec` that names every decision and the reason. When no rule is
    defensible it raises `SpecError` listing the roles it saw -- it never quietly picks a chart.

WHAT IS DELIBERATELY NOT HERE
    * Image understanding: inferring a spec from a raster reference needs a vision model; that is
      the next layer, and it must return a spec that this module can validate, not pixels.
    * A learned mapper: a hand-written ordered rule set is inspectable and testable; a learned
      mapper would need a labelled benchmark before it can be trusted.
    * Silent defaults: ambiguous input is an error with the observed roles, not a bar chart.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import asdict, dataclass, field

import pandas as pd


class SpecError(ValueError):
    """The data do not determine a defensible figure specification."""


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def _is_datetime(series: pd.Series) -> bool:
    return pd.api.types.is_datetime64_any_dtype(series)


def column_roles(df: pd.DataFrame, max_categories: int = 40) -> dict:
    """Partition columns into numeric / datetime / categorical, with the cardinality evidence."""
    roles = {"numeric": [], "datetime": [], "categorical": [], "unusable": []}
    for name in df.columns:
        s = df[name]
        if _is_datetime(s):
            roles["datetime"].append(name)
        elif _is_numeric(s):
            roles["numeric"].append(name)
        else:
            n = int(s.nunique(dropna=True))
            if 1 <= n <= max_categories:
                roles["categorical"].append(name)
            else:
                roles["unusable"].append(name)
    return roles


@dataclass(frozen=True)
class PanelSpec:
    """One declared panel: an intent, its data, and the column mapping it was given."""
    intent: str
    data: pd.DataFrame
    kwargs: dict
    rationale: str = ""

    def to_dict(self) -> dict:
        # the dataframe is carried for rendering, not for serialisation: a spec's JSON records
        # the DECISIONS (intent, mapping, reason), not a copy of the data
        return {"intent": self.intent, "kwargs": self.kwargs, "rationale": self.rationale}


@dataclass(frozen=True)
class FigureSpec:
    """A whole figure declaration. Everything needed to rebuild it is in here."""
    panels: list[PanelSpec]
    columns: float = 2.0
    height_mm: float | None = None
    sharex: bool = False
    sharey: bool = False
    letters: bool = True
    roles: dict = field(default_factory=dict)
    rationale: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"columns": self.columns, "height_mm": self.height_mm,
                "sharex": self.sharex, "sharey": self.sharey, "letters": self.letters,
                "roles": self.roles, "rationale": self.rationale,
                "panels": [p.to_dict() for p in self.panels]}


def _numeric_series(df, name):
    return pd.to_numeric(df[name], errors="coerce").dropna()


def infer_spec(df: pd.DataFrame, *, intent: str | None = None,
               x: str | None = None, y: str | None = None,
               group: str | None = None, columns: float = 2.0,
               height_mm: float | None = None) -> FigureSpec:
    """Infer a defensible FigureSpec from tidy data, or raise SpecError.

    The rules are ordered from the most to the least specific; the first that both fits the
    columns AND is defensible wins, and the returned spec records which rule fired and why.
    """
    if df is None or len(df) == 0:
        raise SpecError("empty data frame: no figure can be specified")
    roles = column_roles(df)
    rationales: list[str] = []
    num, cat, dt = roles["numeric"], roles["categorical"], roles["datetime"]

    # explicit intent: the caller takes responsibility, but the contract is still validated
    if intent is not None:
        kwargs = {}
        for key, val in (("x", x), ("y", y), ("group", group)):
            if val is not None:
                kwargs[key] = val
        spec = FigureSpec(panels=[PanelSpec(intent, df, kwargs, "explicit intent from caller")],
                          columns=columns, height_mm=height_mm, roles=roles,
                          rationale=["caller supplied the intent and columns"])
        # validate through the grammar contract before returning
        from figpipe import grammar
        grammar.panel(intent, df, **kwargs)
        return spec

    # R1 a time column plus a measure -> a trend panel with a fit
    if dt and num:
        kwargs = {"x": dt[0], "y": num[0], "xlabel": str(dt[0]), "ylabel": str(num[0]),
                  "fit": "lm", "band": "fit"}
        rationales.append(f"datetime column {dt[0]!r} orders the rows; {num[0]!r} is the measure")
        return FigureSpec([PanelSpec("trend_with_uncertainty", df, kwargs, rationales[-1])],
                          columns=columns, height_mm=height_mm, roles=roles,
                          rationale=rationales)

    # R2 categorical + measures: the SHAPE of the category determines the encoding, and a
    # second measure matters more than the first one: with several measures per category a
    # grouped bar preserves them all, while ranking would silently drop the rest.
    if cat and num:
        c, v = cat[0], num[0]
        counts = df.groupby(c, observed=True)[v].count()
        if len(num) >= 2 and len(counts) >= 2:
            kwargs = {"x": c, "ycols": num[:3], "xlabel": str(c),
                      "ylabel": str(num[0])}
            rationales.append(f"{c!r} groups {len(counts)} levels and {num[:3]} are parallel "
                              f"measures; grouped bars keep them all")
            return FigureSpec([PanelSpec("grouped_bars", df, kwargs, rationales[-1])],
                              columns=columns, height_mm=height_mm, roles=roles,
                              rationale=rationales)
        if len(counts) >= 2 and counts.min() >= 2 and len(counts) <= 30:
            kwargs = {"group": c, "value": v, "xlabel": str(c), "ylabel": str(v)}
            rationales.append(f"{c!r} has >=2 observations per level ({len(counts)} levels), "
                              f"so {v!r} is shown as a distribution")
            return FigureSpec([PanelSpec("boxplot", df, kwargs, rationales[-1])],
                              columns=columns, height_mm=height_mm, roles=roles,
                              rationale=rationales)
        if len(counts) >= 2:
            kwargs = {"label": c, "value": v, "top": min(len(counts), 20),
                      "xlabel": str(c), "ylabel": str(v)}
            rationales.append(f"{c!r} has {len(counts)} levels with single values; ranked by {v!r}")
            return FigureSpec([PanelSpec("ranked_composition", df, kwargs, rationales[-1])],
                              columns=columns, height_mm=height_mm, roles=roles,
                              rationale=rationales)

    # R5 two numeric measures, no category/time -> relationship
    if not cat and not dt and len(num) >= 2:
        kwargs = {"x": num[0], "y": num[1], "xlabel": str(num[0]), "ylabel": str(num[1])}
        if len(num) >= 2 and df[num[0]].nunique() > 20 and df[num[1]].nunique() > 20:
            rationales.append(f"{num[0]!r} and {num[1]!r} are both continuous; density, not scatter")
            return FigureSpec([PanelSpec("density_relationship", df, kwargs, rationales[-1])],
                              columns=columns, height_mm=height_mm, roles=roles,
                              rationale=rationales)
        rationales.append(f"{num[0]!r} vs {num[1]!r} is the only relationship the data offer")
        return FigureSpec([PanelSpec("scatter_fit", df, kwargs, rationales[-1])],
                          columns=columns, height_mm=height_mm, roles=roles,
                          rationale=rationales)

    # R6 a wide numeric frame with no better reading -> matrix
    if not cat and not dt and len(num) >= 3:
        kwargs = {"xlabel": "column", "ylabel": "row"}
        rationales.append(f"{len(num)} numeric columns and no index: shown as a matrix")
        return FigureSpec([PanelSpec("heatmap", df, kwargs, rationales[-1])],
                          columns=columns, height_mm=height_mm, roles=roles,
                          rationale=rationales)

    raise SpecError(
        "cannot infer a defensible figure from these columns; "
        f"roles={ {k: v for k, v in roles.items() if v} }. "
        "Supply intent= and the column mapping explicitly, or add a measured rule.")


def build(spec: FigureSpec, reference_profile=None):
    """Build the figure from a spec. Style transfer is applied when a reference is supplied."""
    from figpipe import composite, grammar, styleprofile
    if not isinstance(spec, FigureSpec):
        raise TypeError(f"expected FigureSpec, got {type(spec).__name__}")
    panels = []
    for p in spec.panels:
        panels.append(grammar.panel(p.intent, p.data, **p.kwargs))
    rc = None
    height = spec.height_mm
    if reference_profile is not None:
        style = styleprofile.style_from_profile(reference_profile)
        rc = style["rc"]
        height = height or style["height_mm"]
    return grammar.plate(panels, columns=spec.columns, height_mm=height,
                         sharex=spec.sharex, sharey=spec.sharey,
                         letters=spec.letters, rc=rc)
