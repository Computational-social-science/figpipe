"""Classify what a figure IS before judging how it should look.

THE OWNER'S RULE
    没有一个统一的绝对标准，但必须科学且可迭代
    -- there is no single absolute standard; the classification must be scientific and able to
       evolve.

    This is the direct correction of the mistake this project made twice:
      * H02 asserted a "compliant ink band" of 3.3-17.4 % measured on six line plots and
        generalised to "figures"
      * E01/E02 generalised a whole corpus's width and font statistics across main text,
        Extended Data and supplements alike

    Both failed the same way: they averaged over kinds that are not comparable. A mechanism
    diagram, a forest plot and a micrograph do not answer to the same layout rules, and a
    single "Nature standard" that covers all three is an artefact of not having classified them.

WHAT THIS MODULE DOES
    It assigns each figure to a TYPE, using only what is measurable without a vision model:
    the caption text, the crop geometry, and whether the crop is mostly photographic. Each
    type carries its own measured distribution, so a rule can be stated CONDITIONAL on type
    rather than over everything.

    Types are a starting partition, not a truth. The module records the evidence for each
    assignment and how confident it is, so the partition can be revised -- which is what
    "iterable" requires.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Type assignment rules, ordered. First match wins. Each entry states what it keys on.
#: The order matters: "micrograph" is checked before "scatter" because a micrograph caption
#: often mentions axes and statistics without being a plot.
TYPE_RULES = [
    ("micrograph", re.compile(
        r"\b(?:micrograph|electron microscop\w+|scale bar|μm|µm|immunofluor\w+|histolog\w+"
        r"|stain(?:ed|ing)?|cryo-?EM|tomograph\w+|confocal|fluorescence image)\b", re.I)),
    ("network", re.compile(
        r"\b(?:network diagram|node|edge weight|graph of|connectom\w+|tree diagram"
        r"|phylogen\w+|dendrogram)\b", re.I)),
    ("heatmap", re.compile(
        r"\b(?:heat ?map|colour ?map|color ?map|matrix of|correlation matrix|z-score map)\b", re.I)),
    ("scatter", re.compile(
        r"\b(?:scatter|each point|plotted against|regression line|fitted curve|R\s*=\s*0?\.\d"
        r"|Pearson|Spearman|residual)\b", re.I)),
    ("bar", re.compile(
        r"\b(?:bar chart|bars show|bar heights|error bars|grouped bars|stacked bars)\b", re.I)),
    ("boxplot", re.compile(
        r"\b(?:box ?plot|box-and-whisker|violin|quartile|median and interquartile|IQR)\b", re.I)),
    ("time_series", re.compile(
        r"\b(?:time series|over time|trajectory|trend across|from \d{4} to \d{4}|annual)\b", re.I)),
    ("schematic", re.compile(
        r"\b(?:schematic|workflow|pipeline|framework|architecture|overview of the (?:method|approach)"
        r"|illustration|diagram of)\b", re.I)),
    ("supplementary_data", re.compile(
        r"^\s*(?:Supplementary|Extended\s+Data)", re.I)),
]

#: Aspect-ratio bands, used only as a WEAK tiebreak when the caption says nothing.
#: A very wide crop is usually a panel row; a tall one usually a panel column.
ASPECT_WIDE = 2.5
ASPECT_TALL = 0.45


def classify(caption: str, width_mm: float | None, height_mm: float | None,
             kind: str | None = None) -> dict:
    """Assign a type with the evidence and a confidence level.

    Confidence is 'caption' when a caption rule fired (the strongest available signal without
    looking at pixels), 'geometry' when only the aspect ratio spoke, and 'unknown' otherwise.
    An unknown figure is NOT forced into a bucket -- it is reported as unclassified, so the
    distribution does not silently absorb it.
    """
    cap = caption or ""
    for name, pat in TYPE_RULES:
        m = pat.search(cap)
        if m:
            return {"figure_type": name, "confidence": "caption",
                    "evidence": m.group(0)[:60], "kind": kind}

    if width_mm and height_mm:
        aspect = float(width_mm) / float(height_mm) if height_mm else None
        if aspect is not None:
            if aspect >= ASPECT_WIDE:
                return {"figure_type": "panel_row", "confidence": "geometry",
                        "evidence": f"aspect {aspect:.2f} >= {ASPECT_WIDE}", "kind": kind}
            if aspect <= ASPECT_TALL:
                return {"figure_type": "panel_column", "confidence": "geometry",
                        "evidence": f"aspect {aspect:.2f} <= {ASPECT_TALL}", "kind": kind}

    return {"figure_type": "unclassified", "confidence": "none",
            "evidence": "no caption rule fired and geometry is unremarkable", "kind": kind}


def classify_corpus() -> dict:
    """Every figure in the extracted corpus, with its type and the evidence."""
    out = []
    for d in sorted((ROOT / "corpus" / "extracted").iterdir()):
        if not d.is_dir():
            continue
        meta = d / "figures_meta.json"
        if not meta.is_file():
            continue
        fm = json.loads(meta.read_text(encoding="utf-8"))
        for f in fm.get("figures", []):
            bb = f.get("bbox") or {}
            # PDF points to mm
            w = bb.get("w")
            h = bb.get("h")
            rec = classify(f.get("caption_text") or "",
                           (w * 25.4 / 72) if w else None,
                           (h * 25.4 / 72) if h else None,
                           f.get("kind"))
            out.append({"paper": d.name, "figure_id": f.get("figure_id"),
                        "page": f.get("page"), **rec})
    return {"n": len(out), "assignments": out}


def summarise_figure_types(result: dict) -> dict:
    from collections import Counter
    a = result["assignments"]
    by_type = Counter(r["figure_type"] for r in a)
    by_conf = Counter(r["confidence"] for r in a)
    # cross-tab: type x document kind, so main text and Extended Data stay separable
    cross: dict[str, Counter] = {}
    for r in a:
        cross.setdefault(str(r.get("kind")), Counter())[r["figure_type"]] += 1
    return {"n": result["n"],
            "by_type": dict(by_type.most_common()),
            "by_confidence": dict(by_conf.most_common()),
            "by_kind": {k: dict(v.most_common()) for k, v in cross.items()}}


if __name__ == "__main__":
    res = classify_corpus()
    summ = summarise_figure_types(res)
    out = ROOT / "corpus" / "figure_types.json"
    out.write_text(json.dumps({"summary": summ, "assignments": res["assignments"]},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  figures classified: {summ['n']}")
    print()
    print("  by type:")
    for k, v in summ["by_type"].items():
        print(f"    {k:<22} {v:5d}  {100*v/summ['n']:5.1f}%")
    print()
    print("  by confidence:", summ["by_confidence"])
    print()
    print("  by document kind (first rows):")
    for k, v in list(summ["by_kind"].items())[:3]:
        print(f"    {k}: {dict(list(v.items())[:5])}")
    print(f"\n  wrote {out.relative_to(ROOT)}")
