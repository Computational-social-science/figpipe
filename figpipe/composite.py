"""Composing panels into ONE figure -- the 组图 the template library could not make.

THE GAP THIS MODULE CLOSES
    The owner's objection to the first template library was exact: "你在 templates 都是一张
    完整图片的局部，而非组图，而我们需要的往往是优雅的组图！组图，组图，组图". Six templates
    each produced one axes on one canvas. A published figure is almost never one axes: the
    corpus's own figures have a median width of 132.4 mm and only 12.8 % sit at a single
    column, and Nature's double-column plate is a GRID -- a wide key panel, two small
    quantifications beneath it, a legend shared across the row.

    A panel library that cannot place two panels next to each other is therefore not a
    drawing capability; it is a set of swatches.

WHAT THE COMPOSER OWNS
    Geometry. A panel is a drawer plus data plus the cell it occupies; it does not know where
    it sits, how wide it is, or what letter it gets. `composite()` decides all of that from:
      * the requested grid (rows, cols, spans) or the panels' own `at=(row, col[, span])`
      * the MEASURED inter-panel gutter and panel aspect (corpus/composite_layouts.json)
      * the canvas budget: exactly 89 or 183 mm wide, at most 170 mm tall (style.MAX_HEIGHT_MM),
        because the legend has to fit beneath the printed figure
    and then MEASURES what it built, so a gap requested is a gap on the page.

WHY THE GEOMETRY IS COMPUTED IN MILLIMETRES, NOT IN GRIDSPEC FRACTIONS
    `wspace` is a fraction of the average AXES width, and matplotlib's interpretation of it is
    one subtraction away from the obvious one; a composer that sets `wspace=0.1` and hopes is a
    composer whose gutters are whatever they turn out to be. Here every axes rectangle is
    computed directly in mm from the canvas and converted to figure fractions --
    deterministic, independent of matplotlib's layout rules, and measurable after the fact.

THE GUTTER IS NOT THE GAP BETWEEN AXES
    Measured gutters are white space between printed marks. A panel's tick labels and axis
    label are printed marks too, so the physical gap between two AXES is the measured gutter
    PLUS the furniture of the neighbouring panel (~6 mm of tick labels). Setting the axes gap
    equal to the measured gutter -- the obvious mistake -- produced panels whose tick labels
    touched the panel to their left. When the axes are SHARED, the furniture is not drawn, so
    the axes gap drops back to the measured gutter itself.
"""
from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass, field

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import drawlib, layout, style  # noqa: E402

PT_PER_MM = 72.0 / 25.4
MM_PER_PT = 25.4 / 72.0

PRIORS_PATH = ROOT / "corpus" / "composite_layouts.json"

#: Fallback geometry, used only when the measured artefact is absent. Every value is tagged in
#: `priors()['source']`, so a figure can be asked which geometry it was drawn from rather than
#: silently inheriting an invented number.
DEFAULT_PRIOR = {
    "gutter_mm": 3.0,        # white space between the printed marks of two panels
    "panel_aspect": 1.3,     # width:height of one panel
    "letter_dx_mm": 2.0,     # panel letter starts just inside the panel's left edge
    "letter_dy_mm": 1.6,     # and above its top edge (the constant every template uses)
}

#: The measured letter offsets are taken against the BOUNDARY between panels, not against the
#: axes rectangle, and the boundary sits in the white gutter. `dx` survives that shift (the
#: horizontal distance from the panel's own left edge is what the eye sees); `dy` does not, so
#: it stays a placement constant rather than being adopted from a reference the composer does
#: not have. A measured |dx| larger than this is a letter sitting deep inside a wide panel and
#: is not a placement rule, so it is ignored.
LETTER_DX_MAX_MM = 6.0

#: Space a panel's own labels need, in mm. These belong to the panel, not to the gutter.
FURNITURE_X_MM = 6.0         # y tick labels of the panel to the right
FURNITURE_Y_XTICKS_MM = 3.5  # x tick labels of the panel above
FURNITURE_Y_XLABEL_MM = 3.5  # its x axis label, when the axis is not shared
LETTER_HEIGHT_MM = 3.2       # an 8 pt glyph plus a little air

#: Default margins. Inside the canvas (rule L05): `layout.save` never expands the saved box.
MARGINS_MM = {"left": 15.0, "right": 1.5, "top": 7.0, "bottom": 9.0}

#: Reserved inside a cell when a panel carries a colour bar.
CBAR_TOTAL_MM = 5.4
CBAR_WIDTH_MM = 4.0
CBAR_PAD_MM = 1.4

LETTERS = "abcdefghijklmnopqrstuvwxyz"

#: A gap larger than this between two panels is not a gutter; it is the distance between two
#: non-adjacent panels (it spans a panel), and it must not enter the uniformity check.
MAX_GUTTER_MM = 30.0


class CompositeGeometryError(RuntimeError):
    """The built figure does not match the geometry that was asked for."""


# --------------------------------------------------------------------------------------
# Priors: measured, not assumed
# --------------------------------------------------------------------------------------

def priors(path=None) -> dict:
    """Measured layout priors, with the provenance of every number made explicit.

    Returns `gutter_mm`, `panel_aspect`, `letter_dx_mm`, `letter_dy_mm`, per-value `*_n` sample
    sizes where the artefact records them, and `source` naming where they came from. If the
    artefact exists but cannot be read that is an ERROR, not a quiet fallback: a geometry
    prior that silently reverts to an invented number is the same failure shape as a control
    that looks present and does nothing.
    """
    p = pathlib.Path(path or PRIORS_PATH)
    out = dict(DEFAULT_PRIOR)
    out["source"] = "built-in defaults (no measured artefact)"
    out["measured"] = False
    if not p.is_file():
        return out
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CompositeGeometryError(f"cannot read the measured layout priors at {p}: {e}")
    g = j.get("gutter") or {}
    if g.get("median_mm") is not None:
        out["gutter_mm"] = float(g["median_mm"])
        out["gutter_n"] = g.get("n")
    pa = j.get("panel_aspect") or {}
    if pa.get("median") is not None:
        out["panel_aspect"] = float(pa["median"])
        out["panel_aspect_n"] = pa.get("n")
    lo = j.get("letter_offsets") or {}
    dx = lo.get("dx_median_mm")
    if dx is not None and abs(float(dx)) <= LETTER_DX_MAX_MM:
        out["letter_dx_mm"] = float(dx)
    elif dx is not None:
        # measured, but not a placement rule: keep the constant and say which was used
        out["letter_dx_note"] = (f"measured dx {dx} mm exceeds {LETTER_DX_MAX_MM} mm; "
                                 f"kept the constant")
    out["letter_n"] = lo.get("n")
    out["source"] = p.name
    out["measured"] = bool(out.get("gutter_n") or out.get("panel_aspect_n"))
    return out


# --------------------------------------------------------------------------------------
# A panel
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Panel:
    """One cell of a composite: a drawer, its data, its kwargs, and (optionally) its place.

    `draw` must be a key of `figpipe.drawlib.DRAWERS`. `at` is `(row, col)` or
    `(row, col, rowspan, colspan)`; when it is omitted the composer places panels row-major.
    `colorbar` reserves 5.4 mm on the right of the cell for a colour bar -- the bar is inside
    the panel's allotted width, so it never moves the gutter.
    """
    draw: str
    data: pd.DataFrame
    kwargs: dict = field(default_factory=dict)
    at: tuple | None = None
    letter: str | None = None
    colorbar: bool = False
    letter_dx_pt: float | None = None
    letter_dy_pt: float | None = None
    cbar_label: str = ""

    def __post_init__(self):
        if self.draw not in drawlib.DRAWERS:
            raise KeyError(f"unknown drawer {self.draw!r}; available: "
                           f"{sorted(drawlib.DRAWERS)}")
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError(f"panel {self.draw}: data must be a DataFrame, "
                            f"got {type(self.data).__name__}")
        if self.at is not None and len(self.at) not in (2, 4):
            raise ValueError("at must be (row, col) or (row, col, rowspan, colspan)")
        if self.colorbar and self.draw not in drawlib.COLORBAR_CAPABLE:
            raise ValueError(f"drawer {self.draw!r} has no scalar-mappable artist to put a "
                             f"colour bar on; colorbar-capable: "
                             f"{sorted(drawlib.COLORBAR_CAPABLE)}")


# --------------------------------------------------------------------------------------
# Planning
# --------------------------------------------------------------------------------------

@dataclass
class Plan:
    rows: int
    cols: int
    width_mm: float
    height_mm: float
    margins: dict
    gap_x_mm: float
    gap_y_mm: float
    cells: list[dict] = field(default_factory=list)


def _parse_grid(panels: list[Panel], columns: float = 2.0, ncols: int | None = None,
                nrows: int | None = None) -> tuple[int, int, list[dict]]:
    """Rows, columns and per-panel (row, col, rowspan, colspan)."""
    if any(p.at is not None for p in panels):
        if not all(p.at is not None for p in panels):
            raise ValueError("either every panel has `at=` or none does; a half-positioned "
                             "grid would place the rest by a rule the caller cannot see")
        if ncols or nrows:
            raise ValueError("ncols/nrows and `at=` describe the grid twice; pass one")
        cells = []
        for i, p in enumerate(panels):
            a = p.at
            r, c = a[0], a[1]
            rs, cs = (a[2], a[3]) if len(a) == 4 else (1, 1)
            if min(r, c, rs, cs) < 0 or rs < 1 or cs < 1:
                raise ValueError(f"panel {i}: at={a} is not a valid cell")
            cells.append({"index": i, "row": r, "col": c, "rowspan": rs, "colspan": cs})
        rows = max(c["row"] + c["rowspan"] for c in cells)
        cols = max(c["col"] + c["colspan"] for c in cells)
    else:
        n = len(panels)
        if ncols is None and nrows is None:
            # 3 panels read as a row on the double column and as a stack on the single column;
            # 4 as a square. These are the shapes the corpus's own grids take, and an empty
            # cell is never acceptable -- a hole in a printed plate.
            if columns == 1.0:
                cols = 1 if n <= 3 else 2
            else:
                cols = n if n <= 3 else (2 if n <= 4 else 3)
            rows = -(-n // cols)
        elif ncols is not None:
            cols = ncols
            rows = nrows or -(-n // cols)
        else:
            rows = nrows
            cols = -(-n // rows)
        if rows * cols != n:
            raise ValueError(
                f"{n} panels do not fill a {rows}x{cols} grid, leaving "
                f"{rows * cols - n} empty cell(s). A printed plate does not have holes: pass "
                f"`ncols`/`nrows` that divide the count, or place the panels explicitly with "
                f"`at=(row, col[, rowspan, colspan])`.")
        cells = []
        for i in range(n):
            cells.append({"index": i, "row": i // cols, "col": i % cols,
                          "rowspan": 1, "colspan": 1})
    # Overlap check, done on the integer grid so it is exact.
    grid = [[0] * cols for _ in range(rows)]
    for c in cells:
        for r in range(c["row"], c["row"] + c["rowspan"]):
            for k in range(c["col"], c["col"] + c["colspan"]):
                if grid[r][k]:
                    raise ValueError(f"panels {grid[r][k] - 1} and {c['index']} overlap at "
                                     f"cell (row {r}, col {k})")
                grid[r][k] = c["index"] + 1
    return rows, cols, cells


def _plan(panels, columns, height_mm, width_ratios, height_ratios, gutter_mm,
          sharex, sharey, margins, ncols=None, nrows=None) -> Plan:
    """Compute every rectangle in mm. The single source of truth for the layout."""
    rows, cols, cells = _parse_grid(panels, columns=columns, ncols=ncols, nrows=nrows)
    if columns not in (1.0, 2.0):
        raise ValueError("columns must be 1 or 2; Nature prints at 89 or 183 mm only")
    width = style.WIDTH_SINGLE_MM if columns == 1.0 else style.WIDTH_DOUBLE_MM

    pri = priors()
    gutter = float(pri["gutter_mm"] if gutter_mm is None else gutter_mm)
    # Shared axes are drawn without their tick labels, so the gap between them IS the gutter.
    gap_x = gutter + (0.0 if sharey else FURNITURE_X_MM)
    gap_y = (gutter + LETTER_HEIGHT_MM
             + (0.0 if sharex else FURNITURE_Y_XTICKS_MM + FURNITURE_Y_XLABEL_MM))
    m = dict(MARGINS_MM)
    m.update(margins or {})

    if height_mm is None:
        # Height is DERIVED from the measured panel aspect: a panel as wide as its cell and as
        # tall as the corpus says panels are. This is what makes the default output look like a
        # printed figure rather than a square. When the derived height would not fit the page,
        # the page wins -- a default that cannot be printed is not a default -- and the panes
        # are squeezed instead of raising at the caller who asked for no particular height.
        cell_w = (width - m["left"] - m["right"] - (cols - 1) * gap_x) / cols
        cell_h = cell_w / max(float(pri["panel_aspect"]), 0.2)
        derived = m["top"] + m["bottom"] + rows * cell_h + (rows - 1) * gap_y
        height_mm = min(derived, float(style.MAX_HEIGHT_MM))
    height_mm = round(float(height_mm), 2)
    if height_mm > style.MAX_HEIGHT_MM:
        raise ValueError(
            f"height {height_mm} mm exceeds Nature's {style.MAX_HEIGHT_MM} mm maximum; the "
            f"limit leaves room for the legend beneath the figure. Reduce rows or ratios, or "
            f"pass an explicit height_mm.")

    wr = list(width_ratios or [1] * cols)
    hr = list(height_ratios or [1] * rows)
    if len(wr) != cols or len(hr) != rows:
        raise ValueError(f"width_ratios needs {cols} entries, height_ratios {rows}")

    usable_w = width - m["left"] - m["right"]
    usable_h = height_mm - m["top"] - m["bottom"]
    content_w = usable_w - (cols - 1) * gap_x
    content_h = usable_h - (rows - 1) * gap_y
    if content_w <= 0 or content_h <= 0:
        raise ValueError("the canvas is too small for the requested margins and gaps")
    col_w = [content_w * r / sum(wr) for r in wr]
    row_h = [content_h * r / sum(hr) for r in hr]

    plan = Plan(rows=rows, cols=cols, width_mm=width, height_mm=height_mm,
                margins=m, gap_x_mm=gap_x, gap_y_mm=gap_y)
    for c in cells:
        x0 = m["left"] + sum(col_w[:c["col"]]) + c["col"] * gap_x
        w = sum(col_w[c["col"]:c["col"] + c["colspan"]]) + (c["colspan"] - 1) * gap_x
        y_top = height_mm - m["top"] - sum(row_h[:c["row"]]) - c["row"] * gap_y
        h = sum(row_h[c["row"]:c["row"] + c["rowspan"]]) + (c["rowspan"] - 1) * gap_y
        c["rect"] = (x0, y_top - h, w, h)
        plan.cells.append(c)
    return plan


# --------------------------------------------------------------------------------------
# The composer
# --------------------------------------------------------------------------------------

def composite(panels: list[Panel], columns: float = 2.0, height_mm: float | None = None,
              width_ratios=None, height_ratios=None, gutter_mm: float | None = None,
              sharex: bool = False, sharey: bool = False, letters: bool = True,
              margins: dict | None = None, ncols: int | None = None,
              nrows: int | None = None, rc: dict | None = None):
    """Build one multi-panel figure. Returns the matplotlib figure.

    `columns` 1 or 2 -> exactly 89 or 183 mm wide. `height_mm=None` derives the height from
    the measured panel aspect; an explicit height is honoured but must fit 170 mm.

    `ncols`/`nrows` pin the grid; without them 3 panels read as a row and 4 as a square. A
    count that does not fill its grid is REFUSED -- a printed plate does not have holes -- so
    layouts such as "one wide panel over two" use `at=` spans instead.

    `sharex`/`sharey` share axes down columns / across rows, hide the inner tick labels and
    axis labels (a shared axis is labelled once, on the outer panel), and shrink the gap to the
    measured gutter because the labels that needed the furniture are gone. Sharing is defined
    for plain grids: with spans it is refused rather than guessed.
    """
    if not panels:
        raise ValueError("composite() needs at least one panel")
    if (sharex or sharey) and any(p.at is not None for p in panels):
        raise ValueError("sharex/sharey is only defined for a plain grid; with `at=` spans the "
                         "axes in a column need not share a scale. Rejected rather than "
                         "silently sharing the wrong axes.")
    # `rc` lets a caller search the STYLE dimension (font size tier, line width, ...) without
    # forking the composer: the style must be applied before the axes are created, so it has to
    # travel with the layout call rather than being patched afterwards.
    style.apply(**(rc or {}))
    pri = priors()
    gutter = float(pri["gutter_mm"] if gutter_mm is None else gutter_mm)
    plan = _plan(panels, columns, height_mm, width_ratios, height_ratios,
                 gutter, sharex, sharey, margins, ncols=ncols, nrows=nrows)

    fig, _, _ = layout.figure(columns=columns, height_mm=plan.height_mm)
    W, H = plan.width_mm, plan.height_mm
    plan.cells.sort(key=lambda c: (c["row"], c["col"]))

    first_in_col: dict[int, object] = {}
    first_in_row: dict[int, object] = {}
    axes = []
    for p, cell in zip(panels, plan.cells):
        x0, y0, w, h = cell["rect"]
        ax_w = w - (CBAR_TOTAL_MM if p.colorbar else 0.0)
        share = {}
        if sharex and cell["row"] > 0 and cell["col"] in first_in_col:
            share["sharex"] = first_in_col[cell["col"]]
        if sharey and cell["col"] > 0 and cell["row"] in first_in_row:
            share["sharey"] = first_in_row[cell["row"]]
        projection = ("polar" if p.draw in getattr(drawlib, "POLAR_DRAWERS", set())
                      else None)
        ax = fig.add_axes([x0 / W, y0 / H, ax_w / W, h / H],
                          projection=projection, **share)
        first_in_col.setdefault(cell["col"], ax)
        first_in_row.setdefault(cell["row"], ax)
        artist = drawlib.DRAWERS[p.draw](ax, p.data, **dict(p.kwargs))
        if p.colorbar:
            cax = fig.add_axes([(x0 + ax_w + CBAR_PAD_MM) / W, y0 / H,
                                CBAR_WIDTH_MM / W, h / H])
            cb = fig.colorbar(artist, cax=cax)
            if p.cbar_label:
                cb.set_label(p.cbar_label, fontsize=6)
            cb.ax.tick_params(labelsize=5.5)
            cax._figpipe_cbar = True
        axes.append(ax)

    if sharex:
        # the BOTTOM row carries the shared x labels; the rows above it are the inner ones
        bottom = max(cell["row"] for cell in plan.cells)
        for ax, cell in zip(axes, plan.cells):
            if cell["row"] < bottom:
                ax.tick_params(labelbottom=False)
                ax.set_xlabel("")
    if sharey:
        for ax, cell in zip(axes, plan.cells):
            if cell["col"] > 0:
                ax.tick_params(labelleft=False)
                ax.set_ylabel("")

    if letters:
        # order: the order the panels were placed, which is the order a caption walks them
        for i, (p, ax) in enumerate(zip(panels, axes)):
            letter = p.letter or LETTERS[i]
            dx_pt = p.letter_dx_pt if p.letter_dx_pt is not None else \
                pri["letter_dx_mm"] * PT_PER_MM
            dy_pt = p.letter_dy_pt if p.letter_dy_pt is not None else \
                pri["letter_dy_mm"] * PT_PER_MM
            style.panel_letter(ax, letter, dx_pt=dx_pt, dy_pt=dy_pt)

    report = inspect(fig)
    report["priors"] = pri
    report["letters_expected"] = bool(letters)
    report["planned"] = {"rows": plan.rows, "cols": plan.cols,
                         "gap_x_mm": round(plan.gap_x_mm, 2),
                         "gap_y_mm": round(plan.gap_y_mm, 2),
                         "height_mm": plan.height_mm}
    fig._figpipe_report = report
    return fig


# --------------------------------------------------------------------------------------
# Measurement of the built figure
# --------------------------------------------------------------------------------------

def inspect(fig) -> dict:
    """Measure what was actually built: page size, panel boxes, gaps, letters, overflows.

    The composer is not trusted to have produced what it planned; this reads the finished
    figure back. Gaps are measured between CELLS (axes plus colour bar), so a colour bar does
    not masquerade as a wider gutter.
    """
    w_mm = float(fig.get_size_inches()[0] * 25.4)
    h_mm = float(fig.get_size_inches()[1] * 25.4)
    cells = []
    for ax in fig.axes:
        if getattr(ax, "_figpipe_cbar", False) or getattr(ax, "_figpipe_marginal", False):
            continue
        b = ax.get_position()
        cells.append({"x0": float(b.x0 * w_mm), "y0": float(b.y0 * h_mm),
                      "x1": float(b.x1 * w_mm), "y1": float(b.y1 * h_mm),
                      "w": float(b.width * w_mm), "h": float(b.height * h_mm)})
    for ax in fig.axes:
        if not getattr(ax, "_figpipe_cbar", False):
            continue
        b = ax.get_position()
        cb = {"x0": float(b.x0 * w_mm), "x1": float(b.x1 * w_mm),
              "y0": float(b.y0 * h_mm), "y1": float(b.y1 * h_mm)}
        best = None
        for c in cells:
            if abs(c["y0"] - cb["y0"]) < 1.0 and c["x0"] < cb["x0"]:
                if best is None or c["x0"] > best["x0"]:
                    best = c
        if best is not None:
            best["x1"] = max(best["x1"], cb["x1"])
            best["w"] = best["x1"] - best["x0"]

    def _gaps(axis: str):
        # Only IMMEDIATE neighbours count. A three-panel row also has a "gap" between panel 1
        # and panel 3 that spans a whole panel; treating it as a gutter made a perfectly even
        # row look like [3.0, 59.5] mm and fail its own uniformity check.
        out = []
        for i in range(len(cells)):
            for j in range(len(cells)):
                if i == j:
                    continue
                a, b = cells[i], cells[j]
                if axis == "x":
                    same = abs(a["y0"] - b["y0"]) < 0.6 and abs(a["y1"] - b["y1"]) < 0.6
                    if same and 0 <= b["x0"] - a["x1"] <= MAX_GUTTER_MM:
                        out.append(float(round(b["x0"] - a["x1"], 2)))
                else:
                    same = abs(a["x0"] - b["x0"]) < 0.6 and abs(a["x1"] - b["x1"]) < 0.6
                    if same and 0 <= b["y0"] - a["y1"] <= MAX_GUTTER_MM:
                        out.append(float(round(b["y0"] - a["y1"], 2)))
        return sorted(set(out))

    letters = []
    for t in fig.texts:
        s = t.get_text()
        if len(s) == 1 and s.isalpha():
            x, y = t.get_position()
            letters.append({"letter": s, "size_pt": float(round(t.get_fontsize(), 2)),
                            "x_mm": float(round(x * w_mm, 2)),
                            "y_mm": float(round(y * h_mm, 2))})
    overflow = []
    for i, c in enumerate(cells):
        if (c["x0"] < -0.05 or c["y0"] < -0.05
                or c["x1"] > w_mm + 0.05 or c["y1"] > h_mm + 0.05):
            overflow.append({"panel": i, "box": {k: round(v, 2) for k, v in c.items()}})
    return {"width_mm": round(w_mm, 2), "height_mm": round(h_mm, 2),
            "n_panels": len(cells),
            "panels": [{k: round(v, 2) for k, v in c.items()} for c in cells],
            "gaps_x_mm": _gaps("x"), "gaps_y_mm": _gaps("y"),
            "letters": letters, "overflow": overflow}


def check(fig, report: dict | None = None) -> list[str]:
    """Problems with the built figure, as sentences. Empty means it checks out.

    This is the invariant set the composer promises: the page is a stated column width, it fits
    the height limit, every panel is inside the canvas, every panel got its letter at 8 pt, and
    the gutters are UNIFORM -- an uneven gutter is the most visible sign that a figure was
    assembled by a tool rather than composed.
    """
    r = report or inspect(fig)
    out = []
    if not any(abs(r["width_mm"] - a) < 0.6
               for a in (style.WIDTH_SINGLE_MM, style.WIDTH_DOUBLE_MM)):
        out.append(f"width {r['width_mm']} mm is not a Nature column width")
    if r["height_mm"] > style.MAX_HEIGHT_MM:
        out.append(f"height {r['height_mm']} mm exceeds {style.MAX_HEIGHT_MM} mm")
    if r["overflow"]:
        out.append(f"{len(r['overflow'])} panel(s) extend past the canvas")
    if r.get("letters_expected", True) and len(r["letters"]) != r["n_panels"]:
        # title-labelled plates exist: the seed paper's Figs 5 and 7 label their four panes
        # with descriptive titles instead of a-d. A plate built WITHOUT letters is not a
        # defect; a plate that asked for letters and got fewer is.
        out.append(f"{r['n_panels']} panels but {len(r['letters'])} panel letters")
    for lt in r["letters"]:
        if abs(lt["size_pt"] - style.PANEL_LETTER_PT) > 0.2:
            out.append(f"panel letter {lt['letter']!r} is {lt['size_pt']} pt, not "
                       f"{style.PANEL_LETTER_PT} pt")
    for axis, gaps in (("horizontal", r["gaps_x_mm"]), ("vertical", r["gaps_y_mm"])):
        if len(gaps) > 1 and max(gaps) - min(gaps) > 0.6:
            out.append(f"{axis} gutters are uneven: {gaps} mm")
    return out


def save(fig, out_stem) -> list[pathlib.Path]:
    """Write the vector twin and the raster twin through the pipeline's own save()."""
    return [pathlib.Path(p) for p in layout.save(fig, out_stem)]


def render(panels, out_stem, **kw) -> dict:
    """Compose, check, and write. Returns the report (with the paths) -- not just the figure."""
    fig = composite(panels, **kw)
    report = getattr(fig, "_figpipe_report", inspect(fig))
    problems = check(fig, report)
    report["paths"] = [str(p) for p in save(fig, out_stem)]
    report["problems"] = problems
    return report


if __name__ == "__main__":
    pri = priors()
    print("  measured layout priors:")
    for k, v in pri.items():
        print(f"    {k:>16}  {v}")
