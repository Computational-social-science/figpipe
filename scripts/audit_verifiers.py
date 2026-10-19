"""Adversarial sweep of the VERIFICATION layer: `composite` and `audit`.

WHY THIS EXISTS
    LOGICAL_AUDIT.md states the project's real risk profile: the defect rate in the verification
    layer is higher than in the drawing layer. `composite` (geometry) and `audit` (the check that
    everything else trusts) had never been run against inputs designed to fool them.

    The question for a verifier is not "does it work on a good figure" but **"can it be made to pass
    something that is wrong"** and **"can it be made to fail something that is right"**. Both are
    defects: a verifier with false negatives certifies broken output, and one with false positives
    teaches its users to ignore it.

WHAT IT CHECKS
    audit        a deliberately broken figure must FAIL; a correct one must PASS
    composite    overlapping cells, out-of-range `at`, span collisions must be refused
    glyphs       rotated labels must not be reported as collisions; real ones must be

USAGE
    python scripts/audit_verifiers.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, composite, grammar, layout, style  # noqa: E402

OUT = ROOT / "examples" / "output" / "verifiers"


def _render(fig, name: str) -> pathlib.Path:
    OUT.mkdir(parents=True, exist_ok=True)
    return pathlib.Path(layout.save(fig, OUT / name)[0])


def _trend_frame(n=16):
    return pd.DataFrame({"x": np.arange(n, dtype=float),
                         "y": np.linspace(0.1, 0.9, n)})


# --------------------------------------------------------------------------------------
# audit: can it be fooled?
# --------------------------------------------------------------------------------------

def audit_cases() -> list[dict]:
    cases = []

    def record(name, passed, detail):
        cases.append({"module": "audit", "case": name,
                      "status": "ok" if passed else "BROKEN", "detail": detail})

    # 1. a correct figure must PASS
    style.apply()
    panel = grammar.panel("trend_with_uncertainty", _trend_frame(), x="x", y="y", fit="lm")
    fig = grammar.plate([panel], columns=2.0, height_mm=90.0)
    pdf = _render(fig, "good")
    rep = audit.audit(pdf, expect_width_mm=183.0, check_overlap=False)
    hard = [f for f in rep["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    record("correct figure passes", not hard, f"{len(hard)} hard findings on a good figure")

    # 2. text BELOW the 5 pt floor must FAIL -- built by bypassing the style layer
    style.apply()
    fig2, _, _ = layout.figure(columns=2.0, height_mm=60.0)
    ax2 = fig2.add_subplot(111)
    ax2.plot([0, 1], [0, 1])
    ax2.set_xlabel("tiny", fontsize=4.0)          # the defect the project exists to catch
    pdf2 = _render(fig2, "tiny_font")
    rep2 = audit.audit(pdf2, expect_width_mm=183.0, check_overlap=False)
    found = [f for f in rep2["findings"] if f["check"] == "font_size"]
    record("sub-5pt text is caught", bool(found), f"font_size findings: {len(found)}")

    # 3. a WRONG width must FAIL
    style.apply()
    fig3, _, _ = layout.figure(columns=2.0, height_mm=60.0)
    ax3 = fig3.add_subplot(111)
    ax3.plot([0, 1], [0, 1])
    pdf3 = _render(fig3, "wrong_width")
    rep3 = audit.audit(pdf3, expect_width_mm=89.0, check_overlap=False)   # claim 89, page is 183
    width_findings = [f for f in rep3["findings"] if f["check"] == "width"]
    record("wrong width is caught", bool(width_findings),
           f"width findings: {len(width_findings)}")

    # 4. a Type-3 font must FAIL. Simulate by rendering with fonttype 3.
    style.apply()
    plt.rcParams["pdf.fonttype"] = 3
    try:
        fig4, _, _ = layout.figure(columns=2.0, height_mm=60.0)
        ax4 = fig4.add_subplot(111)
        ax4.plot([0, 1], [0, 1])
        pdf4 = _render(fig4, "type3")
    finally:
        style.apply()                              # restore the compliant default
    rep4 = audit.audit(pdf4, expect_width_mm=183.0, check_overlap=False)
    type3 = [f for f in rep4["findings"] if f["check"] == "font_type"]
    record("Type-3 fonts are caught", bool(type3), f"font_type findings: {len(type3)}")

    # 5. glyph collisions: rotated tick labels must NOT be reported
    style.apply()
    df = pd.DataFrame({"label": [f"category-{i}" for i in range(10)],
                       "v": np.arange(10, dtype=float)})
    fig5 = grammar.plate([grammar.panel("ranked_composition", df, label="label", value="v",
                                        top=10, xtick_rotation=45.0)],
                         columns=2.0, height_mm=90.0)
    pdf5 = _render(fig5, "rotated")
    hits = audit.overlapping_glyphs(pdf5)
    record("rotated labels are not false collisions", not hits,
           f"{len(hits)} collisions reported on rotated labels")

    # 6. a REAL collision must be reported: two texts at the same point
    style.apply()
    fig6, _, _ = layout.figure(columns=2.0, height_mm=60.0)
    ax6 = fig6.add_subplot(111)
    ax6.plot([0, 1], [0, 1])
    ax6.text(0.5, 0.5, "AAAAAAAAAA", transform=ax6.transAxes, fontsize=7)
    ax6.text(0.5, 0.5, "BBBBBBBBBB", transform=ax6.transAxes, fontsize=7)
    pdf6 = _render(fig6, "real_collision")
    hits6 = audit.overlapping_glyphs(pdf6)
    record("a real collision is caught", bool(hits6), f"{len(hits6)} collisions reported")
    return cases


# --------------------------------------------------------------------------------------
# composite: can geometry errors slip through?
# --------------------------------------------------------------------------------------

def composite_cases() -> list[dict]:
    cases = []

    def record(name, refused, detail):
        cases.append({"module": "composite", "case": name,
                      "status": "ok" if refused else "BROKEN", "detail": detail})

    df = _trend_frame()

    def panel(**kw):
        return composite.Panel("trend_band", df, {"x": "x", "y": "y"}, **kw)

    # overlapping cells at explicit positions must be refused
    try:
        composite.composite([panel(at=(0, 0)), panel(at=(0, 0))], columns=2.0, height_mm=80.0)
        record("overlapping cells refused", False, "two panels at (0,0) were accepted")
    except Exception as exc:                       # noqa: BLE001
        record("overlapping cells refused", True, f"{type(exc).__name__}: {str(exc)[:80]}")

    # an out-of-range `at` must be refused
    try:
        composite.composite([panel(at=(0, 0)), panel(at=(-1, 0))], columns=2.0, height_mm=80.0)
        record("negative position refused", False, "at=(-1,0) was accepted")
    except Exception as exc:                       # noqa: BLE001
        record("negative position refused", True, f"{type(exc).__name__}: {str(exc)[:80]}")

    # a half-positioned grid must be refused (some panels have at=, some do not)
    try:
        composite.composite([panel(at=(0, 0)), panel()], columns=2.0, height_mm=80.0)
        record("half-positioned grid refused", False, "a mixed grid was accepted")
    except Exception as exc:                       # noqa: BLE001
        record("half-positioned grid refused", True, f"{type(exc).__name__}: {str(exc)[:80]}")

    # a span that collides with another panel must be refused
    try:
        composite.composite([panel(at=(0, 0, 2, 1)), panel(at=(1, 0))],
                            columns=2.0, height_mm=80.0)
        record("span collision refused", False, "a rowspan over another panel was accepted")
    except Exception as exc:                       # noqa: BLE001
        record("span collision refused", True, f"{type(exc).__name__}: {str(exc)[:80]}")

    # an empty panel list must be refused
    try:
        composite.composite([], columns=2.0, height_mm=80.0)
        record("empty plate refused", False, "an empty plate was accepted")
    except Exception as exc:                       # noqa: BLE001
        record("empty plate refused", True, f"{type(exc).__name__}: {str(exc)[:80]}")

    # a colourbar on a drawer that cannot carry one must be refused
    try:
        composite.Panel("trend_band", df, {"x": "x", "y": "y"}, colorbar=True)
        record("impossible colourbar refused", False, "colorbar on a line panel was accepted")
    except Exception as exc:                       # noqa: BLE001
        record("impossible colourbar refused", True, f"{type(exc).__name__}: {str(exc)[:80]}")

    # a figure that fits must still be built and pass its own geometry check
    try:
        fig = composite.composite([panel(at=(0, 0)), panel(at=(0, 1))],
                                  columns=2.0, height_mm=80.0)
        report = getattr(fig, "_figpipe_report", composite.inspect(fig))
        problems = composite.check(fig, report)
        record("a correct plate still passes", not problems, f"geometry problems: {problems}")
    except Exception as exc:                       # noqa: BLE001
        record("a correct plate still passes", False, f"{type(exc).__name__}: {exc}")
    return cases


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    cases = audit_cases() + composite_cases()
    print(f"  {len(cases)} verifier cases")
    print(f"  {'module':<10} {'case':<32} {'status':<7} detail")
    for c in cases:
        print(f"  {c['module']:<10} {c['case']:<32} {c['status']:<7} {str(c['detail'])[:70]}")
    counts = {}
    for c in cases:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    print()
    print("  summary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    bad = [c for c in cases if c["status"] == "BROKEN"]
    if bad:
        print(f"\n  {len(bad)} DEFECT(S) IN THE VERIFICATION LAYER:")
        for c in bad:
            print(f"    {c['module']}.{c['case']}: {c['detail']}")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(cases, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
