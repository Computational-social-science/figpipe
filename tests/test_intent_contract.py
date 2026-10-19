"""The declared vocabulary and the emitted vocabulary must be the same set.

WHY THIS TEST
    `grammar.INTENTS` is the DRAWING CONTRACT: its names are what every drawer, skill and recipe
    uses. `spec.infer_spec` is the DECLARING layer: it reads a table and says what to draw.

    Measured on 2026-10-20, the two had silently diverged:

        spec emitted but grammar DECLARED NOTHING for:
            grouped_bars, boxplot, scatter_fit
        grammar declared but spec NEVER emitted:
            comparison_with_error, distribution, signed_matrix

    So any code doing `grammar.panel(spec.infer_spec(df).panels[0].intent, df)` raised KeyError on
    three of six real table shapes -- and my own CLI worked around it with a hand-written map
    instead of fixing the contract. A hand-written map is a workaround that hides the defect.

    These tests pin the contract so the two vocabularies cannot diverge again.
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

from figpipe import grammar, spec  # noqa: E402


def _shapes() -> list[pd.DataFrame]:
    """Table shapes a researcher actually has, not ones chosen to make the test pass."""
    rng = np.random.default_rng(0)
    return [
        pd.DataFrame({"t": range(30), "v": rng.random(30)}),                       # numeric trend
        pd.DataFrame({"d": pd.date_range("2020-01-01", periods=30, freq="ME"),
                      "v": rng.random(30)}),                                        # dated trend
        pd.DataFrame({"g": ["a", "b"] * 15, "m1": rng.random(30),
                      "m2": rng.random(30)}),                                       # grouped measures
        pd.DataFrame({"c": ["a"] * 15 + ["b"] * 15, "v": rng.random(30)}),          # distribution
        pd.DataFrame({"lab": [f"r{i}" for i in range(6)],
                      "val": [6, 5, 4, 3, 2, 1]}),                                  # ranked
        pd.DataFrame({"x": rng.random(40), "y": rng.random(40)}),                   # relationship
        pd.DataFrame(rng.random((5, 5))),                                           # square matrix
        pd.DataFrame({"s": ["s1", "s2"] * 20, "t": list(range(20)) * 2,
                      "o": rng.random(40)}),                                        # long format
    ]


def test_every_emitted_intent_is_declared():
    """spec must not name an intent the drawing layer cannot draw."""
    undeclared = set()
    for df in _shapes():
        try:
            intent = spec.infer_spec(df).panels[0].intent
        except spec.SpecError:
            continue
        if intent not in grammar.INTENTS:
            undeclared.add(intent)
    assert not undeclared, (
        f"spec emits {sorted(undeclared)} but grammar.INTENTS does not declare them; "
        f"grammar.panel() would raise KeyError. Declared: {sorted(grammar.INTENTS)}")


def test_every_emitted_intent_can_be_drawn():
    """The stronger form: ask the drawing layer, not just the registry."""
    failures = []
    for df in _shapes():
        try:
            intent = spec.infer_spec(df).panels[0].intent
        except spec.SpecError:
            continue
        try:
            grammar.intent(intent)
        except KeyError:
            failures.append(intent)
    assert not failures, (
        f"grammar.intent() rejects {sorted(set(failures))}; a caller driving spec into grammar "
        f"would fail at runtime")


def test_every_declared_intent_has_a_cli_recipe():
    """A declared intent with no recipe is a table the CLI refuses for no good reason.

    The CLI no longer keeps its own map -- it calls `spec.recipe_for`, so this checks the ONE map.
    """
    from figpipe import grammar, spec
    missing = sorted(set(grammar.INTENTS) - set(spec.INTENT_RECIPES))
    assert not missing, (
        f"grammar declares {missing} but spec.INTENT_RECIPES has no recipe, so a table inferred "
        f"as one of them is refused as though the intent were unsupported")
    cli = ROOT / "scripts" / "make_figure.py"
    if cli.is_file():
        assert "spec.recipe_for" in cli.read_text(encoding="utf-8"), (
            "the CLI keeps its own intent map instead of importing spec.recipe_for")


def test_the_declared_set_is_not_empty():
    """Guard against the test passing because everything is empty."""
    assert grammar.INTENTS, "grammar declares no intents; the contract test is vacuous"
    assert len(grammar.INTENTS) >= 5


def test_there_is_exactly_one_intent_recipe_map():
    """Three hard-coded maps is three chances to diverge, and they DID diverge.

    The CLI's copy was built from a hand-picked sample and missed `trend_with_uncertainty`; the
    worked example had its own. `spec.INTENT_RECIPES` is now the single source, and both import it.
    """
    import re
    offenders = []
    for rel in ("scripts/make_figure.py", "examples/worked_example.py"):
        p = ROOT / rel
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        # a dict literal with several intent-looking keys is a second map
        if re.search(r'"\w+_with_\w+"\s*:', src) or src.count('": "') > 12:
            offenders.append(rel)
    assert not offenders, (
        f"these files appear to hard-code their own intent map: {offenders}; import "
        f"spec.recipe_for instead")


def test_the_shared_map_covers_every_declared_intent():
    from figpipe import grammar, spec
    missing = sorted(set(grammar.INTENTS) - set(spec.INTENT_RECIPES))
    assert not missing, f"grammar declares {missing} but spec.INTENT_RECIPES has no recipe"


def test_the_shared_map_names_real_skills():
    from figpipe import skills, spec
    bad = sorted(set(spec.INTENT_RECIPES.values()) - set(skills.SKILLS))
    assert not bad, f"INTENT_RECIPES names skills that do not exist: {bad}"
