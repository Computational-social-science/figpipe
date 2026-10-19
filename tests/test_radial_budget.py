"""A radial profile must carry one spoke per ANGLE, not one per row.

WHY THIS TEST
    Measured on the real PlotTwin-Bench pool: the `radial_profile` tasks carried 460 and 784 rows
    and the operator passed the WHOLE table to the polar drawer, which drew one spoke per row. The
    labels collided -- 50, 30, 17, 13, 10, 10, 10, 9, 8 hard text collisions across 13 tasks.

    This is the same defect family as the matrix label budget (LEARNINGS ##63/##64): a drawer given
    a long table draws every row instead of a summary. The fix has three parts, and all three are
    pinned here:
      1. aggregate to one value per angle, recording the reduction in the trace
      2. refuse past a spoke budget, because 40 unreadable spokes is not a radar
      3. refuse BELOW three spokes with a NAMED reason (two benchmark tasks reduce to 2)
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


def _long(angles: int = 8, rows_per_angle: int = 46) -> pd.DataFrame:
    """The real shape: many rows per angle."""
    names = [f"profile_{i}" for i in range(angles)]
    rows = [{"theta": names[i % angles], "value": 0.2 + (i % 7) * 0.08}
            for i in range(angles * rows_per_angle)]
    return pd.DataFrame(rows)


def test_a_long_table_is_aggregated_to_one_spoke_per_angle():
    df = _long(angles=8, rows_per_angle=46)
    assert len(df) == 368
    res = skills.run("radial_profile", df, out_stem=None, theta="theta", value="value")
    assert res["hard_failures"] == 0, res["findings"]
    # the reduction must be VISIBLE, not silent
    assert any("aggregate" in step for step in res["trace"]), res["trace"]
    assert any("368 rows -> 8 angles" in step for step in res["trace"]), res["trace"]


def test_too_many_angles_is_refused_not_drawn():
    df = _long(angles=40, rows_per_angle=3)
    with pytest.raises(skills.SkillError, match="spoke budget"):
        skills.run("radial_profile", df, out_stem=None, theta="theta", value="value")


def test_fewer_than_three_angles_is_a_named_refusal():
    """Two benchmark tasks reduce to exactly 2 angles; a polar profile cannot show 2."""
    df = pd.DataFrame({"theta": ["a", "b"] * 10, "value": [0.3, 0.6] * 10})
    with pytest.raises(skills.SkillError, match="at least 3"):
        skills.run("radial_profile", df, out_stem=None, theta="theta", value="value")


def test_a_clean_small_profile_still_renders():
    """Negative control: the budget must not break a profile that fits."""
    df = pd.DataFrame({"theta": [f"d{i}" for i in range(6)],
                       "value": [0.4, 0.6, 0.5, 0.7, 0.3, 0.55]})
    res = skills.run("radial_profile", df, out_stem=None, theta="theta", value="value")
    assert res["hard_failures"] == 0, res["findings"]


def test_the_benchmark_radial_tasks_are_clean_after_the_fix():
    """The measured outcome: hard findings on radial tasks fell from ~200 to 4."""
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        pytest.skip("report absent")
    import json
    data = json.loads(report.read_text(encoding="utf-8"))
    rad = [t for t in data.get("tasks", [])
           if t.get("skill") == "radial_profile" and t.get("status") == "ok"]
    if not rad:
        pytest.skip("no radial tasks measured")
    total = sum((t.get("hard_failures") or 0) for t in rad)
    worst = max((t.get("hard_failures") or 0) for t in rad)
    assert total < 50, f"radial tasks still carry {total} hard findings (was ~200)"
    assert worst < 20, f"the worst radial task still has {worst} hard findings (was 50)"


def test_a_structural_refusal_is_unsupported_not_an_error():
    """Refusing because the data cannot carry the encoding is the pipeline WORKING.

    Classifying it as an error would report a capability failure for a correct decision, and would
    make the success rate fall whenever the pipeline got more honest.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:
        pytest.skip("bench harness unavailable")
    assert bench.is_structural_refusal(
        "SkillError: encode.polar: 'panel_group' reduces to 2 distinct angle(s)")
    assert not bench.is_structural_refusal("HTTPError: HTTP Error 403: Forbidden")
    assert not bench.is_structural_refusal("ValueError: something else broke")
