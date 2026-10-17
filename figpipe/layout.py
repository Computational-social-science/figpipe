"""Figure construction helpers that make the wrong size hard to ask for.

WHY THIS MODULE EXISTS
    Every figure in the source project had its size written as a bare `figsize=(...)`, and
    three of six ended up outside the column width. Size is not a free parameter for a journal
    figure -- it is one of exactly two values -- so it should not be expressible as an
    arbitrary pair of floats.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .style import MAX_HEIGHT_MM, WIDTH_DOUBLE_MM, WIDTH_SINGLE_MM

MM = 1 / 25.4


def figure(columns: float = 2.0, height_mm: float = 60.0, **kwargs):
    """Create a figure whose width is exactly one of Nature's column widths.

    `columns` is 1 (89 mm) or 2 (183 mm). A height above `MAX_HEIGHT_MM` raises, because the
    guide's limit exists so the legend fits beneath the figure -- exceeding it is a submission
    defect, not a style choice.

    Returns `(fig, width_mm, height_mm)` so a caller can log what it asked for.
    """
    if columns not in (1.0, 2.0):
        raise ValueError(f"columns must be 1 or 2, got {columns!r}; Nature prints at "
                         f"{WIDTH_SINGLE_MM} or {WIDTH_DOUBLE_MM} mm only")
    width_mm = WIDTH_SINGLE_MM if columns == 1.0 else WIDTH_DOUBLE_MM
    if height_mm > MAX_HEIGHT_MM:
        raise ValueError(f"height {height_mm} mm exceeds Nature's {MAX_HEIGHT_MM} mm maximum; "
                         f"the limit leaves room for the legend beneath the figure")
    fig = plt.figure(figsize=(width_mm * MM, height_mm * MM), **kwargs)
    return fig, width_mm, height_mm


def gridspec(fig, rows: int = 1, cols: int = 1, **kwargs):
    """A gridspec with sane journal margins.

    The defaults leave room for axis labels and tick text; a tight `left` is the usual cause
    of clipped y-labels, which then get "fixed" by shrinking the font below 5 pt.
    """
    defaults = dict(left=0.075, right=0.985, top=0.84, bottom=0.26, wspace=0.42, hspace=0.5)
    defaults.update(kwargs)
    return fig.add_gridspec(rows, cols, **defaults)


def save(fig, path_without_suffix, dpi: int = 400, tight: bool = False) -> list:
    """Save the vector twin (submission) and the raster twin (preview).

    BOTH are produced deliberately:
      .pdf  vector, editable text, fonttype 42 -> the format Nature requires
      .png  raster preview                     -> for embedding, NOT for submission

    `tight=False` BY DEFAULT, and that is deliberate. `bbox_inches="tight"` expands the saved
    box to include anything sticking out past the canvas, so a figure requested at 183.0 mm
    comes out at 189.7 mm -- outside the column width it was designed for. Measured on the
    demo figure by this package's own audit.

    The right fix is to lay the axes out so the labels fit inside the canvas, which
    `gridspec`'s margins do. Passing `tight=True` is allowed for a preview but will change the
    width, and `audit` will say so.
    """
    from .style import suppress_log_exponents
    suppress_log_exponents(fig)
    written = []
    kw_common = {"bbox_inches": "tight"} if tight else {}
    for suffix, extra in ((".pdf", {}), (".png", {"dpi": dpi})):
        p = str(path_without_suffix) + suffix
        fig.savefig(p, **kw_common, **extra)
        written.append(p)
    return written
