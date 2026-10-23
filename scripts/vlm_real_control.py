"""A fifth control: a REAL figure the project drew, whose panel count it knows exactly.

WHY THIS EXISTS
    The first four controls are synthetic: a white page, pure noise, one subplot, three subplots. A
    model that fails the white page might be failing an EXTREME INPUT rather than being unreliable --
    white pages are not what a figure-recognition model sees in training.

    This control closes that gap. It renders a real figpipe figure through the project's own
    pipeline, so the answer is known BY CONSTRUCTION (the panel count the caller asked for) and the
    image looks like the images the model would actually be asked about.

WHY IT IS A SEPARATE MODULE
    `vlm_field_controls` must stay importable without the drawing stack -- it is used to screen
    models, and a screening tool that needs matplotlib to answer "is this model trustworthy" is a
    tool that fails for the wrong reason. This module imports the drawer; the screening tool does
    not.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def real_figure(panels: int = 3) -> bytes:
    """A figpipe-drawn figure with exactly `panels` subplots, as PNG bytes.

    THE ANSWER IS BY CONSTRUCTION. `composite` is told how many panels to lay out, so the expected
    count is not read back from the image -- it is the input.
    """
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import pandas as pd

    from figpipe import composite, layout

    rng = np.random.default_rng(21)
    specs = []
    for _ in range(panels):
        df = pd.DataFrame({"x": np.arange(8), "y": rng.random(8)})
        specs.append(composite.Panel("line_series", df, {"x": "x", "ycols": ["y"]}))
    # THE GRID MUST DIVIDE THE COUNT. figpipe raises rather than draw a plate with an empty cell, so
    # a control for 8 panels has to say it is 4x2 rather than leave the default 3x3 with a hole.
    grid = {1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2), 6: (2, 3), 8: (2, 4), 9: (3, 3)}.get(panels)
    kw = {} if grid is None else {"ncols": grid[1], "nrows": grid[0]}
    fig = composite.composite(specs, columns=2.0, height_mm=60.0, letters=False, **kw)
    import tempfile
    out = pathlib.Path(tempfile.mkdtemp(prefix="vlmreal-")) / "f"
    paths = layout.save(fig, out)
    import matplotlib.pyplot as plt
    plt.close(fig)
    pdf = pathlib.Path(paths[0])
    png = pdf.with_suffix(".png")
    if not png.is_file():
        # render the PDF's first page to PNG so the model sees what a reader sees
        import pymupdf
        doc = pymupdf.open(pdf)
        pix = doc[0].get_pixmap(dpi=200)
        pix.save(png)
        doc.close()
    return png.read_bytes()


#: Panel counts the real control spans.
#:
#: 1, 2, 3, 4 and 6 were used while DESIGNING the control. 8 and 9 are HELD OUT: two local models
#: passed every one of the designed counts and then failed both held-out ones, systematically
#: undercounting by two. A control set whose values are all used in designing it cannot detect that,
#: and "9 of 9" was true while describing a model that cannot count.
REAL_PANEL_COUNTS = (1, 2, 3, 4, 6, 8, 9)


def real_controls() -> list[dict]:
    """Real figpipe figures with known panel counts.

    THE ANSWER IS THE INPUT TO THE DRAWER, not read back from the image. Spanning 1, 2, 3, 4 and 6
    panels is what makes a correct answer informative: a model that says "3" to everything passes a
    single 3-panel control and fails this set.
    """
    return [{"name": f"real-{n}panel", "expect": n, "png": real_figure(n),
             "why": (f"a real figpipe figure with {n} panels; the count is the INPUT to the drawer, "
                     f"not read back from the image")}
            for n in REAL_PANEL_COUNTS]
