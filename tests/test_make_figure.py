"""A researcher must be able to make a compliant figure from their OWN CSV, without Python.

WHY THIS TEST
    The objective asks whether the capability is "reusable and verifiable in research scenarios".
    The evidence used to be `examples/worked_example.py` on INVENTED data -- which proves the
    functions exist, not that a stranger can use them.

    `scripts/make_figure.py` is the path a researcher actually takes: their CSV, a journal column
    width, optionally a reference figure. These tests drive that command end to end on a CSV that
    is NOT the benchmark's and check the RENDERED file, not the return value.

THE BUGS THIS FILE PINS (all found by running it once on a real table):
    1. the CLI passed an EMPTY parameter dict, so every inferred figure was refused for columns
       `spec` had already resolved
    2. the intent -> skill map used INVENTED names, so `grouped_bars` had no recipe and the refusal
       looked deliberate
    3. `columns` was passed as a ratio (183/89 = 2.056) instead of the enum (1 or 2)
    4. spec supplies `xlabel`/`ylabel` that some skills do not accept, and the CLI did not filter
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "make_figure.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CLI)] + args, cwd=ROOT,
                          capture_output=True, text=True, timeout=600)


@pytest.fixture()
def survey_csv(tmp_path) -> pathlib.Path:
    """A table shaped like real survey data, with column names nobody in this repo chose."""
    rng = np.random.default_rng(0)
    rows = []
    for site in ("north", "south", "east", "west"):
        for year in range(2015, 2025):
            rows.append({"site": site, "year": year,
                         "mean_index": round(0.3 + rng.normal(0, 0.05), 4),
                         "se": round(abs(rng.normal(0.01, 0.003)), 4)})
    path = tmp_path / "survey.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_a_strangers_csv_becomes_a_compliant_figure(survey_csv, tmp_path):
    out = tmp_path / "fig"
    cp = _run([str(survey_csv), "--out", str(out)])
    assert cp.returncode == 0, cp.stdout[-3000:] + cp.stderr[-2000:]
    assert "RESULT: compliant" in cp.stdout
    assert (tmp_path / "fig.pdf").is_file(), "no PDF was written"
    assert (tmp_path / "fig.png").is_file(), "no preview PNG was written"


def test_the_output_is_at_the_requested_nature_width(survey_csv, tmp_path):
    """The audit must confirm the RENDERED width, not the width we asked for."""
    for choice, expected in (("1", 89.0), ("2", 183.0)):
        out = tmp_path / f"fig{choice}"
        cp = _run([str(survey_csv), "--out", str(out), "--columns", choice])
        assert cp.returncode == 0, cp.stdout[-2000:]
        assert f"width {expected} mm" in cp.stdout, (
            f"--columns {choice} did not render at {expected} mm:\n{cp.stdout[-1500:]}")


def test_a_second_shape_is_inferred_differently(tmp_path):
    """A two-column ranked table must not be drawn as grouped bars."""
    path = tmp_path / "ranked.csv"
    pd.DataFrame({"region": [f"r{i}" for i in range(6)],
                  "score": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]}).to_csv(path, index=False)
    cp = _run([str(path), "--out", str(tmp_path / "ranked")])
    assert cp.returncode == 0, cp.stdout[-2000:]
    assert "ranked_composition" in cp.stdout
    assert "RESULT: compliant" in cp.stdout


def test_a_reference_figure_transfers_its_style(survey_csv, tmp_path):
    """The reference is an INPUT; the pipeline measures it and applies it."""
    base = tmp_path / "base"
    assert _run([str(survey_csv), "--out", str(base)]).returncode == 0
    styled = tmp_path / "styled"
    cp = _run([str(survey_csv), "--out", str(styled), "--reference", str(tmp_path / "base.pdf")])
    assert cp.returncode == 0, cp.stdout[-2000:]
    assert "reference style" in cp.stdout
    assert "style.profile" in cp.stdout, "the style step is not in the operator trace"


def test_an_ambiguous_table_is_refused_with_a_reason(tmp_path):
    """A tool that silently draws the wrong chart is worse than one that says it cannot."""
    path = tmp_path / "weird.csv"
    pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]}).to_csv(path, index=False)
    cp = _run([str(path), "--out", str(tmp_path / "weird")])
    # either it draws something compliant, or it refuses with a reason and exit 2
    if cp.returncode != 0:
        assert cp.returncode == 2
        assert "REFUSED" in cp.stdout or "cannot" in cp.stdout.lower(), cp.stdout[-1500:]


def test_a_missing_file_is_reported_not_crashed(tmp_path):
    cp = _run([str(tmp_path / "nope.csv"), "--out", str(tmp_path / "x")])
    assert cp.returncode != 0
    # the CLI reports the missing file rather than raising a traceback
    combined = cp.stdout + cp.stderr
    assert ("file not found" in combined or "cannot read" in combined), combined[-800:]
    assert "Traceback" not in combined, "a missing input must not produce a traceback"


def test_the_intent_map_is_the_one_shared_map():
    """THE BUG: the CLI used to keep its own map, built from a hand-picked sample.

    It missed `trend_with_uncertainty`, which a dated time series produces, and the refusal looked
    deliberate. There is now ONE map (`spec.INTENT_RECIPES`) and the CLI calls it.
    """
    sys.path.insert(0, str(ROOT))
    from figpipe import grammar, spec
    src = CLI.read_text(encoding="utf-8")
    assert "spec.recipe_for" in src, (
        "the CLI keeps its own intent map; a second copy is a second chance to diverge")
    missing = sorted(set(grammar.INTENTS) - set(spec.INTENT_RECIPES))
    assert not missing, f"the shared map has no recipe for {missing}"


@pytest.fixture()
def faceted_csv(tmp_path) -> pathlib.Path:
    """One measure across four conditions -- the shape a faceted research figure has."""
    rows = []
    for cond in ("ctrl", "drugA", "drugB", "drugC"):
        for i in range(25):
            rows.append({"condition": cond, "value": 0.3 + (i % 7) * 0.05})
    path = tmp_path / "faceted.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_a_faceted_table_becomes_a_multi_panel_figure(faceted_csv, tmp_path):
    """A research figure is usually several panels; the CLI must reach that capability."""
    out = tmp_path / "facet"
    cp = _run([str(faceted_csv), "--out", str(out), "--facet", "condition", "--value", "value"])
    assert cp.returncode == 0, cp.stdout[-3000:] + cp.stderr[-2000:]
    assert "4 panels" in cp.stdout, cp.stdout[-1500:]
    assert "RESULT: compliant" in cp.stdout
    assert (tmp_path / "facet.pdf").is_file()


def test_faceting_past_the_panel_budget_is_refused(faceted_csv, tmp_path):
    """Dropping panels changes what the figure claims, so it must refuse, not truncate."""
    cp = _run([str(faceted_csv), "--out", str(tmp_path / "x"),
               "--facet", "condition", "--value", "value", "--max-panels", "2"])
    assert cp.returncode == 2, cp.stdout[-1200:]
    assert "REFUSED" in cp.stdout
    assert "changes what the figure claims" in cp.stdout


def test_faceting_needs_a_value_column(faceted_csv, tmp_path):
    cp = _run([str(faceted_csv), "--out", str(tmp_path / "x"), "--facet", "condition"])
    assert cp.returncode != 0
    assert "--value" in (cp.stdout + cp.stderr)


def test_faceting_a_missing_column_is_reported(faceted_csv, tmp_path):
    cp = _run([str(faceted_csv), "--out", str(tmp_path / "x"),
               "--facet", "nope", "--value", "value"])
    assert cp.returncode != 0
    # SystemExit writes to stderr; a user reads both streams
    assert "is not a column" in (cp.stdout + cp.stderr)


def test_a_single_numeric_column_can_be_faceted():
    """THE BUG: `of="hist"` used to fail asking for a SECOND numeric column.

    `op_layout_facets` built all three encoder parameter dicts before selecting one, so the
    trend/scatter branches called `_second_numeric()` even for a histogram. A table with one
    numeric column -- the commonest faceted table there is -- failed.
    """
    sys.path.insert(0, str(ROOT))
    from figpipe import skills
    df = pd.DataFrame({"condition": ["a"] * 20 + ["b"] * 20,
                       "value": list(range(40))})
    res = skills.run("faceted_distribution", df, out_stem=None,
                     value="value", by="condition", of="hist")
    assert res["panels"] == 2
    assert res["hard_failures"] == 0, res["findings"]


def test_facet_and_reference_can_be_combined(survey_csv, faceted_csv, tmp_path):
    """THE BUG: `--facet ... --reference ...` silently produced an UNSTYLED figure.

    The facet path ran before the reference was even loaded, and `run_facet` never accepted style
    parameters -- so the command reported success while ignoring an argument the user passed. That
    is this project's class-A defect (a control that looks present and does nothing) in the CLI.
    """
    base = tmp_path / "ref"
    assert _run([str(survey_csv), "--out", str(base), "--columns", "1"]).returncode == 0

    out = tmp_path / "combo"
    cp = _run([str(faceted_csv), "--out", str(out),
               "--facet", "condition", "--value", "value",
               "--reference", str(tmp_path / "ref.pdf")])
    assert cp.returncode == 0, cp.stdout[-3000:] + cp.stderr[-2000:]
    # the style step MUST appear in the operator trace, or the argument was ignored
    assert "style.profile" in cp.stdout, (
        "the reference was accepted but never applied; the trace shows no style step:\n"
        + cp.stdout[-2000:])
    assert "reference style:" in cp.stdout
    assert "4 panels" in cp.stdout
    assert "RESULT: compliant" in cp.stdout


def test_a_bad_reference_is_reported_not_ignored(survey_csv, tmp_path):
    """A missing reference must fail loudly, not silently fall back to the default style."""
    cp = _run([str(survey_csv), "--out", str(tmp_path / "x"),
               "--reference", str(tmp_path / "nope.pdf")])
    assert cp.returncode != 0
    combined = cp.stdout + cp.stderr
    assert "cannot read reference" in combined, combined[-800:]


def test_every_declared_cli_argument_is_actually_read():
    """A flag that promises something and does nothing is this project's class-A defect.

    Found by asking the question systematically: `--quiet` was declared and never read. Two more
    were worse -- `--reference` was accepted by the facet path and silently ignored, producing an
    UNSTYLED figure while reporting success.
    """
    import re
    src = CLI.read_text(encoding="utf-8")
    declared = set(re.findall(r'ap\.add_argument\("--([\w-]+)"', src))
    declared |= set(re.findall(r'ap\.add_argument\("(csv)"', src))
    assert declared, "no arguments found; the scan is looking at the wrong file"
    unread = []
    for arg in sorted(declared):
        attr = arg.replace("-", "_")
        if f"args.{attr}" not in src:
            unread.append(arg)
    assert not unread, (
        f"these CLI arguments are declared but never read, so they do nothing: {unread}")


def test_quiet_actually_suppresses_output(survey_csv, tmp_path):
    cp = _run([str(survey_csv), "--out", str(tmp_path / "q"), "--quiet"])
    assert cp.returncode == 0, cp.stdout[-1500:] + cp.stderr[-1000:]
    assert cp.stdout.strip() == "", f"--quiet still printed:\n{cp.stdout[:600]}"


def test_a_drawer_valueerror_is_a_refusal_not_a_crash(tmp_path):
    """`FAILED` tells a researcher the tool broke; `REFUSED` tells them the table cannot be drawn."""
    path = tmp_path / "tiny.csv"
    pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}).to_csv(path, index=False)
    cp = _run([str(path), "--out", str(tmp_path / "t")])
    combined = cp.stdout + cp.stderr
    assert "Traceback" not in combined, "a refusal must not produce a traceback"
    if cp.returncode != 0:
        assert "REFUSED" in combined or "compliant" in combined, combined[-1200:]


@pytest.fixture()
def faceted_trend_csv(tmp_path) -> pathlib.Path:
    """A faceted table with a numeric x and y -- the shape a trend/scatter facet needs."""
    rows = []
    for cond in ("ctrl", "drugA", "drugB", "drugC"):
        for t in range(25):
            rows.append({"condition": cond, "time": t, "response": 0.3 + 0.02 * t})
    path = tmp_path / "faceted_trend.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_all_three_facet_encoders_are_reachable(faceted_csv, faceted_trend_csv, tmp_path):
    """`of` accepts hist / trend / scatter; all three must work from the CLI.

    THE BUG: `faceted_distribution` declared `of` but its `optional` tuple omitted `x` and `y`,
    and `value` sat in `required`. So a faceted TREND was refused for passing exactly the
    parameters the recipe demands. The declaration said one thing and the signature another.
    """
    cases = [
        ("hist", faceted_csv, ["--value", "value"]),
        ("trend", faceted_trend_csv, ["--x", "time", "--y", "response"]),
        ("scatter", faceted_trend_csv, ["--x", "time", "--y", "response"]),
    ]
    for of, csv, extra in cases:
        out = tmp_path / f"f_{of}"
        cp = _run([str(csv), "--out", str(out), "--facet", "condition",
                   "--facet-of", of] + extra)
        assert cp.returncode == 0, f"{of} failed:\n{cp.stdout[-2500:]}{cp.stderr[-1200:]}"
        assert "4 panels" in cp.stdout, f"{of}: {cp.stdout[-1200:]}"
        assert "RESULT: compliant" in cp.stdout


def test_a_trend_facet_without_y_is_refused(faceted_trend_csv, tmp_path):
    cp = _run([str(faceted_trend_csv), "--out", str(tmp_path / "x"),
               "--facet", "condition", "--facet-of", "trend", "--x", "time"])
    assert cp.returncode == 2, cp.stdout[-1200:] + cp.stderr[-800:]
    combined = cp.stdout + cp.stderr
    assert "needs --x" in combined or "needs --y" in combined, combined[-800:]
