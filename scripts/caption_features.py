"""Caption features measured from TEXT, not from a vision model.

WHY TEXT RATHER THAN VLM FOR THIS
    The adversarial audit proved the local VLM FABRICATES: given a blank page it answered
    `column_width: single` and `high_contrast: true`; across three controls it made 20
    assertions about images that have no figure (verdict: FABRICATES). Its agreement with the
    PDF geometry on column_width was 55 %.

    Three of the fields the task asked for are properties of the CAPTION STRING, not of the
    pixels:
        caption_overview_first   does it open with a summary sentence?
        caption_panel_by_panel   does it then walk the panels?
        caption_has_stats        does it state n, a test, or an error definition?
        caption_stats_last       is that statistical material at the end?
    Asking a model to read these off an image is asking it to do OCR badly. Measuring them from
    the text is exact, reproducible, and costs nothing.

WHAT IS MEASURED, AND HOW THE RULE WAS DERIVED
    The rules below were written after reading real Nature captions, and each one is stated so
    a reader can disagree with it. They are HEURISTICS over text, so every feature carries the
    evidence that produced it, and the extractor reports how often each rule fired -- a rule
    that never fires is not doing work.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "caption_features.jsonl"

#: Panel walkers: "(a) ...", "(b)", "a, ", "Left:" -- Nature uses several forms.
PANEL_RE = re.compile(r"\((?:[a-h]|[ivx]{1,4})\)|(?<![A-Za-z])(?:[a-h])\s*[,)]\s")
#: Statistical material: sample sizes, tests, intervals, error definitions.
STATS_RE = re.compile(
    r"\b(?:n\s*=\s*[\d,]+|\bp\s*[<=>]\s*0?\.\d+|P\s*[<=>]\s*0?\.\d+"
    r"|\d+\s*%\s*(?:CI|confidence)|confidence\s+interval|s\.?d\.?|s\.?e\.?m\.?"
    r"|mean\s*±\s*|±\s*[\d.]+|two-tailed|one-tailed|ANOVA|t-test|χ2|chi-squared"
    r"|Wilcoxon|Mann–Whitney|Mann-Whitney|Kruskal|bootstrap|error bars?)\b", re.I)
#: An error-definition phrase is a strong marker that the caption explains its own metric.
ERROR_DEF_RE = re.compile(r"\b(?:error\s+(?:bars?|rate|definition)|defined\s+as|we\s+define)\b", re.I)
#: The label Nature puts in front of a figure caption.
LABEL_RE = re.compile(r"^\s*(?:Extended\s+Data\s+)?(?:Fig(?:ure)?\.?\s*\d+\s*[|｜:]?\s*)", re.I)
#: "Title case sentence." -- an overview sentence rather than a panel walk.
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def strip_label(text: str) -> str:
    return LABEL_RE.sub("", text).strip()


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def measure(caption: str) -> dict:
    """Every caption feature, with the evidence that produced it."""
    raw = caption or ""
    body = strip_label(raw)
    sents = sentences(body)
    first = sents[0] if sents else ""
    last = sents[-1] if sents else ""

    panel_hits = PANEL_RE.findall(body)
    stats_hits = STATS_RE.findall(body)
    stat_positions = [m.start() for m in STATS_RE.finditer(body)]

    # overview-first: the opening sentence is a general statement, i.e. it does NOT itself
    # start a panel walk and is not shot through with statistics.
    first_is_panel = bool(PANEL_RE.match(first)) if first else False
    first_has_stats = bool(STATS_RE.search(first)) if first else False
    overview_first = bool(first) and not first_is_panel and not first_has_stats

    # panel-by-panel: panel markers appear after the opening sentence.
    panel_by_panel = len(panel_hits) >= 2

    # stats present; and whether the LAST sentence carries them.
    has_stats = bool(stats_hits)
    stats_last = bool(has_stats and last and STATS_RE.search(last))
    # where in the string does the first statistical marker fall (0..1), for a distribution
    first_stat_frac = round(stat_positions[0] / len(body), 3) if stat_positions else None

    return {
        "caption_chars": len(body),
        "n_sentences": len(sents),
        "n_panel_markers": len(panel_hits),
        "n_stat_markers": len(stats_hits),
        "caption_overview_first": overview_first,
        "caption_panel_by_panel": panel_by_panel,
        "caption_has_stats": has_stats,
        "caption_stats_last": stats_last,
        "caption_defines_error": bool(ERROR_DEF_RE.search(body)),
        "first_stat_fraction": first_stat_frac,
        "overview_evidence": first[:120],
        "stats_evidence": (stats_hits[:5] if stats_hits else []),
        "panel_evidence": (panel_hits[:6] if panel_hits else []),
    }


def main() -> int:
    papers = [d for d in (ROOT / "corpus" / "extracted").iterdir() if d.is_dir()]
    rows = []
    for d in sorted(papers):
        meta = d / "figures_meta.json"
        if not meta.is_file():
            continue
        fm = json.loads(meta.read_text(encoding="utf-8"))
        for f in fm.get("figures", []):
            cap = (f.get("caption_text") or "").strip()
            if not cap:
                continue
            rows.append({
                "paper": d.name,
                "figure_id": f.get("figure_id"),
                "kind": f.get("kind"),
                "page": f.get("page"),
                "caption_text": cap,
                **measure(cap),
            })
    OUT.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    n = len(rows)
    if not n:
        print("  no captions found")
        return 1
    def rate(key):
        k = sum(1 for r in rows if r.get(key))
        return f"{k:4d}/{n} = {100*k/n:5.1f}%"

    print(f"  captions measured: {n}")
    print()
    print(f"  caption_overview_first : {rate('caption_overview_first')}")
    print(f"  caption_panel_by_panel : {rate('caption_panel_by_panel')}")
    print(f"  caption_has_stats      : {rate('caption_has_stats')}")
    print(f"  caption_stats_last     : {rate('caption_stats_last')}")
    print(f"  caption_defines_error  : {rate('caption_defines_error')}")
    print()
    main_text = [r for r in rows if str(r["kind"]) == "figure"]
    if main_text:
        k = sum(1 for r in main_text if r["caption_panel_by_panel"])
        print(f"  main-text figures only : {k}/{len(main_text)} = "
              f"{100*k/len(main_text):.1f}% walk the panels")
    print(f"\n  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
