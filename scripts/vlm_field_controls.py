"""Build the field-level control set VLM_DECISION.md requires, and test a local model on it.

WHY THIS EXISTS
    `VLM_DECISION.md` states the path to using a local VLM honestly:

        * build a control set specific to the field (blank, noise, text-only, and a figure whose
          true value is known by construction)
        * require the model to answer the controls correctly before its labels count
        * use the labels as a second opinion that is checked, never as an answer key

    That was written as "a measurement project, not a feature". This is the measurement.

    The earlier control experiment asked ONE model for TEN fields and got 20 fabricated values. The
    protocol here is narrower on purpose: ONE field, FOUR controls, and a pass/fail that the model
    cannot talk its way out of.

WHY `panel_count` AND NOT SOMETHING RICHER
    It meets the three tests the project set: a reader can answer it by looking (visually
    decidable), no deterministic check can (the PDF has the panels but counting them from path
    operators is what `structure.panel_labels_from_sizes` already does -- a VLM adds nothing there),
    and the true value is known BY CONSTRUCTION for every control.

    A field the deterministic route already answers is the right first test: if the model cannot
    match a number this project can compute exactly, no richer field is safe.

WHAT A PASS MEANS, AND WHAT IT DOES NOT
    A pass means the model answered four controls whose answers were fixed before it saw them. It
    does NOT mean the model is accurate on real figures -- that needs a larger sample. It means the
    model is not obviously fabricating, which is the bar the previous attempt failed.
"""
from __future__ import annotations

import base64
import json
import pathlib
import sys
import tempfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "gemma3:12b"

#: One field, asked in a form whose answer is a single integer.
QUESTION = ("How many separate plotting panels (subplots) are visible in this image? "
            "Answer with ONE integer and nothing else. If there are no panels at all, answer 0.")


def _ask(model: str, image_png: bytes, timeout: int = 180) -> str:
    payload = {
        "model": model,
        "prompt": QUESTION,
        "images": [base64.b64encode(image_png).decode()],
        "stream": False,
        "options": {"temperature": 0},
    }
    req = urllib.request.Request(
        OLLAMA, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get("response", "")


def _first_int(text: str) -> int | None:
    import re
    m = re.search(r"-?\d+", text or "")
    return int(m.group(0)) if m else None


def _render(panels: int) -> bytes:
    """A figure with EXACTLY `panels` subplots, or a blank/noise page when panels == 0."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, max(1, panels), figsize=(6.0, 2.2), squeeze=False)
    rng = np.random.default_rng(7)
    for i, ax in enumerate(axes[0]):
        ax.plot(np.arange(12), rng.random(12), "-o", ms=2)
        ax.set_xlabel(f"x{i}")
    if panels == 0:
        plt.close(fig)
        fig = plt.figure(figsize=(6.0, 2.2))
    path = pathlib.Path(tempfile.mkdtemp(prefix="vlmctl-")) / "c.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path.read_bytes()


def _noise() -> bytes:
    """Pure noise: no axes, no labels, no panels."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    rng = np.random.default_rng(11)
    fig = plt.figure(figsize=(6.0, 2.2))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(rng.random((60, 160)), cmap="gray", aspect="auto")
    ax.set_axis_off()
    path = pathlib.Path(tempfile.mkdtemp(prefix="vlmnoise-")) / "n.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path.read_bytes()


def controls() -> list[dict]:
    """The four controls, with answers fixed BEFORE the model sees them."""
    return [
        {"name": "blank", "expect": 0, "png": _render(0),
         "why": "a page with no panels; a model that reports one is fabricating"},
        {"name": "noise", "expect": 0, "png": _noise(),
         "why": "an image with no axes at all; same test with texture present"},
        {"name": "one-panel", "expect": 1, "png": _render(1),
         "why": "a single subplot, the most common real case"},
        {"name": "three-panel", "expect": 3, "png": _render(3),
         "why": "three subplots; a model counting axes rather than panels will miss"},
    ]


def run(model: str = MODEL) -> dict:
    results = []
    for ctl in controls():
        try:
            raw = _ask(model, ctl["png"])
            got = _first_int(raw)
            err = None
        except Exception as exc:                       # noqa: BLE001 - reported, not hidden
            raw, got, err = "", None, f"{type(exc).__name__}: {exc}"
        results.append({"control": ctl["name"], "expect": ctl["expect"], "got": got,
                        "raw": (raw or "")[:80], "why": ctl["why"], "error": err,
                        "correct": got == ctl["expect"]})
    n = len(results)
    n_ok = sum(1 for r in results if r["correct"])
    return {
        "model": model,
        "field": "panel_count",
        "controls": results,
        "n": n, "n_correct": n_ok,
        "passed": n_ok == n,
        "verdict": (f"{model} answered all {n} controls correctly on `panel_count`; its labels on "
                    f"this field may be used as a CHECKED second opinion"
                    if n_ok == n else
                    f"{model} answered {n_ok} of {n} controls correctly on `panel_count`; its labels "
                    f"on this field must NOT be trusted"),
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--out", default=str(ROOT / "corpus" / "vlm_field_controls.json"))
    args = ap.parse_args(argv)

    out = run(args.model)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                      encoding="utf-8")
    for r in out["controls"]:
        mark = "OK  " if r["correct"] else "FAIL"
        print(f"  [{mark}] {r['control']:<12} expect={r['expect']} got={r['got']}"
              + (f"  ({r['error'][:40]})" if r["error"] else ""))
    print(f"\n  {out['verdict']}")
    print(f"  wrote {args.out}")
    return 0 if out["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
