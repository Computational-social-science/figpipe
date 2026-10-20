"""The operator trace must distinguish figures that differ.

WHY THIS TEST
    `SkillContext`'s docstring promised "Every mutation is traced", but the trace recorded only the
    operator name and its primary columns. Measured on 2026-10-20, three DIFFERENT figures produced
    the SAME trace:

        fit=None        -> ['encode.trend(x,y)', 'layout.plate', ...]
        fit='lm'        -> ['encode.trend(x,y)', 'layout.plate', ...]
        fit='lm',band='fit' -> ['encode.trend(x,y)', 'layout.plate', ...]

    That matters beyond tidiness: the web layer answers "was the style applied?" from the trace, and
    a user reading a trace cannot tell a fitted trend from an unfitted one. A trace that cannot
    distinguish its own outputs is not a record of what happened.

    The fix records the OPTIONS that changed the drawing, only when set, so a difference in the
    trace always means a difference in the figure and the default case does not grow noise.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import skills  # noqa: E402


@pytest.fixture()
def trend_frame() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({"x": range(40), "y": rng.random(40)})


def _trace(res: dict) -> list[str]:
    return res.get("trace") or []


def test_different_fits_produce_different_traces(trend_frame):
    """THE BUG: three different figures, one trace."""
    plain = skills.run("trend_with_uncertainty", trend_frame, out_stem=None,
                       x="x", y="y", fit=None)
    fitted = skills.run("trend_with_uncertainty", trend_frame, out_stem=None,
                        x="x", y="y", fit="lm")
    banded = skills.run("trend_with_uncertainty", trend_frame, out_stem=None,
                        x="x", y="y", fit="lm", band="fit")
    assert _trace(plain) != _trace(fitted), (
        f"an unfitted and a fitted trend have the same trace: {_trace(plain)}")
    assert _trace(fitted) != _trace(banded), (
        f"a fitted trend and one with a band have the same trace: {_trace(fitted)}")
    assert any("fit='lm'" in t for t in _trace(fitted))
    assert any("band='fit'" in t for t in _trace(banded))


def test_options_left_unset_are_not_recorded(trend_frame):
    """Only options that were SET are recorded -- `None` must not appear as if it were chosen.

    The first version of this test asserted "at most one options line", which was wrong: each
    operator legitimately records its own options, so a two-operator skill has two lines. The
    property that actually matters is that an UNSET option is absent.
    """
    default = skills.run("trend_with_uncertainty", trend_frame, out_stem=None, x="x", y="y")
    joined = " ".join(_trace(default))
    assert "band=" not in joined, f"an unset band was recorded: {joined}"
    assert "reference=" not in joined, f"an unset reference was recorded: {joined}"
    # and a set option IS recorded
    assert "fit='lm'" in joined


def test_facet_encoder_is_recorded():
    """`of` decides hist vs trend vs scatter -- the most consequential facet option."""
    df = pd.DataFrame({"c": ["a"] * 20 + ["b"] * 20, "v": list(range(40))})
    res = skills.run("faceted_distribution", df, out_stem=None,
                     value="v", by="c", of="hist")
    joined = " ".join(_trace(res))
    assert "of='hist'" in joined, f"the facet encoder is not in the trace: {_trace(res)}"


def test_every_recorded_option_line_names_its_operator():
    """A bare `options(...)` line would be unattributable in a multi-panel trace."""
    df = pd.DataFrame({"c": ["a"] * 20 + ["b"] * 20, "v": list(range(40))})
    res = skills.run("faceted_distribution", df, out_stem=None,
                     value="v", by="c", of="hist")
    for line in _trace(res):
        if ".options(" in line:
            assert line.split(".options(")[0], f"unattributable option line: {line!r}"


def test_the_trace_still_starts_with_the_operator(trend_frame):
    """Recording options must not reorder the trace or hide the primary columns."""
    res = skills.run("trend_with_uncertainty", trend_frame, out_stem=None, x="x", y="y")
    assert _trace(res)[0].startswith("encode.trend("), _trace(res)[:3]
