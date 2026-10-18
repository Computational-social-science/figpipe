"""Profile a figure's style from its PDF, and compare two profiles.

WHY A CLI
    The style profile is the input to template generation: a reference PDF in, a measured
    profile out, and a distance when comparing a candidate against the reference. Having it as
    a command keeps the measurement inspectable -- the same script that produces the numbers in
    the docs produces the JSON in the repository.

USAGE
    python scripts/profile_figure.py --pdf PATH --page 1 [--bbox x0 y0 x1 y1 | --caption "Fig. 7 |"] \
        --out corpus/style/name.json [--suggest]
    python scripts/profile_figure.py --compare A.json B.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import styleprofile  # noqa: E402


def _suggest(prof: styleprofile.StyleProfile) -> dict:
    """A first-cut style setting derived from the measurement, inside Nature's bands.

    This is a SUGGESTION, not an automatic transfer: the measured medians are clamped into the
    submission bands (5-7 pt) and everything the profile cannot decide (which palette slot for
    which series, what the axes limits are) is left to the template. It exists to show that the
    profile is actionable, not to pretend the style problem is solved by one dictionary.
    """
    sizes = sorted(prof.sizes_pt)
    median = sizes[len(sizes) // 2] if sizes else 6.0
    base = min(max(median, 5.0), 7.0)
    palette = [c["okabe"] for c in prof.colours[:6]
               if c["okabe"] and c["rgb_distance"] <= 60]
    widths = sorted(prof.line_widths_pt)
    return {
        "base_font_pt": round(base, 2),
        "axis_label_pt": round(min(max(base, 6.0), 7.0), 2),
        "tick_label_pt": round(min(max(base - 0.5, 5.0), 6.5), 2),
        "panel_letter_pt": round(prof.panel_letters[0]["size_pt"], 2)
        if prof.panel_letters else 8.0,
        "line_width_pt": round(widths[len(widths) // 2], 2) if widths else 0.5,
        "palette_okabe": palette,
        "gridlines": (prof.rules_h + prof.rules_v) > 0,
        "note": "measurement mapped into the 5-7 pt band; content choices stay with the template",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--caption", help="locate the region above a caption containing this text")
    ap.add_argument("--out", help="write the profile JSON here")
    ap.add_argument("--suggest", action="store_true", help="print a first-cut style setting")
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"),
                    help="compare two saved profiles")
    args = ap.parse_args(argv)

    if args.compare:
        a = styleprofile.StyleProfile.load(args.compare[0])
        b = styleprofile.StyleProfile.load(args.compare[1])
        result = styleprofile.compare(a, b)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if not args.pdf:
        ap.error("--pdf is required unless --compare is used")
    prof = styleprofile.StyleProfile.from_pdf(
        args.pdf, page=args.page, bbox_pt=args.bbox, caption_prefix=args.caption)
    if args.out:
        prof.save(args.out)
        print(f"  wrote {args.out}")
    print(json.dumps(prof.summary(), indent=2, ensure_ascii=False))
    if args.suggest:
        print(json.dumps(_suggest(prof), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
