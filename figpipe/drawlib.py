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

import matplotlib.pyplot as plt  # noqa: E402  (after style, which selects the Agg backend)

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
    labels = [str(v) for v in (xtick_labels if xtick_labels is not None else df[x])]
    if len(labels) <= 24:
        ax.set_xticks(pos)
        ax.set_xticklabels(labels, rotation=xtick_rotation,
                           ha="right" if xtick_rotation else "center")
    else:
        # one tick per bar is unreadable past ~24 bars (and a numeric locator tries to draw
        # thousands); keep every BAR and thin only the LABELS, evenly spaced
        from matplotlib.ticker import MaxNLocator
        step = int(np.ceil(len(labels) / 12))
        ax.set_xticks(pos[::step])
        ax.set_xticklabels(labels[::step], rotation=xtick_rotation,
                           ha="right" if xtick_rotation else "center")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=12))
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
    raw_x = df[x].to_numpy(dtype=float)
    raw_y = df[y].to_numpy(dtype=float)
    ok = np.isfinite(raw_x) & np.isfinite(raw_y)
    xv, yv = raw_x[ok], raw_y[ok]
    ax.plot(xv, yv, "o", ms=2.8, color=style.OKABE_ITO["blue"],
            markeredgecolor="black", markeredgewidth=0.3, alpha=0.85)
    if len(xv) >= 3 and np.ptp(xv) > 0 and np.ptp(yv) > 0:
        try:
            xs = np.linspace(xv.min(), xv.max(), 50)
            gy, _ = _ols_fit(xv, yv, xs, 1)
            ax.plot(xs, gy, "-", lw=0.9, color=style.OKABE_ITO["vermillion"])
            if annotate_r:
                r = float(np.corrcoef(xv, yv)[0, 1])
                ax.text(0.03, 0.96, f"r = {r:+.2f}", transform=ax.transAxes,
                        va="top", fontsize=6)
        except (ValueError, np.linalg.LinAlgError):
            pass
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
               ylabel: str = "", color: str | None = None):
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
        patch.set_facecolor(color or style.OKABE_ITO["sky_blue"])
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
# THE IDIOMS OF THE SEED PAPER -- measured, then generalised
# --------------------------------------------------------------------------------------
# Five of the seven figures in the seed paper (GBM/NHB-2026 national influence) are built from
# ONE idiom: a yearly series drawn as points, a shaded uncertainty band, a fitted line and an
# explicit reference line, with the correlation stated in the panel corner. Two more are a
# ranked share bar and a log-log density hexbin. These are the recurring visual sentences; the
# drawers below carry them so a new paper is described as intents plus tidy data, not as a
# page of plotting calls.
#
# The numbers used here (band alpha, marker size, reference-line style) are the seed paper's
# own conventions, read off its figures and its R recipe, not invented.

#: Fits a trend panel may use. "lm" is the seed's line for the centrality panels, "poly3" its
#: cubic for the Gini panels, and "loess" stands in for ggplot2's loess, the seed's default for
#: the dyad panels. A name outside this tuple is a ValueError, never a quiet fallback.
FITS = ("lm", "poly3", "loess")


def _design(x: np.ndarray, x0: float, degree: int) -> np.ndarray:
    return np.vstack([(x - x0) ** k for k in range(degree + 1)]).T


def _ols_fit(x, y, x_grid, degree: int = 1):
    """OLS fit with the classical prediction standard error.

    x is centred and scaled before the fit: raw x values in the 1e9 range (epoch seconds,
    nanometres, years since a geological epoch) make the Vandermonde matrix ill-conditioned and
    np.linalg.lstsq raises "SVD did not converge" -- a benchmark task failed exactly this way.
    Non-finite pairs are dropped rather than poisoning the whole fit.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < degree + 2 or np.ptp(x) == 0:
        raise ValueError(f"cannot fit degree {degree} to {len(x)} usable points")
    xm = float(np.mean(x))
    xs = float(np.std(x)) or 1.0
    xn = (x - xm) / xs
    x_grid = (np.asarray(x_grid, dtype=float) - xm) / xs
    X = np.vstack([xn ** k for k in range(degree + 1)]).T
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = max(len(x) - X.shape[1], 1)
    sigma2 = float(resid @ resid) / dof
    Xg = np.vstack([x_grid ** k for k in range(degree + 1)]).T
    cov = sigma2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", Xg, cov, Xg), 0.0))
    return Xg @ beta, se


def _loess_fit(x, y, x_grid, frac: float = 0.75):
    """Local-linear smoother with an approximate standard error for the fitted mean.

    ggplot2's loess is what the seed's dyad panels use; matplotlib has no loess, so this is a
    tricube-weighted local linear fit at the same span. The band is an APPROXIMATION: the
    weighted-least-squares variance of the local mean with the global residual variance
    substituted, rather than loess's own pointwise variance. It is documented as one because a
    band that looks like loess's and is computed differently must not be presented as equal.
    """
    n = len(x)
    if n < 4:
        raise ValueError(f"loess needs at least 4 points, got {n}")
    h = max(np.quantile(np.abs(x - np.median(x)), min(frac, 1.0)), 1e-9)
    fitted = np.empty(n)
    for i, x0 in enumerate(x):
        d = np.abs(x - x0) / h
        w = np.where(d < 1, (1 - d ** 3) ** 3, 0.0)
        if w.sum() <= 0:
            fitted[i] = y[i]
            continue
        X = _design(x, x0, 1)
        W = np.diag(w)
        beta, *_ = np.linalg.lstsq(X.T @ W @ X, X.T @ W @ y, rcond=None)
        fitted[i] = beta[0]
    sigma2 = float(np.mean((y - fitted) ** 2)) if n > 2 else 1.0
    out = np.empty(len(x_grid))
    se = np.empty(len(x_grid))
    for i, x0 in enumerate(x_grid):
        d = np.abs(x - x0) / h
        w = np.where(d < 1, (1 - d ** 3) ** 3, 0.0)
        sw = w.sum()
        if sw <= 0:
            out[i], se[i] = np.nan, np.nan
            continue
        X = _design(x, x0, 1)
        W = np.diag(w)
        beta, *_ = np.linalg.lstsq(X.T @ W @ X, X.T @ W @ y, rcond=None)
        out[i] = beta[0]
        # variance of the local mean: sigma^2 * sum(w^2) / (sum w)^2, weighted N
        neff = sw ** 2 / max((w ** 2).sum(), 1e-12)
        se[i] = np.sqrt(sigma2 / max(neff, 1.0))
    return out, se


def _band_curve(x, y, kind: str, x_grid=None):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if kind not in FITS:
        raise ValueError(f"unknown fit {kind!r}; available: {FITS}")
    if x_grid is None:
        x_grid = np.linspace(x.min(), x.max(), 80)
    if kind == "lm":
        return _ols_fit(x, y, x_grid, 1)
    if kind == "poly3":
        return _ols_fit(x, y, x_grid, 3)
    return _loess_fit(x, y, x_grid)


def _series_style(series: list[str], palette=None, markers=None):
    colours = list(palette or _palette(max(len(series), 1)))
    marks = list(markers or _MARKERS)
    return {s: (colours[i % len(colours)], marks[i % len(marks)])
            for i, s in enumerate(series)}


def _empty_corner(ax, xs, ys):
    """The axes-fraction corner with the fewest data points, for auto-placed annotations.

    The published figures put 'r = ...' in whichever corner the panel left empty -- a decision
    the author made per panel. A drawer that always writes at top-left collides with the data on
    exactly the panels where the series rises into that corner, which is why the reproduction
    kept sprouting overlaps that the original did not have.
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) == 0:
        return (0.03, 0.97)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    fx = (xs - x0) / (x1 - x0) if x1 != x0 else np.zeros_like(xs)
    fy = (ys - y0) / (y1 - y0) if y1 != y0 else np.zeros_like(ys)
    candidates = [
        ((0.03, 0.97), (fx < 0.45) & (fy > 0.55)),
        ((0.97, 0.97), (fx > 0.55) & (fy > 0.55)),
        ((0.03, 0.03), (fx < 0.45) & (fy < 0.45)),
        ((0.97, 0.03), (fx > 0.55) & (fy < 0.45)),
    ]
    return min(candidates, key=lambda c: int(c[1].sum()))[0]


def ax_trend_band(ax, df: pd.DataFrame, x: str, y: str, lo: str | None = None,
                  hi: str | None = None, series: str | None = None,
                  fit: str | None = None, reference: float | None = None,
                  annotate: dict[str, str] | None = None, notes=None,
                  xlabel: str | None = None, ylabel: str | None = None,
                  legend: bool = True,
                  legend_cols: int | None = None, legend_loc: str = "best",
                  annotate_xy=(0.03, 0.97), band_alpha: float = 0.25,
                  band: str | None = None, connect: bool = False,
                  marker_size: float = 2.6, palette=None, markers=None,
                  fit_color=None, data_band_color=None,
                  legend_below: bool = False,
                  xticks=None, title: str | None = None):
    """A yearly series with its uncertainty: the seed paper's dominant panel.

    points + shaded band + fitted line + an explicit reference line + the correlation stated in
    the corner. That sentence covers five of the seed's seven figures; the same drawer produces
    a Gini panel (no band, cubic fit), a centrality panel (mean ± s.e.m., linear fit) and the
    four dyad panes (the fit's own confidence band, linear or smooth fit).

    BOTH KINDS OF BAND OCCUR IN THE SEED, AND THEY MEAN DIFFERENT THINGS:
      band="data"  the interval comes from the data (lo/hi, e.g. mean ± s.e.m.). This is the
                   centrality panels of Fig. 3c: the band moves with the yearly means.
      band="fit"   the interval is the fitted line's own confidence band. This is Figs 5 and 7:
                   the band follows the smooth curve, not the points.
    Conflating them would mis-state the uncertainty, so the choice is explicit and one without
    its inputs raises rather than falling back to the other.

    `connect=True` draws the thin line between the yearly points that the seed's dyad panels
    have under the fit. `annotate` maps a series name to its corner text (the r/P string),
    coloured like the series; `notes` are free annotations [{x, y, text, colour?, ha?, va?}].
    """
    df = _uniq(df)
    if band not in (None, "data", "fit"):
        raise ValueError(f"band must be None, 'data' or 'fit', got {band!r}")
    if band == "data":
        if lo is None or hi is None:
            raise ValueError("band='data' needs lo and hi")
    if band == "fit" and fit is None:
        raise ValueError("band='fit' needs fit=")
    for col in [x, y] + ([lo, hi] if lo else []) + ([series] if series else []):
        if col not in df.columns:
            raise KeyError(f"column {col!r} not in frame; has {list(df.columns)}")
    groups = list(dict.fromkeys(df[series].astype(str))) if series else [None]
    sty = _series_style(groups if series else ["_"], palette, markers)
    xs_all: list[float] = []
    ys_all: list[float] = []
    for g in groups:
        sub = df if g is None else df[df[series].astype(str) == g]
        sub = sub.sort_values(x)
        is_datetime = pd.api.types.is_datetime64_any_dtype(sub[x])
        if is_datetime:
            # a datetime axis plotted as raw numbers shows matplotlib's epoch offset
            # ("x1e15") whose exponent renders at 4.2 pt -- outside Nature's 5-7 pt band.
            # Convert to date numbers and format real dates instead.
            import matplotlib.dates as mdates
            xs = mdates.date2num(pd.to_datetime(sub[x]).dt.to_pydatetime())
        else:
            xs = sub[x].to_numpy(dtype=float)
        ys = sub[y].to_numpy(dtype=float)
        xs_all.extend(xs.tolist())
        ys_all.extend(ys.tolist())
        colour, marker = sty[g if series else "_"]
        if connect:
            ax.plot(xs, ys, "-", lw=0.6, color="#8c8c8c", zorder=1)
        if band == "data":
            ax.fill_between(xs, sub[lo].to_numpy(dtype=float),
                            sub[hi].to_numpy(dtype=float),
                            color=data_band_color or colour,
                            alpha=band_alpha, linewidth=0, zorder=1)
        ax.plot(xs, ys, "o", ms=marker_size, color=colour, markeredgecolor="black",
                markeredgewidth=0.25, zorder=3, label=str(g) if g is not None else None)
        if fit:
            # an unknown fit name is a programming error, not a degeneracy: validate it BEFORE
            # the guard below, which exists only for data that cannot support a fit
            if fit not in FITS:
                raise ValueError(f"unknown fit {fit!r}; available: {FITS}")
            gx = np.linspace(xs.min(), xs.max(), 80)
            try:
                gy, gse = _band_curve(xs, ys, fit, gx)
            except (ValueError, np.linalg.LinAlgError):
                gy = gse = None
            if gy is not None:
                if band == "fit":
                    ax.fill_between(gx, gy - 1.96 * gse, gy + 1.96 * gse, color="#b3b3b3",
                                    alpha=0.55, linewidth=0, zorder=1)
                ax.plot(gx, gy, "-", lw=1.0, color=fit_color or colour, zorder=2)
    if reference is not None:
        ax.axhline(reference, linestyle=(0, (4, 3)), color="black", linewidth=0.6,
                   zorder=0)
    if annotate:
        for g, spec in annotate.items():
            colour = sty[g][0] if g in sty else "black"
            # a tuple (text, x, y) places one series' note; a bare string uses annotate_xy,
            # which may be "auto" -- the emptiest corner of the panel. Two series annotated at
            # one point is an overlap; a fixed corner that lands on the data is a collision the
            # target never had, because the original author nudged each label per panel.
            if isinstance(spec, (tuple, list)) and len(spec) == 3:
                text, ax_x, ax_y = spec
                ha = "left"
            else:
                text = spec
                ax_x, ax_y = _empty_corner(ax, xs_all, ys_all) if annotate_xy == "auto" \
                    else annotate_xy
                ha = "left" if ax_x <= 0.5 else "right"
            ax.text(ax_x, ax_y, text, transform=ax.transAxes,
                    fontsize=6, color=colour, va="top", ha=ha)
    for note in notes or []:
        ax.text(note.get("x", 0.5), note.get("y", 0.5), note["text"],
                transform=ax.transAxes if note.get("axes", True) else ax.transData,
                fontsize=6, color=note.get("colour", "black"),
                ha=note.get("ha", "center"), va=note.get("va", "center"))
    if is_datetime:
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        ax.xaxis.get_offset_text().set_visible(False)
    if xticks is not None:
        ax.set_xticks(list(xticks))
    # "" suppresses the label deliberately; None means "use the column name". The two cases are
    # different in a plate, where an inner panel must carry NO label while its data still names
    # the axis.
    _frame(ax, x if xlabel is None else xlabel, y if ylabel is None else ylabel)
    if title:
        ax.set_title(title, fontsize=7)
    if legend and series:
        if legend_below:
            # the published figures put the legend BENEATH the axes, not inside the data area;
            # an inside legend is the most common way a faithful reproduction starts to look
            # "assembled" rather than drawn
            ax.legend(frameon=False, ncol=legend_cols or len(groups),
                      loc="upper center", bbox_to_anchor=(0.5, -0.26),
                      handlelength=1.0, columnspacing=1.0, handletextpad=0.4, fontsize=6)
        else:
            ax.legend(frameon=False, ncol=legend_cols or len(groups), loc=legend_loc,
                      handlelength=1.0, columnspacing=1.0, handletextpad=0.4,
                      fontsize=6)
    return None


def ax_ranked_share(ax, df: pd.DataFrame, label: str, value: str, top: int = 20,
                    percent: bool = False, xlabel: str = "", ylabel: str = "",
                    value_fmt: str | None = None, bar_color=None,
                    xtick_rotation: float = 0.0):
    """A ranked composition: bars in decreasing order, value printed above each bar.

    The seed's Fig. 1a. Ranking plus the number printed on the bar means a reader can take the
    value without reading the axis, which is why this idiom travels: it is the same drawing
    whether the quantity is a share of papers, of citations or of funding.
    """
    df = _uniq(df)
    if top < 1:
        raise ValueError("top must be >= 1")
    d = df.dropna(subset=[label, value]).copy()
    d[value] = pd.to_numeric(d[value], errors="coerce")
    d = d.dropna(subset=[value]).sort_values(value, ascending=False).head(top)
    if d.empty:
        raise ValueError("no rows left after dropping missing values")
    vals = d[value].to_numpy(dtype=float)
    pos = np.arange(len(d))
    fmt = value_fmt or ("{:.0f}%" if percent else "{:.3g}")
    shown = vals * 100 if percent else vals
    ax.bar(pos, shown, width=0.72, color=bar_color or style.OKABE_ITO["blue"],
           edgecolor="black", linewidth=0.35)
    span = float(np.nanmax(shown)) if np.nanmax(shown) > 0 else 1.0
    for i, v in enumerate(shown):
        ax.text(i, v + 0.02 * span, fmt.format(v), ha="center", va="bottom", fontsize=5.5)
    ax.set_ylim(0, span * 1.12)
    ax.set_xticks(pos)
    ax.set_xticklabels([str(s) for s in d[label]],
                       rotation=xtick_rotation,
                       ha="right" if xtick_rotation else "center")
    _frame(ax, xlabel or "", ylabel or "")
    return None


def ax_hexbin_corr(ax, df: pd.DataFrame, x: str, y: str, gridsize: int = 30,
                   xscale: str = "log", yscale: str = "log", cmap: str = "viridis",
                   annotate_r: bool = True, xlabel: str = "", ylabel: str = "",
                   marginals: bool = False):
    """A 2-D density of many points on log axes, with the correlation stated.

    The seed's Fig. 1b: 10,046 terms, x = term papers, y = attributional papers. A scatter of
    10k points over four decades is a solid black cloud; a hexbin shows where the mass is, and
    the plain-number log ticks (rule L04) keep every glyph in the 5-7 pt band.

    `marginals=True` adds the seed's small histograms above and to the right. They are drawn as
    inset axes marked `_figpipe_marginal`, which `composite.inspect` ignores when counting
    panels -- a marginal distribution is part of one panel, not a panel of its own.
    """
    df = _uniq(df)
    xv = pd.to_numeric(df[x], errors="coerce").to_numpy(dtype=float)
    yv = pd.to_numeric(df[y], errors="coerce").to_numpy(dtype=float)
    keep = np.isfinite(xv) & np.isfinite(yv)
    xv, yv = xv[keep], yv[keep]
    if len(xv) < 10:
        raise ValueError(f"hexbin needs at least 10 complete pairs, got {len(xv)}")
    hb = ax.hexbin(xv, yv, gridsize=gridsize, cmap=cmap, mincnt=1,
                   xscale=xscale, yscale=yscale, linewidths=0.15)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    if annotate_r:
        # THE CORRELATION IS COMPUTED ON THE SCALE THAT IS PLOTTED. On a log-log axes a raw
        # Pearson r is dominated by the few largest points and does not describe the cloud the
        # reader sees; the seed's caption value (r = 0.78) is the log-space correlation, and a
        # figure that annotates +0.83 next to a log-log cloud would be quoting a different
        # statistic from the one it draws.
        xr = np.log10(xv) if xscale == "log" else xv
        yr = np.log10(yv) if yscale == "log" else yv
        r = float(np.corrcoef(xr, yr)[0, 1])
        ax.text(0.03, 0.97, f"r = {r:.2f}", transform=ax.transAxes,
                va="top", fontsize=6)
    if marginals:
        _marginals(ax, xv, yv, top_only=(marginals == "top"))
    _frame(ax, xlabel or x, ylabel or y)
    return hb


def _marginals(ax, xv, yv, top_only: bool = False) -> None:
    """Small histograms above and to the right of `ax`, on the same log scales."""
    top = ax.inset_axes([0.0, 1.02, 1.0, 0.18], transform=ax.transAxes)
    bins_x = np.logspace(np.log10(max(xv.min(), 1e-9)), np.log10(xv.max()), 30)
    top.hist(xv, bins=bins_x, color="#4d4d4d", edgecolor="black", linewidth=0.2)
    top.set_xscale("log")
    top.tick_params(labelsize=5, length=1.5, width=0.4, direction="out")
    top.set_yticks([])
    top.set_xticklabels([])
    # a marginal distribution belongs to the panel: the composer must not count it as one
    top._figpipe_marginal = True
    if top_only:
        return
    right = ax.inset_axes([1.02, 0.0, 0.18, 1.0], transform=ax.transAxes)
    bins_y = np.logspace(np.log10(max(yv.min(), 1e-9)), np.log10(yv.max()), 30)
    right.hist(yv, bins=bins_y, color="#4d4d4d", edgecolor="black", linewidth=0.2,
               orientation="horizontal")
    right.set_yscale("log")
    right.tick_params(labelsize=5, length=1.5, width=0.4, direction="out")
    right.set_xticks([])
    right.set_yticklabels([])
    right._figpipe_marginal = True


def ax_tile_diverging(ax, df: pd.DataFrame, cmap: str = "RdBu_r",
                      annotate: bool = True, annot_fmt: str = "{:.2f}",
                      missing_color: str = "#d9d9d9", xlabel: str = "",
                      ylabel: str = "", cbar_label: str = "", tick_rotation: float = 0.0):
    """A matrix of signed values: one hue each side of zero, grey where data are missing.

    The seed's Fig. 6b. Two decisions are made deliberately rather than copied: the diverging
    map is red-BLUE, not the paper's red-green (red-green is the pair Nature's own guide warns
    about, and figpipe's colour check would flag it), and missing cells are grey rather than
    white so that "no data" is visibly different from "zero".
    """
    df = _uniq(df)
    data = df.to_numpy(dtype=float)
    finite = np.isfinite(data)
    if not finite.any():
        raise ValueError("the matrix has no finite values")
    lo, hi = float(np.nanmin(data)), float(np.nanmax(data))
    norm = None
    if lo < 0 < hi:
        from matplotlib.colors import TwoSlopeNorm
        norm = TwoSlopeNorm(vmin=lo, vcenter=0.0, vmax=hi)
    cmap_obj = plt.get_cmap(cmap).copy()
    cmap_obj.set_bad(missing_color)
    im = ax.imshow(np.ma.masked_invalid(data), cmap=cmap_obj, norm=norm,
                   aspect="auto", interpolation="nearest")
    ax.set_xticks(range(data.shape[1]))
    ax.set_xticklabels([str(c) for c in df.columns],
                       rotation=tick_rotation,
                       ha="right" if tick_rotation else "center")
    ax.set_yticks(range(data.shape[0]))
    ax.set_yticklabels([str(i) for i in df.index])
    if annotate and finite.sum() <= 200:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if np.isfinite(data[i, j]):
                    ax.text(j, i, annot_fmt.format(data[i, j]), ha="center",
                            va="center", fontsize=5.5, color="black")
    _frame(ax, xlabel or "", ylabel or "")
    return im


def ax_histogram(ax, df: pd.DataFrame, value: str, bins: int = 20,
                 group: str | None = None, density: bool = True,
                 xlabel: str = "", ylabel: str = "",
                 xscale: str = "linear", yscale: str = "linear",
                 alpha: float = 0.42, legend: bool = True,
                 title: str | None = None, color: str | None = None):
    """Distribution of one measured column, optionally split by a categorical column.

    A histogram is the classic sanity check a reader expects before trusting a mean; it is also
    the cheapest way to show that a "significant" difference is two shifted clouds rather than
    two different mechanisms. `density=True` lets panels with different n share a y axis.
    """
    df = _uniq(df)
    if xscale == "log":
        vals = df[value].to_numpy(dtype=float)
        if np.any(vals <= 0):
            raise ValueError("histogram on a log axis needs strictly positive values")
    if group:
        groups = [str(g) for g in pd.unique(df[group])][:6]
        for i, g in enumerate(groups):
            sub = df.loc[df[group].astype(str) == g, value].to_numpy(dtype=float)
            ax.hist(sub, bins=bins, density=density, alpha=alpha,
                    color=_palette(len(groups))[i], edgecolor="black",
                    linewidth=0.25, label=g)
        if legend:
            ax.legend(frameon=False, fontsize=5.5, handlelength=1.0,
                      columnspacing=0.8, handletextpad=0.3)
    else:
        vals = df[value].to_numpy(dtype=float)
        ax.hist(vals, bins=bins, density=density, alpha=0.55,
                color=color or style.OKABE_ITO["sky_blue"], edgecolor="black",
                linewidth=0.3)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    _frame(ax, xlabel or value, ylabel or ("density" if density else "count"))
    if title:
        ax.set_title(title)
    return None


def ax_dual_series(ax, df: pd.DataFrame, x: str, y1: str, y2: str,
                   xlabel: str = "", ylabel: str = "", ylabel2: str = "",
                   annotate: bool = False):
    """Two measured series on one x with separate y axes (left: y1, right: y2).

    A dual axis is a rhetorical device: it invites the reader to compare shapes. It is therefore
    forbidden to imply a causal relation silently -- both series are direct-labelled and the two
    axis labels are always written, never left to the caption.
    """
    df = _uniq(df)
    xs = df[x].to_numpy()
    ax.plot(xs, df[y1].to_numpy(dtype=float), "-o", ms=2.4, lw=0.9,
            color=style.OKABE_ITO["blue"], markeredgecolor="black",
            markeredgewidth=0.2, label=ylabel or y1)
    ax2 = ax.twinx()
    ax2.plot(xs, df[y2].to_numpy(dtype=float), "-s", ms=2.2, lw=0.9,
             color=style.OKABE_ITO["vermillion"], markeredgecolor="black",
             markeredgewidth=0.2, label=ylabel2 or y2)
    _frame(ax, xlabel or x, ylabel or y1)
    ax2.set_ylabel(ylabel2 or y2)
    ax2.tick_params(axis="y", labelsize=6)
    ax.tick_params(axis="y", labelsize=6)
    if annotate:
        for a in (ax, ax2):
            for sp in ("top",):
                a.spines[sp].set_visible(False)
    return None


def ax_polar_profile(ax, df: pd.DataFrame, theta: str, value: str,
                     xlabel: str = "", ylabel: str = "", title: str | None = None,
                     colour: str | None = None, line: bool = True,
                     grid_labels: bool = True, direction: int = 1):
    """A radial profile: one measured value per angle, as a closed line and/or bars.

    WHY THIS DRAWER EXISTS
        PlotTwin-Bench contains 13 Polar/Radial tasks and the pipeline could not draw a single
        one: every drawer assumed Cartesian axes, so the benchmark mapper had no operator and the
        task failed. A polar axis is not a style variant of a bar chart -- the axes projection
        itself changes -- so it is a new drawer plus a projection flag in the composer, not a
        parameter on an existing one.

    The angle column is taken as a CATEGORY (a compass direction, a month, a phase bin) unless
    it parses as a number, in which case it is read as an angle in DEGREES. Both readings are
    explicit and a value outside 0-360 is an error, never silently wrapped.
    """
    df = _uniq(df)
    labels = [str(v) for v in df[theta]]
    vals = df[value].to_numpy(dtype=float)
    if not np.all(np.isfinite(vals)):
        raise ValueError(f"polar profile: {value!r} has non-finite values")
    if len(vals) < 3:
        # a radial profile needs enough spokes to be a profile; with one or two points
        # matplotlib autoscales theta to a sliver and its ThetaLocator tries to draw
        # thousands of spokes (observed: "attempting to generate 1582 ticks")
        raise ValueError(f"polar profile needs at least 3 angles, got {len(vals)}")
    numeric_theta = all(_is_number(v) for v in labels)
    if numeric_theta:
        angles = np.deg2rad(df[theta].to_numpy(dtype=float))
        if np.any(angles < 0) or np.any(angles > 2 * np.pi + 1e-9):
            raise ValueError("polar profile: numeric angles must be within 0-360 degrees")
        if np.any(np.diff(angles) < 0):
            order = np.argsort(angles)
            angles, vals = angles[order], vals[order]
            labels = [labels[i] for i in order]
    else:
        n = len(vals)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    col = colour or style.OKABE_ITO["blue"]
    if line:
        closed_a = np.append(angles, angles[0])
        closed_v = np.append(vals, vals[0])
        ax.plot(closed_a, closed_v, "-", lw=1.0, color=col, marker="o", ms=2.6,
                markeredgecolor="black", markeredgewidth=0.25)
    else:
        ax.bar(angles, vals, width=0.8 * (angles[1] - angles[0] if len(angles) > 1 else 1.0),
               color=col, edgecolor="black", linewidth=0.3)
    if grid_labels:
        if numeric_theta:
            # a numeric angle axis gets at most 8 spokes; matplotlib's default locator tries to
            # fill the circle and warns about >1000 ticks on dense data
            step = max(1, int(np.ceil(len(angles) / 8)))
            ax.set_xticks(angles[::step])
        else:
            ax.set_xticks(angles)
            ax.set_xticklabels(labels, fontsize=6)
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_thetalim(0, 2 * np.pi)      # fixed full circle: an autoscaled sliver is unreadable
    ax.set_theta_direction(direction)
    ax.tick_params(labelsize=6)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=10)
    if title:
        ax.set_title(title, fontsize=7)
    return None


#: Drawers that need a non-Cartesian axes. The composer reads this set to create the right
#: projection; a polar drawer on a Cartesian axes would silently draw a straight line.
POLAR_DRAWERS = {"polar_profile"}


#: The idiom drawers join the same registry the templates use. The registry lives here, after
#: every drawer it names, so a new drawing style is registered by existing rather than by an
#: out-of-date list at the top of the module.
DRAWERS.update({
    "trend_band": ax_trend_band,
    "ranked_share": ax_ranked_share,
    "hexbin_corr": ax_hexbin_corr,
    "tile_diverging": ax_tile_diverging,
    "histogram": ax_histogram,
    "dual_series": ax_dual_series,
    "polar_profile": ax_polar_profile,
})


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
COLORBAR_CAPABLE = {"heatmap", "hexbin_corr", "tile_diverging"}


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
