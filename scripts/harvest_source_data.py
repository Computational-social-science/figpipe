"""Harvest numeric tables from the corpus as reusable plotting data.

WHY THIS IS THE RIGHT SOURCE
    The owner's target: obtain the papers' original data, reproduce the typical plotting
    styles, and turn the result into reusable high-quality templates.

    Nature's figure-level Source Data sits in separate supplementary workbooks that are not in
    these PDFs. But docling's `content.md` already contains the papers' TABLES as markdown, and
    a table is data. Measured over the 84-paper corpus: 42 papers carry markdown tables, 89 of
    them with at least one numeric column and 3+ rows.

    That is enough to drive real chart templates: a bar chart, a scatter, a grouped comparison
    and a line series can all be built from a table with a label column and a numeric column.

WHAT IS KEPT AND WHAT IS REJECTED
    A table is accepted only if
      * it has a header row and >= 3 data rows,
      * at least one column parses as numbers in the majority of its non-empty cells,
      * and it has at least one non-numeric column to serve as the category / x axis.
    Everything else is counted with its reason. A file of half-parsed tables would be worse
    than no file: a template built on garbled numbers teaches the wrong shape.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "extracted"
OUT = ROOT / "corpus" / "source_data.json"

NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$")


def parse_number(cell: str):
    """A number, or None. Handles thousands separators, %, and a trailing (sd)."""
    c = cell.strip().replace(",", "").replace("%", "").strip()
    c = re.sub(r"\s*\(.*?\)\s*$", "", c)          # drop "1,200 (249)" -> 1200
    if NUM_RE.match(c):
        try:
            return float(c)
        except ValueError:
            return None
    return None


def md_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Markdown tables as (header, rows), separator rows dropped."""
    blocks, cur = [], []
    for ln in text.splitlines():
        if ln.strip().startswith("|") and ln.count("|") >= 2:
            cur.append(ln)
        else:
            if len(cur) >= 3:
                blocks.append(cur)
            cur = []
    if len(cur) >= 3:
        blocks.append(cur)

    out = []
    for b in blocks:
        cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in b]
        cells = [r for r in cells
                 if not (r and all(re.fullmatch(r":?-{2,}:?", c) for c in r if c))]
        if len(cells) >= 2:
            out.append((cells[0], cells[1:]))
    return out


def classify(header: list[str], rows: list[list[str]]) -> dict:
    """Which column can be x, which can be y. Rejects a table that cannot carry a chart."""
    n_cols = len(header)
    if n_cols < 2:
        return {"usable": False, "reason": "single column"}
    if len(rows) < 3:
        return {"usable": False, "reason": "fewer than 3 rows"}

    numeric_cols, label_cols = [], []
    for ci in range(n_cols):
        vals = [r[ci] for r in rows if ci < len(r) and r[ci].strip()]
        if not vals:
            continue
        nums = [parse_number(v) for v in vals]
        n_num = sum(1 for x in nums if x is not None)
        if n_num >= max(2, int(0.6 * len(vals))):
            numeric_cols.append({"col": ci, "header": header[ci] if ci < len(header) else "",
                                 "n_numeric": n_num, "values": [x for x in nums if x is not None]})
        else:
            label_cols.append({"col": ci, "header": header[ci] if ci < len(header) else "",
                               "n_rows": len(vals)})

    if not numeric_cols:
        return {"usable": False, "reason": "no numeric column"}
    if not label_cols:
        return {"usable": False, "reason": "no label column for an axis"}
    return {"usable": True, "reason": "", "numeric_cols": numeric_cols,
            "label_cols": label_cols, "n_rows": len(rows)}


def main() -> int:
    accepted, rejected = [], {}
    for d in sorted(CORPUS.iterdir()):
        if not d.is_dir():
            continue
        md = d / "content.md"
        if not md.is_file():
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        for ti, (header, rows) in enumerate(md_tables(text)):
            verdict = classify(header, rows)
            if not verdict["usable"]:
                rejected[verdict["reason"]] = rejected.get(verdict["reason"], 0) + 1
                continue
            accepted.append({
                "paper": d.name, "table_index": ti,
                "header": header, "n_rows": verdict["n_rows"],
                "numeric_cols": [{"col": c["col"], "header": c["header"],
                                  "values": c["values"]} for c in verdict["numeric_cols"]],
                "label_cols": [{"col": c["col"], "header": c["header"]} for c in verdict["label_cols"]],
                "rows_preview": rows[:6],
            })

    OUT.write_text(json.dumps({
        "about": ("Numeric tables extracted from the corpus's content.md. These are the "
                  "papers' own tabulated values, used to drive plotting templates with real "
                  "data rather than invented data."),
        "n_accepted": len(accepted),
        "n_rejected": sum(rejected.values()),
        "rejected_by_reason": rejected,
        "tables": accepted,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  tables accepted : {len(accepted)}")
    print(f"  tables rejected : {sum(rejected.values())}  {rejected}")
    papers = len({t['paper'] for t in accepted})
    print(f"  papers covered  : {papers}")
    print()
    print("  sample (first 5):")
    for t in accepted[:5]:
        nc = t["numeric_cols"][0]
        print(f"    {t['paper'][:44]:<44} {t['n_rows']:4d} rows  "
              f"y='{nc['header'][:18]}' n={len(nc['values'])}")
    print(f"\n  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
