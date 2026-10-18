"""Transfer the measured style of a reference PDF onto a figure built from your data.

WHAT THIS IS
    The first end-to-end capability built on the peer absorption: profile a reference figure
    (vector PDF, exact measurement -- no VLM), derive a compliant style from it (font tier
    clamped into Nature's 5-7 pt band, palette taken from the reference's own colours, height
    from its aspect ratio), then search the small space of compliant variants and keep the one
    whose RENDERED page is closest to the reference. Every candidate is audited and measured;
    the report shows the distance before and after, per variant.

WHY IT IS A CAPABILITY AND NOT A DEMO
    The input is not hard-coded to the seed paper: any reference profile JSON and any tidy data
    frame work. The output is a PDF/PNG pair plus a machine-readable report, and the search is
    exhaustive over an explicit, bounded space -- so the same invocation produces the same
    figure and the same numbers.

TWO PRESETS
    --preset fig7   the seed's four-pane mimicry plate (derived data already in the repo); target
                    style = the measured profile of the published Fig. 7 region
    --preset panel  one trend panel from --data (columns x/y and optionally lo/hi)

USAGE
    python scripts/style_transfer.py --preset fig7
    python scripts/style_transfer.py --preset panel --data my.csv --x Year --y mean
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import shutil
import sys
import tempfile

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from figpipe import audit, composite, grammar, layout, sources, styleprofile  # noqa: E402

OUT = ROOT / "templates" / "transfer"
DEFAULT_REFERENCE = ROOT / "corpus" / "style" / "published_fig7.json"


def _fit_colour(palette: list[str]) -> str | None:
    """First reference colour with actual chroma (the published fit line is indigo, not grey)."""
    for h in palette:
        rgb = styleprofile._rgb(h)
        if rgb is None:
            continue
        if max(rgb) - min(rgb) > 30:
            return h
    return palette[0] if palette else None


def _variant_axes(reference: styleprofile.StyleProfile,
                  default_height: float | None) -> list[dict]:
    """The bounded, exhaustive variant space: style source x aspect match x fit colour source.

    Three binary choices, so the whole space is eight pages -- small enough to evaluate all of
    them rather than sample, and every page is a legal Nature figure.
    """
    derived = styleprofile.style_from_profile(reference)
    rc_options = [("default", None), ("profile", derived["rc"])]
    height_options = [("default", default_height), ("aspect", derived["height_mm"])]
    palette_options = [("default", None), ("profile", derived["palette"])]
    out = []
    for rc_name, rc in rc_options:
        for h_name, h in height_options:
            for p_name, pal in palette_options:
                out.append({"rc": rc_name, "height": h_name, "palette": p_name,
                            "rc_params": rc, "height_mm": h,
                            "palette_colours": pal})
    return out


def _apply_panels(panels, variant, panel_style: str):
    """Return a deep copy of the panels with the variant's style applied."""
    out = copy.deepcopy(panels)
    colour = _fit_colour(variant["palette_colours"] or [])
    for p in out:
        if variant["rc_params"] is not None:
            p.kwargs["band_alpha"] = p.kwargs.get("band_alpha", 0.25)
        if colour and p.draw in ("trend_band", "hexbin_corr"):
            p.kwargs["fit_color"] = colour
            if panel_style == "single":
                p.kwargs["palette"] = [colour]
        if colour and p.draw == "ranked_share":
            p.kwargs["bar_color"] = colour
    return out


def _render_and_measure(panels, layout_kw: dict, variant, reference, out_stem):
    fig_layout = {k: v for k, v in layout_kw.items()
                  if k not in ("height_mm", "rc")}
    height = variant["height_mm"] or layout_kw.get("height_mm") or 140.0
    fig = grammar.plate(panels, height_mm=height, rc=variant["rc_params"], **fig_layout)
    paths = layout.save(fig, out_stem)
    pdf = pathlib.Path(paths[0])
    profile = styleprofile.StyleProfile.from_pdf(pdf)
    dist = styleprofile.compare(reference, profile)
    a = audit.audit(pdf, expect_width_mm=183.0, check_overlap=False)
    hard = [f for f in a["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    collisions = audit.overlapping_glyphs(pdf)
    reward = 1.0 - dist["distance"] - 0.5 * len(hard) - (0.5 if collisions else 0.0)
    return {"pdf": str(pdf), "png": str(paths[1]), "distance": dist,
            "hard_findings": [f["check"] for f in hard],
            "collisions": collisions, "reward": round(max(0.0, min(1.0, reward)), 4),
            "profile": profile}


def transfer(panels, layout_kw: dict, reference: styleprofile.StyleProfile,
             out_dir=OUT, panel_style: str = "plate") -> dict:
    """Evaluate every variant, keep the closest page, and write the artefacts + report."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-transfer-"))
    variants = _variant_axes(reference, layout_kw.get("height_mm"))
    records = []
    try:
        for i, variant in enumerate(variants):
            panels_i = _apply_panels(panels, variant, panel_style)
            key = f"v{i}_{variant['rc']}_{variant['height']}_{variant['palette']}"
            rec = _render_and_measure(panels_i, layout_kw, variant, reference, work / key)
            rec.update({"variant": {k: variant[k] for k in ("rc", "height", "palette")},
                        "state": key})
            rec["profile"].save(work / f"{key}_profile.json")
            records.append(rec)
        baseline = next(r for r in records
                        if r["variant"] == {"rc": "default", "height": "default",
                                             "palette": "default"})
        best = max(records, key=lambda r: r["reward"])
        for suffix in (".pdf", ".png"):
            src = pathlib.Path(best["pdf"] if suffix == ".pdf" else best["png"])
            if src.is_file():
                shutil.copy2(src, out_dir / f"style_transfer_best{suffix}")
        best["profile"].save(out_dir / "style_transfer_best_profile.json")
        from figpipe import score as score_mod
        sc = score_mod.score_panel(out_dir / "style_transfer_best.pdf",
                                   reference_profile=reference,
                                   expected_panels=None if not any(
                                       p.kwargs.get("letter") for p in panels) else len(panels))
        report = {
            "reference": reference.summary(),
            "derived_style": styleprofile.style_from_profile(reference),
            "baseline": {k: baseline[k] for k in ("distance", "reward", "hard_findings",
                                                  "collisions", "variant")},
            "best": {k: best[k] for k in ("distance", "reward", "hard_findings",
                                          "collisions", "variant")},
            "improvement": {
                "distance": round(baseline["distance"]["distance"]
                                  - best["distance"]["distance"], 4),
                "reward": round(best["reward"] - baseline["reward"], 4)},
            "variants": [{"variant": r["variant"], "distance": r["distance"]["distance"],
                          "reward": r["reward"],
                          "hard_findings": r["hard_findings"],
                          "collisions": len(r["collisions"])} for r in records],
            "score": sc,
            "note": ("exhaustive over eight compliant variants; every page was rendered, "
                     "audited and profiled; the same invocation gives the same table"),
        }
        (out_dir / "style_transfer_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    finally:
        sources.assert_writable(work)
        shutil.rmtree(work, ignore_errors=True)


def _fig7_panels():
    import reproduce_seed
    panels, meta = reproduce_seed.plate_fig7()
    return panels, meta["layout"]


def _panel_from_data(path: pathlib.Path, x: str, y: str, lo: str | None,
                     hi: str | None, intent: str):
    df = pd.read_csv(path, encoding="utf-8")
    kw = {"x": x, "y": y, "xlabel": x, "ylabel": y, "fit": "lm", "band": "fit"}
    if lo and hi:
        kw.update({"lo": lo, "hi": hi, "band": "data"})
    return [grammar.panel(intent, df, **kw)], {"columns": 2.0, "height_mm": 90.0,
                                               "letters": True,
                                               "margins": {"bottom": 12.0}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--preset", choices=["fig7", "panel"], default="fig7")
    ap.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    ap.add_argument("--data")
    ap.add_argument("--x", default="Year")
    ap.add_argument("--y", default="mean")
    ap.add_argument("--lo")
    ap.add_argument("--hi")
    ap.add_argument("--intent", default="trend_with_uncertainty")
    args = ap.parse_args(argv)
    reference = styleprofile.StyleProfile.load(args.reference)
    if args.preset == "fig7":
        panels, layout_kw = _fig7_panels()
        panel_style = "plate"
    else:
        if not args.data:
            print("  --data is required with --preset panel")
            return 2
        panels, layout_kw = _panel_from_data(pathlib.Path(args.data), args.x, args.y,
                                             args.lo, args.hi, args.intent)
        panel_style = "single"
    report = transfer(panels, layout_kw, reference, panel_style=panel_style)
    print(f"  reference: {args.reference}")
    print(f"  baseline distance: {report['baseline']['distance']['distance']}  "
          f"best: {report['best']['distance']['distance']}  "
          f"improvement: {report['improvement']['distance']}")
    print(f"  best variant: {report['best']['variant']}")
    for v in report["variants"]:
        print(f"    {v['variant']}  distance={v['distance']}  reward={v['reward']}")
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
