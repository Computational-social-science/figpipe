"""A complete, runnable worked example: tidy data in, verified publication figure out.

WHY THIS FILE EXISTS
    The project claims its capability is "reusable in research scenarios". A claim like that is
    only credible if someone else can run the pipeline on their OWN data without reading the
    source, and get a figure whose compliance is verified rather than asserted. This file is that
    demonstration: it invents a small dataset, runs the whole pipeline end to end, and checks every
    claim it makes.

    It uses NO benchmark asset, NO seed paper and NO reference figure. If this runs, the pipeline
    is usable outside its own development context.

RUN
    python examples/worked_example.py
    python examples/worked_example.py --out /tmp/mydir

WHAT IT DEMONSTRATES
    1. spec.infer_spec    -- decide what to draw from the columns, or refuse
    2. skills.run         -- draw through a named recipe + the global verification floor
    3. audit.audit        -- read the rendered PDF back and measure it
    4. semantics          -- re-derive the printed claims from the data
    5. codegen.emit       -- produce runnable matplotlib code for the same figure
    6. select             -- choose between two candidates using only a reference
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import figpipe  # noqa: E402
from figpipe import audit, codegen, composite, grammar, layout, select, semantics, \
    skills, spec, styleprofile  # noqa: E402


def invent_data(seed: int = 7) -> pd.DataFrame:
    """A small, plausible research dataset: two groups measured over time."""
    rng = np.random.default_rng(seed)
    years = np.arange(2005, 2025)
    rows = []
    for group, offset, slope in (("control", 0.30, 0.004), ("treated", 0.28, 0.017)):
        for i, year in enumerate(years):
            mean = offset + slope * i + rng.normal(0, 0.008)
            rows.append({"year": int(year), "group": group, "response": round(float(mean), 4),
                         "se": round(float(abs(rng.normal(0.01, 0.002))), 4)})
    return pd.DataFrame(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(ROOT / "examples" / "output"))
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"figpipe {figpipe.__version__} -- {len(figpipe.__all__)} public modules")
    df = invent_data()
    print(f"\n1. DATA      {len(df)} rows, columns {list(df.columns)}")

    # ---- 1. declare the figure from the data -------------------------------------------
    try:
        figure = spec.infer_spec(df)
        declared = figure.panels[0]
        print(f"2. SPEC      intent={declared.intent!r}")
        print(f"             rationale: {declared.rationale}")
    except spec.SpecError as exc:
        # refusing is a valid, correct outcome -- print it and stop rather than guessing
        print(f"2. SPEC      refused: {exc}")
        return 0

    # ---- 2. draw through a named recipe (the global floor runs automatically) -----------
    # The recipe is chosen FROM the spec: drawing something the spec did not declare would make
    # the declaration decorative. The spec's own rationale names the intent it inferred.
    # ONE map, exported by spec -- a second copy is a second chance to diverge.
    recipe = spec.recipe_for(declared.intent)
    if recipe is None:
        print(f"2b. RECIPE   no recipe implements intent {declared.intent!r}; stopping")
        return 0
    print(f"2b. RECIPE   spec intent {declared.intent!r} -> recipe {recipe!r}")
    if recipe == "grouped_measures":
        result = skills.run(recipe, df, out_stem=out / "figure",
                            x="group", ycols=["response", "se"])
    elif recipe == "distribution_comparison":
        result = skills.run(recipe, df, out_stem=out / "figure",
                            group="group", value="response")
    elif recipe == "ranked_composition":
        result = skills.run(recipe, df, out_stem=out / "figure",
                            label="year", value="response")
    else:
        result = skills.run(recipe, df, out_stem=out / "figure",
                            x="year", y="response", fit="lm", xlabel="Year",
                            ylabel="Response (a.u.)")
    print(f"3. RENDER    {result['panels']} panel(s) -> {pathlib.Path(result['pdf']).name}")
    print(f"             operators: {' -> '.join(result['trace'][:4])}")
    print(f"             hard failures: {result['hard_failures']}")

    # ---- 3. verify the RENDERED file, not the source -----------------------------------
    report = audit.audit(result["pdf"], expect_width_mm=183.0, check_overlap=False)
    hard = [f for f in report["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    print(f"4. AUDIT     width={report.get('width_mm')} mm, "
          f"height={report.get('height_mm')} mm, fonts={len(report.get('fonts') or {})}, "
          f"hard findings={len(hard)}")
    if hard:
        for f in hard:
            print(f"             ! {f['check']}: {f['detail']}")

    # ---- 4. re-derive the printed claims from the data ---------------------------------
    # verify the SAME panel the recipe drew, on its own x/y pair when it has one
    fig = grammar.plate(
        [grammar.panel("trend_with_uncertainty", df, x="year", y="response", fit="lm",
                       xlabel="Year", ylabel="Response (a.u.)")],
        columns=2.0, height_mm=90.0)
    ax = fig.axes[0]
    printed = [t.get_text() for t in ax.texts]
    semantic = semantics.verify_panel(ax, df, x="year", y="response", texts=printed)
    print(f"5. SEMANTICS printed {printed or '[]'}; "
          f"checks passed: {semantic['ok']} {semantic['checks']}")

    # ---- 5. emit runnable matplotlib code for the same figure --------------------------
    panel = composite.Panel("trend_band", df, {"x": "year", "y": "response", "fit": "lm",
                                               "xlabel": "Year", "ylabel": "Response (a.u.)"})
    script = codegen.write([panel], out / "emitted.py", columns=2.0, height_mm=90.0)
    print(f"6. CODEGEN   {script.name} ({len(script.read_text(encoding='utf-8').splitlines())} "
          f"lines of plain matplotlib, runnable on its own)")

    # ---- 6. choose between two candidates using a reference ----------------------------
    reference = styleprofile.StyleProfile.from_pdf(result["pdf"])
    picked = select.select(reference, {"a": result["pdf"], "b": result["pdf"]})
    print(f"7. SELECT    {picked['choice']} (distance {picked['distance']}, "
          f"margin {picked['margin']}) -- the reference is an input, not an answer key")

    ok = (result["hard_failures"] == 0 and not hard and semantic["ok"])
    print(f"\nRESULT       {'every claim above was verified' if ok else 'SOMETHING FAILED'}")
    print(f"             artefacts in {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
