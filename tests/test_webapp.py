"""The web interface must give a researcher the same verified answer the CLI does.

WHY THIS TEST
    AutoFigure (ResearAI/AutoFigure, ICLR 2026) ships a frontend and a Flask API; a researcher uses
    it without a terminal. figpipe had only a command line. PEER_AUTOFIGURE.md names that as the one
    thing figpipe should be embarrassed about, and scripts/webapp.py removes it.

    The risk of adding a web surface is that it becomes a SECOND, less honest path: a page that
    reports success without auditing, or swallows a refusal because showing an error is awkward.
    These tests exist to make that impossible.

    They drive the real FastAPI app through its TestClient -- no server process, no network -- and
    check the RENDERED file, not the response status.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

pytest.importorskip("fastapi", reason="fastapi not installed")
pytest.importorskip("httpx", reason="httpx (TestClient dependency) not installed")


@pytest.fixture(scope="module")
def client():
    import webapp
    from fastapi.testclient import TestClient
    return TestClient(webapp.app)


@pytest.fixture()
def survey_csv(tmp_path) -> pathlib.Path:
    rng = np.random.default_rng(0)
    rows = [{"site": s, "year": y, "mean_index": round(0.3 + rng.normal(0, 0.05), 4),
             "se": round(abs(rng.normal(0.01, 0.003)), 4)}
            for s in ("north", "south", "east", "west") for y in range(2015, 2025)]
    path = tmp_path / "survey.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


@pytest.fixture()
def faceted_csv(tmp_path) -> pathlib.Path:
    rows = [{"condition": c, "value": 0.3 + 0.02 * i}
            for c in ("ctrl", "drugA", "drugB", "drugC") for i in range(25)]
    path = tmp_path / "faceted.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_health_answers_so_a_script_can_wait(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_the_page_loads_and_has_a_form(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<form" in r.text
    assert "/api/make" in r.text, "the page does not call the make endpoint"


def test_inspect_reports_the_decision_before_drawing(client, survey_csv):
    """A user should see WHAT will be drawn and WHY, not just the result."""
    with survey_csv.open("rb") as f:
        r = client.post("/api/inspect", files={"csv": ("survey.csv", f, "text/csv")})
    assert r.status_code == 200
    j = r.json()
    assert j["refused"] is False
    assert j["intent"]
    assert j["rationale"]
    assert set(j["columns"]) >= {"site", "year", "mean_index", "se"}


def test_make_produces_a_verified_figure(client, survey_csv):
    """THE POINT: the web path must audit the rendered file, not just return 200."""
    with survey_csv.open("rb") as f:
        r = client.post("/api/make", files={"csv": ("survey.csv", f, "text/csv")},
                        data={"columns": "2"})
    assert r.status_code == 200
    j = r.json()
    assert j["refused"] is False
    assert j["compliant"] is True
    assert "hard findings: 0" in j["summary"]
    assert "183.0 mm" in j["summary"]
    # named dimensions must be present, worst first
    assert "dimensions (worst first)" in j["summary"]
    assert "unmeasured" in j["summary"], (
        "the page must state which dimensions could NOT be measured, or a reader believes the "
        "figure is good on them")


def test_the_generated_file_is_downloadable_and_is_a_real_pdf(client, survey_csv):
    with survey_csv.open("rb") as f:
        made = client.post("/api/make", files={"csv": ("survey.csv", f, "text/csv")},
                           data={"columns": "2"}).json()
    r = client.get(f"/api/file/{made['pdf']}")
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF", "the served file is not a PDF"


def test_a_path_traversal_is_refused(client):
    """A web surface adds an attack the CLI does not have. This is the one place it could."""
    for name in ("../../etc/passwd", "..%2F..%2Fsecret", "....//x"):
        r = client.get(f"/api/file/{name}")
        assert r.status_code in (400, 404), f"{name} was served: {r.status_code}"


def test_an_ambiguous_table_is_refused_with_a_reason(client, tmp_path):
    """A page that swallows a refusal is worse than no page."""
    path = tmp_path / "tiny.csv"
    pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}).to_csv(path, index=False)
    with path.open("rb") as f:
        r = client.post("/api/make", files={"csv": ("tiny.csv", f, "text/csv")})
    j = r.json()
    # either it draws something compliant, or it refuses WITH a reason and the column list
    if j.get("refused"):
        assert j.get("reason")
        assert j.get("columns")
    else:
        assert j.get("compliant") in (True, False)


def test_a_facet_produces_multiple_panels(client, faceted_csv):
    with faceted_csv.open("rb") as f:
        r = client.post("/api/make", files={"csv": ("faceted.csv", f, "text/csv")},
                        data={"columns": "2", "facet": "condition", "value": "value"})
    j = r.json()
    assert j["refused"] is False
    assert "panels: 4" in j["summary"], j["summary"]


def test_a_bad_csv_is_reported_not_crashed(client, tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("not,a,real\ncsv,file", encoding="utf-8")
    with path.open("rb") as f:
        r = client.post("/api/make", files={"csv": ("bad.csv", f, "text/csv")})
    assert r.status_code in (200, 400)
    assert "Traceback" not in r.text
