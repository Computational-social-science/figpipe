"""Render every template with REAL data from the corpus, then audit the output.

WHY REAL DATA AND A REAL AUDIT
    "复现各类典型绘图样式，并形成高质量的通用模板" -- a template demonstrated on invented
    numbers proves that matplotlib works, not that the template can carry a real figure.

    So each template is driven by a table harvested from a Nature paper's own content.md, and
    each rendered figure is put through figpipe's own audit. A template that fails the audit is
    not a template; it is a defect generator.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, drawlib  # noqa: E402

SRC = ROOT / "corpus" / "source_data.json"
OUT = ROOT / "templates" / "out"


def tables() -> list[dict]:
    j = json.loads(SRC.read_text(encoding="utf-8"))
    return j["tables"]


def numeric_frame(t: dict) -> pd.DataFrame | None:
    ncs = t["numeric_cols"]
    if len(ncs) < 2:
        return None
    lens = [len(c["values"]) for c in ncs]
    n = min(lens)
    if n < 3:
        return None
    # DUPLICATE HEADERS COLLAPSE IN A DICT. Two columns whose header text is identical (common
    # when docling splits a wide table) silently became one column, so a table with 5 numeric
    # columns produced a 1-column frame. Uniquify the names.
    data = {}
    for i, c in enumerate(ncs[:5]):
        name = (c["header"] or f"col{i}")[:24].strip() or f"col{i}"
        if name in data:
            name = f"{name}_{i}"
        data[name] = c["values"][:n]
    return pd.DataFrame(data)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = [t for t in tables() if len(t["numeric_cols"]) >= 2]
    print(f"  tables with >=2 numeric columns: {len(ts)}")
    if not ts:
        print("  not enough source data to demonstrate the templates")
        return 1

    results = []
    plans = [
        ("bar_with_errors", 0, {"x": None}),
        ("scatter_fit", 0, {}),
        ("line_series", 0, {}),
        ("heatmap", 0, {}),
        ("boxplot", 0, {}),
    ]

    # pick a table whose shape suits the template, rather than the first one available
    def pick(min_cols: int, min_rows: int = 4):
        for cand in sorted(ts, key=lambda x: -len(x["numeric_cols"])):
            if len(cand["numeric_cols"]) >= min_cols and cand["n_rows"] >= min_rows:
                return cand
        return None

    for name, _ti, _kw in plans:
        t = pick(2) or ts[0]
        df = numeric_frame(t)
        if df is None:
            print(f"  {name:<18} SKIP: no usable frame")
            continue
        if name in ("scatter_fit", "line_series") and len(df.columns) < 2:
            print(f"  {name:<18} SKIP: needs 2 numeric columns, got {len(df.columns)}")
            continue
        stem = OUT / f"template_{name}"
        try:
            if name == "bar_with_errors":
                d = df.copy()
                d.insert(0, "label", [f"s{i+1}" for i in range(len(d))])
                fig = drawlib.bar_with_errors(d, x="label", y=d.columns[1],
                                              ylabel=d.columns[1], xlabel="series")
            elif name == "scatter_fit":
                fig = drawlib.scatter_fit(df, x=df.columns[0], y=df.columns[1],
                                          xlabel=df.columns[0], ylabel=df.columns[1])
            elif name == "line_series":
                fig = drawlib.line_series(df, x=df.columns[0], ycols=list(df.columns[1:3]),
                                          xlabel=df.columns[0], ylabel="value")
            elif name == "heatmap":
                fig = drawlib.heatmap(df, xlabel=df.columns[0], ylabel="row", label="value")
            elif name == "boxplot":
                d = df.melt(var_name="group", value_name="value")
                fig = drawlib.boxplot(d, group="group", value="value",
                                      xlabel="series", ylabel="value")
            else:
                continue
            from figpipe import layout
            paths = layout.save(fig, stem)
            pdf = pathlib.Path(paths[0])
            rep = audit.audit(pdf, expect_width_mm=183 if "2" in stem.name else None,
                              check_overlap=False)
            results.append({
                "template": name, "paper": t["paper"], "n_rows": len(df),
                "pdf": str(pdf.relative_to(ROOT)), "audit_ok": rep["ok"],
                "width_mm": rep["width_mm"], "height_mm": rep["height_mm"],
                "findings": [f["check"] + ": " + f["detail"][:70] for f in rep["findings"]],
            })
            print(f"  {name:<18} {len(df):3d} rows  {rep['width_mm']:6.1f} x "
                  f"{rep['height_mm']:5.1f} mm  audit={'OK' if rep['ok'] else 'FAIL'}")
            for f in rep["findings"]:
                print(f"      {f['check']}: {f['detail'][:80]}")
        except Exception as e:                                   # noqa: BLE001
            results.append({"template": name, "error": f"{type(e).__name__}: {e}"})
            print(f"  {name:<18} ERROR {type(e).__name__}: {str(e)[:60]}")

    (ROOT / "templates" / "render_report.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for r in results if r.get("audit_ok"))
    print(f"\n  rendered {len(results)} templates, {ok} pass the audit")
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
