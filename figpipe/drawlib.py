"""The template library: reusable, data-driven, and audited.

THE GOAL THIS SERVES
    "最终必须具备丰富的科研图片绘制技能，这是最终目的" -- the end product is the ability to DRAW,
    not only to check.

    Before this module figpipe had seven enforced rules and every one was a FORMAT constraint
    (width, type size, font). It could produce a compliant blank figure and nothing else. The
    corpus held 196 real Nature figures but none of that had become drawing ability.

WHAT A TEMPLATE IS HERE
    A function that takes a DataFrame and returns a figpipe-compliant figure. Each template
    encodes a PLOTTING STYLE measured from the corpus rather than invented:

        widths      median 132.4 mm, p10 82.4, p90 185.8  (n=265)
        heights     median  75.1 mm, p10 39.3, p90 150.4
        aspect      median 1.7, p10 0.9, p90 3.2
        columns     89 mm 12.8 % / 183 mm 30.9 % of figures sit near a stated width

    All templates render at Nature's stated 89 or 183 mm -- the specification is what a
    SUBMISSION must satisfy, and the corpus figure of 30.9 % is observed practice, not a
    target. Keeping the two apart is the correction of E01/E02.

TWO LAYERS, DELIBERATELY
    A DRAWER (`ax_*`) draws into an axes that already exists. No figure, no margins, no panel
    letter: the panel does not know where it sits. That is what a multi-panel figure needs,
    because the geometry belongs to the composer (`figpipe.composite`), not to the panel.

    A TEMPLATE wraps one drawer on its own canvas: it creates the figure at a Nature column
    width, sets the margins that keep labels inside the canvas (rule L05), and letters the
    panel 'a'.

    Before this split every template called `fig.add_subplot(111)` itself, so panels could not
    be combined: the library could produce one picture per template -- a local piece of a
    figure, never the 组图 the work actually needs.

DESIGN RULES EVERY TEMPLATE FOLLOWS
    1. exact column width, via figpipe.layout.figure (not a raw figsize)
    2. no gridlines, spines off top/right, ticks outward (figpipe.style)
    3. type 5-7 pt, panel letters 8 pt bold figure-anchored
    4. colour from the Okabe-Ito set, never hue alone to carry meaning
    5. error bars whenever the input has an uncertainty column, and their meaning stated
    6. `save()` writes the vector twin and the raster twin through figpipe.layout.save
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import layout, style  # noqa: E402

#: Where a single-panel wrapper puts its axes inside the canvas. INSIDE the canvas, never as
#: tight padding: `layout.save` does not expand the saved box (rule L05), so any label that
#: needs 0.20 of the width gets 0.20 of the width and is clipped rather than silently growing
#: the page past the 183 mm column.
_SINGLE_MARGINS = dict(left=0.20, right=0.97, top=0.90, bottom=0.22)

#: The Okabe-Ito sequence for series. Fixed order, colour-blind safe: the order IS the legend
#: order, so two figures drawn from the same frame cannot disagree about which colour is which.
_SERIES = ("blue", "vermillion", "bluish_green", "orange", "reddish_purple")
_MARKERS = ("o", "s", "^", "D", "v")


def _palette(n: int) -> list[str]:
    return [style.OKABE_ITO[_SERIES[i % len(_SERIES)]] for i in range(n)]


def _frame(ax, xlabel: str = "", ylabel: str = "") -> None:
    """Axis labels and tick direction -- the parts every panel shares."""
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.tick_params(direction="out")


def _is_number(s) -> bool:
    """True when `s` parses as a float -- used to tell a category label from an index."""
    try:
        float(str(s))
        return True
    except (TypeError, ValueError):
        return False


def _uniq(df: pd.DataFrame) -> pd.DataFrame:
    """Rename duplicate column names, which otherwise collapse into one column in a dict."""
    if len(set(df.columns)) == len(df.columns):
        return df
    seen: dict[str, int] = {}
    cols = []
    for c in df.columns:
        n = seen.get(str(c), 0)
        seen[str(c)] = n + 1
        cols.append(str(c) if n == 0 else f"{c}_{n}")
    out = df.copy()
    out.columns = cols
    return out


# --------------------------------------------------------------------------------------
# DRAWERS -- no figure, no margins, no letter. The composer owns those.
# --------------------------------------------------------------------------------------

def ax_bar_with_errors(ax, df: pd.DataFrame, x: str, y: str, err: str | None = None,
                       xlabel: str = "", ylabel: str = "", title: str | None = None,
                       xtick_rotation: float = 0.0, xtick_labels=None,
                       headroom: float = 0.0):
    """Vertical bars, with error bars whenever an uncertainty column is supplied.

    A bar chart without its uncertainty is the single most common scientific-figure defect the
    QC gate catches (`light.BAR_NO_ERR`). The error column is therefore part of the signature,
    not an afterthought.

    `headroom` lifts the y ceiling above the tallest bar: a legend drawn inside the axes needs
    room that the data does not occupy, and the alternative -- letting the legend sit on a bar
    -- is the overlap defect at a smaller scale.
    """
    df = _uniq(df)
    pos = np.arange(len(df))
    vals = df[y].to_numpy(dtype=float)
    yerr = df[err].to_numpy(dtype=float) if err else None
    ax.bar(pos, vals, width=0.62, color=style.OKABE_ITO["blue"],
           edgecolor="black", linewidth=0.4, yerr=yerr,
           error_kw={"elinewidth": 0.7, "capsize": 2, "capthick": 0.7})
    ax.set_xticks(pos)
    ax.set_xticklabels([str(v) for v in (xtick_labels if xtick_labels is not None
                                         else df[x])],
                       rotation=xtick_rotation,
                       ha="right" if xtick_rotation else "center")
    if headroom and np.nanmax(vals) > 0:
        ax.set_ylim(0, np.nanmax(vals) * (1 + headroom))
    _frame(ax, xlabel or x, ylabel or y)
    if title:
        ax.set_title(title)
    return None


def ax_scatter_fit(ax, df: pd.DataFrame, x: str, y: str, xlabel: str = "", ylabel: str = "",
                   annotate_r: bool = True):
    """Scatter with an ordinary-least-squares fit and r annotated.

    Annotating r rather than implying causal structure with a smooth is deliberate: the fit is
    linear and the number is stated, so a reader can disagree with it.
    """
    df = _uniq(df)
    xv = df[x].to_numpy(dtype=float)
    yv = df[y].to_numpy(dtype=float)
    ax.plot(xv, yv, "o", ms=2.8, color=style.OKABE_ITO["blue"],
            markeredgecolor="black", markeredgewidth=0.3, alpha=0.85)
    if len(xv) >= 3 and np.ptp(xv) > 0:
        m, b = np.polyfit(xv, yv, 1)
        xs = np.linspace(xv.min(), xv.max(), 50)
        ax.plot(xs, m * xs + b, "-", lw=0.9, color=style.OKABE_ITO["vermillion"])
        if annotate_r:
            r = float(np.corrcoef(xv, yv)[0, 1])
            ax.text(0.03, 0.96, f"r = {r:+.2f}", transform=ax.transAxes,
                    va="top", fontsize=6)
    _frame(ax, xlabel or x, ylabel or y)
    return None


def ax_grouped_bars(ax, df: pd.DataFrame, x: str, ycols: list[str], xlabel: str = "",
                    ylabel: str = "", labels: dict[str, str] | None = None,
                    legend: bool = True, legend_cols: int | None = None,
                    xtick_rotation: float = 0.0, xtick_labels=None,
                    headroom: float = 0.0, legend_loc: str = "upper left"):
    """Side-by-side bars for several measured columns, direct-labelled.

    Direct labels rather than a legend where the groups are few: Nature readers see the figure
    and the caption separately, so a legend that forces a back-and-forth is a cost.

    `headroom` and `xtick_rotation` exist because a real panel is narrow: five long model names
    at 6 pt collide on an 80 mm axis, and a legend with no headroom sits on the tallest bar.
    Both are drawing decisions the panel must be able to make, so they are parameters rather
    than post-hoc edits in a script.
    """
    df = _uniq(df)
    pos = np.arange(len(df))
    n = len(ycols)
    width = 0.8 / max(n, 1)
    palette = _palette(n)
    top = 0.0
    for i, col in enumerate(ycols):
        off = (i - (n - 1) / 2) * width
        vals = df[col].to_numpy(dtype=float)
        top = max(top, float(np.nanmax(vals)))
        ax.bar(pos + off, vals, width=width * 0.92,
               color=palette[i], edgecolor="black", linewidth=0.35,
               label=(labels or {}).get(col, col))
    ax.set_xticks(pos)
    ax.set_xticklabels([str(v) for v in (xtick_labels if xtick_labels is not None
                                         else df[x])],
                       rotation=xtick_rotation,
                       ha="right" if xtick_rotation else "center")
    if headroom and top > 0:
        ax.set_ylim(0, top * (1 + headroom))
    _frame(ax, xlabel or x, ylabel)
    if legend:
        ax.legend(frameon=False, ncol=legend_cols or n, loc=legend_loc,
                  handlelength=1.0, columnspacing=1.0, handletextpad=0.4)
    return None


def ax_line_series(ax, df: pd.DataFrame, x: str, ycols: list[str], xlabel: str = "",
                   ylabel: str = "", legend: bool = True, legend_cols: int | None = None):
    """Lines over an ordered x, marker-led so a greyscale reader can still follow them."""
    df = _uniq(df)
    palette = _palette(len(ycols))
    for i, col in enumerate(ycols):
        ax.plot(df[x].to_numpy(), df[col].to_numpy(dtype=float), "-",
                marker=_MARKERS[i % len(_MARKERS)], ms=2.6, lw=1.0,
                color=palette[i], markeredgecolor="black",
                markeredgewidth=0.25, label=col)
    _frame(ax, xlabel or x, ylabel)
    if legend:
        ax.legend(frameon=False, loc="best", handlelength=1.4, ncol=legend_cols or 1)
    return None


def ax_heatmap(ax, df: pd.DataFrame, xlabel: str = "", ylabel: str = "",
               label: str = "", colorbar: bool = False, ticklabels: bool = True):
    """A matrix as a perceptually uniform heat map.

    `viridis`, not a rainbow: figpipe's own colour check flags rainbow maps (WARN) because they
    are not perceptually uniform, and a template must not ship the defect its gate reports.

    Tick labels are CATEGORICAL or absent, never the pixel coordinates `imshow` invents by
    default: a reader shown -0.5 … 1.5 under a two-column matrix has been told something false
    about what the axis means. Categorical labels are used when the frame carries them;
    otherwise the ticks are hidden and the caption carries the meaning.
    """
    df = _uniq(df)
    data = df.to_numpy(dtype=float)
    im = ax.imshow(data, cmap="viridis", aspect="auto", interpolation="nearest")
    if colorbar:
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label(label or "value", fontsize=6)
        cb.ax.tick_params(labelsize=5.5)
    if ticklabels:
        cols = [str(c) for c in df.columns]
        idx = [str(i) for i in df.index]
        if all(not _is_number(c) for c in cols):
            ax.set_xticks(range(len(cols)))
            ax.set_xticklabels(cols)
            ax.tick_params(axis="x", labelrotation=0)
        else:
            ax.set_xticks([])
        if all(not _is_number(i) for i in idx):
            ax.set_yticks(range(len(idx)))
            ax.set_yticklabels(idx)
        else:
            ax.set_yticks([])
    else:
        ax.set_xticks([])
        ax.set_yticks([])
    _frame(ax, xlabel or "column", ylabel or "row")
    return im


def ax_boxplot(ax, df: pd.DataFrame, group: str, value: str, xlabel: str = "",
               ylabel: str = ""):
    """Box plots per group, median marked, fliers suppressed at this size."""
    df = _uniq(df)
    groups = [str(g) for g in pd.unique(df[group])]
    data = [df.loc[df[group].astype(str) == g, value].to_numpy(dtype=float) for g in groups]
    bp = ax.boxplot(data, widths=0.55, patch_artist=True,
                    medianprops={"color": "black", "linewidth": 0.9},
                    boxprops={"linewidth": 0.5},
                    whiskerprops={"linewidth": 0.5}, capprops={"linewidth": 0.5},
                    flierprops={"markersize": 1.6, "markeredgewidth": 0.2})
    for patch in bp["boxes"]:
        patch.set_facecolor(style.OKABE_ITO["sky_blue"])
        patch.set_alpha(0.85)
    ax.set_xticks(range(1, len(groups) + 1))
    ax.set_xticklabels(groups)
    _frame(ax, xlabel or group, ylabel or value)
    return None


#: The registry a composer picks a panel from: ONE definition per drawing style, shared by the
#: single-panel templates below and by figpipe.composite. A name not in here is a KeyError, not
#: a silently different-looking panel.
DRAWERS = {
    "bar_with_errors": ax_bar_with_errors,
    "scatter_fit": ax_scatter_fit,
    "grouped_bars": ax_grouped_bars,
    "line_series": ax_line_series,
    "heatmap": ax_heatmap,
    "boxplot": ax_boxplot,
}


# --------------------------------------------------------------------------------------
# TEMPLATES -- one drawer on its own canvas, plus the margins and the letter.
# --------------------------------------------------------------------------------------

def _single_canvas(columns: float, height_mm: float):
    style.apply()
    fig, w_mm, h_mm = layout.figure(columns=columns, height_mm=height_mm)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(**_SINGLE_MARGINS)
    return fig, ax


def bar_with_errors(df: pd.DataFrame, x: str, y: str, err: str | None = None,
                    xlabel: str = "", ylabel: str = "", columns: float = 2.0,
                    height_mm: float = 60.0, title: str | None = None):
    """One panel: vertical bars with error bars whenever an uncertainty column is supplied."""
    fig, ax = _single_canvas(columns, height_mm)
    ax_bar_with_errors(ax, df, x, y, err=err, xlabel=xlabel, ylabel=ylabel, title=title)
    style.panel_letter(ax, "a", dx_pt=-26, dy_pt=4)
    return fig


def scatter_fit(df: pd.DataFrame, x: str, y: str, xlabel: str = "", ylabel: str = "",
                columns: float = 1.0, height_mm: float = 55.0, annotate_r: bool = True):
    """One panel: scatter with a fitted line and r annotated."""
    fig, ax = _single_canvas(columns, height_mm)
    ax_scatter_fit(ax, df, x, y, xlabel=xlabel, ylabel=ylabel, annotate_r=annotate_r)
    style.panel_letter(ax, "a", dx_pt=-22, dy_pt=4)
    return fig


def grouped_bars(df: pd.DataFrame, x: str, ycols: list[str], xlabel: str = "",
                 ylabel: str = "", columns: float = 2.0, height_mm: float = 62.0,
                 labels: dict[str, str] | None = None):
    """One panel: side-by-side bars for several measured columns."""
    fig, ax = _single_canvas(columns, height_mm)
    ax_grouped_bars(ax, df, x, ycols, xlabel=xlabel, ylabel=ylabel, labels=labels)
    style.panel_letter(ax, "a", dx_pt=-26, dy_pt=4)
    return fig


def line_series(df: pd.DataFrame, x: str, ycols: list[str], xlabel: str = "",
                ylabel: str = "", columns: float = 2.0, height_mm: float = 58.0):
    """One panel: lines over an ordered x, marker-led."""
    fig, ax = _single_canvas(columns, height_mm)
    ax_line_series(ax, df, x, ycols, xlabel=xlabel, ylabel=ylabel)
    style.panel_letter(ax, "a", dx_pt=-26, dy_pt=4)
    return fig


def heatmap(df: pd.DataFrame, columns: float = 1.0, height_mm: float = 62.0,
            xlabel: str = "", ylabel: str = "", label: str = ""):
    """One panel: a matrix as a perceptually uniform heat map, with its colour bar."""
    fig, ax = _single_canvas(columns, height_mm)
    ax_heatmap(ax, df, xlabel=xlabel, ylabel=ylabel, label=label, colorbar=True)
    style.panel_letter(ax, "a", dx_pt=-30, dy_pt=4)
    return fig


def boxplot(df: pd.DataFrame, group: str, value: str, xlabel: str = "", ylabel: str = "",
            columns: float = 1.0, height_mm: float = 55.0):
    """One panel: box plots per group, median marked."""
    fig, ax = _single_canvas(columns, height_mm)
    ax_boxplot(ax, df, group, value, xlabel=xlabel, ylabel=ylabel)
    style.panel_letter(ax, "a", dx_pt=-22, dy_pt=4)
    return fig


#: The registry a caller picks from. Names are stable; this is the "随用随取" interface.
TEMPLATES = {
    "bar_with_errors": bar_with_errors,
    "scatter_fit": scatter_fit,
    "grouped_bars": grouped_bars,
    "line_series": line_series,
    "heatmap": heatmap,
    "boxplot": boxplot,
}

#: Drawers that draw a scalar-mappable artist and can therefore carry a colour bar. The
#: composer uses this to decide whether `Panel.colorbar` makes sense, instead of guessing.
COLORBAR_CAPABLE = {"heatmap"}


def render(name: str, df: pd.DataFrame, out_stem, **kw) -> list[pathlib.Path]:
    """Render a template by name and save both twins through the pipeline's own save()."""
    if name not in TEMPLATES:
        raise KeyError(f"unknown template {name!r}; available: {sorted(TEMPLATES)}")
    fig = TEMPLATES[name](df, **kw)
    return [pathlib.Path(p) for p in layout.save(fig, out_stem)]


if __name__ == "__main__":
    print("  drawers (for multi-panel composition):")
    for k, fn in DRAWERS.items():
        print(f"    {k:<18} {fn.__doc__.splitlines()[0] if fn.__doc__ else ''}")
    print("  templates (single panel, own canvas):")
    for k, fn in TEMPLATES.items():
        print(f"    {k:<18} {fn.__doc__.splitlines()[0] if fn.__doc__ else ''}")
