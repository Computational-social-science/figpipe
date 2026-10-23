"""Does figpipe's deterministic audit cover what the benchmark's vision channel judges?

WHY THIS EXISTS
    The score has not moved since 2026-10-19 because 65 % of it is the vision channel, and that
    channel is not run. The usual answer is "we need a VLM". That answer was tested and closed: all
    nine local vision models failed a held-out control.

    But the channel is not a general aesthetic judgement. Its rubric is about defects that appear
    ONLY once the code runs -- overlapping elements, a legend covering a curve, text cut off at the
    frame, crowded tick labels. Those are DETERMINISTIC properties of the rendered page, and figpipe
    already measures them on the PDF.

    This script asks, per rubric item, whether figpipe has a check that decides it without a model.
    It is not a claim that the deterministic check equals the judge -- it is a claim that for these
    four classes a reader can point at a measurement rather than an opinion.

WHAT IT DOES NOT DO
    It does not produce an S_vision number. The benchmark's judge is a model with its own prompt and
    its own scale, and inventing a substitute number would be exactly the "a control that looks
    present and does nothing" defect this project keeps finding. What it produces is the evidence a
    human needs to decide whether the deterministic route is worth arguing for.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#: The vision channel's rubric, as the benchmark describes it, mapped to the check that decides it.
#:
#: `deterministic` names a function in `figpipe.audit` or `figpipe.semantics`; `evidence` is what that
#: function returns that a human can read.
RUBRIC = {
    "element overlap": {
        "deterministic": "audit.overlapping_glyphs",
        "why": "two glyph boxes that overlap by more than a ratio are colliding on the page",
        "blind_spot": "an overlap between a line and a glyph is not a glyph-glyph overlap",
    },
    "legend occlusion": {
        "deterministic": "audit.legend_occlusion",
        "why": ("a legend frame is filled, so the drawing segments under it are hidden; the check "
                "walks the path items and measures the frame area they cover"),
        "blind_spot": ("a legend over a FILLED REGION (a heatmap, a band) is counted only through "
                       "the region's edge paths, so a fully covered legend can under-report"),
    },
    "text truncation": {
        "deterministic": "audit.text_spans",
        "why": "text outside the page box is measurable from its span coordinates",
        "blind_spot": "text clipped by a clip-path inside the axes is not detected",
    },
    "dense tick crowding": {
        "deterministic": "audit.overlapping_glyphs",
        "why": "crowded tick labels ARE overlapping glyphs, so the same check decides it",
        "blind_spot": "labels that are close but do not overlap are not flagged",
    },
    "wrong printed scale": {
        "deterministic": "semantics.check_colorbar_scale",
        "why": "the colour bar's tick labels are text and can be compared to the data range",
        "blind_spot": "a bar whose labels are absent cannot be checked",
    },
    "axes not covering the data": {
        "deterministic": "semantics.check_axis_range",
        "why": "the axis tick labels state the coordinates the raster spans",
        "blind_spot": "a figure with no tick labels cannot be checked",
    },
}


def _available(name: str) -> bool:
    module, _, fn = name.partition(".")
    try:
        mod = __import__(f"figpipe.{module}", fromlist=[fn])
    except ImportError:
        return False
    return callable(getattr(mod, fn, None))


def survey() -> dict:
    rows = []
    for item, spec in RUBRIC.items():
        rows.append({"rubric_item": item, "check": spec["deterministic"],
                     "exists": _available(spec["deterministic"]),
                     "why": spec["why"], "blind_spot": spec["blind_spot"]})
    n = len(rows)
    n_ok = sum(1 for r in rows if r["exists"])
    return {
        "rubric": rows, "n": n, "n_covered": n_ok,
        "verdict": (f"{n_ok} of {n} vision-channel rubric items have a deterministic check in this "
                    f"project; each row names its blind spot, because a check that claims to "
                    f"replace a judge without saying where it stops is the defect class this "
                    f"project records most often"),
    }


def main(argv=None) -> int:
    out = survey()
    path = ROOT / "corpus" / "vision_rubric_coverage.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in out["rubric"]:
        mark = "YES" if r["exists"] else "NO "
        print(f"  [{mark}] {r['rubric_item']:<30} <- {r['check']}")
        print(f"        blind spot: {r['blind_spot']}")
    print(f"\n  {out['verdict']}")
    print(f"  wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
