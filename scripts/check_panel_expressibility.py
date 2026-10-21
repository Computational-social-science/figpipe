"""Does the validation figure actually EXPRESS the dimensions it is used to test?

WHY THIS EXISTS
    Round 48 found that the validation draws a single-series trend panel, which uses ONE colour and
    has ONE axis. Two of the six style dimensions therefore cannot appear in it:

        palette   one series -> one colour      (ties 8/30)
        letters   one panel  -> no letters      (ties 28/30)

    A dimension the figure cannot express ties on almost every pair, and a tie is a limit of the
    EXPERIMENT, not a weakness of the metric. Reporting "palette scores 0.727" without that context
    invites a reader to think the component is broken.

    This script answers the question directly and mechanically: render the figure, re-profile the
    OUTPUT, and count how many of the supplied palette colours and panel letters actually arrived.

WHAT IT CHECKS
    1. the single-series panel CANNOT express a palette or letters (proving the old limitation)
    2. the multi-series multi-panel figure CAN express both (proving the fix is real)

Both directions matter. If only (2) were checked, a figure that happened to show colour for an
unrelated reason would pass.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from figpipe import composite, layout, styleprofile  # noqa: E402

#: A palette whose colours are unmistakably not the drawer's default.
TEST_PALETTE = ["#c00000", "#0072b2", "#009e73"]


def _profile(fig, out_stem) -> styleprofile.StyleProfile:
    paths = layout.save(fig, out_stem)
    return styleprofile.StyleProfile.from_pdf(paths[0], page=1)


def single_series(out_dir) -> dict:
    """The panel the validation used before round 48: one line, one axis."""
    df = pd.DataFrame({"x": np.arange(24.0),
                       "y": np.linspace(0.10, 0.92, 24),
                       "lo": np.linspace(0.05, 0.87, 24),
                       "hi": np.linspace(0.15, 0.97, 24)})
    panel = composite.Panel("trend_band", df,
                            {"x": "x", "y": "y", "lo": "lo", "hi": "hi",
                             "band": "data", "fit": "lm", "palette": TEST_PALETTE})
    fig = composite.composite([panel], columns=2.0, height_mm=80.0, letters=True)
    prof = _profile(fig, pathlib.Path(out_dir) / "single")
    return _measure(prof)


def multi_series(out_dir) -> dict:
    """Three series coloured from the reference's palette, across two lettered panels."""
    n = 12
    df = pd.DataFrame({
        "x": list(range(n)) * 3,
        "y": (list(np.linspace(0.10, 0.90, n))
              + list(np.linspace(0.20, 0.80, n))
              + list(np.linspace(0.30, 0.70, n))),
        "series": ["s1"] * n + ["s2"] * n + ["s3"] * n,
    })
    kw = {"x": "x", "y": "y", "series": "series", "fit": "lm",
          "palette": TEST_PALETTE}
    panels = [composite.Panel("trend_band", df, dict(kw)) for _ in range(2)]
    fig = composite.composite(panels, columns=2.0, height_mm=80.0, letters=True)
    prof = _profile(fig, pathlib.Path(out_dir) / "multi")
    return _measure(prof)


def _measure(prof) -> dict:
    """How many of the supplied palette colours, and how many panel letters, reached the output."""
    got = {c["hex"].lower() for c in (prof.colours or [])}
    palette_present = [hex_ for hex_ in TEST_PALETTE if hex_.lower() in got]
    return {"palette_expected": len(TEST_PALETTE),
            "palette_present": len(palette_present),
            "palette_colours": palette_present,
            "panel_letters": len(prof.panel_letters or [])}


def main(argv=None) -> int:
    import tempfile
    out = pathlib.Path(tempfile.mkdtemp(prefix="express-"))
    single = single_series(out)
    multi = multi_series(out)

    print("  SINGLE-SERIES PANEL (what the validation used before round 48):")
    print(f"    palette colours that reached the figure: "
          f"{single['palette_present']}/{single['palette_expected']}")
    print(f"    panel letters drawn                    : {single['panel_letters']}")
    print()
    print("  MULTI-SERIES MULTI-PANEL FIGURE:")
    print(f"    palette colours that reached the figure: "
          f"{multi['palette_present']}/{multi['palette_expected']}  {multi['palette_colours']}")
    print(f"    panel letters drawn                    : {multi['panel_letters']}")
    print()

    ok = True
    if multi["palette_present"] < 2:
        print("  FAIL: the multi-series figure does not carry the palette, so `palette` is still")
        print("        untestable and the round-48 diagnosis would be wrong.")
        ok = False
    if multi["panel_letters"] < 2:
        print("  FAIL: the multi-panel figure draws no panel letters, so `letters` is untestable.")
        ok = False
    if single["panel_letters"] >= 2:
        print("  NOTE: the single-series panel drew panel letters, which contradicts round 48.")
        ok = False
    if ok:
        print("  => the multi-series multi-panel figure EXPRESSES both `palette` and `letters`.")
        print("     The single-series panel does not. The round-48 diagnosis is confirmed, and")
        print("     this figure is what those two dimensions need in order to be measured.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
