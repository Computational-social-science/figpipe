"""Render multi-panel plates (组图) from REAL corpus tables, then audit them.

WHY THIS SCRIPT EXISTS
    "我们最终形成的技能一定是可以绘制复杂的组图" -- the end product is composite figures, not
    single panels. `figpipe.composite` is the mechanism; this script is the demonstration that
    the mechanism produces publishable plates from the papers' own numbers rather than from
    invented data. A template demonstrated on invented numbers proves matplotlib works, not
    that the template can carry a real figure.

WHAT IT BUILDS
    plate_eval_2x2        a 2x2 evaluation plate: grouped bars, a scaling line, a third metric
                          bar panel and a size-vs-score scatter, all from the tables of one
                          paper (joint speech/text translation)
    plate_mixed_1plus2    the classic asymmetric plate: one wide panel across both columns and
                          two panels beneath it, one of them a heat map with its colour bar
    plate_shared_1x3      three panels sharing one y axis -- the "same models, three metrics"
                          strip, which is what axis sharing is for

    Every panel records the paper, the table index and the column headers it was drawn from, so
    a reader can check the numbers against the source table.

WHAT IS CHECKED
    Each plate goes through figpipe's own audit (type sizes, column width, embedded fonts) and
    through `composite.check` (panel letters, uniform gutters, nothing past the canvas). A
    plate that fails either is reported as a failure, not quietly shipped.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, composite  # noqa: E402

SRC = ROOT / "corpus" / "source_data.json"
OUT = ROOT / "templates" / "composite"
COLUMNS = 2.0
WIDTH_MM = 183.0


def tables() -> list[dict]:
    return json.loads(SRC.read_text(encoding="utf-8"))["tables"]


def _short(header: str, i: int) -> str:
    """A column name short enough for a 6 pt legend on an 80 mm panel."""
    seg = header.split(" - ")[-1] if " - " in header else header
    seg = re.sub(r"\(.[^)]*\)", "", seg)             # drop "(↑BLEU) (n = 81)" style units
    seg = seg.replace("↑", "").replace("↓", "").strip(" -_[]")
    seg = re.sub(r"\s+", " ", seg)
    return (seg[:16].strip() or f"col{i}")


def _num(val) -> float:
    try:
        return float(str(val).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return float("nan")


def frame(t: dict, max_num: int = 4, max_rows: int = 14) -> pd.DataFrame | None:
    """A DataFrame from one harvested table, with its real row labels and real column names."""
    ncs = [c for c in t["numeric_cols"] if len(c["values"]) >= 3][:max_num]
    if len(ncs) < 1:
        return None
    n = min([t["n_rows"], len(t["rows_preview"])] + [len(c["values"]) for c in ncs])
    if n < 3 or n > max_rows:
        return None
    rows = t["rows_preview"][:n]
    data: dict[str, list] = {}
    label_cols = t["label_cols"][:3]
    if not label_cols:
        return None
    for j, _lc in enumerate(label_cols):
        name = "label" if j == 0 else f"label{j}"
        data[name] = [str(r[j]).strip() if j < len(r) else "" for r in rows]
    for i, c in enumerate(ncs):
        base = _short(c["header"], i)
        name, k = base, 1
        # a wide table's header can repeat after truncation ("Acc. ..." twice); a legend with
        # two identical entries is unreadable, so the second gets an index
        while name in data:
            k += 1
            name = f"{base} ({k})"
        data[name] = [float(v) for v in c["values"][:n]]
    df = pd.DataFrame(data)
    # a row whose every numeric cell failed to parse would be drawn as a gap; there are none
    # in the harvested tables, but the check keeps a future table from silently shortening a
    # panel -- the frame is in the same order and length as the paper's own table
    numeric = [c for c in df.columns if c not in ("label", "label1", "label2")]
    return df.dropna(axis=0, how="all", subset=numeric) if numeric else None


def _metric_cols(df: pd.DataFrame, k: int) -> list[str]:
    return [c for c in df.columns if c not in ("label", "label1", "label2")][:k]


def _parse_sizes(df: pd.DataFrame) -> pd.DataFrame:
    """Turn a model-size label column ('3.3B', '1.5B') into a numeric axis."""
    out = df.copy()
    if "label1" not in out.columns:
        return None
    def conv(s):
        m = re.match(r"^\s*([0-9.]+)\s*([BbMmKk]?)\s*$", str(s))
        if not m:
            return float("nan")
        v = float(m.group(1))
        return v * {"B": 1.0, "M": 1e-3, "K": 1e-6, "": 1.0}[m.group(2)]
    out["size_B"] = [conv(v) for v in out["label1"]]
    return out if np.isfinite(out["size_B"]).all() and (out["size_B"] > 0).all() else None


def _provenance(t: dict, df: pd.DataFrame) -> dict:
    return {"paper": t["paper"], "table_index": t["table_index"], "rows": int(len(df)),
            "as_read": [c for c in df.columns if c not in ("label", "label1", "label2")]}


def build_plates() -> list[dict]:
    """The three plates: a tuple (name, panels, composite kwargs, provenance)."""
    all_t = tables()
    by = {}
    for t in all_t:
        by.setdefault(t["paper"], []).append(t)
    plates = []

    # ---- plate 1: 2x2, one paper, four panels -------------------------------------
    eval_paper = next(p for p in by if p.startswith("2025_nature_joint_speech"))
    ev = by[eval_paper]
    t3 = next(t for t in ev if t["table_index"] == 3)
    t4 = next(t for t in ev if t["table_index"] == 4)
    df3, df4 = frame(t3), frame(t4)
    m3, m4 = _metric_cols(df3, 4), _metric_cols(df4, 3)
    df3s = _parse_sizes(df3)
    df3s = df3 if df3s is None else df3s
    xsize = "size_B" if "size_B" in df3s.columns else df3s.columns[0]
    panels = [
        composite.Panel("grouped_bars", df3,
                        {"x": "label", "ycols": m3[:3], "xlabel": "model",
                         "ylabel": m3[0], "legend_cols": 1, "headroom": 0.32,
                         "xtick_rotation": 32,
                         "xtick_labels": [s[:12] for s in df3["label"]],
                         "labels": {c: c[:14] for c in m3[:3]}}),
        composite.Panel("line_series", df3s,
                        {"x": xsize, "ycols": m3[2:4], "xlabel": "model size (B)",
                         "ylabel": m3[2], "legend_cols": 1}),
        composite.Panel("grouped_bars", df4,
                        {"x": "label", "ycols": m4[:3], "xlabel": "model",
                         "ylabel": m4[0], "legend_cols": 1, "headroom": 0.32,
                         "xtick_rotation": 32,
                         "xtick_labels": [s[:12] for s in df4["label"]],
                         "labels": {c: c[:14] for c in m4[:3]}}),
        composite.Panel("scatter_fit", df3s,
                        {"x": xsize, "y": m3[0], "xlabel": "model size (B)",
                         "ylabel": m3[0][:14]}),
    ]
    prov = [_provenance(t3, df3), _provenance(t3, df3s), _provenance(t4, df4),
            _provenance(t3, df3s)]
    plates.append({"name": "plate_eval_2x2", "panels": panels, "prov": prov,
                   "kw": {"columns": COLUMNS, "height_mm": 148.0,
                          # rotated model names need room under the bottom row; the default
                          # 9 mm fits horizontal labels only
                          "margins": {"bottom": 16.0}}})

    # ---- plate 2: the asymmetric 1+2 -------------------------------------------------
    mix_paper = next(p for p in by if p.startswith("2026_nature_synthesizing")
                     and len(by[p]) >= 3)
    mix = [t for t in by[mix_paper] if frame(t) is not None]
    ta, tb, tc = mix[0], mix[1], mix[2]
    dfa, dfb, dfc = frame(ta), frame(tb), frame(tc)
    ma, mb = _metric_cols(dfa, 4), _metric_cols(dfb, 3)
    mats = dfc[[c for c in dfc.columns
                if c not in ("label", "label1", "label2")]].dropna(axis=1)
    panels = [
        composite.Panel("grouped_bars", dfa,
                        {"x": "label", "ycols": ma[:4], "xlabel": "model", "ylabel": ma[0],
                         "legend_cols": 4, "headroom": 0.18,
                         "labels": {c: c[:12] for c in ma[:4]}},
                        at=(0, 0, 1, 2)),
        composite.Panel("line_series", dfb,
                        {"x": "label", "ycols": mb[:2], "xlabel": "model",
                         "ylabel": mb[0], "legend_cols": 1},
                        at=(1, 0)),
        composite.Panel("heatmap", mats,
                        {"xlabel": "", "ylabel": "row", "label": mats.columns[0][:12]},
                        at=(1, 1), colorbar=True),
    ]
    prov = [_provenance(ta, dfa), _provenance(tb, dfb), _provenance(tc, dfc)]
    plates.append({"name": "plate_mixed_1plus2", "panels": panels, "prov": prov,
                   "kw": {"columns": COLUMNS, "height_mm": 132.0}})

    # ---- plate 3: 1x3 sharing one y axis ---------------------------------------------
    df4b = frame(t4)
    m4b = _metric_cols(df4b, 4)
    share_panels = [
        composite.Panel("grouped_bars", df4b,
                        {"x": "label", "ycols": [c], "xlabel": "model",
                         "ylabel": c[:14], "legend": False,
                         "xtick_rotation": 32,
                         "xtick_labels": [s[:10] for s in df4b["label"]]})
        for c in m4b[:3]
    ]
    prov = [_provenance(t4, df4b)] * 3
    plates.append({"name": "plate_shared_1x3", "panels": share_panels, "prov": prov,
                   "kw": {"columns": COLUMNS, "height_mm": 66.0, "sharey": True,
                          "margins": {"bottom": 16.0}}})
    return plates


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    plates = build_plates()
    results = []
    ok_count = 0
    for spec in plates:
        stem = OUT / spec["name"]
        try:
            rep = composite.render(spec["panels"], stem, **spec["kw"])
        except Exception as e:                                   # noqa: BLE001
            results.append({"plate": spec["name"], "error": f"{type(e).__name__}: {e}"})
            print(f"  {spec['name']:<20} ERROR {type(e).__name__}: {str(e)[:80]}")
            continue
        pdf = pathlib.Path(rep["paths"][0])
        a = audit.audit(pdf, expect_width_mm=WIDTH_MM, check_overlap=False)
        hard = [f for f in a["findings"] if f["check"] in
                ("font_size", "width", "height", "font_type", "exists")]
        ok = a["ok"] and not rep["problems"]
        ok_count += int(ok)
        results.append({
            "plate": spec["name"], "pdf": str(pdf.relative_to(ROOT)),
            "png": str(pathlib.Path(rep["paths"][1]).relative_to(ROOT)),
            "width_mm": a["width_mm"], "height_mm": a["height_mm"],
            "n_panels": rep["n_panels"],
            "letters": [l["letter"] for l in rep["letters"]],
            "gaps_x_mm": rep["gaps_x_mm"], "gaps_y_mm": rep["gaps_y_mm"],
            "planner": rep["planned"], "priors": {k: v for k, v in rep["priors"].items()},
            "geometry_problems": rep["problems"],
            "audit_ok": a["ok"], "audit_hard_findings": hard,
            "provenance": spec["prov"],
        })
        print(f"  {spec['name']:<20} {rep['n_panels']} panels  {a['width_mm']:.1f} x "
              f"{a['height_mm']:.1f} mm  letters={[l['letter'] for l in rep['letters']]}  "
              f"audit={'OK' if a['ok'] else 'FAIL'}  geometry={'OK' if not rep['problems'] else rep['problems']}")
        for f in a["findings"]:
            print(f"      {f['check']}: {f['detail'][:100]}")
    report = {"about": "Multi-panel plates composed from the corpus's own tables.",
              "plates": results}
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
    print(f"\n  {ok_count}/{len(results)} plates pass both checks")
    return 0 if ok_count == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
