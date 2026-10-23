"""A zero must say what it was a zero over.

WHY THIS EXISTS
    Rounds 82-86 established that a count of zero is ambiguous, and the project got it wrong twice in
    opposite directions:

        legend_occlusions: 0 over 139 figures, of which NONE has a legend   -> VACUOUS
        text_collision:    0 over 139 figures carrying 101-245 glyphs each  -> MEANINGFUL

    The second could only be told from the first because the glyph count was measured BY HAND in a
    test. A hand measurement is not a mechanism.

WHAT THIS PINS
    Every check in `audit.audit()` now returns an `Examined` record: what it examined (its own units),
    and what it found. Three states, not two:

        pass            found nothing, and examined something
        findings        found something
        not_exercised   found nothing because there was NOTHING TO EXAMINE

    The third state is the one that was missing, and reporting it as `pass` is exactly how a vacuous
    zero gets read as a clean result.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("pymupdf")


def _line_figure(tmp_path, *, text=True):
    import matplotlib
    matplotlib.use("Agg")
    from figpipe import composite, layout

    plt_mod = __import__("matplotlib.pyplot", fromlist=["pyplot"])
    plt_mod.rcdefaults()
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"x": np.arange(12), "a": rng.random(12), "b": rng.random(12)})
    panel = composite.Panel("line_series", df, {"x": "x", "ycols": ["a", "b"]})
    fig = composite.composite([panel], columns=1.0, height_mm=60.0, letters=False)
    pdf = layout.save(fig, tmp_path / "f")[0]
    if not text:
        # strip every label so the text checks have nothing to examine
        import matplotlib.pyplot as plt2
        plt2.close(fig)
        fig2, ax2 = plt2.subplots(figsize=(2.0, 2.0))
        ax2.plot([0, 1], [0, 1])
        ax2.set_xticks([])
        ax2.set_yticks([])
        for s in ax2.spines.values():
            s.set_visible(False)
        pdf = tmp_path / "notext.pdf"
        fig2.savefig(pdf)
        plt2.close(fig2)
    return pdf


def test_every_check_reports_a_denominator(tmp_path):
    """THE MECHANISM. A finding count with no denominator cannot be read."""
    from figpipe import audit

    report = audit.audit(_line_figure(tmp_path))
    ex = report.get("examined") or {}
    checks = ex.get("checks") or []
    assert checks, "the audit reports no examined records"
    for c in checks:
        assert "denominator" in c, f"{c['check']} has no denominator"
        assert "unit" in c and c["unit"], f"{c['check']} does not name its unit"
        assert "state" in c
        assert c["state"] in ("pass", "findings", "not_exercised")


def test_a_figure_with_text_PASSES_the_text_checks(tmp_path):
    """A real figure: the text checks examined something and found nothing wrong."""
    from figpipe import audit

    report = audit.audit(_line_figure(tmp_path))
    checks = {c["check"]: c for c in report["examined"]["checks"]}
    assert checks["font_size"]["denominator"] > 0
    assert checks["font_size"]["state"] == "pass"
    assert checks["overlap"]["denominator"] > 0


def test_a_figure_with_NO_TEXT_reports_NOT_EXERCISED(tmp_path):
    """THE STATE THAT WAS MISSING. A page with no text must not report 'pass' on text checks."""
    from figpipe import audit

    report = audit.audit(_line_figure(tmp_path, text=False))
    checks = {c["check"]: c for c in report["examined"]["checks"]}
    for name in ("font_size", "overlap"):
        assert checks[name]["denominator"] == 0, (
            f"{name} found {checks[name]['denominator']} objects on a page with no text")
        assert checks[name]["state"] == "not_exercised", (
            f"{name} reports '{checks[name]['state']}' on a page with no text; a zero over no "
            f"objects is not a pass")


def test_the_summary_keeps_not_exercised_APART_from_pass(tmp_path):
    """THE AGGREGATE DEFECT. Counting the two together gives '0 problems' over checks that never ran."""
    from figpipe import audit

    report = audit.audit(_line_figure(tmp_path, text=False))
    ex = report["examined"]
    assert ex["n_pass"] == 0, f"{ex['n_pass']} checks reported a pass on a page with no text"
    assert ex["n_not_exercised"] > 0
    assert "NOTHING" in ex["verdict"] or "not a pass" in ex["verdict"]


def test_the_examined_record_states_its_own_conclusion():
    """A record that needs a second computation to be read is a record that will be read wrong."""
    from figpipe.examined import Examined

    assert Examined("c", 10, "glyphs", 0).state == "pass"
    assert Examined("c", 10, "glyphs", 3).state == "findings"
    assert Examined("c", 0, "glyphs", 0).state == "not_exercised"
    # and the one that used to be indistinguishable
    assert Examined("c", 0, "glyphs", 0).state != Examined("c", 10, "glyphs", 0).state


def test_a_zero_denominator_is_never_reported_as_a_pass():
    """THE RULE, exhaustively. Any finding count over zero objects is not_exercised."""
    from figpipe.examined import NOT_EXERCISED, Examined

    for n_findings in (0, 1, 5):
        assert Examined("c", 0, "glyphs", n_findings).state == NOT_EXERCISED
