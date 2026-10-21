"""A polar spoke label must fit inside the page, not be cut by it.

WHY THIS EXISTS
    The pool reported 9 text collisions, 4 of them on `radial_profile`:

        'a' over 'raw_plot_measurement'
        'a' over 'site_design_summaries'

    The collision was not a layout problem. On the right-hand panel of a two-column figure a
    22-character category label extends past the page edge, and the PDF boundary CUTS it -- so the
    rendered text layer held both `site_design_summaries` and `site_design_summaries` (bbox
    x1 = 521.5 against a 518.7 pt page). matplotlib does not clip a tick label to the canvas; it
    draws it and the page boundary cuts it.

    Three wrapping strategies were tried and two were wrong:
      1. split once at the middle -> `raw_plot` + `measurement`, and `measurement` is 11 chars,
         wider than the 10 the panel has. Still overflowed by 1.1 pt.
      2. greedy from the left     -> `raw_plot` + `measuremen` + `t`. Every line fits and the
         result is unreadable.
      3. balanced split           -> `raw plot` + `measur` + `ement`. Fits and reads.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import drawlib  # noqa: E402

pytest.importorskip("pymupdf", reason="PyMuPDF is needed to inspect a rendered PDF")

LONG = ["raw_plot_measurement", "site_design_summaries", "condition_measurements",
        "trajectory_replicates", "averylonglabelwithnoseparator"]


def test_a_short_label_is_untouched():
    assert drawlib._wrap_spoke("short") == "short"
    assert drawlib._wrap_spoke("exactly10c") == "exactly10c"


def test_no_wrapped_line_exceeds_the_width():
    """THE CONSTRAINT: every line must fit the room the panel has."""
    for label in LONG:
        out = drawlib._wrap_spoke(label)
        for line in out.split("\n"):
            assert len(line) <= drawlib.POLAR_LABEL_WRAP, (
                f"{label!r} wrapped to {out!r}; the line {line!r} is {len(line)} chars, wider "
                f"than the {drawlib.POLAR_LABEL_WRAP} the panel has room for")


def test_wrapping_does_not_lose_characters():
    """Truncating is never an option: the reader cannot tell the labels apart afterwards."""
    for label in LONG:
        out = drawlib._wrap_spoke(label)
        # separators are consumed as break points, so compare with them removed
        got = out.replace("\n", "").replace(" ", "").replace("_", "").replace("-", "")
        want = label.replace("_", "").replace("-", "").replace(" ", "")
        assert got == want, f"{label!r} -> {out!r} lost or changed characters"


def test_no_line_is_a_single_letter():
    """THE SECOND FAILURE: `raw_plot` + `measuremen` + `t` fits every line and is unreadable."""
    for label in LONG:
        out = drawlib._wrap_spoke(label)
        lines = out.split("\n")
        if len(lines) > 1:
            assert all(len(ln) > 1 for ln in lines), (
                f"{label!r} wrapped to {out!r}, which leaves a one-character line")


def test_a_long_label_does_not_overflow_a_two_panel_page():
    """END TO END: the defect the pool reported, reproduced and fixed."""
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import pandas as pd
    import pymupdf
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    cats = LONG + ["aa", "bb", "cc"]
    df = pd.DataFrame({"theta": cats * 3, "value": rng.random(len(cats) * 3)})
    panels = [composite.Panel("polar_profile", df, {"theta": "theta", "value": "value"})
              for _ in range(2)]
    fig = composite.composite(panels, columns=2.0, height_mm=80.0, letters=False)
    out = pathlib.Path(__file__).parent / "_polar_tmp.pdf"
    try:
        paths = layout.save(fig, out.with_suffix(""))
        doc = pymupdf.open(paths[0])
        page = doc[0]
        over = [w for w in page.get_text("words") if w[2] > page.rect.width + 0.5]
        width = page.rect.width
        doc.close()
        assert not over, (
            f"{len(over)} word(s) past the {width:.1f} pt page edge: "
            f"{[(w[4], round(w[2] - width, 1)) for w in over]}")
    finally:
        for p in pathlib.Path(__file__).parent.glob("_polar_tmp*"):
            p.unlink(missing_ok=True)


# ---------------------------------------------------------------------------------------
# THE SAME DEFECT ON A MATRIX AXIS: the budget counted LABELS, not their WIDTH
#
# Measured on the pool: 5 collisions on matrix_plate whose tick labels were
# `individual channel performance`, `influent-loading-band totals`, ... -- three or four labels,
# well inside the 12-label count budget, each too wide for a 90 mm panel.
# ---------------------------------------------------------------------------------------

def test_a_matrix_with_long_column_names_hides_its_ticks():
    """END TO END: the labels that collided on the pool are now hidden, not overlapped."""
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import pandas as pd
    import pymupdf
    from figpipe import audit, composite, layout

    rng = np.random.default_rng(0)
    long_cols = ["individual channel performance", "influent-loading-band totals",
                 "paired inoculum uplift", "watershed-cluster variance"]
    df = pd.DataFrame({c: rng.normal(0, 1, 6) for c in long_cols})
    panel = composite.Panel("tile_diverging", df, {})
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    stem = pathlib.Path(__file__).parent / "_matrix_tmp"
    try:
        paths = layout.save(fig, stem)
        rep = audit.audit(paths[0], check_overlap=True)
        assert not [f for f in rep["findings"] if f["check"] == "overlap"], (
            f"long matrix labels still overlap: {rep['findings']}")
        doc = pymupdf.open(paths[0])
        text = doc[0].get_text()
        doc.close()
        assert "individual channel performance" not in text, (
            "the long label was drawn anyway; the width budget did not apply")
    finally:
        for f in pathlib.Path(__file__).parent.glob("_matrix_tmp*"):
            f.unlink(missing_ok=True)


def test_a_matrix_with_short_names_keeps_its_ticks():
    """NEGATIVE CONTROL: the width budget must not hide labels that fit."""
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import pandas as pd
    import pymupdf
    from figpipe import composite, layout

    rng = np.random.default_rng(0)
    df = pd.DataFrame({c: rng.normal(0, 1, 6) for c in ("alpha", "beta", "gamma")})
    panel = composite.Panel("tile_diverging", df, {})
    fig = composite.composite([panel], columns=2.0, height_mm=90.0, letters=False)
    stem = pathlib.Path(__file__).parent / "_matrix_short"
    try:
        paths = layout.save(fig, stem)
        doc = pymupdf.open(paths[0])
        text = doc[0].get_text()
        doc.close()
        assert "alpha" in text, "short column names were hidden; the budget is too tight"
    finally:
        for f in pathlib.Path(__file__).parent.glob("_matrix_short*"):
            f.unlink(missing_ok=True)
