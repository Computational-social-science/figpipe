"""Color utilities for the Set primitive.

Wraps ``colorspacious`` for sRGB → CIELAB → CIEDE2000 when available; falls
back to a hand-rolled CIEDE2000 implementation built on ``numpy`` (per the
agent brief, the package is small enough that a vendored math kernel is
preferable to a hard dependency).
"""

from __future__ import annotations

import logging
import math
from typing import Tuple

logger = logging.getLogger(__name__)

try:  # pragma: no cover - prefer the well-tested library when present
    import colorspacious as _colorspacious  # type: ignore

    _HAVE_COLORSPACIOUS = True
except Exception:  # pragma: no cover
    _colorspacious = None
    _HAVE_COLORSPACIOUS = False


def _parse_hex(hex_color: str) -> Tuple[float, float, float]:
    s = hex_color.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"invalid hex color: {hex_color!r}")
    try:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
    except ValueError as exc:
        raise ValueError(f"invalid hex color: {hex_color!r}") from exc
    return r, g, b


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_xyz(r: float, g: float, b: float) -> Tuple[float, float, float]:
    # sRGB D65 → XYZ (D65)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    return x, y, z


def _xyz_to_lab(x: float, y: float, z: float) -> Tuple[float, float, float]:
    # D65 reference white
    xn, yn, zn = 0.95047, 1.00000, 1.08883

    def f(t: float) -> float:
        delta = 6.0 / 29.0
        if t > delta**3:
            return t ** (1.0 / 3.0)
        return t / (3 * delta * delta) + 4.0 / 29.0

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return L, a, b


def hex_to_lab(hex_color: str) -> Tuple[float, float, float]:
    """Convert an sRGB hex string (``"#rrggbb"`` or ``"#rgb"``) to CIELAB.

    Uses ``colorspacious`` when available; otherwise a hand-rolled
    sRGB → linear RGB → XYZ(D65) → L*a*b* pipeline.
    """
    if _HAVE_COLORSPACIOUS:
        r, g, b = _parse_hex(hex_color)
        lab = _colorspacious.cspace_convert([r, g, b], "sRGB1", "CIELab")
        return float(lab[0]), float(lab[1]), float(lab[2])
    r, g, b = _parse_hex(hex_color)
    rl, gl, bl = (_srgb_to_linear(c) for c in (r, g, b))
    x, y, z = _linear_to_xyz(rl, gl, bl)
    return _xyz_to_lab(x, y, z)


def _ciede2000_lab(
    lab1: Tuple[float, float, float],
    lab2: Tuple[float, float, float],
) -> float:
    """CIEDE2000 ΔE between two CIELAB triples.

    Reference: Sharma, Wu, Dalal (2005), "The CIEDE2000 Color-Difference
    Formula: Implementation Notes, Supplementary Test Data, and Mathematical
    Observations." Constants kL = kC = kH = 1.
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    C_bar = (C1 + C2) / 2.0
    G = 0.5 * (1 - math.sqrt(C_bar**7 / (C_bar**7 + 25**7)))
    a1p = (1 + G) * a1
    a2p = (1 + G) * a2

    C1p = math.hypot(a1p, b1)
    C2p = math.hypot(a2p, b2)

    def _h(ap: float, bp: float) -> float:
        if ap == 0.0 and bp == 0.0:
            return 0.0
        h = math.degrees(math.atan2(bp, ap))
        return h + 360.0 if h < 0 else h

    h1p = _h(a1p, b1)
    h2p = _h(a2p, b2)

    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    else:
        diff = h2p - h1p
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        dhp = diff
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2.0))

    L_bar_p = (L1 + L2) / 2.0
    C_bar_p = (C1p + C2p) / 2.0
    if C1p * C2p == 0:
        h_bar_p = h1p + h2p
    else:
        d = abs(h1p - h2p)
        s = h1p + h2p
        if d <= 180:
            h_bar_p = s / 2.0
        elif s < 360:
            h_bar_p = (s + 360) / 2.0
        else:
            h_bar_p = (s - 360) / 2.0

    T = (
        1
        - 0.17 * math.cos(math.radians(h_bar_p - 30))
        + 0.24 * math.cos(math.radians(2 * h_bar_p))
        + 0.32 * math.cos(math.radians(3 * h_bar_p + 6))
        - 0.20 * math.cos(math.radians(4 * h_bar_p - 63))
    )
    delta_theta = 30 * math.exp(-(((h_bar_p - 275) / 25) ** 2))
    R_C = 2 * math.sqrt(C_bar_p**7 / (C_bar_p**7 + 25**7))
    S_L = 1 + (0.015 * (L_bar_p - 50) ** 2) / math.sqrt(20 + (L_bar_p - 50) ** 2)
    S_C = 1 + 0.045 * C_bar_p
    S_H = 1 + 0.015 * C_bar_p * T
    R_T = -math.sin(math.radians(2 * delta_theta)) * R_C

    dE = math.sqrt(
        (dLp / S_L) ** 2
        + (dCp / S_C) ** 2
        + (dHp / S_H) ** 2
        + R_T * (dCp / S_C) * (dHp / S_H)
    )
    return dE


def ciede2000(hex_a: str, hex_b: str) -> float:
    """CIEDE2000 ΔE between two sRGB hex colors.

    Returns a non-negative float; 0 means identical color, values >~5 are
    typically perceptible to a trained observer.
    """
    if _HAVE_COLORSPACIOUS:
        try:
            ra, ga, ba = _parse_hex(hex_a)
            rb, gb, bb = _parse_hex(hex_b)
            d = _colorspacious.deltaE(
                [ra, ga, ba], [rb, gb, bb], input_space="sRGB1"
            )
            return float(d)
        except Exception:  # pragma: no cover - defensive
            logger.debug("colorspacious deltaE failed; using fallback", exc_info=True)
    return _ciede2000_lab(hex_to_lab(hex_a), hex_to_lab(hex_b))


__all__ = ["hex_to_lab", "ciede2000"]
