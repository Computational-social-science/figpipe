"""The decision bridge must be explicit: a calibrated choice, or a named failure.

WHY THESE TESTS
    StartLux-Decision is a shared operator outside this repo. The failure mode that matters is
    the one this project has fought repeatedly: a control that looks present and does nothing --
    e.g. a decision client that silently falls back to a regex or a guess when the service is
    down. These tests pin the contract:

      * a valid choice is returned with its confidence
      * none_probability >= threshold -> DecisionRejected (a forced choice is not a free one)
      * a choice outside the offered options -> DecisionUnavailable
      * an unreachable client -> DecisionUnavailable (no heuristic, no default)
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

decision = pytest.importorskip("figpipe.decision", reason="decision bridge absent")


class FakeResult(dict):
    @property
    def none_probability(self):
        return self.get("none_probability")

    @property
    def confidence(self):
        return self.get("confidence")


class FakeClient:
    NONE_THRESHOLD = 0.2

    def __init__(self, result=None):
        self.result = result

    def choose(self, instructions, options, evidence, **controls):
        return FakeResult(self.result)

    def health(self, timeout=5.0):
        return {"up": True, "url": "http://fake"}


def good(choice="histogram", none_p=0.02):
    return {"choice": choice, "confidence": 0.81, "none_probability": none_p,
            "probabilities": {choice: 0.81}, "_model": "fake"}


def test_a_valid_choice_is_returned(monkeypatch):
    monkeypatch.setattr(decision, "_client", lambda: FakeClient(good()))
    res = decision.choose("pick", {"histogram": "a histogram", "matrix_plate": "a matrix"},
                          {"columns": ["x", "y"]})
    assert res["choice"] == "histogram"
    assert res["confidence"] == 0.81
    assert res["model"] == "fake"


def test_none_probability_rejects_a_forced_choice(monkeypatch):
    monkeypatch.setattr(decision, "_client", lambda: FakeClient(good(none_p=0.55)))
    with pytest.raises(decision.DecisionRejected, match="none_probability"):
        decision.choose("pick", {"histogram": "a histogram"}, {"columns": ["x"]})


def test_a_choice_outside_the_options_is_unavailable(monkeypatch):
    monkeypatch.setattr(decision, "_client", lambda: FakeClient(good(choice="magic")))
    with pytest.raises(decision.DecisionUnavailable, match="not one of"):
        decision.choose("pick", {"histogram": "a histogram"}, {"columns": ["x"]})


def test_unreachable_service_never_falls_back(monkeypatch):
    def boom():
        raise decision.DecisionUnavailable("service down")
    monkeypatch.setattr(decision, "_client", boom)
    with pytest.raises(decision.DecisionUnavailable):
        decision.choose("pick", {"histogram": "a histogram"}, {"columns": ["x"]})


def test_health_reports_down_without_raising(monkeypatch):
    def boom():
        raise decision.DecisionUnavailable("service down")
    monkeypatch.setattr(decision, "_client", boom)
    assert decision.health()["up"] is False


def test_choose_skill_offers_only_figpipe_contract_names(monkeypatch):
    seen = {}

    class Client(FakeClient):
        def choose(self, instructions, options, evidence, **controls):
            seen["options"] = set(options)
            seen["instructions"] = instructions
            return FakeResult(good(choice="scatter_relationship"))

    monkeypatch.setattr(decision, "_client", lambda: Client())
    res = decision.choose_skill("Scatter", ["x", "y"], evidence={"panel_mode": "single"})
    assert res["choice"] == "scatter_relationship"
    assert seen["options"] == set(decision.SKILL_OPTIONS)
    assert "Scatter" in seen["instructions"]
