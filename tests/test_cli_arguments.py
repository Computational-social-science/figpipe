"""Every CLI argument in every script must actually be read.

WHY THIS TEST
    Round 26 found three arguments that were declared and never used -- worst of all
    `--reference`, which the facet path accepted and silently ignored, producing an UNSTYLED figure
    while reporting `RESULT: compliant`. An argument that is parsed and dropped is worse than one
    that is missing: the missing one fails loudly, the dropped one lies.

    This test generalises the check to every script, so the next such argument fails here rather
    than in a user's hands.

WHAT COUNTS AS A READ
    Three forms, and the detector must accept all three or it cries wolf -- and a detector that
    cries wolf is one people learn to ignore:
        args.attr                      direct
        getattr(args, "attr", ...)     guarded (the --fresh override uses this)
        vars(args)                     bulk dynamic read (run_skill.py builds params this way)
"""
from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _declared(src: str) -> set[str]:
    found = set(re.findall(r'add_argument\(\s*"--([\w-]+)"', src))
    found |= set(re.findall(r'add_argument\(\s*"(\w+)",', src))
    found.discard("help")
    return found


def _unread(src: str) -> list[str]:
    declared = _declared(src)
    if "vars(args)" in src:
        # a bulk dynamic read means nothing is provably unread
        return []
    out = []
    for arg in sorted(declared):
        attr = arg.replace("-", "_")
        if f"args.{attr}" in src:
            continue
        if f'"{attr}"' in src or f"'{attr}'" in src:
            continue
        out.append(arg)
    return out


def test_every_script_reads_every_argument_it_declares():
    offenders = {}
    scanned = 0
    for path in sorted(SCRIPTS.glob("*.py")):
        src = path.read_text(encoding="utf-8", errors="replace")
        if "add_argument" not in src:
            continue
        scanned += 1
        bad = _unread(src)
        if bad:
            offenders[path.name] = bad
    assert scanned >= 5, f"only {scanned} scripts scanned; the test is looking at too little"
    assert not offenders, (
        "these scripts declare arguments they never read, so the arguments do nothing: "
        + repr(offenders))


def test_the_detector_can_fail():
    """NEGATIVE CONTROL: a synthetic script with an unread argument must be caught.

    Without this, a detector that always returns [] would pass the test above.
    """
    synthetic = (
        "import argparse\n"
        "ap = argparse.ArgumentParser()\n"
        'ap.add_argument("--used", default=None)\n'
        'ap.add_argument("--ignored", default=None)\n'
        "args = ap.parse_args()\n"
        "print(args.used)\n"
    )
    assert _unread(synthetic) == ["ignored"], (
        "the detector did not catch a declared-but-unread argument, so the scan above proves "
        "nothing")


def test_the_detector_accepts_all_three_read_forms():
    """A detector with false positives gets ignored, which is worse than no detector."""
    direct = 'ap.add_argument("--a", default=1)\nprint(args.a)\n'
    guarded = ('ap.add_argument("--a", default=1)\n'
               'x = getattr(args, "a", False)\n')
    bulk = 'ap.add_argument("--a", default=1)\nx = vars(args)\n'
    for label, src in (("direct", direct), ("guarded", guarded), ("bulk", bulk)):
        assert _unread(src) == [], f"the {label} read form was reported as unread"
