"""A scalar field must carry a colour scale, and the scale must survive the page edge.

WHY THIS EXISTS
    All 15 `field_map` tasks in the pool were reported `unverifiable`, and the reason was accurate:
    a field is one imshow path, so the cell values reach the PDF only as colour.

    But investigating WHY found two defects stacked on top of each other:

    1. `op_encode_field` never set `colorbar=True`, and `ax_field_2d` has no colour bar of its own.
       So the figure printed a raster whose colours encoded a scale the reader could not see -- and
       carried no numbers at all, which is why nothing could be checked.

    2. Even with `colorbar=True` the labels did not appear. `CBAR_TOTAL_MM` reserved 4.0 mm for the
       bar plus 1.4 mm of pad, but a colour bar's tick labels sit OUTSIDE its right edge. Measured:
       the bar landed at figure-x 0.970-0.992 on a 518.7 pt page and its labels fell off the canvas.

    The colour bar is the ONE checkable claim a field figure can carry -- "the printed colour range
    equals the data range" -- so both defects had to be fixed for the figure to be decodable at all.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf", reason="PyMuPDF is needed to read the rendered page")


@pytest.fixture(scope="module")
def field_frame():
    rng = np.random.default_rng(0)
    n = 20
    z = rng.normal(0, 1, n * n)
    return pd.DataFrame({"x": np.repeat(np.linspace(0, 1, n), n),
                         "y": np.tile(np.linspace(0, 1, n), n),
                         "z": z})


def test_the_field_operator_requests_a_colorbar():
    """THE FIRST DEFECT: the operator never asked for one."""
    import inspect
    from figpipe import skills
    src = inspect.getsource(skills.op_encode_field)
    assert "colorbar=True" in src, (
        "encode.field does not request a colour bar, so the raster's colours encode a scale the "
        "reader cannot see and no rendered-file check can state what they mean")


def test_the_label_room_is_reserved():
    """THE SECOND DEFECT: bar+pad were reserved and the labels were not."""
    from figpipe import composite
    assert composite.CBAR_TOTAL_MM > composite.CBAR_WIDTH_MM + composite.CBAR_PAD_MM, (
        "the colour-bar reservation covers only the bar and its pad; the tick labels sit outside "
        "its right edge and will fall off the page")
    assert composite.CBAR_LABEL_MM >= 3.0, "no room is reserved for the labels"


def test_a_field_figure_prints_its_colour_scale(field_frame, tmp_path):
    """END TO END: the numbers must reach the PDF, and none may overflow the page."""
    import pymupdf
    from figpipe import skills

    result = skills.run("field_map", field_frame, out_stem=tmp_path / "f",
                        x="x", y="y", value="z")
    pdf = result.get("pdf") or (result.get("paths") or [None])[0]
    assert pdf, "the field skill produced no file"
    doc = pymupdf.open(pdf)
    page = doc[0]
    text = page.get_text()
    over = [w for w in page.get_text("words") if w[2] > page.rect.width + 0.5]
    width = page.rect.width
    doc.close()

    # the colour bar's tick labels must be present as text
    import re
    nums = [float(v.replace("\u2212", "-")) for v in re.findall(r"[\u2212-]?\d+\.?\d*", text)]
    data_min, data_max = field_frame["z"].min(), field_frame["z"].max()
    inside = [v for v in nums if data_min - 1.5 <= v <= data_max + 1.5]
    assert len(inside) >= 3, (
        f"the figure carries only {len(inside)} numbers near the data range "
        f"[{data_min:.2f}, {data_max:.2f}]; the colour scale is not printed. text={text[:200]!r}")
    assert not over, (
        f"{len(over)} word(s) past the {width:.1f} pt page edge: "
        f"{[(w[4], round(w[2] - width, 1)) for w in over]}")
