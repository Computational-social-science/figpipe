"""Fill column_width from PDF geometry instead of asking the vision model.

WHY
    The adversarial audit found the VLM's `column_width` label disagreed with the PDF geometry
    in 45 % of cases (22/40 agreement). The project's own control experiment had already shown
    the model asserts figure properties on a BLANK page -- 20 fabricated assertions across 3
    controls, verdict FABRICATES.

    `column_width` is not a perception problem. It is `bbox_width_mm` compared against Nature's
    89 / 183 mm columns. Asking a vision model to guess it, then treating the guess as a label,
    produces a column of data that is 45 % wrong about something exactly measurable.

THE RULE APPLIED HERE
    When a value can be computed exactly, compute it. Do not ask a model, and do not report a
    model's guess alongside the computed value as if the two were comparable.

    The VLM may still describe what it SEES (figure type, panel layout, palette) -- those are
    genuinely perceptual. Geometry is not.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(r"E:\2026-AI4S\figpipe")
# The live label file is the newest vlm_labels*.jsonl; the v1 file is retained for the audit
# trail because its prompt differed.
LABELS = ROOT / "corpus" / "vlm_labels.jsonl"
if not LABELS.is_file():
    cands = sorted((ROOT / "corpus").glob("vlm_labels*.jsonl"))
    LABELS = cands[-1] if cands else LABELS
REPORT = ROOT / "corpus" / "vlm_report.json"

#: Nature's printed widths, and the tolerance used everywhere else in this project.
COLUMNS = {"single": 89.0, "double": 183.0}
TOL_MM = 3.0


def width_to_column(width_mm: float) -> tuple[str | None, float]:
    """Nearest Nature column and the distance to it. None when neither is close."""
    best, best_d = None, float("inf")
    for name, target in COLUMNS.items():
        d = abs(width_mm - target)
        if d < best_d:
            best, best_d = name, d
    return (best if best_d <= TOL_MM else None), round(best_d, 1)


def main() -> int:
    if not LABELS.is_file():
        print("  no labels file"); return 1
    rows = [json.loads(l) for l in LABELS.read_text(encoding="utf-8").splitlines() if l.strip()]
    changed = 0
    for r in rows:
        geo = r.get("source_geometry") or {}
        # The geometry block already carries the column, computed from the crop width.
        col = geo.get("column_from_geometry")
        w = geo.get("crop_width_mm")
        if col is None and w is not None:
            col, _d = width_to_column(float(w))
        if col is None:
            continue
        dist = (abs(float(w) - COLUMNS[col]) if w is not None and col in COLUMNS else None)
        parsed = r.get("parsed") or {}
        vlm_said = parsed.get("column_width")
        r["column_width_geometry"] = {
            "from_pdf_width_mm": (round(float(w), 1) if w is not None else None),
            "column": col,
            "distance_mm": (round(dist, 1) if dist is not None else None),
            "method": "computed from the figure bbox, not asked of the model",
        }
        if vlm_said is not None:
            r["column_width_vlm"] = vlm_said
            r["column_width_vlm_agrees"] = (vlm_said == col)
            # The VLM value is retained for the audit trail but marked as NOT the label.
            parsed.pop("column_width", None)
            r["parsed"] = parsed
            changed += 1

    LABELS.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    agree = [r for r in rows if r.get("column_width_vlm_agrees") is True]
    disagree = [r for r in rows if r.get("column_width_vlm_agrees") is False]
    comparable = len(agree) + len(disagree)

    print(f"  records              : {len(rows)}")
    print(f"  column_width replaced: {changed}")
    if comparable:
        print(f"  VLM agreement        : {len(agree)}/{comparable} = "
              f"{len(agree)/comparable:.0%}  (the reason it was removed as a label)")
    print()
    print("  column_width is now COMPUTED from the bbox and the VLM value is kept only as")
    print("  an audit-trail field, marked as not-the-label.")

    if REPORT.is_file():
        rep = json.loads(REPORT.read_text(encoding="utf-8"))
        rep["column_width_policy"] = {
            "decision": "computed from PDF geometry; the VLM is no longer asked for it",
            "reason": ("VLM agreement with geometry was 45 % (22/40) and the model fabricates "
                       "figure properties on blank pages (20 assertions across 3 controls). "
                       "A value that can be computed exactly must not be guessed."),
            "vlm_agreement_when_comparable": (f"{len(agree)}/{comparable}" if comparable else None),
        }
        REPORT.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  wrote policy into {REPORT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
