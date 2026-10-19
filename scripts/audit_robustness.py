"""Adversarial sweep of the modules the recent fixes touched, but never stress-tested.

WHY THIS EXISTS
    The data-shape audit covers the SKILL layer. Every change of the last four rounds, however,
    landed in `styleprofile`, `codegen` or `select` -- and none of them had been run against inputs
    that are not the benchmark's. That is exactly how the matrix pivot regression happened: a fix
    committed without being run against the inputs that exercise it.

    This script feeds those modules degenerate, malformed and adversarial inputs and records what
    each one does. The required behaviour is one of two things, never a silent wrong answer:
        HANDLED   returned a sensible value (and the value is checked, not just "no exception")
        REFUSED   raised a specific exception with a message that names the problem
        BROKEN    returned something wrong, or crashed with an unhelpful error

USAGE
    python scripts/audit_robustness.py
    python scripts/audit_robustness.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import traceback

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import codegen, select, styleprofile  # noqa: E402

OUT = ROOT / "examples" / "output" / "robustness"


# --------------------------------------------------------------------------------------
# Fixtures: images a user could plausibly hand the profiler
# --------------------------------------------------------------------------------------

def _save(arr: np.ndarray, name: str) -> pathlib.Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    Image.fromarray(arr).save(path)
    return path


def fixtures() -> dict[str, pathlib.Path]:
    rng = np.random.default_rng(3)
    h, w = 120, 160
    return {
        # a blank page: no ink at all
        "blank": _save(np.full((h, w, 3), 255, np.uint8), "blank.png"),
        # one solid black rectangle: ink everywhere, no structure
        "solid": _save(np.zeros((h, w, 3), np.uint8), "solid.png"),
        # pure noise: no lines, no palette
        "noise": _save(rng.integers(0, 256, (h, w, 3), dtype=np.uint8), "noise.png"),
        # 1 pixel wide
        "one_px_wide": _save(np.full((h, 1, 3), 255, np.uint8), "wide1.png"),
        # 1 pixel tall
        "one_px_tall": _save(np.full((1, w, 3), 255, np.uint8), "tall1.png"),
        # two colours only, one line
        "two_colour": _save(np.where(
            (np.arange(w)[None, :] % 40 == 0)[..., None].repeat(3, 2) & 1,
            0, 255).astype(np.uint8).repeat(h, 0), "two_colour.png"),
        # a genuinely normal small figure: frame + one horizontal line
        "normal": _normal_figure(),
    }


def _normal_figure() -> pathlib.Path:
    arr = np.full((120, 160, 3), 255, np.uint8)
    arr[20:100, 25:150] = 255
    arr[20, 25:150] = 30          # top spine
    arr[99, 25:150] = 30          # bottom spine
    arr[20:100, 25] = 30          # left spine
    arr[20:100, 149] = 30         # right spine
    arr[60, 25:150] = 170         # a grid line, INSIDE the ink threshold (the first version
                                  # used 200, which is not ink, so the fixture silently tested
                                  # nothing -- a test bug, not a code bug)
    return _save(arr, "normal.png")


# --------------------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------------------

def _expect_raises(fn, *exc_types) -> tuple[bool, str]:
    try:
        fn()
    except exc_types as exc:
        return True, f"{type(exc).__name__}: {str(exc)[:90]}"
    except Exception as exc:                       # noqa: BLE001 - wrong exception type is a finding
        return False, f"raised {type(exc).__name__} (expected {exc_types}): {exc}"
    return False, "did not raise"


def profile_cases(fx: dict[str, pathlib.Path]) -> list[dict]:
    cases = []

    def run(name, fn, check=None):
        try:
            value = fn()
        except Exception as exc:                   # noqa: BLE001 - recorded, not raised
            cases.append({"module": "styleprofile", "case": name, "status": "REFUSED",
                          "detail": f"{type(exc).__name__}: {str(exc)[:100]}"})
            return
        problem = check(value) if check else None
        cases.append({"module": "styleprofile", "case": name,
                      "status": "BROKEN" if problem else "HANDLED",
                      "detail": problem or "", "value": value})

    # blank / solid / noise must not claim structure they do not have
    for label in ("blank", "solid", "noise"):
        def probe(path=fx[label], lbl=label):
            prof = styleprofile.StyleProfile.from_image_detailed(path)
            return {"colours": len(prof.colours), "rules": prof.rules_h + prof.rules_v,
                    "spines": sum((prof.spines or {}).values()),
                    "tick": prof.tick_direction}
        def degenerate_is_honest(value, lbl=label):
            if lbl in ("blank", "solid", "noise"):
                if value["spines"] != 0:
                    return f"a {lbl} image has no spines, but {value['spines']} were reported"
                if value["rules"] != 0:
                    return f"a {lbl} image has no rules, but {value['rules']} were reported"
            return None

        run(f"detailed:{label}", probe, degenerate_is_honest)

    # degenerate sizes
    for label in ("one_px_wide", "one_px_tall"):
        def probe(path=fx[label], lbl=label):
            prof = styleprofile.StyleProfile.from_image_detailed(path)
            return {"width": prof.width_mm, "height": prof.height_mm}
        def degenerate_is_honest(value, lbl=label):
            if lbl in ("blank", "solid", "noise"):
                if value["spines"] != 0:
                    return f"a {lbl} image has no spines, but {value['spines']} were reported"
                if value["rules"] != 0:
                    return f"a {lbl} image has no rules, but {value['rules']} were reported"
            return None

        run(f"detailed:{label}", probe, degenerate_is_honest)

    # a normal figure must yield the structure it actually has
    def normal():
        prof = styleprofile.StyleProfile.from_image_detailed(fx["normal"])
        return {"rules": prof.rules_h, "spines": sum((prof.spines or {}).values()),
                "tick": prof.tick_direction}

    def normal_is_correct(value):
        # the fixture HAS four spines and one interior grid rule; a profiler that reports zero
        # rules on it is as wrong as one that reports four spines on a blank page
        if value["spines"] != 4:
            return f"expected 4 spines, got {value['spines']}"
        if value["rules"] < 1:
            return f"expected >=1 interior grid rule, got {value['rules']}"
        return None

    run("detailed:normal", normal, normal_is_correct)

    # style derivation on every profile, including the degenerate ones
    for label in ("blank", "solid", "noise", "normal"):
        def derive(path=fx[label], lbl=label):
            prof = styleprofile.StyleProfile.from_image_detailed(path)
            st = codegen.style_from_image_profile(prof)
            return {"palette": len(st.get("palette") or []),
                    "aspect": st.get("figure_aspect"),
                    "undetermined": len(st.get("undetermined_dimensions") or [])}
        run(f"derive:{label}", derive)

    # a missing file must raise FileNotFoundError, not a confusing attribute error
    ok, detail = _expect_raises(
        lambda: styleprofile.StyleProfile.from_image_detailed(OUT / "does_not_exist.png"),
        FileNotFoundError, OSError)
    cases.append({"module": "styleprofile", "case": "missing_file",
                  "status": "REFUSED" if ok else "BROKEN", "detail": detail})
    return cases


def codegen_cases() -> list[dict]:
    cases = []

    def run(name, fn, check=None):
        try:
            value = fn()
        except (codegen.CodegenError, ValueError) as exc:
            cases.append({"module": "codegen", "case": name, "status": "REFUSED",
                          "detail": f"{type(exc).__name__}: {str(exc)[:100]}"})
            return
        except Exception as exc:                   # noqa: BLE001
            cases.append({"module": "codegen", "case": name, "status": "BROKEN",
                          "detail": f"raised {type(exc).__name__}: {str(exc)[:110]}"})
            return
        problem = check(value) if check else None
        cases.append({"module": "codegen", "case": name,
                      "status": "BROKEN" if problem else "HANDLED",
                      "detail": problem or "", "value": str(value)[:90]})

    import pandas as pd
    from figpipe import composite
    df = pd.DataFrame({"x": np.arange(10.0), "y": np.linspace(0, 1, 10)})
    panel = composite.Panel("trend_band", df, {"x": "x", "y": "y", "fit": "lm"})

    def must_compile(text):
        try:
            compile(text, "<emitted>", "exec")
        except SyntaxError as exc:
            return f"emitted script does not compile: {exc}"
        if "df" in text and "df =" not in text:
            return "emitted script references df without defining it"
        return None

    run("emit:normal", lambda: codegen.emit([panel]), must_compile)
    run("emit:naive", lambda: codegen.emit([panel], style=codegen.naive_style()),
        must_compile)
    run("emit:nan_data", lambda: codegen.emit(
        [composite.Panel("trend_band",
                         pd.DataFrame({"x": [1.0, np.nan, 3.0], "y": [1.0, 2.0, np.nan]}),
                         {"x": "x", "y": "y"})]), must_compile)
    run("emit:empty_panels", lambda: codegen.emit([]))
    run("emit:unknown_drawer", lambda: codegen.emit(
        [composite.Panel("polar_profile", df, {"theta": "x", "value": "y"})]))

    def bad_style():
        # a style dict with hostile values must be refused, not emitted into the script
        return codegen.emit([panel], style={"figure_aspect": 0.0, "grid": None,
                                            "linewidth": "wide", "palette": ["not-a-colour"]})
    run("emit:hostile_style", bad_style, must_compile)

    for label, bad in (("nan", float("nan")), ("inf", float("inf")),
                       ("zero", 0.0), ("negative", -1.5)):
        def hostile_aspect(value=bad):
            return codegen.emit([panel], style={"figure_aspect": value})
        run(f"emit:aspect_{label}", hostile_aspect, must_compile)
    return cases


def select_cases() -> list[dict]:
    cases = []

    def run(name, fn, check=None):
        try:
            value = fn()
        except (ValueError, FileNotFoundError) as exc:
            cases.append({"module": "select", "case": name, "status": "REFUSED",
                          "detail": f"{type(exc).__name__}: {str(exc)[:100]}"})
            return
        except Exception as exc:                   # noqa: BLE001
            cases.append({"module": "select", "case": name, "status": "BROKEN",
                          "detail": f"raised {type(exc).__name__}: {str(exc)[:110]}"})
            return
        problem = check(value) if check else None
        cases.append({"module": "select", "case": name,
                      "status": "BROKEN" if problem else "HANDLED",
                      "detail": problem or "", "value": str(value)[:100]})

    OUT.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    from figpipe import grammar, layout
    frames = {}
    for label, height in (("a", 80.0), ("b", 150.0)):
        panel = grammar.panel("trend_with_uncertainty",
                              pd.DataFrame({"x": np.arange(12.0), "y": np.linspace(0, 1, 12)}),
                              x="x", y="y", fit="lm")
        fig = grammar.plate([panel], columns=2.0, height_mm=height)
        frames[label] = pathlib.Path(layout.save(fig, OUT / f"sel_{label}")[0])

    reference = styleprofile.StyleProfile.from_pdf(frames["a"])

    run("select:empty", lambda: select.select(reference, {}))
    run("select:missing_candidate",
        lambda: select.select(reference, {"ghost": OUT / "nope.pdf"}))
    run("select:one_candidate",
        lambda: select.select(reference, {"only": frames["a"]}),
        lambda v: None if v["choice"] == "only" and v["margin"] is None
        else "single candidate must win with margin None")
    run("select:two_candidates",
        lambda: select.select(reference, {"a": frames["a"], "b": frames["b"]}),
        lambda v: None if v["choice"] == "a" and v["margin"] is not None
        else f"the identical candidate should win, got {v['choice']}")
    run("select:png_input",
        lambda: select.select(reference, {"png": frames["a"].with_suffix(".png")}))
    return cases


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    fx = fixtures()
    cases = profile_cases(fx) + codegen_cases() + select_cases()

    print(f"  {len(cases)} adversarial cases")
    print(f"  {'module':<14} {'case':<26} {'status':<9} detail")
    for c in cases:
        detail = c.get("detail") or c.get("value", "")
        print(f"  {c['module']:<14} {c['case']:<26} {c['status']:<9} {str(detail)[:78]}")

    counts = {}
    for c in cases:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    print()
    print("  summary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    bad = [c for c in cases if c["status"] == "BROKEN"]
    if bad:
        print(f"\n  {len(bad)} DEFECT(S):")
        for c in bad:
            print(f"    {c['module']}.{c['case']}: {c.get('detail')}")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(cases, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
