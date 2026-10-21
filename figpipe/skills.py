"""Global skills + classic operators: the response to "there is no single figure standard".

WHY THIS LAYER (and how it differs from `grammar`)
    `grammar` names four panel INTENTS (trend with uncertainty, ranked composition, density,
    signed matrix). An intent fixes what a panel means; it does not fix how a new requirement
    is assembled. Real requests vary along dimensions the intents do not cover: log axes, a
    second y axis, a colour bar, a shared legend, a reference profile, a statistics reconciliation,
    a panel letter convention, a target journal. Hard-coding one pipeline per request is how the
    project previously drifted between "template" and "one-off script".

    This module adds the two missing abstractions, deliberately separated:

        OPERATOR  a small, single-purpose, classic transformation
                  (encode.trend, encode.ranked, layout.plate, style.profile, verify.audit, ...)
        SKILL     a named, versioned recipe: an ordered list of operators, a parameter contract,
                  a verification step, and an example. A new requirement is a NEW SKILL composed
                  from existing operators -- the operators do not multiply, only the recipes do.

    The global skill is the floor every recipe inherits: Nature compliance, no text collisions,
    and a spec/skill trace so the figure can be rebuilt.

WHAT THIS IS NOT
    Not an agent prompt bundle (the peer projects ship those). A skill here is executable,
    inspectable and tested; its parameters are declared and unknown ones are an error, not a
    prompt hint. Models may later PROPOSE a skill or its parameters; verification stays here.
"""
from __future__ import annotations

import inspect
import json
import pathlib
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, composite, grammar, layout, semantics, styleprofile  # noqa: E402


class SkillError(RuntimeError):
    """A skill or operator was invoked with a contract violation."""


#: How many bars one axis can carry with readable tick labels at 6 pt on a ~85 mm panel.
#: Past this the labels collide whatever the rotation, so a bar panel is the wrong encoding:
#: a line/trend panel is the right one. Refusing names the fix; drawing it hides the problem.
#: `layout.split_panels(max_bars=...)` may override it for probing; this is the audited default.
MAX_BARS = 12

#: How many rows a table with NO 2-D reading may have before `encode.matrix` refuses instead of
#: drawing unlabelable tiles. `encode.matrix(max_rows=...)` may override it for probing.
MAX_MATRIX_ROWS = 40


# --------------------------------------------------------------------------------------
# Context and operators
# --------------------------------------------------------------------------------------

@dataclass
class SkillContext:
    """The mutable state a skill's operators act on. Every mutation is traced."""
    data: pd.DataFrame
    params: dict
    panels: list = field(default_factory=list)
    layout: dict = field(default_factory=lambda: {
        "columns": 2.0, "height_mm": None, "sharex": False,
        "sharey": False, "letters": True, "margins": None})
    rc: dict | None = None
    reference: styleprofile.StyleProfile | None = None
    meta: dict = field(default_factory=dict)      # axis scales, facet options, provenance
    trace: list[str] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)

    def add_panel(self, panel) -> None:
        self.panels.append(panel)

    def note_options(self, op: str, **options) -> None:
        """Record the drawing OPTIONS that changed the output, after the operator's own trace line.

        Why this exists: the trace named the operator and its primary columns only, so
        `encode.trend(x,y)` was recorded for an unfitted trend, a linear fit, and a fit with a
        confidence band alike -- three different figures, one trace. A reader (and the web layer,
        which asks "was the style applied?") could not tell them apart.

        Only options that were actually SET are recorded, and only when they are not None, so the
        trace stays short and a difference in the trace always means a difference in the figure.
        """
        shown = {k: v for k, v in options.items() if v is not None}
        if shown:
            rendered = ", ".join(f"{k}={v!r}" for k, v in shown.items())
            self.trace.append(f"{op}.options({rendered})")


@dataclass(frozen=True)
class Operator:
    """A classic, single-purpose transformation over the skill context."""
    name: str
    kind: str          # "build" (mutates context) or "verify" (reads the rendered artefact)
    fn: Callable
    doc: str


OPERATORS: dict[str, Operator] = {}


def operator(name: str, kind: str):
    """Register an operator. `kind` must be build or verify."""
    if kind not in ("build", "verify"):
        raise ValueError(f"operator {name!r}: kind must be 'build' or 'verify', got {kind!r}")

    def deco(fn):
        doc = (inspect.getdoc(fn) or "").splitlines()[0]
        OPERATORS[name] = Operator(name, kind, fn, doc)
        return fn
    return deco


# ---------------------------------------------------------------- build operators

@operator("layout.plate", "build")
def op_layout_plate(ctx: SkillContext, columns: float = 2.0, height_mm=None,
                    sharex: bool = False, sharey: bool = False, letters: bool = True,
                    margins: dict | None = None):
    """Set the plate geometry: column width, height, sharing, letters, margins."""
    if columns not in (1.0, 2.0):
        raise SkillError(f"columns must be 1 or 2, got {columns!r}")
    if height_mm is None and ctx.layout.get("height_mm") is not None:
        height_mm = ctx.layout["height_mm"]
    ctx.layout.update(columns=columns, height_mm=height_mm, sharex=sharex,
                      sharey=sharey, letters=letters, margins=margins)
    ctx.trace.append("layout.plate")
    ctx.note_options("layout.plate", columns=ctx.layout.get("columns"),
                     letters=ctx.layout.get("letters"),
                     sharex=ctx.layout.get("sharex") or None,
                     sharey=ctx.layout.get("sharey") or None)


@operator("encode.trend", "build")
def op_encode_trend(ctx: SkillContext, x: str, y: str, lo: str | None = None,
                    hi: str | None = None, fit: str | None = "lm",
                    band: str | None = None, reference: float | None = None,
                    series: str | None = None, title: str | None = None,
                    xlabel: str | None = None, ylabel: str | None = None):
    """Encode a trend panel: points, optional interval, fit, reference line."""
    kw = {"x": x, "y": y, "fit": fit, "reference": reference, "series": series,
          "title": title, "xlabel": xlabel, "ylabel": ylabel}
    if lo is not None or hi is not None:
        kw.update(lo=lo, hi=hi)
    if band is not None:
        kw["band"] = band
    ctx.add_panel(grammar.panel("trend_with_uncertainty", ctx.data, **kw))
    ctx.trace.append(f"encode.trend({x},{y})")
    ctx.note_options("encode.trend", fit=fit, band=band, reference=reference,
                     lo=lo, hi=hi, series=series, title=title)


@operator("encode.ranked", "build")
def op_encode_ranked(ctx: SkillContext, label: str, value: str, top: int = 20,
                     percent: bool = False, xtick_rotation: float = 45.0,
                     xlabel: str | None = None, ylabel: str | None = None):
    """Encode a ranked composition: bars sorted by value, number printed on each bar."""
    ctx.add_panel(grammar.panel(
        "ranked_composition", ctx.data, label=label, value=value, top=top,
        percent=percent, xtick_rotation=xtick_rotation,
        xlabel=xlabel or "", ylabel=ylabel or ""))
    ctx.trace.append(f"encode.ranked({label},{value})")


@operator("encode.density", "build")
def op_encode_density(ctx: SkillContext, x: str, y: str, marginals=False,
                      colorbar: bool = False, gridsize: int = 30):
    """Encode a dense relationship as a hexbin with optional marginals and colour bar."""
    ctx.add_panel(grammar.panel(
        "density_relationship", ctx.data, x=x, y=y, gridsize=gridsize,
        marginals=marginals, colorbar=colorbar))
    ctx.trace.append(f"encode.density({x},{y})")


@operator("encode.matrix", "build")
def op_encode_matrix(ctx: SkillContext, columns: str | None = None,
                     colorbar: bool = True, max_rows: int | None = None):
    """Encode a numeric matrix (all numeric columns, or a comma list) as signed tiles.

    `max_rows` is the refusal budget for a table with NO 2-D reading: past it the tiles cannot
    be labelled, so the operator refuses and names `field_map` instead. It is a parameter rather
    than a literal so the mutation loop (`figpipe/mutation.py`) can probe whether the budget is
    set where the evidence puts it. The default is the value the data-shape audit chose, so
    behaviour is unchanged for every existing caller.
    """
    if columns:
        cols = [c.strip() for c in columns.split(",") if c.strip()]
        data = ctx.data[cols]
    else:
        data = ctx.data.select_dtypes("number")
    if data.shape[1] < 2 or data.shape[0] < 2:
        raise SkillError("encode.matrix needs at least 2x2 numeric data")
    # A LONG table is not a matrix. A field table of 48 (x, y, value) rows passed straight to a
    # tile drawer becomes a 48-row matrix whose tick labels all collide -- the data-shape audit
    # found exactly that. Pivot onto the first two numeric columns when the table looks like a
    # field, and record the pivot so the figure can be rebuilt.
    if data.shape[0] > 24:
        budget = MAX_MATRIX_ROWS if max_rows is None else int(max_rows)
        # A pivot needs two columns that VARY (bookkeeping such as panel_row has one value) and a
        # value column distinct from both. Guessing "the first two columns" produced a 1x1 pivot
        # and refused a task that previously rendered -- a regression this project's own loop
        # caught within one cycle.
        varying = [c for c in data.columns if data[c].nunique() >= 2]
        best = None
        for i, a in enumerate(varying):
            for bcol in varying[i + 1:]:
                for val in varying:
                    if val in (a, bcol):
                        continue
                    piv = data.pivot_table(index=bcol, columns=a, values=val,
                                           aggfunc="mean")
                    if piv.shape[0] >= 2 and piv.shape[1] >= 2:
                        score = piv.shape[0] * piv.shape[1]
                        if best is None or score > best[0]:
                            best = (score, a, bcol, val, piv)
        if best is not None:
            _, a, bcol, val, pivoted = best
            # THE BUDGET APPLIES TO THE PIVOTED SHAPE, not only to the unpivoted table. A pivot
            # that lands 40 rows on a 90 mm panel draws 2.25 mm per row; the drawer then hides both
            # the tick labels and the annotations, so the figure carries no recoverable values and
            # the task is reported unverifiable. A figure nobody can read is not a figure.
            if pivoted.shape[0] > budget:
                raise SkillError(
                    f"encode.matrix: pivoting {a} x {bcol} gives {pivoted.shape[0]} rows, past the "
                    f"{budget}-row budget; at that size the tiles cannot be labelled and the figure "
                    f"would carry no readable value -- aggregate {bcol} to fewer levels, or use "
                    f"field_map")
            ctx.trace.append(f"encode.matrix.pivot({a} x {bcol} of {val}: "
                             f"{data.shape[0]} rows -> {pivoted.shape[0]}x{pivoted.shape[1]})")
            data = pivoted
        elif data.shape[0] > budget:
            # no 2-D reading exists AND the table is too long to label: refuse, naming the fix
            raise SkillError(
                f"encode.matrix: {data.shape[0]} rows have no 2-D reading "
                f"(no column pair varies enough to pivot) and exceed the {budget}-row "
                f"budget; use field_map or pass a wide frame")
        # otherwise fall through: a 25-40 row frame is drawable as-is and was before this change
    ctx.add_panel(grammar.panel("signed_matrix", data, colorbar=colorbar,
                                cbar_label=""))
    ctx.trace.append("encode.matrix")


@operator("encode.box", "build")
def op_encode_box(ctx: SkillContext, group: str, value: str):
    """Encode a distribution comparison as box plots."""
    ctx.add_panel(grammar.panel("distribution", ctx.data, group=group, value=value))
    ctx.trace.append(f"encode.box({group},{value})")


@operator("encode.bars", "build")
def op_encode_bars(ctx: SkillContext, x: str, ycols, agg: str = "mean"):
    """Encode parallel measures per category as grouped bars, ONE bar per category level.

    WHY AGGREGATION IS NOT OPTIONAL: a long table has many rows per category (40 rows over 2
    groups in the worked example). Drawing one bar per ROW stacks 40 overlapping groups and makes
    the tick labels collide -- the example caught exactly that as three hard findings while the
    compliance audit reported zero. A grouped bar encodes a SUMMARY per level, so the summary must
    be stated: mean by default, and the choice is written into the trace.
    """
    if isinstance(ycols, str):
        ycols = [c.strip() for c in ycols.split(",") if c.strip()]
    missing = [c for c in [x] + list(ycols) if c not in ctx.data.columns]
    if missing:
        raise SkillError(f"encode.bars: missing columns {missing}")
    if agg not in ("mean", "median", "sum"):
        raise SkillError(f"encode.bars: unsupported aggregation {agg!r}")
    counts = ctx.data[x].astype(str).value_counts()
    if int(counts.max()) > 1:
        # more than one row per level: summarise, and say so
        data = (ctx.data.groupby(ctx.data[x].astype(str), observed=True)[list(ycols)]
                .agg(agg).reset_index().rename(columns={"index": x}))
        ctx.trace.append(f"encode.bars.aggregate({x} by {agg}: "
                         f"{len(ctx.data)} rows -> {len(data)} levels)")
    else:
        data = ctx.data
    ctx.add_panel(composite.Panel("grouped_bars", data,
                                  {"x": data.columns[0], "ycols": list(ycols),
                                   "labels": {c: c for c in ycols}}))
    ctx.trace.append(f"encode.bars({x},{ycols})")
    # `agg` is the option that changes a bar panel: it decides what each bar MEANS.
    ctx.note_options("encode.bars", agg=agg)


@operator("encode.scatter", "build")
def op_encode_scatter(ctx: SkillContext, x: str, y: str,
                      xlabel: str | None = None, ylabel: str | None = None):
    """Encode a relationship as a scatter with a fit and r."""
    ctx.add_panel(composite.Panel("scatter_fit", ctx.data,
                                  {"x": x, "y": y, "xlabel": xlabel or "",
                                   "ylabel": ylabel or ""}))
    ctx.trace.append(f"encode.scatter({x},{y})")
    ctx.note_options("encode.scatter", xlabel=xlabel, ylabel=ylabel)


@operator("encode.hist", "build")
def op_encode_hist(ctx: SkillContext, value: str, bins: int = 20,
                   group: str | None = None, density: bool = True,
                   xscale: str | None = None, yscale: str | None = None,
                   title: str | None = None):
    """Encode the distribution of one measured column (optionally split by a category)."""
    kw = {"value": value, "bins": bins, "group": group, "density": density,
          "xscale": xscale or ctx.meta.get("xscale", "linear"),
          "yscale": yscale or ctx.meta.get("yscale", "linear"),
          "title": title}
    ctx.add_panel(composite.Panel(draw="histogram", data=ctx.data, kwargs=kw))
    ctx.trace.append(f"encode.hist({value})")
    ctx.note_options("encode.hist", bins=bins, group=group, title=title)


@operator("encode.dual", "build")
def op_encode_dual(ctx: SkillContext, x: str, y1: str, y2: str,
                   ylabel: str = "", ylabel2: str = ""):
    """Encode two series on one x with separate left/right y axes (both labelled)."""
    ctx.add_panel(composite.Panel(draw="dual_series", data=ctx.data,
                                  kwargs={"x": x, "y1": y1, "y2": y2,
                                          "ylabel": ylabel, "ylabel2": ylabel2}))
    ctx.trace.append(f"encode.dual({y1},{y2})")


@operator("axis.log", "build")
def op_axis_log(ctx: SkillContext, which: str = "xy"):
    """Set log scale for x, y, or both; encoders read it from the context."""
    if not set(which) <= set("xy") or not which:
        raise SkillError(f"axis.log: which must be 'x', 'y' or 'xy', got {which!r}")
    if "x" in which:
        ctx.meta["xscale"] = "log"
    if "y" in which:
        ctx.meta["yscale"] = "log"
    ctx.trace.append(f"axis.log({which})")


@operator("layout.facets", "build")
def op_layout_facets(ctx: SkillContext, of: str = "hist", by: str = "",
                     value: str | None = None, bins: int = 20,
                     group: str | None = None, x: str | None = None,
                     y: str | None = None, columns: float = 2.0,
                     max_panels: int = 4, title: bool = True, **kwargs):
    """Repeat one classic encoding for each level of a facet column.

    This is the operator behind multi-panel benchmark tasks: the same encoding, one panel per
    condition/site/region. It refuses silently truncated facets: more levels than `max_panels`
    is an error, because dropping panels changes the claim.
    """
    if not by:
        raise SkillError("layout.facets needs a facet column (by=...)")
    if by not in ctx.data.columns:
        raise SkillError(f"layout.facets: {by!r} is not a column of the data")
    levels = sorted(str(v) for v in pd.unique(ctx.data[by]))
    if len(levels) > max_panels:
        raise SkillError(f"layout.facets: {len(levels)} levels but max_panels={max_panels}; "
                         "raise max_panels deliberately or choose a coarser facet")
    encoders = {"hist": op_encode_hist, "trend": op_encode_trend,
                "scatter": op_encode_scatter}
    if of not in encoders:
        raise SkillError(f"layout.facets: unsupported encoder {of!r}; "
                         f"choose from {sorted(encoders)}")
    for level in levels:
        sub = ctx.data[ctx.data[by].astype(str) == level].reset_index(drop=True)
        child = SkillContext(data=sub, params=dict(ctx.params),
                             layout=dict(ctx.layout), meta=dict(ctx.meta),
                             rc=ctx.rc)
        enc = encoders[of]
        # ONLY the chosen branch is built. A dict literal evaluates every value first, so the
        # previous form ran _second_numeric() for the trend/scatter branches even when `of` was
        # "hist" -- and a table with one numeric column failed asking for a histogram.
        if of == "hist":
            call = dict(value=value or _first_numeric(ctx), bins=bins, group=group)
        else:
            call = dict(x=x or _first_numeric(ctx), y=y or _second_numeric(ctx))
        if of == "hist" and title:
            call["title"] = level
        elif of == "trend" and title:
            call["title"] = level
        enc(child, **{k: v for k, v in call.items() if v is not None})
        ctx.panels.extend(child.panels)
    ctx.layout["columns"] = columns
    ctx.meta["facets"] = {"by": by, "levels": levels}
    ctx.trace.append(f"layout.facets({by}:{len(levels)})")
    ctx.note_options("layout.facets", of=of, bins=bins, columns=columns,
                     max_panels=max_panels)


def _first_numeric(ctx) -> str:
    num = [c for c in ctx.data.columns if pd.api.types.is_numeric_dtype(ctx.data[c])]
    if not num:
        raise SkillError("layout.facets: no numeric column to encode")
    return num[0]


def _second_numeric(ctx) -> str:
    num = [c for c in ctx.data.columns if pd.api.types.is_numeric_dtype(ctx.data[c])]
    if len(num) < 2:
        raise SkillError("layout.facets: need two numeric columns for scatter/trend")
    return num[1]


@operator("encode.error_bars", "build")
def op_encode_error_bars(ctx: SkillContext, x: str, y: str, err: str | None = None,
                         title: str | None = None, xtick_rotation: float = 30.0,
                         xlabel: str | None = None, ylabel: str | None = None):
    """Encode a few entities compared with their uncertainty, as bars + error bars."""
    kw = {"x": x, "y": y, "xtick_rotation": xtick_rotation,
          "xlabel": xlabel or "", "ylabel": ylabel or "", "title": title}
    if err:
        kw["err"] = err
    ctx.add_panel(composite.Panel("bar_with_errors", ctx.data, kw))
    ctx.trace.append(f"encode.error_bars({x},{y},{err})")
    ctx.note_options("encode.error_bars", xtick_rotation=xtick_rotation, title=title)


@operator("layout.split_panels", "build")
def op_layout_split_panels(ctx: SkillContext, by: str, of: str = "error_bars",
                           x: str | None = None, y: str | None = None,
                           err: str | None = None, columns: float = 2.0,
                           max_panels: int = 4, max_rows: int = 200,
                           max_bars: int | None = None,
                           xtick_rotation: float = 30.0, **kwargs):
    """Build one panel per level of a grouping column from a long table.

    This is the operator behind benchmark "Composite" tasks: a single table carries several
    sub-figures distinguished by a group column (panel_group / panel_block), and the honest
    reading is one panel per group. More levels than `max_panels` is an error, because silently
    dropping a panel changes what the figure claims.

    `max_bars` is the category budget for one axis: past it the tick labels collide whatever the
    rotation, so a bar panel is the wrong encoding. It is a parameter rather than a literal so
    the mutation loop (`figpipe/mutation.py`) can probe where the budget belongs. `None` keeps
    the audited default, so behaviour is unchanged for every existing caller.
    """
    if not by or by not in ctx.data.columns:
        raise SkillError(f"layout.split_panels needs a grouping column; got {by!r}")
    levels = [str(v) for v in pd.unique(ctx.data[by])]
    if len(levels) > max_panels:
        raise SkillError(f"layout.split_panels: {len(levels)} levels but max_panels="
                         f"{max_panels}; raise it deliberately")
    if of != "error_bars":
        raise SkillError(f"layout.split_panels: unsupported encoder {of!r}")
    label = x or _first_categorical(ctx)
    #: How many bars an axis can carry with readable tick labels at 6 pt on a ~85 mm panel.
    #: Past this the labels collide whatever the rotation, so a bar panel is the wrong encoding:
    #: a line/trend panel is the right one. Refusing names the fix; drawing it hides the problem.
    #: The operator's `max_bars` parameter overrides it for probing; `None` means "use this".
    budget = MAX_BARS if max_bars is None else int(max_bars)
    if budget < 2:
        raise SkillError(f"layout.split_panels: max_bars={budget} cannot carry a comparison")
    for level in levels:
        n_levels = ctx.data.loc[ctx.data[by].astype(str) == level, label].nunique()
        if n_levels > budget:
            raise SkillError(
                f"layout.split_panels: {level!r} has {n_levels} distinct {label!r} values; a bar "
                f"panel can carry at most {budget} with readable labels. Use the trend encoder "
                f"for an ordered axis, or pass of='error_bars' with a coarser label.")
    aggregated: list[str] = []
    for level in levels:
        sub = ctx.data[ctx.data[by].astype(str) == level].reset_index(drop=True)
        if len(sub) > max_rows:
            # A bar panel with 300 bars is not a comparison, it is a smear: every bar is
            # narrower than a pixel and the axis carries 300 ticks. Aggregate by the categorical
            # axis and RECORD it -- silently truncating would change what the panel claims.
            grouped = (sub.groupby(label, observed=True)[y or _first_numeric(ctx)]
                       .mean().reset_index())
            if len(grouped) > max_rows:
                grouped = grouped.head(max_rows)
                aggregated.append(f"{level}: top {max_rows} of {len(grouped)}")
            else:
                aggregated.append(f"{level}: {len(sub)} rows -> mean per {label}")
            sub = grouped
        # ONE bar per axis level, not one per row: a long table gives 20 rows per level, and
        # drawing them all stacks the tick labels into collisions (found by the data-shape audit).
        # `y or _first_numeric(<context>)` -- the throwaway context was assigned to a name and
        # never read; _first_numeric only needs a SkillContext to look at the columns.
        value_col = y or _first_numeric(SkillContext(data=sub, params={}))
        if sub[label].astype(str).duplicated().any():
            # Aggregate the VALUE and, when present, the ERROR column. Keeping only value_col
            # dropped `err`, and the child panel then raised KeyError on a column the caller had
            # legitimately supplied -- three benchmark tasks failed that way.
            cols = [value_col] + ([err] if err and err in sub.columns else [])
            agg = (sub.groupby(sub[label].astype(str), observed=True)[cols]
                   .mean().reset_index())
            note = f"{level}: {len(sub)} rows -> mean per {label}"
            if len(cols) > 1:
                note += f" (with {err} averaged)"
            aggregated.append(note)
            sub = agg
        child = SkillContext(data=sub, params=dict(ctx.params), layout=dict(ctx.layout),
                             meta=dict(ctx.meta), rc=ctx.rc)
        op_encode_error_bars(child, x=label, y=value_col,
                             err=err, title=level, xtick_rotation=xtick_rotation)
        ctx.panels.extend(child.panels)
    ctx.layout["columns"] = columns
    ctx.meta["split"] = {"by": by, "levels": levels, "aggregated": aggregated}
    ctx.trace.append(f"layout.split_panels({by}:{len(levels)})")
    for note in aggregated:
        ctx.trace.append(f"layout.split_panels.aggregate({note})")


def _first_categorical(ctx) -> str:
    for c in ctx.data.columns:
        if not pd.api.types.is_numeric_dtype(ctx.data[c]):
            if 2 <= ctx.data[c].nunique() <= 30:
                return c
    raise SkillError("layout.split_panels: no categorical axis column found")


@operator("encode.field", "build")
def op_encode_field(ctx: SkillContext, x: str, y: str, value: str,
                    contour: bool = False, cbar_label: str = "",
                    cmap: str = "viridis"):
    """Encode a scalar field over a 2-D coordinate grid (position x time, x x y, ...)."""
    # THE COLOUR BAR IS NOT OPTIONAL FOR A FIELD. Without it the raster's colours encode a scale
    # the reader cannot see, and no rendered-file check can state what the colours mean. It is also
    # the only numeric content a field figure carries: the tick labels ARE text in the PDF.
    ctx.add_panel(composite.Panel("field_2d", ctx.data,
                                  {"x": x, "y": y, "value": value,
                                   "contour": contour, "cmap": cmap,
                                   "cbar_label": cbar_label},
                                  colorbar=True))
    ctx.trace.append(f"encode.field({x},{y},{value})")


#: How many spokes a polar axis can carry with readable labels. Past this the labels overlap
#: whatever the font size, and the profile stops being a profile -- it becomes a ring of text.
#: Drawers that actually DRAW a colour bar.
#: `encode.field` gives `field_2d` one; `encode.matrix` does not give `tile_diverging` one.
#: The scale check applies only where a scale is claimed, and asking the drawer is exact --
#: more geometric heuristics are not (9 pool tasks were flagged by axis labels that looked
#: like a scale).
DRAWERS_WITH_COLORBAR = {"field_2d", "tile_diverging"}

MAX_POLAR_SPOKES = 16


@operator("encode.polar", "build")
def op_encode_polar(ctx: SkillContext, theta: str, value: str,
                    line: bool = True, title: str | None = None,
                    max_spokes: int | None = None, agg: str = "mean"):
    """Encode a radial profile: one value per angle (category or degrees).

    ONE SPOKE PER ANGLE, NOT ONE PER ROW. A long table (the benchmark's radar tasks carry 460 and
    784 rows) passed straight to the polar drawer draws one spoke per row, and every label
    collides: measured at 50 hard text collisions on a single task. A radial profile encodes a
    SUMMARY per angle, so the summary must be stated -- mean by default -- and the reduction is
    written into the trace.

    Past `max_spokes` the operator REFUSES rather than drawing a ring of overlapping text, because
    a radar with 40 unreadable spokes is not a radar. The budget is a parameter so the mutation loop
    can probe where it belongs.
    """
    budget = MAX_POLAR_SPOKES if max_spokes is None else int(max_spokes)
    if agg not in ("mean", "median", "sum"):
        raise SkillError(f"encode.polar: unsupported aggregation {agg!r}")
    data = ctx.data
    counts = data[theta].astype(str).value_counts()
    if int(counts.max()) > 1:
        data = (data.assign(**{theta: data[theta].astype(str)})
                .groupby(theta, observed=True)[value].agg(agg).reset_index())
        ctx.trace.append(f"encode.polar.aggregate({theta} by {agg}: "
                         f"{len(ctx.data)} rows -> {len(data)} angles)")
    n = len(data)
    if n < 3:
        # a radial profile with fewer than three spokes is not a profile: matplotlib autoscales
        # theta to a sliver and its locator tries to draw thousands of ticks. Two benchmark tasks
        # aggregate to exactly this, so it must be a NAMED refusal, not a bare ValueError.
        raise SkillError(
            f"encode.polar: {theta!r} reduces to {n} distinct angle(s); a polar profile needs at "
            f"least 3. This data has no angular reading -- use a bar or trend encoding.")
    if n > budget:
        raise SkillError(
            f"encode.polar: {n} distinct angles exceeds the {budget}-spoke budget; labels overlap "
            f"past it. Aggregate to fewer angles, or pass max_spokes deliberately.")
    ctx.add_panel(composite.Panel("polar_profile", data,
                                  {"theta": theta, "value": value, "line": line,
                                   "title": title}))
    ctx.trace.append(f"encode.polar({theta},{value})")


@operator("style.profile", "build")
def op_style_profile(ctx: SkillContext, profile=None):
    """Apply a measured reference style: rcParams, palette, and its aspect-derived height."""
    if profile is None:
        raise SkillError("style.profile needs a profile path or StyleProfile")
    prof = (styleprofile.StyleProfile.load(profile)
            if isinstance(profile, (str, pathlib.Path)) else profile)
    derived = styleprofile.style_from_profile(prof)
    ctx.rc = derived["rc"]
    ctx.reference = prof
    if ctx.layout.get("height_mm") is None:
        ctx.layout["height_mm"] = derived["height_mm"]
    # a reference style may supply the series palette to panels that carry one
    pal = derived["palette"]
    if pal:
        for p in ctx.panels:
            if "palette" in p.kwargs:
                p.kwargs["palette"] = pal
            elif p.draw in ("histogram", "boxplot"):
                p.kwargs["color"] = pal[0]
    ctx.trace.append(f"style.profile({getattr(prof, 'source', 'profile')})")


# ---------------------------------------------------------------- verify operators

@operator("verify.audit", "verify")
def op_verify_audit(ctx: SkillContext, fig, pdf_path):
    """Compliance audit on the rendered PDF (fonts, width, height, embedded fonts)."""
    rep = audit.audit(pdf_path, expect_width_mm=183.0 if ctx.layout["columns"] == 2.0
                      else 89.0, check_overlap=False)
    hard = [f for f in rep["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    for f in hard:
        ctx.findings.append({"check": f["check"], "detail": f["detail"],
                             "severity": "hard"})
    ctx.trace.append("verify.audit")


@operator("verify.collisions", "verify")
def op_verify_collisions(ctx: SkillContext, fig, pdf_path):
    """Glyph-level text collisions (rotated tick labels are not false positives)."""
    hits = audit.overlapping_glyphs(pdf_path)
    for h in hits:
        ctx.findings.append({"check": "text_collision",
                             "detail": f"{h['a']!r} over {h['b']!r}",
                             "severity": "hard"})
    ctx.trace.append("verify.collisions")


def _value_column(ctx, kw) -> str | None:
    """Which column the colour encodes, from what the operator recorded -- never guessed.

    `encode.field` passes `value` as a kwarg. `encode.matrix` pivots and writes
    `encode.matrix.pivot(<a> x <b> of <val>: ...)` into the trace. Both are facts the caller holds.
    """
    import re
    if kw.get("value"):
        return str(kw["value"])
    for t in ctx.trace:
        m = re.search(r"matrix\.pivot\(.* of (\w+)", t)
        if m:
            return m.group(1)
    return None


def _drawn_values(fig, panel):
    """The array the drawer actually plotted, when it recorded one.

    A drawer that PIVOTS or aggregates knows the drawn values and nothing else does -- a caller's
    frame still spans the raw rows. `ax_field_2d` records its grid on the axes so a check can read
    what was plotted rather than what was passed in.
    """
    try:
        for ax in fig.axes:
            arr = getattr(ax, "_figpipe_drawn", None)
            if arr is not None:
                return arr
    except (AttributeError, TypeError):
        pass
    return None


@operator("verify.semantics", "verify")
def op_verify_semantics(ctx: SkillContext, fig, pdf_path):
    """The panel's printed claims must match the data it was drawn from.

    This is the only check in the pipeline that re-derives NUMBERS from the rendered figure; the
    audit checks geometry, styleprofile checks appearance, score checks dimensions. A figure that
    prints "r = +0.80" over data whose r is -0.20 passes every other check in this project.
    """
    #: Drawers whose geometry we can verify against the data: one mark per row on x/y.
    #: A heatmap, a field or a bar panel draws a different geometry, and applying a point-count
    #: check to them would produce a false failure -- which is how a check gets switched off.
    POINT_DRAWERS = {"scatter_fit", "trend_band"}
    #: Drawers whose marks ARE the aggregated values, so the drawn geometry can be compared to the
    #: data the panel carries. Adding these two covers 34 of the 94 tasks that were unverified --
    #: `grouped_measures` (18 pool tasks) and `distribution_comparison` (16).
    BAR_DRAWERS = {"grouped_bars", "bar_with_errors"}
    BOX_DRAWERS = {"boxplot"}
    #: A histogram is the drawer behind `faceted_distribution`'s per-level panels, which accounted
    #: for 15 of the pool's unverified tasks.
    HIST_DRAWERS = {"histogram"}
    #: A radial profile draws a closed polygon with one vertex per angular level.
    RADIAL_DRAWERS = {"polar_profile"}
    for i, (panel, ax) in enumerate(zip(ctx.panels, fig.axes)):
        if panel.draw in BAR_DRAWERS:
            kw = dict(panel.kwargs)
            res = semantics.check_bar_heights(ax, panel.data, x=kw.get("x"),
                                              ycols=kw.get("ycols") or [])
            for f in res["findings"]:
                ctx.findings.append({"check": f"semantics.{f['check']}",
                                     "detail": f["detail"], "severity": "hard"})
            continue
        if panel.draw in RADIAL_DRAWERS:
            kw = dict(panel.kwargs)
            res = semantics.check_radial_profile(ax, panel.data, theta=kw.get("theta"),
                                                 value=kw.get("value"))
            for f in res["findings"]:
                ctx.findings.append({"check": f"semantics.{f['check']}",
                                     "detail": f["detail"], "severity": "hard"})
            continue
        if panel.draw in HIST_DRAWERS:
            kw = dict(panel.kwargs)
            res = semantics.check_histogram(ax, panel.data, value=kw.get("value"),
                                            bins=int(kw.get("bins") or 20),
                                            density=bool(kw.get("density", True)),
                                            group=kw.get("group"))
            for f in res["findings"]:
                ctx.findings.append({"check": f"semantics.{f['check']}",
                                     "detail": f["detail"], "severity": "hard"})
            continue
        if panel.draw in BOX_DRAWERS:
            kw = dict(panel.kwargs)
            res = semantics.check_box_positions(ax, panel.data, value=kw.get("value"),
                                                group=kw.get("group"))
            for f in res["findings"]:
                ctx.findings.append({"check": f"semantics.{f['check']}",
                                     "detail": f["detail"], "severity": "hard"})
            continue
        if panel.draw not in POINT_DRAWERS:
            # A mesh drawer cannot be checked from the rendered file at all, and saying so with the
            # REASON is different from "we have not written the rule yet". The trace records which.
            why = semantics.mesh_unverifiable(panel.draw)
            if why:
                # THE PDF CANNOT BE READ, BUT THE DATA CAN. The mesh panel carries the frame the
                # drawer was handed, so the operator's data pass-through is still checkable -- and
                # that is where a mesh pipeline actually breaks (a silent truncation, a dropped
                # column). A truncation the operator DECLARED is reported; one nobody declared is a
                # finding.
                kw = dict(panel.kwargs)
                # THE OPERATOR SAYS WHEN IT PIVOTED, in the trace it already writes. Reading that
                # is honest; inventing an attribute nothing sets would be a check that is silently
                # always-false.
                pivoted = any("matrix.pivot" in t for t in ctx.trace)
                res = semantics.check_mesh_panel_data(panel.data, ctx.data,
                                                      max_rows=kw.get("max_rows"),
                                                      pivoted=pivoted)
                for f in res["findings"]:
                    ctx.findings.append({"check": f"semantics.{f['check']}",
                                         "detail": f["detail"], "severity": "hard"})
                # THE COLOUR SCALE IS THE ONE NUMERIC CLAIM A MESH FIGURE MAKES. Its tick labels
                # are text, so the rendered file can be held to them even though the cell values
                # cannot be read back. Without this the figure is `unverifiable` in every respect;
                # with it, one claim is checked and the trace says so.
                #
                # ONLY A DRAWER THAT DRAWS A COLOUR BAR CAN BE CHECKED THIS WAY. `field_2d` gets
                # one from `encode.field`; `tile_diverging` does not, and on the pool 9 of its tasks
                # were flagged because their AXIS tick labels landed near the right edge and looked
                # like a scale. Asking the drawer is exact; more geometric heuristics are not.
                # THE CALLER KNOWS; THE CHECK DOES NOT HAVE TO GUESS. `panel.colorbar` is the flag
                # that produced the bar. Reading word positions to decide whether a bar exists is a
                # heuristic standing in for a fact, and it produced false positives: a matrix's
                # column of cell annotations is a monotone vertical stack at the right edge, which
                # is geometrically indistinguishable from a bar.
                if panel.draw in DRAWERS_WITH_COLORBAR and panel.colorbar:
                    # THE DRAWN VALUES, NOT THE CALLER'S FRAME. `ax_field_2d` and `ax_tile_diverging`
                    # both pivot and aggregate, so the colour range covers CELL VALUES. The drawer
                    # records what it plotted on the axes; without that the check compared the
                    # scale to the RAW range and reported a violation on every aggregating task.
                    drawn_arr = _drawn_values(fig, panel)
                    # WHICH COLUMN CARRIES THE COLOUR. `encode.field` names it `value`;
                    # `encode.matrix` records it in the pivot trace. Guessing the widest numeric
                    # column read a COORDINATE as the value and reported a 29% shortfall on a
                    # correct figure.
                    scale = semantics.check_mesh_scale(
                        pdf_path, ctx.data, value=_value_column(ctx, kw),
                        drawn=(drawn_arr if drawn_arr is not None else panel.data))
                else:
                    scale = {"ok": None, "state": "unverifiable",
                             "why": f"{panel.draw} draws no colour bar, so no scale is claimed"}
                if scale.get("state") == "violation":
                    ctx.findings.append({
                        "check": "semantics.mesh_scale",
                        "detail": (f"panel {i} ({panel.draw}): the printed colour scale does not "
                                   f"cover the data it drew -- {scale.get('detail')}"),
                        "severity": "hard"})
                scale_note = (f"; scale check: {scale['state']}"
                              + (f" ({scale.get('detail')})" if scale.get("detail") else ""))
                ctx.trace.append(
                    f"verify.semantics(mesh panel {i}: {panel.draw} -- {why}; "
                    f"data-level check: {res['note']}{scale_note})")
            else:
                ctx.trace.append(f"verify.semantics(skip panel {i}: {panel.draw})")
            continue
        kw = dict(panel.kwargs)
        x, y = kw.get("x"), kw.get("y")
        if not x or not y or x not in panel.data.columns or y not in panel.data.columns:
            ctx.trace.append(f"verify.semantics(skip panel {i}: no x/y pair)")
            continue
        texts = [t.get_text() for t in ax.texts]
        res = semantics.verify_panel(ax, panel.data, x=x, y=y, texts=texts,
                                     mark_kind="points")
        for f in res["findings"]:
            ctx.findings.append({"check": f"semantics.{f['check']}",
                                 "detail": f["detail"], "severity": "hard"})
    ctx.trace.append("verify.semantics")


@operator("verify.statistics", "verify")
def op_verify_statistics(ctx: SkillContext, fig, pdf_path,
                         published: dict | None = None, computed: dict | None = None,
                         tolerance: float = 0.01):
    """Reconcile reproduced statistics against the published values."""
    if not published or not computed:
        ctx.trace.append("verify.statistics(skipped: no values)")
        return
    worst = 0.0
    for k, v in published.items():
        if isinstance(v, dict) or computed.get(k) is None:
            continue
        worst = max(worst, abs(float(computed[k]) - float(v)))
    ctx.findings.append({"check": "statistics",
                         "detail": f"worst |delta| = {worst:.4f}",
                         "severity": "hard" if worst > tolerance else "ok"})
    ctx.trace.append("verify.statistics")


#: The global skill: every recipe inherits these checks, whether it lists them or not.
GLOBAL_VERIFY = ("verify.audit", "verify.collisions", "verify.semantics")


# --------------------------------------------------------------------------------------
# Skills
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    build: tuple[tuple[str, dict], ...]
    required: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()
    examples: tuple[dict, ...] = ()
    verify: tuple[tuple[str, dict], ...] = ()
    version: int = 1

    def to_dict(self) -> dict:
        return {"name": self.name, "version": self.version,
                "description": self.description,
                "required": list(self.required), "optional": list(self.optional),
                "build": [{"operator": op, "params": p} for op, p in self.build],
                "verify": [{"operator": op, "params": p} for op, p in self.verify],
                "global_checks": list(GLOBAL_VERIFY),
                "examples": list(self.examples)}


SKILLS: dict[str, Skill] = {}


def define(skill: Skill) -> Skill:
    if skill.name in SKILLS:
        raise ValueError(f"duplicate skill {skill.name!r}")
    for op_name, _ in skill.build + skill.verify:
        if op_name not in OPERATORS:
            raise ValueError(f"skill {skill.name!r} uses unknown operator {op_name!r}")
    SKILLS[skill.name] = skill
    return skill


def _params_for(fn, supplied: dict) -> dict:
    """Only pass parameters the operator actually accepts; report what was consumed.

    An operator with **kwargs receives the remaining skill parameters: that is how
    `layout.facets` forwards `value`/`bins`/`group` to the encoder it repeats per facet.
    """
    sig = inspect.signature(fn)
    names = [p.name for p in sig.parameters.values()
             if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
    has_var_kw = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
    if has_var_kw:
        skip = {"published", "computed"}
        return {k: v for k, v in supplied.items() if k not in skip}
    return {k: v for k, v in supplied.items() if k in names}


def run(name: str, data: pd.DataFrame, out_stem=None, **params):
    """Execute a skill: build operators -> figure -> global + skill verification.

    Every provided parameter must be understood by at least one operator, or the call fails:
    a skill that silently ignores a request is worse than one that refuses it.
    """
    if name not in SKILLS:
        raise SkillError(f"unknown skill {name!r}; available: {sorted(SKILLS)}")
    skill = SKILLS[name]
    unknown = set(params) - set(skill.required) - set(skill.optional) - {"profile"}
    if unknown:
        raise SkillError(f"skill {name!r} does not understand parameters {sorted(unknown)}; "
                         f"required={list(skill.required)}, optional={list(skill.optional)}")
    missing = [k for k in skill.required if k not in params]
    if missing:
        raise SkillError(f"skill {name!r} requires {missing}")
    ctx = SkillContext(data=data, params=dict(params))
    consumed: set[str] = set()

    for op_name, defaults in skill.build:
        merged = {**defaults, **params}
        fn = OPERATORS[op_name].fn
        used = _params_for(fn, merged)
        consumed.update(used)
        fn(ctx, **used)
    if not ctx.panels:
        raise SkillError(f"skill {name!r} produced no panels; check its build steps")
    # a profile is a GLOBAL optional parameter: any skill can be rendered in a measured
    # reference style, which is what the style-transfer benchmark asks for.
    if params.get("profile") and ctx.reference is None:
        op_style_profile(ctx, profile=params["profile"])
    if ctx.reference is not None:
        if "height_mm" not in params:
            # a reference style's aspect is the point of style transfer; a skill's default
            # height must not silently win over it when the caller did not ask for one.
            # The height depends on the COLUMN WIDTH the skill draws at: deriving it from a
            # hard-coded 183 mm while drawing at 89 mm doubles the aspect error.
            ctx.layout["height_mm"] = styleprofile.style_from_profile(
                ctx.reference, columns=ctx.layout["columns"])["height_mm"]
        pal = styleprofile.style_from_profile(ctx.reference)["palette"]
        if pal:
            for p in ctx.panels:
                if "palette" in p.kwargs:
                    p.kwargs["palette"] = pal

    stem = pathlib.Path(out_stem) if out_stem else (
        ROOT / "templates" / "skills" / name)
    stem.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig = grammar.plate(ctx.panels, columns=ctx.layout["columns"],
                            height_mm=ctx.layout["height_mm"],
                            sharex=ctx.layout["sharex"], sharey=ctx.layout["sharey"],
                            letters=ctx.layout["letters"], margins=ctx.layout["margins"],
                            rc=ctx.rc)
        paths = layout.save(fig, stem)
        pdf = pathlib.Path(paths[0])
        verify_names = list(GLOBAL_VERIFY)
        for op_name, _ in skill.verify:
            if op_name not in verify_names:
                verify_names.append(op_name)
        for op_name in verify_names:
            fn = OPERATORS[op_name].fn
            used = _params_for(fn, {**params, "published": params.get("published"),
                                    "computed": params.get("computed")})
            if op_name in ("verify.audit", "verify.collisions", "verify.semantics"):
                fn(ctx, fig, pdf)
            else:
                fn(ctx, fig, pdf, **used)
        hard = [f for f in ctx.findings if f["severity"] == "hard"]
        return {"skill": skill.name, "version": skill.version,
                "panels": len(ctx.panels), "pdf": str(pdf), "png": str(paths[1]),
                "findings": ctx.findings, "hard_failures": len(hard),
                "trace": ctx.trace, "layout": dict(ctx.layout),
                "consumed_params": sorted(consumed)}
    finally:
        pass


def catalogue() -> dict:
    """The vocabulary as data: skills, operators, contracts. Written to knowledge/."""
    return {
        "about": "Global skill floor + classic operators + named recipes for scientific figures.",
        "global_verify": list(GLOBAL_VERIFY),
        "operators": [{"name": o.name, "kind": o.kind, "doc": o.doc}
                      for o in OPERATORS.values()],
        "skills": [s.to_dict() for s in SKILLS.values()],
    }


def export_catalogue(path=None) -> pathlib.Path:
    p = pathlib.Path(path or ROOT / "knowledge" / "skills_catalog.json")
    p.write_text(json.dumps(catalogue(), indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8")
    return p


# --------------------------------------------------------------------------------------
# The global skill floor and the classic recipes
# --------------------------------------------------------------------------------------

_SKILLS = [
    Skill(
        name="trend_with_uncertainty",
        description="A measured trend: points, optional interval, fit, reference line, r.",
        build=(("encode.trend", {}), ("layout.plate", {})),
        required=("x", "y"),
        optional=("lo", "hi", "fit", "band", "reference", "series", "title",
                  "xlabel", "ylabel", "columns", "height_mm", "published", "computed"),
        examples=({"x": "year", "y": "mean"},),
        verify=(("verify.statistics", {}),),
    ),
    Skill(
        name="ranked_composition",
        description="Ranked composition: sorted bars with the value printed on each bar.",
        build=(("encode.ranked", {}), ("layout.plate", {"height_mm": 100.0,
                                                        "margins": {"bottom": 26.0}})),
        required=("label", "value"),
        optional=("top", "percent", "xtick_rotation", "xlabel", "ylabel", "columns",
                  "height_mm"),
        examples=({"label": "country", "value": "share", "percent": True},),
        verify=(),
    ),
    Skill(
        name="density_relationship",
        description="A dense relationship on log axes: hexbin, marginals, colour bar.",
        build=(("encode.density", {}), ("layout.plate", {"height_mm": 96.0,
                                                         "margins": {"top": 17.0}})),
        required=("x", "y"),
        optional=("marginals", "colorbar", "gridsize", "columns", "height_mm"),
        examples=({"x": "papers", "y": "cites", "marginals": "top"},),
        verify=(),
    ),
    Skill(
        name="distribution_comparison",
        description="Compare distributions across categories with box plots.",
        build=(("encode.box", {}), ("layout.plate", {"height_mm": 70.0})),
        required=("group", "value"),
        optional=("columns", "height_mm"),
        examples=({"group": "condition", "value": "score"},),
        verify=(),
    ),
    Skill(
        name="grouped_measures",
        description="Parallel measures per category as grouped bars.",
        build=(("encode.bars", {}), ("layout.plate", {"height_mm": 90.0})),
        required=("x", "ycols"),
        optional=("columns", "height_mm"),
        examples=({"x": "model", "ycols": ["accuracy", "f1"]},),
        verify=(),
    ),
    Skill(
        name="matrix_plate",
        description="A signed numeric matrix as tiles with a colour bar.",
        build=(("encode.matrix", {}), ("layout.plate", {"columns": 1.0,
                                                        "height_mm": 90.0})),
        required=(),
        optional=("columns", "colorbar", "height_mm", "max_rows"),
        examples=({},),
        verify=(),
    ),
    Skill(
        name="styled_trend",
        description="A trend rendered in the measured style of a reference figure.",
        build=(("style.profile", {}), ("encode.trend", {}), ("layout.plate", {})),
        required=("x", "y", "profile"),
        optional=("lo", "hi", "fit", "band", "reference", "columns", "height_mm",
                  "published", "computed"),
        examples=({"x": "year", "y": "mean", "profile": "corpus/style/published_fig7.json"},),
        verify=(("verify.statistics", {}),),
    ),
    Skill(
        name="histogram",
        description="Distribution of one measure, optionally split by a category.",
        build=(("encode.hist", {}), ("layout.plate", {"height_mm": 70.0})),
        required=("value",),
        optional=("bins", "group", "density", "columns", "height_mm"),
        examples=({"value": "score", "bins": 25},),
        verify=(),
    ),
    Skill(
        name="dual_measure",
        description="Two measures on one x with separate, labelled y axes.",
        build=(("encode.dual", {}), ("layout.plate", {"height_mm": 70.0})),
        required=("x", "y1", "y2"),
        optional=("ylabel", "ylabel2", "columns", "height_mm"),
        examples=({"x": "year", "y1": "temperature", "y2": "precipitation"},),
        verify=(),
    ),
    Skill(
        name="scatter_relationship",
        description="A relationship: scatter with an OLS fit and r stated in the panel.",
        build=(("encode.scatter", {}), ("layout.plate", {"height_mm": 70.0})),
        required=("x", "y"),
        optional=("columns", "height_mm"),
        examples=({"x": "papers", "y": "citations"},),
        verify=(),
    ),
    Skill(
        name="log_scatter",
        description="A relationship on log axes: scatter after axis.log.",
        build=(("axis.log", {}), ("encode.scatter", {}), ("layout.plate", {"height_mm": 70.0})),
        required=("x", "y"),
        optional=("which", "columns", "height_mm"),
        examples=({"x": "papers", "y": "citations", "which": "xy"},),
        verify=(),
    ),
    Skill(
        name="error_comparison",
        description="A few entities compared with their uncertainty, as bars with error bars.",
        build=(("encode.error_bars", {}), ("layout.plate", {"height_mm": 90.0})),
        required=("x", "y"),
        optional=("err", "title", "xtick_rotation", "columns", "height_mm"),
        examples=({"x": "model", "y": "estimate", "err": "se"},),
        verify=(),
    ),
    Skill(
        name="composite_groups",
        description="One panel per level of a grouping column, drawn from a long table.",
        build=(("layout.split_panels", {}), ("layout.plate", {"height_mm": 140.0})),
        required=("by", "x", "y"),
        optional=("err", "columns", "height_mm", "max_panels", "max_bars",
                  "xtick_rotation"),
        examples=({"by": "panel_group", "x": "outcome_name", "y": "estimate",
                   "err": "se"},),
        verify=(),
    ),
    Skill(
        name="field_map",
        description="A scalar field over a 2-D coordinate grid, as a colour field with an "
                    "optional contour overlay.",
        build=(("encode.field", {}), ("layout.plate", {"columns": 1.0, "height_mm": 100.0})),
        required=("x", "y", "value"),
        optional=("contour", "cbar_label", "cmap", "columns", "height_mm"),
        examples=({"x": "position_mm", "y": "elapsed_time_min",
                   "value": "concentration"},),
        verify=(),
    ),
    Skill(
        name="radial_profile",
        description="A radial profile: one measured value per angle, drawn on a polar axis.",
        build=(("encode.polar", {}), ("layout.plate", {"columns": 1.0, "height_mm": 70.0})),
        required=("theta", "value"),
        optional=("line", "columns", "height_mm"),
        examples=({"theta": "direction", "value": "speed"},),
        verify=(),
    ),
    Skill(
        name="faceted_distribution",
        description="One classic encoder repeated over a facet column: hist, trend or scatter.",
        build=(("layout.facets", {"of": "hist"}), ("layout.plate", {"height_mm": 130.0})),
        # `of` selects hist / trend / scatter. trend and scatter REQUIRE x and y, so those must be
        # declared here or a caller asking for a faceted trend is refused for passing exactly the
        # parameters the recipe demands.
        # `value` is required for of="hist"; trend/scatter need x and y instead. A flat tuple
        # cannot say "one of these", so both shapes are accepted here and the OPERATOR enforces
        # the real condition (`_first_numeric` / `_second_numeric` raise with a clear reason).
        required=("by",),
        optional=("value", "bins", "group", "columns", "height_mm", "of", "max_panels", "x", "y"),
        examples=({"value": "score", "by": "condition"},
                  {"value": "response", "by": "condition", "of": "trend", "x": "time", "y": "response"}),
        verify=(),
    ),
]

for _s in _SKILLS:
    define(_s)


if __name__ == "__main__":
    print(json.dumps(catalogue(), indent=2, ensure_ascii=False))
