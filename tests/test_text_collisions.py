"""The collision gate must catch real overlaps and stay quiet on rotated labels.

WHY THIS FILE EXISTS
    The reproduction figures kept sprouting text-on-text defects, and the check that should have
    caught them had two holes:

    1. it was DISABLED in the reproduction renders (`check_overlap=False`), and
    2. its span-bbox form reports 22 "collisions" on Fig 1a, whose 20 country names are rotated
       45 degrees -- the boxes overlap, the glyphs do not.

    A check that is off where the defects are, or cries wolf on a legitimate layout, is the same
    failure shape this project keeps finding: a control that looks present and does nothing.
    These tests prove the glyph-level gate fires on a real overlap and stays silent on rotated
    labels, in both directions.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, grammar, layout  # noqa: E402


def _save(fig, tmp_path: pathlib.Path, name: str) -> pathlib.Path:
    paths = layout.save(fig, tmp_path / name)
    return pathlib.Path(paths[0])


def test_deliberate_overlap_is_detected(tmp_path):
    """POSITIVE CONTROL: two strings printed at the same point must be reported."""
    fig, _, _ = layout.figure(columns=1.0, height_mm=50.0)
    fig.text(0.20, 0.50, "abcdefghij", fontsize=6)
    fig.text(0.20, 0.50, "0123456789", fontsize=6)
    pdf = _save(fig, tmp_path, "overlap")
    hits = audit.overlapping_glyphs(pdf)
    assert hits, "two text runs printed on top of each other were not detected"
    assert hits[0]["glyph_pairs"] > 0


def test_rotated_labels_are_not_reported_as_collisions(tmp_path):
    """NEGATIVE CONTROL: the rotated country names of a ranked panel are clean."""
    df = pd.DataFrame({"country": [f"Country name {i}" for i in range(20)],
                       "pct": np.linspace(0.20, 0.01, 20)})
    panel = grammar.panel("ranked_composition", df, label="country", value="pct",
                          percent=True, xtick_rotation=45)
    fig = grammar.plate([panel], columns=1.0, margins={"bottom": 30.0})
    pdf = _save(fig, tmp_path, "rotated")
    assert audit.overlapping_glyphs(pdf) == [], (
        "rotated tick labels were reported as collisions; the glyph-level test has regressed "
        "to the span-bbox behaviour it exists to replace")


def test_the_reproduction_report_keeps_the_gate_on():
    """The stored report must show zero glyph collisions for every reproduced figure."""
    report = ROOT / "templates" / "seed" / "report.json"
    if not report.is_file():
        pytest.skip("no reproduction report yet")
    import json
    r = json.loads(report.read_text(encoding="utf-8"))
    assert r["self_check"]["text_collisions"] == 0, (
        "a reproduced figure has text printed on text")
    for f in r["figures"]:
        assert f["text_collisions"] == [], f"{f['figure']}: {f['text_collisions'][:2]}"
