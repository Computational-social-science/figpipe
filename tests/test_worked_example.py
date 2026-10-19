"""The worked example must run, and it must keep finding real defects.

WHY THIS TEST EXISTS
    "Reusable in research scenarios" is a claim about someone ELSE being able to run the pipeline
    on their own data. The worked example is that demonstration, so it is tested like production
    code rather than kept as documentation.

    It has already earned its place twice:
      * spec inferred `grouped_bars` while the example drew a trend -- the declaration was
        decorative until the example was made to follow it
      * grouped bars drew ONE BAR PER ROW (40 rows over 2 groups), stacking labels into three
        hard text collisions that the compliance audit did not see
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "worked_example.py"


def test_the_example_exists_and_runs(tmp_path):
    if not SCRIPT.is_file():
        pytest.skip("worked example absent")
    cp = subprocess.run([sys.executable, str(SCRIPT), "--out", str(tmp_path)],
                        cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert cp.returncode == 0, cp.stdout[-3000:] + cp.stderr[-3000:]
    assert "every claim above was verified" in cp.stdout
    for name in ("figure.pdf", "emitted.py"):
        assert (tmp_path / name).is_file(), f"{name} not produced"


def test_the_public_surface_is_importable():
    """A hidden public surface is not a reusable one."""
    sys.path.insert(0, str(ROOT))
    import figpipe
    assert len(figpipe.__all__) >= 12
    for name in figpipe.__all__:
        assert hasattr(figpipe, name), f"{name} exported but not importable"


def test_grouped_bars_aggregate_to_one_bar_per_level():
    """40 rows over 2 categories must produce 2 bars, not 40 overlapping ones.

    This was a real defect: the drawer drew one bar per ROW, so tick labels stacked and collided
    while `audit` reported zero hard findings (it checks typography, not label duplication).
    """
    import numpy as np
    import pandas as pd
    sys.path.insert(0, str(ROOT))
    from figpipe import skills
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "group": ["a"] * 20 + ["b"] * 20,
        "m1": rng.normal(size=40),
        "m2": rng.normal(size=40),
    })
    res = skills.run("grouped_measures", df, out_stem=None, x="group", ycols=["m1", "m2"])
    assert res["hard_failures"] == 0, res["findings"]
    assert any("aggregate" in step for step in res["trace"]), res["trace"]
