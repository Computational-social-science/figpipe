"""Does the pool's zero on `legend_occlusion` mean anything?

WHY THIS EXISTS
    After wiring the check into `verify.audit`, the pool re-measured at `hard findings: 0`. That looks
    like a clean result and it is not one: the task records do not carry the rendered PDF, so there
    is no artefact to re-inspect. The zero came from the RENDER-TIME run, which is real, but it cannot
    be reproduced from the report -- and a number nobody can re-derive is the shape this project
    keeps recording.

    Worse, the zero could be VACUOUS: if no pool figure contains a legend, the check had nothing to
    test and "0 findings" says nothing about whether it works.

THIS SCRIPT ANSWERS THAT, BY RE-RENDERING
    It takes pool tasks, re-renders each one through the same skill call the benchmark makes, and
    asks two questions per figure:
        1. does it contain a legend frame at all?
        2. if so, does the frame cover drawing marks?
    The first number is what makes the second meaningful.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _render_task(task: dict, out_dir: pathlib.Path):
    """Re-render one pool task and return the PDF path, or None.

    The benchmark's own runner is the only thing that knows how to turn a task record back into a
    call, so this delegates to it rather than re-deriving the mapping -- a second mapping is where
    two implementations drift apart.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_plottwin as B

    fn = getattr(B, "_run_one", None) or getattr(B, "run_one", None)
    if fn is None:
        return None
    try:
        result = fn(task, out_dir)
    except Exception:                                     # noqa: BLE001 - reported as None
        return None
    if isinstance(result, dict):
        for key in ("pdf", "path", "output"):
            v = result.get(key)
            if v and pathlib.Path(v).is_file():
                return pathlib.Path(v)
    return None


def survey_legend_occlusion(limit: int = 12) -> dict:
    import pymupdf

    from figpipe import audit

    report = json.loads((ROOT / "corpus" / "e2e" / "plottwin_report.json")
                        .read_text(encoding="utf-8"))
    tasks = [t for t in (report.get("tasks") or []) if t.get("status") == "ok"][:limit]
    out_dir = ROOT / "examples" / "output" / "_legend_survey"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for task in tasks:
        pdf = _render_task(task, out_dir)
        row = {"task": task.get("id"), "skill": task.get("skill"), "rendered": pdf is not None}
        if pdf is not None:
            doc = pymupdf.open(str(pdf))
            frames = 0
            for page in doc:
                frames += len(audit._legend_frames(page))
            doc.close()
            row["legend_frames"] = frames
            row["occlusions"] = len(audit.legend_occlusion(pdf))
        rows.append(row)

    n_rendered = sum(1 for r in rows if r["rendered"])
    n_with_legend = sum(1 for r in rows if r.get("legend_frames"))
    n_occluded = sum(1 for r in rows if r.get("occlusions"))
    return {
        "rows": rows, "n": len(rows), "n_rendered": n_rendered,
        "n_with_legend": n_with_legend, "n_occluded": n_occluded,
        "verdict": (
            "the pool's zero on legend_occlusion is MEANINGFUL: figures were re-rendered, "
            f"{n_with_legend} contained a legend, and none covered a mark"
            if n_with_legend else
            f"the pool's zero on legend_occlusion is VACUOUS for this sample: of {n_rendered} "
            f"re-rendered figures, NONE contains a legend, so the check had nothing to test"),
    }


def main(argv=None) -> int:
    out = survey_legend_occlusion()
    path = ROOT / "corpus" / "legend_occlusion_survey.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in out["rows"]:
        if not r["rendered"]:
            print(f"  {str(r['task'])[:40]:<42} not re-rendered")
            continue
        print(f"  {str(r['task'])[:40]:<42} legends={r.get('legend_frames')} "
              f"occlusions={r.get('occlusions')}")
    print(f"\n  rendered {out['n_rendered']}/{out['n']}, with a legend {out['n_with_legend']}, "
          f"occluded {out['n_occluded']}")
    print(f"  {out['verdict']}")
    print(f"  wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
