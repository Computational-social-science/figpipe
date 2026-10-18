"""Journal figure style presets, corrected against the official specifications.

WHY THIS MODULE EXISTS
    Every project that draws scientific figures re-derives its matplotlib settings, and the
    re-derivation is where compliance is lost. This module is the single definition, so a
    figure's compliance is a property of the import rather than of the author's memory.

THE FOUR DEFECTS IN THE COMMUNITY DEFAULT
    `plt.style.use(['science', 'nature'])` from SciencePlots is the de facto standard, and it
    is a good base. Measured against Nature's own guide, it has four problems:

        parameter              SciencePlots        required
        --------------------   -----------------   ---------------------------
        pdf.fonttype           3                   **42** (editable TrueType)
        axes.spines.top        True                hidden
        axes.spines.right      True                hidden
        font.sans-serif[0]     DejaVu Sans         **Arial or Helvetica**

    fonttype=3 is the serious one: it converts text to Type-3 outlines, which Nature
    explicitly rejects ("Do not outline text; embed fonts (True Type 2 or 42)"). A figure
    produced with the stock style fails submission on that alone, and nothing in the output
    looks wrong -- which is why it survives unnoticed.

THE LOG-AXIS TRAP, WHICH IS ARITHMETICALLY UNSOLVABLE
    matplotlib renders a `10^n` tick label as two spans: the base at the configured size and
    the exponent at roughly 0.7x. Measured: base 5.0 -> exponent 3.50 pt; base 6.0 -> 4.20 pt;
    base 7.0 -> 4.90 pt. Nature's band is 5-7 pt, so NO admissible base produces a compliant
    exponent. The only fix is to stop using 10^n and print plain numbers (100, 1000, 10000),
    which `apply()` does via `suppress_log_exponents=True`.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

try:  # SciencePlots is the base style; degrade gracefully if absent.
    import scienceplots  # noqa: F401  -- registers styles on import; must precede style.use
    _HAS_SCIENCEPLOTS = True
except ImportError:  # pragma: no cover
    _HAS_SCIENCEPLOTS = False

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter

#: Nature printed widths in mm.
WIDTH_SINGLE_MM = 89.0
WIDTH_DOUBLE_MM = 183.0
MAX_HEIGHT_MM = 170.0

#: Type size band, in points. Panel letters are a separate, larger size.
MIN_PT = 5.0
MAX_PT = 7.0
PANEL_LETTER_PT = 8.0

#: Okabe-Ito, exactly as Nature's guide lists it (hex from the guide).
OKABE_ITO = {
    "black": "#000000",
    "orange": "#e69f00",
    "sky_blue": "#56b4e9",
    "bluish_green": "#009e73",
    "yellow": "#f0e442",
    "blue": "#0072b2",
    "vermillion": "#d55e00",
    "reddish_purple": "#cc79a7",
}

#: Colour-blind-UNSAFE pairs to avoid; Nature explicitly warns about red/green.
UNSAFE_PAIRS = [("vermillion", "bluish_green"), ("orange", "bluish_green")]

#: Corrections applied on top of the base style.
_OVERRIDES = {
    "text.usetex": False,       # never require a TeX installation
    "savefig.bbox": None,       # do NOT let the style pad the output; the
                                # figure is created at the exact column width
                                # and padding would move it off-spec
    "savefig.pad_inches": 0.0,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "savefig.dpi": 400,
    "figure.dpi": 400,
    # Explicit sizes only: a named size such as "large" resolves to 1.2x the base
    # and lands ABOVE the 7 pt ceiling. Measured at 8.4 pt on panel titles.
    # The BASE size is pinned too: matplotlib's default is 10 pt, which fails the
    # 5-7 pt Nature band for every text element that has no explicit override.
    "font.size": 6.0,
    "axes.titlesize": 7.0,
    "axes.labelsize": 7.0,
    "xtick.labelsize": 6.0,
    "ytick.labelsize": 6.0,
    "legend.fontsize": 6.0,
    "figure.titlesize": 7.0,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "lines.linewidth": 1.0,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.top": False,
    "ytick.right": False,
    "axes.labelpad": 2.5,
    "axes.titlepad": 3.0,

}


def apply(base=("science", "nature", "no-latex"), **overrides) -> dict:
    """Apply the style and return the rcParams that were set.

    `no-latex` is included by default: the plain `science` style sets `text.usetex=True`, and
    on a machine without a TeX installation EVERY text call fails, so the figure cannot be
    produced at all. That is a hard dependency imposed silently by the community style, and a
    journal figure does not want TeX anyway -- it wants editable text.

    `base` falls back to matplotlib's default if SciencePlots is unavailable, so the module
    still enforces the compliance-critical settings on a machine without it.
    """
    if _HAS_SCIENCEPLOTS and base:
        try:
            plt.style.use(list(base))
        except (OSError, ValueError):
            # A style name may be absent in an older SciencePlots; fall back to what exists.
            usable = [b for b in base if b in plt.style.available]
            if usable:
                plt.style.use(usable)
    plt.rcParams.update(_OVERRIDES)
    if overrides:
        plt.rcParams.update(overrides)
    return {**_OVERRIDES, **overrides}


def panel_letter(ax, letter: str, dx_pt: float = -12.0, dy_pt: float = 6.0) -> None:
    """Draw a Nature-compliant panel label: 8 pt bold, upright, lowercase.

    PLACED IN FIGURE COORDINATES FROM THE AXES BBOX, not in axes coordinates. An earlier
    version used x=-0.30 in axes space, which for a narrow panel falls outside the canvas and
    the letter is silently clipped -- the demo figure rendered with no visible 'a'. Offsets in
    POINTS are independent of panel width, so the label lands in the same place whatever the
    layout.
    """
    fig = ax.figure
    bbox = ax.get_position()
    x = bbox.x0 + dx_pt / 72.0 / fig.get_size_inches()[0]
    y = bbox.y1 + dy_pt / 72.0 / fig.get_size_inches()[1]
    fig.text(max(x, 0.005), min(y, 0.995), letter, fontsize=PANEL_LETTER_PT,
             fontweight="bold", va="bottom", ha="left")


def suppress_log_exponents(fig) -> None:
    """Replace `10^n` log labels with plain numbers, and drop minor labels.

    REQUIRED, not cosmetic. A `10^n` label cannot satisfy the 5-7 pt band because matplotlib
    draws the exponent at ~0.7x the base: even a 7 pt base yields a 4.9 pt exponent, below the
    5 pt floor. Plain numbers put every glyph at the configured size.
    """
    for ax in fig.get_axes():
        if ax.get_yscale() == "log":
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: "%g" % v))
        if ax.get_xscale() == "log":
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: "%g" % v))


def violations() -> list[str]:
    """Check the CURRENTLY APPLIED rcParams against the specification."""
    out = []
    if plt.rcParams.get("pdf.fonttype") != 42:
        out.append("pdf.fonttype is %r, must be 42 (Nature rejects Type-3)"
                   % plt.rcParams.get("pdf.fonttype"))
    if plt.rcParams.get("ps.fonttype") != 42:
        out.append("ps.fonttype is %r, must be 42" % plt.rcParams.get("ps.fonttype"))
    for side in ("top", "right"):
        if plt.rcParams.get(f"axes.spines.{side}"):
            out.append(f"{side} spine is visible; hide it")
    if plt.rcParams.get("axes.grid"):
        out.append("gridlines are on; Nature avoids background gridlines")
    for key in ("font.size", "axes.titlesize", "axes.labelsize",
                "xtick.labelsize", "ytick.labelsize", "legend.fontsize"):
        raw = plt.rcParams.get(key)
        try:
            size = float(raw)
        except (TypeError, ValueError):
            out.append(f"{key} is {raw!r}, not an explicit number; a named size can resolve "
                       f"outside the {MIN_PT}-{MAX_PT} pt band")
            continue
        if not (MIN_PT <= size <= MAX_PT):
            out.append(f"{key} is {size}, outside the {MIN_PT}-{MAX_PT} pt band")
    fam = plt.rcParams.get("font.sans-serif") or []
    if not fam or fam[0] not in ("Arial", "Helvetica"):
        out.append(f"preferred font is {fam[0] if fam else 'none'}; use Arial or Helvetica")
    return out
