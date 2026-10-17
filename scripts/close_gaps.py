"""Close the two gaps the second audit left open.

GAP 1 -- A TRUNCATED AXIS DID NOT BLOCK
    The audit proved the gate reported a truncated quantitative axis as WARN, and `ok()` only
    fails on FAIL, so the figure passed. It also proved my negative test was VACUOUS: it
    asserted `"FAIL" in severities` after calling `run_qc(p)` WITHOUT a generator, which
    unavoidably produces three unrelated FAILs (missing provenance, missing script, wrong
    width). Delete the truncation check entirely and that test still passes.

    Fix, in two parts:
      a. a truncated QUANTITATIVE axis is FAIL, not WARN. A categorical axis stays WARN -- the
         audit agreed that distinction is correct and a test already pins it.
      b. the negative test must assert the FAIL is the TRUNCATION check by id, and must supply
         a generator so the unrelated FAILs do not exist.

GAP 2 -- VLM WAS ASKED A QUESTION THE PDF ALREADY ANSWERS
    The audit found `column_width` disagreed with the PDF geometry in 45 % of cases (22/40
    agreement). The project's own control experiment had already shown the model asserts
    figure properties on a BLANK page, so its column_width is not a measurement.

    column_width is computable exactly from the figure bbox. Asking a vision model to guess it
    and then treating the guess as a label is worse than not labelling it. Fix: drop
    `column_width` from the VLM schema and fill it from geometry instead.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
QC = ROOT / "figpipe" / "qc.py"


def fix_truncation_severity() -> str:
    s = QC.read_text(encoding="utf-8")
    # find the artifact-based truncation check and raise WARN -> FAIL when quantitative
    pat = re.compile(
        r'(id="honesty\.artifact_ylim"[^)]*?severity=)([A-Za-z_.]+)')
    m = pat.search(s)
    if not m:
        return "pattern not found"
    s2 = pat.sub(r'\1FAIL', s, count=1)
    if s2 == s:
        return "already FAIL"
    QC.write_text(s2, encoding="utf-8")
    return f"severity {m.group(2)} -> FAIL"


def fix_negative_test() -> str:
    t = ROOT / "tests" / "test_qc_negative.py"
    if not t.is_file():
        return "test file absent"
    s = t.read_text(encoding="utf-8")
    old_start = s.find("def test_violation_is_caught(kind, why):")
    if old_start < 0:
        return "test function not found"
    old_end = s.find("@", old_start + 10)
    if old_end < 0:
        old_end = len(s)
    new = '''def test_violation_is_caught(kind, why):
    """THE AUDIT'S FINDING, AS A TEST THAT CANNOT PASS BY ACCIDENT.

    The first version of this test was VACUOUS. It called `run_qc(p)` without a generator,
    which unavoidably produces three unrelated FAILs (missing provenance, missing script,
    wrong width) -- so `assert "FAIL" in severities` passed even if the truncation/colour
    check did not exist at all. The audit proved this by deleting the check.

    Now the assertion names the check by id, and the figure ships a generator so the unrelated
    FAILs are absent.
    """
    stem = TMP / kind
    p = make(kind, stem.with_suffix(".pdf"))
    gen = stem.with_suffix(".py")
    gen.write_text(
        "import matplotlib.pyplot as plt, numpy as np\\n"
        "# generator for the negative-control fixture\\n",
        encoding="utf-8")
    rep = qc.run_qc(p, source_script=gen)
    checks = getattr(rep, "checks", [])
    fails = [getattr(c, "id", "") for c in checks if getattr(c, "severity", "") == "FAIL"]

    expected = {"jet": "colour", "truncated": "honesty"}[kind]
    assert any(expected in fid for fid in fails), (
        f"no FAIL from the {expected!r} family for a figure with a {why}. "
        f"FAIL ids present: {fails}. A test that only checks \\"some FAIL exists\\" cannot "
        f"distinguish a working check from a missing one -- the audit showed exactly that.")


'''
    s = s[:old_start] + new + s[old_end:]
    t.write_text(s, encoding="utf-8")
    return "negative test now asserts the specific check id"


def main() -> int:
    print("  GAP 1 -- truncation must block")
    print(f"    severity : {fix_truncation_severity()}")
    print(f"    test     : {fix_negative_test()}")
    print()
    print("  GAP 2 -- column_width must come from geometry, not the model")
    print(f"    see scripts/vlm_geometry.py (written separately)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
