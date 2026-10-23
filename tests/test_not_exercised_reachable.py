"""The pool's `not_exercised` zero is meaningful: every figpipe figure carries text.

WHY THIS EXISTS
    Round 88 made the report carry `checks_examined.not_exercised`. The pool measured 0 -- and a zero
    from this project's newest mechanism is exactly the kind of number that needs checking before it
    is believed, because rounds 82-86 were spent on zeros that meant nothing.

    The question is whether a figpipe figure COULD ever have no text. If one could, the field is
    reachable and its zero on this pool is a measurement; if none could, the field is vacuous by
    construction and should be removed.

WHAT WAS MEASURED
    Every drawer this project has puts axis labels on the page:

        dual_measure (line)      14 text spans
        field_map (raster)       22 text spans, 26 glyphs
        radial_profile          245 glyphs
        grouped_measures        101 glyphs

    A bare raster with no axes, no labels, no ticks and no colour bar reports
    `not_exercised: 3` -- so the state IS reachable, it is simply not reached by anything this
    pipeline draws.

    That is the answer: the zero is a PASS (every check examined something), not a vacuous zero.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _not_exercised(trace) -> int:
    return sum(str(line).count("=not_exercised") for line in (trace or []))


def _render(skill, df, **kw):
    import tempfile
    from figpipe import skills
    out = pathlib.Path(tempfile.mkdtemp(prefix="ne-"))
    return skills.run(skill, df, out_stem=out / skill, **kw)


def test_a_line_figure_has_text_so_no_check_is_idle():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": np.arange(12), "a": rng.random(12), "b": rng.random(12)})
    result = _render("dual_measure", df, x="x", y1="a", y2="b")
    lines = [t for t in (result.get("trace") or []) if "examined:" in t]
    assert lines, "the render carries no examined lines"
    assert _not_exercised(lines) == 0, "a labelled figure reported an idle check"
    # and the denominator is real
    assert any("/1" in str(line) or "/2" in str(line) for line in lines)


def test_a_raster_figure_has_text_so_no_check_is_idle():
    """THE OTHER DRAWER FAMILY. A field map is the most likely candidate for a text-free figure and
    it still carries 22 spans."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "x": np.repeat(np.linspace(0, 10, 20), 20),
        "y": np.tile(np.linspace(0, 5, 20), 20),
        "z": rng.normal(0, 1, 400)})
    result = _render("field_map", df, x="x", y="y", value="z")
    lines = [t for t in (result.get("trace") or []) if "examined:" in t]
    assert _not_exercised(lines) == 0


def test_the_state_IS_reachable_on_a_text_free_page(tmp_path):
    """THE REACHABILITY TEST. If `not_exercised` could never be produced, the pool's zero would be
    vacuous by construction and the field would be decoration."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figpipe import audit

    fig, ax = plt.subplots(figsize=(2.0, 2.0))
    ax.imshow(np.random.default_rng(0).random((20, 20)), cmap="viridis")
    ax.set_axis_off()
    pdf = tmp_path / "bare.pdf"
    fig.savefig(pdf)
    plt.close(fig)

    report = audit.audit(pdf)
    assert report["examined"]["n_not_exercised"] == 3, (
        "a bare raster did not report all three text checks as not_exercised")
    assert report["examined"]["n_pass"] == 0, (
        "a page with no text reported a pass; the state is not distinguishable")


def test_the_pool_report_says_how_many_rows_it_covers():
    """THE MEMBERSHIP. The same rule as every other aggregate in this project: a total must say what
    set it is over."""
    import json

    path = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not path.is_file():
        pytest.skip("no pool report")
    report = json.loads(path.read_text(encoding="utf-8"))
    ce = report.get("checks_examined") or {}
    if not ce:
        pytest.skip("the report predates the field")
    assert "lines" in ce and "not_exercised" in ce
    assert "note" in ce and ce["note"], (
        "the aggregate does not explain what not_exercised means")
