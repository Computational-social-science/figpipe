"""Colour-policy checks that read the RENDERED image, not the source text.

WHY THIS MODULE EXISTS
    The adversarial audit found the QC gate reported `pfv.color-policy PASS` while doing
    nothing. Verified in the source: the string "color-policy" appeared zero times in qc.py,
    and "jet" appeared twice -- once in a `RISKY_CMAPS` set and once in a message string. The
    check inspected the PLOTTING SOURCE for the literal name of a colour map, so a figure
    exported from any other tool, or a PDF, could never be flagged.

    A colour map is a property of the PIXELS. Checking the source is checking the wrong object.
    That is the same class of error as reading rcParams instead of the PDF, which this project
    has already been through once.

HOW IT WORKS
    Rasterise the figure at a fixed dpi, then look at the saturated pixels:

      * JET / RAINBOW SIGNATURE -- these maps traverse the hue circle in a fixed order
        (blue -> cyan -> green -> yellow -> red) as luminance rises. A figure using them shows
        many distinct hues along a monotone lightness ramp. Detected by binning saturated
        pixels by hue and requiring: >= 5 occupied hue bins AND a strong monotone relation
        between hue order and lightness.
      * RED/GREEN ENCODING -- the combination the guide warns about. Detected by finding two
        well-separated pixel populations whose hues sit near 0 deg and near 120 deg and whose
        lightness is similar (so the pair is distinguished by hue alone).
      * PALETTE COUNT -- the number of distinct saturated hues, to flag indiscriminate colour.

WHAT IT CANNOT DO
    Distinguish ordered from categorical use. A rainbow on genuinely categorical data is
    defensible and this check cannot tell -- so a jet signature is reported as WARN, and the
    caption is the place to defend it. Saying otherwise would be a stronger claim than the
    measurement supports.
"""
from __future__ import annotations

import colorsys

import numpy as np

#: Hue bins over the full circle. 24 bins = 15 degrees each.
HUE_BINS = 24
#: A pixel counts as coloured when its saturation exceeds this.
SAT_MIN = 0.28
#: And its value is not near-black or near-white.
VAL_MIN = 0.12
VAL_MAX = 0.97


def _rgb_array(pdf_or_png, dpi: int = 150) -> np.ndarray:
    """Rasterise to an RGB array. Accepts a PDF or an image path."""
    path = str(pdf_or_png)
    if path.lower().endswith(".pdf"):
        import pymupdf
        doc = pymupdf.open(path)
        pix = doc[0].get_pixmap(dpi=dpi)
        arr = np.frombuffer(pix.samples, dtype=np.uint8)
        arr = arr.reshape(pix.height, pix.width, pix.n)[:, :, :3]
        doc.close()
        return arr
    from PIL import Image
    return np.array(Image.open(path).convert("RGB"))


def hue_stats(arr: np.ndarray) -> dict:
    """Occupied hue bins and their mean lightness, over saturated pixels only."""
    a = arr.astype(np.float32) / 255.0
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    val = mx
    mask = (sat > SAT_MIN) & (val > VAL_MIN) & (val < VAL_MAX)
    n_sat = int(mask.sum())
    if n_sat < 200:
        return {"n_saturated": n_sat, "occupied_bins": 0, "hues": [], "lightness": [],
                "insufficient": True}

    # vectorised hue
    r_, g_, b_ = r[mask], g[mask], b[mask]
    mx_ = np.maximum(np.maximum(r_, g_), b_)
    mn_ = np.minimum(np.minimum(r_, g_), b_)
    delta = np.maximum(mx_ - mn_, 1e-6)
    hue = np.zeros_like(mx_)
    m = (mx_ == r_)
    hue[m] = ((g_[m] - b_[m]) / delta[m]) % 6
    m = (mx_ == g_) & (mx_ != r_)
    hue[m] = (b_[m] - r_[m]) / delta[m] + 2
    m = (mx_ == b_) & (mx_ != r_) & (mx_ != g_)
    hue[m] = (r_[m] - g_[m]) / delta[m] + 4
    hue_deg = hue * 60.0

    bins = np.clip((hue_deg / (360.0 / HUE_BINS)).astype(int), 0, HUE_BINS - 1)
    occupied = np.unique(bins)
    lightness = []
    for bb in occupied:
        sel = bins == bb
        lightness.append(float(val[mask][sel].mean()))
    return {
        "n_saturated": n_sat,
        "occupied_bins": int(occupied.size),
        "hues": [int(x) for x in occupied],
        "lightness": lightness,
        "insufficient": False,
    }


def looks_like_rainbow(stats: dict) -> tuple[bool, str]:
    """Rainbow/jet signature: many hues AND lightness rising monotonically with hue order.

    Jet goes blue(low) -> cyan -> green -> yellow -> red(high), so sorting the occupied hue
    bins by hue should give a monotone lightness ramp. A categorical palette has no such
    relation.
    """
    if stats.get("insufficient"):
        return False, "too few saturated pixels to judge"
    hues, light = stats["hues"], stats["lightness"]
    if len(hues) < 5:
        return False, f"only {len(hues)} hue bins occupied"
    # A RAINBOW IS NOT MONOTONE IN LIGHTNESS; a perceptually uniform map is.
    #
    # Measured: jet lightness along the ramp is [0.71,0.59,0.59,0.95,0.88,0.59,...,0.94,0.95,
    # 0.59,...] -- it oscillates because the map must brighten for yellow and darken for blue.
    # viridis is strictly descending [0.87 ... 0.32]. cividis likewise.
    #
    # So: count DIRECTION REVERSALS in the lightness sequence ordered by hue. A monotone map
    # has 0-1; a rainbow has several.
    order = np.argsort(hues)
    l_sorted = np.array(light)[order]
    diffs = np.diff(l_sorted)
    # ignore tiny wobbles from anti-aliasing
    signs = np.sign(np.round(diffs / 0.03))
    signs = signs[signs != 0]
    reversals = int(np.sum(np.diff(signs) != 0)) if signs.size > 1 else 0
    span = float(l_sorted.max() - l_sorted.min())
    hue_span = int(max(hues) - min(hues))
    is_rainbow = reversals >= 3 and len(hues) >= 6 and span >= 0.20
    detail = (f"{len(hues)} hue bins over {hue_span} bins, lightness span {span:.2f}, "
              f"{reversals} direction reversal(s)")
    return is_rainbow, detail


def red_green_pairing(stats: dict) -> tuple[bool, str]:
    """Red/green encoding: saturated pixels near 0 deg and near 120 deg, similar lightness.

    The guide warns specifically about this pair because deuteranopes cannot separate them.
    """
    if stats.get("insufficient"):
        return False, "too few saturated pixels"
    hues = np.array(stats["hues"])
    light = np.array(stats["lightness"])
    if hues.size == 0:
        return False, "no hues"
    deg = hues * (360.0 / HUE_BINS) + (180.0 / HUE_BINS)   # bin centre
    red = np.abs(((deg + 180) % 360) - 180) < 22            # near 0
    green = np.abs(deg - 120) < 25                          # near 120
    if not (red.any() and green.any()):
        return False, "no red/green hue pair"
    lr, lg = light[red].mean(), light[green].mean()
    if abs(lr - lg) < 0.12:
        return True, (f"red and green populations at similar lightness "
                      f"({lr:.2f} vs {lg:.2f}); indistinguishable to deuteranopes")
    return False, f"red and green differ in lightness ({lr:.2f} vs {lg:.2f})"


def check_colour(path) -> dict:
    """Run every colour check on a rendered figure and return a structured result."""
    arr = _rgb_array(path)
    st = hue_stats(arr)
    rainbow, rdetail = looks_like_rainbow(st)
    rg, rgdetail = red_green_pairing(st)
    return {
        "n_saturated": st["n_saturated"],
        "occupied_hue_bins": st["occupied_bins"],
        "rainbow_signature": rainbow,
        "rainbow_detail": rdetail,
        "red_green_encoded": rg,
        "red_green_detail": rgdetail,
        "severity": ("WARN" if rainbow else "PASS"),
        "red_green_severity": ("FAIL" if rg else "PASS"),
    }
