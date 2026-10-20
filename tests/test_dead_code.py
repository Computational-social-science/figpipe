"""No module may compute a value and never read it.

WHY THIS TEST
    Round 28 learned that a substring is not an identity. Following that outward: is this control
    connected to ANYTHING? A local variable that is assigned and never read is the same defect in
    its most literal form -- code that looks like a check and does nothing.

    Fifteen turned up. Most were harmless, but three mattered:
      * slim.py computed a `hits` list and built the result from a different expression instead
      * cron_run.py computed `evolve_failed` while `ok_evolve` already carried the fact
      * skills.py bound a throwaway context to a name never read again

    The scan is mechanical, which is the point: this question can be asked of the whole codebase
    instead of one file at a time.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Names that are conventionally allowed to be assigned and unused.
ALLOWED = {"_", "__", "self", "cls"}

#: Modules scanned. Fixtures and tests may legitimately keep a value for a later reader.
TARGETS = list((ROOT / "figpipe").glob("*.py")) + list((ROOT / "scripts").glob("*.py"))


def _dead_locals(path: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        stores: dict[str, int] = {}
        loads: set[str] = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    stores.setdefault(node.id, node.lineno)
                else:
                    loads.add(node.id)
            elif isinstance(node, ast.Global):
                # `global X` means X is read by OTHER functions at module scope, so assigning it
                # here is not dead. Without this the detector flags every module-level flag.
                loads.update(node.names)
        for name, line in stores.items():
            if name in ALLOWED or name.startswith("_"):
                continue
            if name not in loads:
                out.append(f"{path.name}:{line} {fn.name}() assigns {name!r} and never reads it")
    return out


def test_no_module_assigns_a_value_it_never_reads():
    offenders = []
    for path in TARGETS:
        offenders.extend(_dead_locals(path))
    assert not offenders, (
        "these assignments are computed and never used, so they are code that looks like a check "
        "and does nothing:\n  " + "\n  ".join(offenders))


def test_the_scan_can_fail():
    """NEGATIVE CONTROL: a synthetic module with a dead assignment must be caught."""
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp())
    f = d / "deadmod.py"
    f.write_text("def f():\n    used = 1\n    unused = 2\n    return used\n", encoding="utf-8")
    found = _dead_locals(f)
    assert any("unused" in x for x in found), (
        f"the scan did not catch a dead assignment; it reported {found}")
    import shutil
    shutil.rmtree(d, ignore_errors=True)


def test_the_uncertainty_column_is_not_dropped_silently():
    """THE DEFECT: `err` was detected and never passed, so error bars were silently omitted.

    The scan found it as a dead assignment. Wiring it through then exposed two further problems,
    both real:
      * `ci95_lower` is a LOWER BOUND, not a magnitude -- passing it as yerr gives negative values
        and matplotlib refuses (correctly)
      * the column may not exist in every panel subset, so the split raised KeyError

    The rule that survives all three: use the column as `err` ONLY when it is non-negative and
    present in every panel; otherwise draw without error bars AND say so in the rationale.
    """
    import inspect
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_plottwin as bench
    src = inspect.getsource(bench.choose_reading)
    assert "params[\"err\"]" in src or "params['err']" in src, (
        "the mapper no longer passes the error column; error bars are silently omitted")
    assert "(col >= 0).all()" in src, (
        "the mapper does not check that the uncertainty column is a magnitude; a lower BOUND "
        "passed as yerr raises 'must not contain negative values'")
    assert "not a magnitude" in src, (
        "an omitted uncertainty column must be recorded in the rationale, not dropped silently")


def test_aggregation_keeps_the_error_column():
    """`split_panels` aggregated only the value column, so `err` vanished and the child raised
    KeyError on a column the caller had legitimately supplied -- three benchmark tasks failed."""
    import sys
    sys.path.insert(0, str(ROOT))
    import pandas as pd
    from figpipe import skills
    df = pd.DataFrame({
        "panel": ["A"] * 20 + ["B"] * 20,
        "lab": [f"c{i % 4}" for i in range(40)],
        "val": [0.5] * 40,
        "ci_lower": [0.05] * 40,
    })
    res = skills.run("composite_groups", df, out_stem=None,
                     by="panel", x="lab", y="val", err="ci_lower")
    assert res["panels"] == 2
    assert res["hard_failures"] == 0, res["findings"]
    # the aggregation must SAY it carried the error column
    assert any("with ci_lower averaged" in t for t in res["trace"]), res["trace"]
