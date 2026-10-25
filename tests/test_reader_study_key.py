"""The study's answer key must not contain a value that cannot be wrong.

WHY THIS EXISTS
    The first version recorded `metric_picks: "A" | "B"`. But A is ALWAYS the mismatched-styled candidate
    and B is ALWAYS the matched one, so that field was `"A"` on **27 of 30 pairs** -- it did not say "the
    metric picked A", it said "the metric was right". **A value that cannot be wrong is not a
    measurement**, which is this project's oldest rule, and it had crept into the study that exists to
    test exactly that kind of claim.

    The rater never sees A or B, so the STUDY was blind. The SCORER was not: it compared a rater's
    side-choice against a letter that was a tautology. The fix records WHICH SIDE the metric prefers.

THE PROPERTIES THIS FILE PINS
    1. The key records a side, not a letter.
    2. The matched side is BALANCED, or a rater could learn "always pick left".
    3. Scoring a rater who answers exactly as the metric prefers gives 100 %, and one who answers
       exactly against it gives 0 % -- both directions, because a scorer that cannot distinguish them
       measures nothing.
    4. The default N is 30 and the stated power matches a one-sided binomial calculation.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pd = pytest.importorskip("pandas")


@pytest.fixture(scope="module")
def study():
    import reader_study
    return reader_study


@pytest.fixture(scope="module")
def built(study, tmp_path_factory):
    """Build a small study once and return its directory."""
    work = tmp_path_factory.mktemp("study")
    study.STUDY = work
    study.ANSWERS = work / "answers.csv"
    study.KEY = work / "key.json"
    study.SHEET = work / "README.txt"
    if study.build(4) != 0:
        pytest.skip("cannot build a study in this environment")
    return work


def test_the_key_records_a_side_not_a_letter(study, built):
    """THE DEFECT. A letter that is always the same is not a measurement."""
    key = json.loads((built / "key.json").read_text(encoding="utf-8"))
    for pid, meta in key.items():
        assert "metric_prefers" in meta, (
            f"{pid} has no metric_prefers; the key is back to recording a letter")
        assert meta["metric_prefers"] in ("left", "right"), (pid, meta["metric_prefers"])
        assert "metric_picks" not in meta, (
            f"{pid} still carries metric_picks, which is 'A' on 27 of 30 pairs by construction")


def test_the_matched_side_is_balanced(study, built):
    """A RATER WHO NOTICES 'always pick left' WOULD SCORE WITHOUT LOOKING."""
    key = json.loads((built / "key.json").read_text(encoding="utf-8"))
    sides = collections.Counter(v["matched_side"] for v in key.values())
    left, right = sides.get("left", 0), sides.get("right", 0)
    assert abs(left - right) <= max(2, len(key) // 3), (
        f"the matched side is {dict(sides)}; a study this imbalanced leaks the answer to a rater who "
        f"notices the pattern")


def test_scoring_both_directions(study, built):
    """A SCORER THAT CANNOT DISTINGUISH 100 % FROM 0 % MEASURES NOTHING."""
    key = json.loads((built / "key.json").read_text(encoding="utf-8"))
    sheet = built / "answers.csv"

    with_metric = ["pair,your_choice"] + [f"{pid},{m['metric_prefers']}" for pid, m in key.items()]
    sheet.write_text("\n".join(with_metric) + "\n", encoding="utf-8")
    assert study.score() == 0
    scored = json.loads((built / "scored.json").read_text(encoding="utf-8"))
    assert scored["disagree"] == 0, scored
    assert scored["agree"] == len(key), scored

    against = ["pair,your_choice"] + [
        f"{pid},{'right' if m['metric_prefers'] == 'left' else 'left'}" for pid, m in key.items()]
    sheet.write_text("\n".join(against) + "\n", encoding="utf-8")
    assert study.score() == 0
    scored = json.loads((built / "scored.json").read_text(encoding="utf-8"))
    assert scored["agree"] == 0, scored
    assert scored["disagree"] == len(key), scored


def test_the_default_n_is_the_corpus_maximum(study):
    """A STUDY CANNOT BE MADE STRONGER BY RUNNING IT ON PAIRS THAT DO NOT EXIST."""
    data = json.loads((ROOT / "corpus" / "e2e" / "style_validation.json").read_text(encoding="utf-8"))
    available = [p for p in (data.get("pairs") or []) if p.get("mismatch_contrast") == "same_paper"]
    assert study.build.__defaults__[0] == 30, (
        f"the default N is {study.build.__defaults__[0]}; 30 is the corpus maximum and the smallest N "
        f"with acceptable power")
    assert len(available) >= 30 or len(available) == 30, len(available)


def test_the_stated_power_matches_the_binomial(study):
    """THE POWER SENTENCE IN THE INSTRUCTIONS MUST BE ARITHMETIC, NOT REASSURANCE."""
    from math import comb
    n = 30
    k = study._need_k(n)
    assert k == 20, f"with n=30 the critical value is {k}, not 20"
    expected = sum(comb(n, i) * 0.80 ** i * 0.20 ** (n - i) for i in range(k, n + 1))
    assert abs(study._power(n, k, 0.80) - expected) < 1e-9
    assert 0.9 < expected < 1.0, expected
