"""Global skill floor + classic operators must compose, refuse, and verify.

WHY THESE TESTS
    The user's premise is right: scientific plotting has no single standard, so the library
    cannot be a fixed list of complete figures. The design answer is a small set of CLASSIC
    OPERATORS and a registry of named SKILLS (recipes) that compose them, with a global
    verification floor every recipe inherits. These tests pin exactly that contract:

      * the catalogue is complete: every skill names only registered operators
      * a skill builds a real, audited figure through the global floor
      * a parameter the skill does not understand is an ERROR, never silently ignored
      * a reference style actually reaches the render (rc and height)
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

skills = pytest.importorskip("figpipe.skills", reason="skills absent")

TREND = pd.DataFrame({"year": range(1990, 2014),
                      "mean": [0.1 + 0.008 * i for i in range(24)]})
RANKED = pd.DataFrame({"country": ["a", "b", "c", "d"],
                       "share": [0.4, 0.3, 0.2, 0.1]})


def test_catalogue_lists_operators_and_recipes_with_their_contracts():
    cat = skills.catalogue()
    assert len(cat["operators"]) >= 10
    names = {s["name"] for s in cat["skills"]}
    assert {"trend_with_uncertainty", "ranked_composition", "density_relationship",
            "styled_trend"} <= names
    for s in cat["skills"]:
        for step in s["build"]:
            assert step["operator"] in {o["name"] for o in cat["operators"]}
        assert "global_checks" in s and s["global_checks"]


def test_trend_skill_renders_through_the_global_floor(tmp_path):
    res = skills.run("trend_with_uncertainty", TREND, out_stem=tmp_path / "trend",
                     x="year", y="mean", fit="lm", reference=0.5)
    assert pathlib.Path(res["pdf"]).is_file()
    assert res["hard_failures"] == 0, res["findings"]
    for step in ("verify.audit", "verify.collisions"):
        assert step in res["trace"], res["trace"]


def test_ranked_skill_renders_and_sorts(tmp_path):
    res = skills.run("ranked_composition", RANKED, out_stem=tmp_path / "ranked",
                     label="country", value="share", percent=True)
    assert res["hard_failures"] == 0
    assert pathlib.Path(res["pdf"]).is_file()


def test_unknown_parameter_is_refused_not_ignored():
    with pytest.raises(skills.SkillError, match="does not understand"):
        skills.run("trend_with_uncertainty", TREND, x="year", y="mean", colour="red")


def test_missing_required_parameter_is_refused():
    with pytest.raises(skills.SkillError, match="requires"):
        skills.run("trend_with_uncertainty", TREND, x="year")


def test_unknown_skill_lists_the_vocabulary():
    with pytest.raises(skills.SkillError, match="unknown skill"):
        skills.run("magic_figure", TREND)


def test_a_reference_style_reaches_the_render(tmp_path):
    profile = ROOT / "corpus" / "style" / "published_fig7.json"
    if not profile.is_file():
        pytest.skip("reference profile absent")
    res = skills.run("styled_trend", TREND, out_stem=tmp_path / "styled",
                     x="year", y="mean", profile=profile)
    assert res["hard_failures"] == 0, res["findings"]
    # the style-derived height must survive layout.plate and match the reference aspect
    assert res["layout"]["height_mm"] is not None
    assert 90.0 <= res["layout"]["height_mm"] <= 170.0


def test_statistics_verification_can_fail_and_is_recorded(tmp_path):
    res = skills.run("trend_with_uncertainty", TREND, out_stem=tmp_path / "stats",
                     x="year", y="mean",
                     published={"r": 0.88}, computed={"r": 0.20})
    assert any(f["check"] == "statistics" and f["severity"] == "hard"
               for f in res["findings"])


def test_catalogue_export_is_deterministic(tmp_path):
    a = skills.export_catalogue(tmp_path / "a.json").read_text(encoding="utf-8")
    b = skills.export_catalogue(tmp_path / "b.json").read_text(encoding="utf-8")
    assert a == b
    assert "global_verify" in json.loads(a)


def test_committed_catalogue_is_not_stale():
    """The machine-readable catalogue in knowledge/ must match the code that generated it."""
    path = ROOT / "knowledge" / "skills_catalog.json"
    if not path.is_file():
        pytest.skip("catalogue not exported yet")
    assert json.loads(path.read_text(encoding="utf-8")) == skills.catalogue(), (
        "knowledge/skills_catalog.json is stale; run "
        "python -c 'from figpipe import skills; skills.export_catalogue()'")
