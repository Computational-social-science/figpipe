"""figpipe -- a reusable, spec-driven pipeline for publication figures.

The pipeline exists because the defects that get figures rejected are NOT visible in the
source code. They appear in the rendered file: type that is 4.2 pt instead of 5, a 198 mm
width instead of 183, exponents at 3.15 pt. A source linter cannot see any of them.

Usage
-----
    from figpipe import style, layout, audit

    style.apply()                       # compliant rcParams, SciencePlots base corrected
    fig, w, h = layout.figure(columns=2, height_mm=60)
    gs = layout.gridspec(fig, 1, 3)
    ...
    layout.save(fig, "docs/figN_name")  # writes .pdf (submission) + .png (preview)
    report = audit.audit("docs/figN_name.pdf", expect_width_mm=183)
    assert report["ok"], report["findings"]
"""
from . import audit, layout, style  # noqa: F401

__all__ = ["style", "layout", "audit"]
__version__ = "0.1.0"
