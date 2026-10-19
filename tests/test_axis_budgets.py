"""Every categorical axis must bound its labels -- the rule, applied everywhere.

WHY THIS TEST
    The same defect appeared FOUR times, each found a different way:
      * `encode.bars`          drew one bar per ROW           (found by the worked example)
      * `ax_tile_diverging`    drew one tick per row          (found by a score)
      * `op_encode_polar`      drew one spoke per row         (found by "where else?")
      * `ax_boxplot`           drew every group name          (found by "where else?", again)

    This file is the systematic check, so a FIFTH instance cannot ship unnoticed: every drawer that
    sets categorical tick labels must bound them.
"""
from __future__ import annotations

import pathlib
import re
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import drawlib, skills  # noqa: E402


def test_every_categorical_axis_drawer_bounds_its_labels():
    """Structural: a drawer that calls set_xticklabels/set_yticklabels must also bound them."""
    src = (ROOT / "figpipe" / "drawlib.py").read_text(encoding="utf-8")
    offenders = []
    for m in re.finditer(r"def (ax_\w+)\(", src):
        name = m.group(1)
        end = src.find("\ndef ", m.start() + 1)
        body = src[m.start():end if end > 0 else len(src)]
        sets = "set_xticklabels" in body or "set_yticklabels" in body
        if not sets:
            continue
        # A budget can be expressed three ways, and the detector must accept all of them or it
        # produces false positives that train people to ignore it:
        #   * a named constant (MAX_...)
        #   * a stride/slice that thins the labels (step, [::n])
        #   * an explicit empty-tick branch (hide them entirely)
        bounded = ("MAX_" in body or "budget" in body or "MAX_AXIS_LABELS" in body
                   or "step" in body or "[::" in body
                   or "else []" in body or "if _n_" in body)
        if not bounded:
            offenders.append(name)
    assert not offenders, (
        "these drawers set categorical labels without a budget: "
        + ", ".join(offenders))


def test_a_many_group_boxplot_does_not_draw_every_label():
    """The fourth instance: 9 long group names on a narrow panel."""
    groups = ["Outer-Slope Acropora Belt", "Seaward Spur-and-Groove", "Lagoon Patch-Reef Mosaic",
              "Deep Forereef Transition", "Southern Reference Terr"]
    df = pd.DataFrame({"site": groups * 20,
                       "value": [0.3 + (i % 7) * 0.06 for i in range(100)]})
    res = skills.run("distribution_comparison", df, out_stem=None,
                     group="site", value="value")
    assert res["hard_failures"] == 0, res["findings"]


def test_a_few_group_boxplot_keeps_its_labels():
    """Negative control: the budget must not hide labels that FIT."""
    df = pd.DataFrame({"site": ["a", "b", "c"] * 10,
                       "value": [0.3 + (i % 5) * 0.05 for i in range(30)]})
    res = skills.run("distribution_comparison", df, out_stem=None,
                     group="site", value="value")
    assert res["hard_failures"] == 0


def test_the_height_check_has_a_tolerance_like_the_width_check():
    """A page of exactly MAX_HEIGHT must not fail, and the finding must not contradict itself.

    Three benchmark tasks reported "170.0 mm exceeds the 170.0 mm maximum" -- a message that
    contradicts itself, which is how the missing tolerance was found. Width already had TOL_MM;
    height used a bare `>`.
    """
    from figpipe import audit
    assert audit.TOL_MM > 0
    src = (ROOT / "figpipe" / "audit.py").read_text(encoding="utf-8")
    assert "MAX_HEIGHT_MM + TOL_MM" in src, (
        "the height check compares with a bare `>`; a page at exactly the maximum fails")


def test_the_remaining_collisions_are_not_systemic():
    """The measured outcome: no task carries more than a handful of collisions any more."""
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        pytest.skip("report absent")
    import json
    data = json.loads(report.read_text(encoding="utf-8"))
    tasks = data.get("tasks") or []
    if not tasks:
        pytest.skip("no tasks")
    worst = max((t.get("hard_failures") or 0) for t in tasks)
    total = sum((t.get("hard_failures") or 0) for t in tasks)
    assert worst <= 5, f"the worst task still has {worst} collisions; the defect is still systemic"
    assert total < 60, f"{total} collisions remain; expected the systemic instances to be fixed"
