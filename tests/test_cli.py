"""The CLI must wrap the library, not reimplement it, and its exit code must mean something.

WHY THIS EXISTS
    The five README entry points are all `import`-first, which is right for a library and wrong for the
    one thing most users need first: check a PDF they already made. A researcher holding a rejected
    figure does not want a REPL; they want

        figpipe audit figure.pdf --expect-width 183

    and an exit code they can put in a Makefile.

THE TWO PROPERTIES THAT MATTER
    1. **The exit code is the verdict.** `audit` returns 1 for a figure that is not submittable, 2 for a
       missing file, 0 otherwise. A CLI whose exit code is always 0 is a logging tool.
    2. **The CLI calls the same function the library does.** A CLI that reimplements a check is a second
       implementation to keep in sync -- the defect this project records most often.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

pd = pytest.importorskip("pandas")


def _run(args, cwd):
    """Run the CLI as a SUBPROCESS, the way a Makefile would."""
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run([sys.executable, "-m", "figpipe.cli", *args],
                          capture_output=True, text=True, cwd=str(cwd), env=env, timeout=300)


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    """One real figure, rendered by the CLI itself so the test exercises the whole path."""
    work = tmp_path_factory.mktemp("cli")
    csv = work / "data.csv"
    csv.write_text("year,mean\n" + "\n".join(f"{2010 + i},{0.1 * i:.2f}" for i in range(12)),
                   encoding="utf-8")
    r = _run(["render", str(csv), "--x", "year", "--y", "mean", "--out", "fig"], work)
    assert r.returncode == 0, f"render failed: {r.stderr[-400:]}"
    pdf = work / "fig.pdf"
    assert pdf.is_file(), f"render reported success but wrote no PDF: {list(work.iterdir())}"
    return work, pdf


def test_render_produces_a_pdf(rendered):
    work, pdf = rendered
    assert pdf.stat().st_size > 1000


def test_audit_returns_zero_for_a_compliant_figure(rendered):
    work, pdf = rendered
    r = _run(["audit", str(pdf), "--expect-width", "183"], work)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK" in r.stdout


def test_audit_returns_one_for_a_figure_that_fails(rendered):
    """THE EXIT CODE IS THE VERDICT. Asking for the wrong width must fail."""
    work, pdf = rendered
    r = _run(["audit", str(pdf), "--expect-width", "89"], work)
    assert r.returncode == 1, (
        f"audit exited {r.returncode} for a 183 mm figure judged against 89 mm; a CLI whose exit code "
        f"is always 0 cannot gate a build. stdout: {r.stdout[:200]}")
    assert "NOT SUBMITTABLE" in r.stdout


def test_audit_returns_two_for_a_missing_file(rendered):
    """A usage error is not a compliance failure; the codes must be distinguishable."""
    work, _ = rendered
    r = _run(["audit", str(work / "does-not-exist.pdf")], work)
    assert r.returncode == 2, r.stdout + r.stderr


def test_style_reports_the_reference_profile(rendered):
    work, pdf = rendered
    r = _run(["style", str(pdf)], work)
    assert r.returncode == 0, r.stdout + r.stderr
    import json
    data = json.loads(r.stdout)
    assert data["sizes_pt"], data
    assert data["colours"], data


def test_style_ranks_candidates(rendered):
    work, pdf = rendered
    r = _run(["style", str(pdf), str(pdf)], work)
    assert r.returncode == 0, r.stdout + r.stderr
    import json
    data = json.loads(r.stdout)
    assert "choice" in data, data


def test_the_cli_calls_the_library_rather_than_copying_it():
    """THE STRUCTURAL PROPERTY. `figpipe.cli` must import from `figpipe`, not reimplement a check."""
    src = (ROOT / "figpipe" / "cli.py").read_text(encoding="utf-8")
    assert "from figpipe import" in src, "the CLI does not import the library"
    # the checks themselves must NOT appear here
    for forbidden in ("get_text(", "page.get_drawings", "MEDIABOX", "findings.append"):
        assert forbidden not in src, (
            f"figpipe/cli.py contains {forbidden!r}, which means it reimplements a check instead of "
            f"calling the library")


def test_the_entry_point_is_declared():
    """A CLI nobody can install is a script in a repo."""
    import tomllib
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = data.get("project", {}).get("scripts") or {}
    assert scripts.get("figpipe") == "figpipe.cli:main", scripts
