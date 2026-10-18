"""Polar panels must actually use a polar projection, and refuse invalid angles.

WHY THIS TEST
    PlotTwin-Bench has 13 Polar/Radial tasks. The pipeline could not draw one, so those tasks
    failed with "no operator". The fix is a new drawer PLUS a projection flag in the composer --
    and the failure mode to guard against is exactly the project''s recurring one: a panel that
    looks like a radial chart but is drawn on Cartesian axes.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import composite, drawlib, layout  # noqa: E402

CAT = pd.DataFrame({"direction": list("NESW"), "speed": [3.0, 5.0, 2.0, 4.0]})


def _render(panels, stem):
    fig = composite.composite(panels, columns=1.0, height_mm=70.0, letters=True)
    return fig, pathlib.Path(layout.save(fig, stem)[0])


def test_the_axis_really_is_polar(tmp_path):
    fig, pdf = _render([composite.Panel("polar_profile", CAT,
                                        {"theta": "direction", "value": "speed"})],
                       tmp_path / "polar")
    name = fig.axes[0].name
    assert name == "polar", f"expected a polar axes, got {name!r}"
    assert pdf.is_file() and pdf.stat().st_size > 0


def test_numeric_angles_in_degrees_are_accepted_and_sorted(tmp_path):
    df = pd.DataFrame({"angle": [180.0, 0.0, 90.0], "v": [1.0, 2.0, 3.0]})
    fig, _ = _render([composite.Panel("polar_profile", df,
                                      {"theta": "angle", "value": "v"})], tmp_path / "deg")
    assert fig.axes[0].name == "polar"


def test_an_out_of_range_angle_is_refused(tmp_path):
    df = pd.DataFrame({"angle": [0.0, 90.0, 400.0], "v": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="0-360"):
        _render([composite.Panel("polar_profile", df,
                                 {"theta": "angle", "value": "v"})], tmp_path / "oor")


def test_non_finite_values_are_refused():
    df = pd.DataFrame({"d": list("NESW"), "v": [1.0, np.nan, 3.0, 4.0]})
    with pytest.raises(ValueError, match="non-finite"):
        fig, _ = _render([composite.Panel("polar_profile", df,
                                          {"theta": "d", "value": "v"})], "/tmp/x")


def test_the_polar_drawer_is_registered_for_the_composer():
    assert "polar_profile" in drawlib.DRAWERS
    assert "polar_profile" in drawlib.POLAR_DRAWERS


def test_a_two_angle_profile_is_refused(tmp_path):
    """A radial profile with one or two spokes is not a profile: matplotlib autoscales theta
    to a sliver and its locator asks for thousands of ticks. Refuse it instead."""
    df = pd.DataFrame({"d": ["N", "S"], "v": [1.0, 2.0]})
    with pytest.raises(ValueError, match="at least 3 angles"):
        fig, _ = _render([composite.Panel("polar_profile", df,
                                          {"theta": "d", "value": "v"})], tmp_path / "two")


def test_the_full_circle_is_always_drawn(tmp_path):
    import numpy as np
    df = pd.DataFrame({"d": list("NSEW"), "v": [1.0, 2.0, 3.0, 4.0]})
    fig, _ = _render([composite.Panel("polar_profile", df,
                                      {"theta": "d", "value": "v"})], tmp_path / "full")
    lo, hi = fig.axes[0].get_xlim()
    assert abs(hi - lo - 2 * np.pi) < 1e-6
