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
                     colorbar: bool = True):
    """Encode a numeric matrix (all numeric columns, or a comma list) as signed tiles."""
    if columns:
        cols = [c.strip() for c in columns.split(",") if c.strip()]
        data = ctx.data[cols]
    else:
        data = ctx.data.select_dtypes("number")
    if data.shape[1] < 2 or data.shape[0] < 2:
        raise SkillError("encode.matrix needs at least 2x2 numeric data")
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


@operator("encode.scatter", "build")
def op_encode_scatter(ctx: SkillContext, x: str, y: str,
                      xlabel: str | None = None, ylabel: str | None = None):
    """Encode a relationship as a scatter with a fit and r."""
    ctx.add_panel(composite.Panel("scatter_fit", ctx.data,
                                  {"x": x, "y": y, "xlabel": xlabel or "",
                                   "ylabel": ylabel or ""}))
    ctx.trace.append(f"encode.scatter({x},{y})")


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
        call = {"hist": dict(value=value or _first_numeric(ctx),
                             bins=bins, group=group),
                "trend": dict(x=x or _first_numeric(ctx), y=y or _second_numeric(ctx)),
                "scatter": dict(x=x or _first_numeric(ctx), y=y or _second_numeric(ctx))}[of]
        if of == "hist" and title:
            call["title"] = level
        elif of == "trend" and title:
            call["title"] = level
        enc(child, **{k: v for k, v in call.items() if v is not None})
        ctx.panels.extend(child.panels)
    ctx.layout["columns"] = columns
    ctx.meta["facets"] = {"by": by, "levels": levels}
    ctx.trace.append(f"layout.facets({by}:{len(levels)})")


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


@operator("layout.split_panels", "build")
def op_layout_split_panels(ctx: SkillContext, by: str, of: str = "error_bars",
                           x: str | None = None, y: str | None = None,
                           err: str | None = None, columns: float = 2.0,
                           max_panels: int = 4, max_rows: int = 200,
                           xtick_rotation: float = 30.0, **kwargs):
    """Build one panel per level of a grouping column from a long table.

    This is the operator behind benchmark "Composite" tasks: a single table carries several
    sub-figures distinguished by a group column (panel_group / panel_block), and the honest
    reading is one panel per group. More levels than `max_panels` is an error, because silently
    dropping a panel changes what the figure claims.
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
        child = SkillContext(data=sub, params=dict(ctx.params), layout=dict(ctx.layout),
                             meta=dict(ctx.meta), rc=ctx.rc)
        op_encode_error_bars(child, x=label, y=y or _first_numeric(child),
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
    ctx.add_panel(composite.Panel("field_2d", ctx.data,
                                  {"x": x, "y": y, "value": value,
                                   "contour": contour, "cmap": cmap,
                                   "cbar_label": cbar_label}))
    ctx.trace.append(f"encode.field({x},{y},{value})")


@operator("encode.polar", "build")
def op_encode_polar(ctx: SkillContext, theta: str, value: str,
                    line: bool = True, title: str | None = None):
    """Encode a radial profile: one value per angle (category or degrees)."""
    ctx.add_panel(composite.Panel("polar_profile", ctx.data,
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
    for i, (panel, ax) in enumerate(zip(ctx.panels, fig.axes)):
        if panel.draw not in POINT_DRAWERS:
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
        optional=("columns", "colorbar", "height_mm"),
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
        optional=("err", "columns", "height_mm", "max_panels", "xtick_rotation"),
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
        description="The same distribution encoder repeated over a facet column.",
        build=(("layout.facets", {"of": "hist"}), ("layout.plate", {"height_mm": 130.0})),
        required=("value", "by"),
        optional=("bins", "group", "columns", "height_mm", "of", "max_panels"),
        examples=({"value": "score", "by": "condition"},),
        verify=(),
    ),
]

for _s in _SKILLS:
    define(_s)


if __name__ == "__main__":
    print(json.dumps(catalogue(), indent=2, ensure_ascii=False))
