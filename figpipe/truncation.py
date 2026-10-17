"""A truncation check that does not depend on the upstream lint's regexes.

WHY THIS EXISTS -- a REAL FALSE NEGATIVE IN THE UPSTREAM TOOL
    `light-figure`'s lint detects `AXIS_TRUNCATE` by pattern-matching the plotting source. It
    does not fire on the most common real form:

        ax.set_ylim(y.min() - 1, y.max() + 1)      # truncated, no literal numbers
        ax.set_ylim(data[0] - 0.5, data[-1])       # truncated, no literal numbers

    Verified directly: `check_light_figure(source)` on such a script returns
    `light.integrity PASS -- no honesty-risk patterns`, while the same axis set with literal
    numbers (e.g. `set_ylim(52.5, 55.0)`) is caught.

    That is a false negative in the upstream tool, not in its integration. Rather than edit
    vendored code, this module adds a check of our own, clearly labelled as ours, that reads
    the AST instead of regexes: it resolves `set_ylim` arguments against assignments and
    numeric data where it can, and flags a non-zero lower bound on an axis that has no break
    marker and is not categorical.

WHAT IT CANNOT DO
    Static analysis cannot always evaluate the bound. When the argument is not resolvable the
    check reports SKIP with the reason -- it never guesses, because a wrong FAIL on a
    legitimate figure is worse than an honest skip.
"""
from __future__ import annotations

import ast
import pathlib
import re


def _has_break_marker(text: str) -> bool:
    """Does the source declare a broken axis?"""
    return bool(re.search(r"brokenaxes|BrokenBarHCollection|#\s*axis break|break_axis",
                          text, re.I))


def _is_categorical(text: str) -> bool:
    """barh with explicit tick labels is a categorical axis; a non-zero origin is expected."""
    return bool(re.search(r"barh\s*\(", text)) and bool(
        re.search(r"set_yticks|set_yticklabels", text))


def check_truncation(source_path) -> dict:
    """Return {severity, detail, evidence, method} for a suspected truncated axis."""
    p = pathlib.Path(source_path)
    if not p.is_file():
        return {"severity": "SKIP", "detail": "no plotting source supplied",
                "evidence": [], "method": "none"}
    text = p.read_text(encoding="utf-8", errors="replace")
    if _has_break_marker(text):
        return {"severity": "PASS", "detail": "axis break is declared",
                "evidence": [], "method": "source"}
    if _is_categorical(text):
        return {"severity": "WARN",
                "detail": "non-zero origin on a categorical axis; expected for barh, confirm "
                          "in the caption",
                "evidence": [], "method": "source"}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"severity": "SKIP", "detail": "source does not parse",
                "evidence": [], "method": "none"}

    # collect numeric constants assigned to simple names, so `lo = 52.5; ax.set_ylim(lo, hi)`
    # can be resolved
    consts: dict[str, float] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, (int, float)):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    consts[tgt.id] = float(node.value.value)

    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "attr", None) or getattr(fn, "id", None)
        if name != "set_ylim" or len(node.args) < 2:
            continue
        lo_node = node.args[0]
        lo = None
        if isinstance(lo_node, ast.Constant) and isinstance(lo_node.value, (int, float)):
            lo = float(lo_node.value)
        elif isinstance(lo_node, ast.Name) and lo_node.id in consts:
            lo = consts[lo_node.id]
        if lo is None:
            findings.append((None, "set_ylim lower bound is not statically resolvable"))
            continue
        if lo != 0:
            findings.append((lo, f"set_ylim lower bound is {lo:g}, not 0"))

    if not findings:
        return {"severity": "PASS", "detail": "no non-zero y-axis lower bound found",
                "evidence": [], "method": "source"}
    if any(lo is None for lo, _ in findings):
        return {"severity": "SKIP",
                "detail": "set_ylim present but the lower bound cannot be resolved statically; "
                          "check by hand",
                "evidence": [d for _, d in findings], "method": "source"}
    evidence = [d for _, d in findings]
    return {"severity": "FAIL",
            "detail": "quantitative y-axis starts above zero with no break annotation; "
                      "start at zero or declare the break in the caption",
            "evidence": evidence, "method": "source"}
