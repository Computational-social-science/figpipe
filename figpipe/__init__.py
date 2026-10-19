"""figpipe -- a reusable, spec-driven pipeline for publication figures.

The pipeline exists because the defects that get figures rejected are NOT visible in the
source code. They appear in the rendered file: type that is 4.2 pt instead of 5, a 198 mm
width instead of 183, exponents at 3.15 pt. A source linter cannot see any of them.

WHAT YOU CAN DO WITH IT (five entry points, in increasing order of ambition)
---------------------------------------------------------------------------
1. Draw one compliant panel from tidy data:
       from figpipe import grammar
       panel = grammar.panel("trend_with_uncertainty", df, x="year", y="mean", fit="lm")

2. Compose a plate, then verify the rendered file:
       from figpipe import grammar, layout, audit
       fig = grammar.plate([panel_a, panel_b], columns=2.0, height_mm=140.0)
       pdf = layout.save(fig, "fig2")[0]
       report = audit.audit(pdf, expect_width_mm=183.0)
       assert report["ok"], report["findings"]

3. Declare the figure from the data instead of by hand:
       from figpipe import spec
       figure = spec.infer_spec(df)          # raises SpecError rather than guessing

4. Run a named recipe over classic operators, with the global verification floor:
       from figpipe import skills
       result = skills.run("trend_with_uncertainty", df, x="year", y="mean")

5. Measure a reference's style and transfer it, then ship the closer candidate:
       from figpipe import styleprofile, select
       ref = styleprofile.StyleProfile.from_pdf("published.pdf", page=3)
       picked = select.select(ref, {"plain": a_pdf, "styled": b_pdf})

EVERY entry point above is verified: `audit` reads the PDF back, `semantics` re-derives printed
claims from the data, `select` compares rendered pages, and `skills` runs the compliance floor
automatically. A control that cannot be re-run is not a control.

MODULES
-------
Core      style, layout, audit, composite, grammar, drawlib
Declare   spec
Recipes   skills
Style     styleprofile, select
Verify    audit, semantics, score
Benchmark codegen, decision
"""
from . import (audit, codegen, composite, decision, drawlib, grammar, layout,  # noqa: F401
               score, select, semantics, skills, sources, spec, style, styleprofile)

__all__ = ["audit", "codegen", "composite", "decision", "drawlib", "grammar", "layout",
           "score", "select", "semantics", "skills", "sources", "spec", "style",
           "styleprofile"]
__version__ = "0.2.0"
