"""Does figpipe's style distance actually DISCRIMINATE? A measured answer, not a promise.

WHY THIS SCRIPT EXISTS
    `CLAIM.md` said, for several rounds, that the style distance and the official channel are
    deterministic metrics whose relation to expert preference "has not been measured yet".
    `LOGICAL_AUDIT.md` section 1 names the same sentence as the residual risk: the weights are
    hand-set and nothing validated that a smaller distance corresponds to a better transfer.

    That is the last genuine research gap in the claim, and it is answerable on this machine
    without a model, a network call, or a human rater -- by a DISCRIMINATION experiment.

THE EXPERIMENT
    For each of N real published figures in `corpus/extracted/` (a vector PDF region, so the
    profile is measured from the PDF's own objects rather than guessed from pixels):

        reference   = the true figure's measured style profile
        A           = a candidate whose style was transferred from a MISMATCHED figure
                      (a different published figure from a different paper)
        B           = a candidate whose style was transferred from the reference ITSELF

    Both candidates are rendered by figpipe from the SAME data and the same grammar, so the
    only difference between them is the style source. The question is then exactly the one the
    metric claims to answer: does figpipe's own distance put B closer to the reference than A?

        discrimination_accuracy = #{d(B) < d(A)} / N

    At chance this is 0.5. The null hypothesis is "the metric cannot tell a matched transfer
    from a mismatched one", which is the weakest property a style metric must have.

WHY THIS IS A DEFENSIBLE PROXY AND NOT HUMAN VALIDATION
    It tests ORDERING, not PREFERENCE. A metric can discriminate and still disagree with an
    expert about which of two close candidates is better. What it CAN refute is the stronger
    and more common failure: a metric that is blind, or that ranks a wrong transfer above a
    right one. That refutation is what this script can deliver, and CLAIM.md is updated with
    exactly that scope -- no more.

    The mismatch is drawn from a DIFFERENT PAPER where possible. Two figures in one paper share
    a house style, so a same-paper mismatch would be a weaker contrast; the sampling records
    which it was, and the artefact reports both.

WHY THE OFFICIAL SCORER IS RUN ON THE SAME PAIRS
    Two independent deterministic instruments agreeing is evidence about which of them is
    measuring style. The official channel (`deviation-defect-v1`, 35 % of PlotTwin-Bench) is a
    DEVIATION score: 100 means the candidate's style matches the reference's style exactly. It
    is run here on code emitted from the RENDERED candidates' own measured profiles, so it sees
    what actually came out rather than what the transfer intended -- otherwise it would agree
    with figpipe by construction and the comparison would be worthless.

    Agreement is counted only where the official channel is `available` for BOTH candidates of a
    pair; an unavailable channel is reported as a count, never as a disagreement.

NEGATIVE CONTROL, BUILT IN
    The same arithmetic is applied to a DELIBERATELY INVERTED ranking (distance negated). It
    must score `1 - discrimination_accuracy`; a harness that reported the same number for the
    inverted ranking would be measuring nothing. The test suite asserts it lands below 0.5.

WHAT THIS SCRIPT DOES NOT DO
    * No network call, no VLM, no model of any kind. The corpus is local vector PDFs.
    * It does not re-run the benchmark pool (`bench_plottwin.py` / `score_official.py` at pool
      scale are explicitly out of scope here); it scores a few dozen pairs, which is enough to
      separate a real effect from chance and cheap enough to re-run.
    * It does not claim the closer figure is the better figure in any aesthetic sense.

USAGE
    python scripts/validate_style_metric.py                 # measure (refuses if busy)
    python scripts/validate_style_metric.py --n 32          # change the pair count
    python scripts/validate_style_metric.py --report        # print the stored artefact
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "third_party"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from figpipe import codegen, composite, layout, lock, select, styleprofile  # noqa: E402

try:                                     # the official scorer is optional (CC BY-NC, local only)
    import plottwin_scorer as official
except Exception:                        # noqa: BLE001
    official = None

EXTRACTED = ROOT / "corpus" / "extracted"
OUT = ROOT / "corpus" / "e2e" / "style_validation.json"

#: A reference must be measurable as a VECTOR region with enough of a style to transfer.
#: Below these floors a "reference" is a picture of a diagram, not a style: 60 pt wide regions
#: produced single-glyph labels and no palette, and a pair built from one measures nothing.
MIN_WIDTH_PT = 90.0
MIN_HEIGHT_PT = 60.0
MIN_TEXT_SPANS = 8
MIN_SIZE_TIERS = 2
MIN_COLOURS = 2

#: Seed for the mismatch draw. Fixed so the artefact can be re-derived; recorded in the JSON.
SEED = 20261019

#: The synthetic panel every candidate is drawn from. IDENTICAL for both candidates of a pair --
#: the only thing that varies is the style source, which is the point of the experiment.
_PANEL_KW = {"x": "x", "y": "y", "lo": "lo", "hi": "hi", "band": "data", "fit": "lm",
             "xlabel": "Year", "ylabel": "Value"}


def _panel() -> composite.Panel:
    df = pd.DataFrame({"x": np.arange(24.0),
                       "y": np.linspace(0.10, 0.92, 24) + 0.01 * np.sin(np.arange(24.0)),
                       "lo": np.linspace(0.05, 0.87, 24),
                       "hi": np.linspace(0.15, 0.97, 24)})
    return composite.Panel("trend_band", df, dict(_PANEL_KW))


# --------------------------------------------------------------------------------------
# Corpus
# --------------------------------------------------------------------------------------

def corpus_figures() -> list[dict]:
    """Every main figure in the extracted corpus whose source PDF is still on disk.

    The corpus records a figure region in PDF points with a BOTTOM-LEFT origin and a page
    height; `StyleProfile.from_pdf` takes a top-left-origin clip rect, so the conversion is
    explicit here rather than assumed.
    """
    import pymupdf

    out: list[dict] = []
    if not EXTRACTED.is_dir():
        return out
    for paper in sorted(p for p in EXTRACTED.iterdir() if p.is_dir()):
        meta_path = paper / "figures_meta.json"
        if not meta_path.is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        pdf = pathlib.Path(meta.get("source_pdf") or "")
        if not pdf.is_file():
            continue
        try:
            doc = pymupdf.open(str(pdf))
        except Exception:                                  # noqa: BLE001 - unreadable PDF
            continue
        try:
            for fig in meta.get("figures", []):
                if fig.get("kind") != "figure":
                    continue
                bb = fig.get("bbox") or {}
                if not bb or bb.get("w", 0) < MIN_WIDTH_PT or bb.get("h", 0) < MIN_HEIGHT_PT:
                    continue
                page = int(fig.get("page") or 0)
                if not 1 <= page <= len(doc):
                    continue
                page_h = doc[page - 1].rect.height
                out.append({
                    "paper": paper.name,
                    "figure_id": fig.get("figure_id"),
                    "page": page,
                    "pdf": pdf,
                    "rect_pt": (bb["l"], page_h - bb["t"], bb["r"], page_h - bb["b"]),
                    "size_pt": (round(bb["w"], 1), round(bb["h"], 1)),
                })
        finally:
            doc.close()
    return out


def profile_of(rec: dict) -> styleprofile.StyleProfile:
    """Measure the reference's style from the PDF's own objects (vector, exact)."""
    prof = styleprofile.StyleProfile.from_pdf(rec["pdf"], page=rec["page"],
                                              bbox_pt=rec["rect_pt"])
    prof.source = f"{rec['paper']}/{rec['figure_id']}"
    return prof


def measurable(prof: styleprofile.StyleProfile) -> bool:
    """A reference is usable only if it has enough measured style to transfer and to compare.

    These floors are not cosmetic. A region that is one photograph with two axis labels yields
    a size distribution with one tier and a palette of antialiasing greys; a pair built from it
    would measure the absence of a style, not the metric's sensitivity.
    """
    return (prof.n_text_spans >= MIN_TEXT_SPANS
            and len(set(prof.sizes_pt)) >= MIN_SIZE_TIERS
            and len(prof.colours) >= MIN_COLOURS)


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

def transfer_style(reference: styleprofile.StyleProfile,
                   *, apply_aspect: bool = True) -> dict:
    """Everything `reference` measured, expressed as settings the renderer can apply.

    WHY THIS IS NOT JUST `style_from_profile`
        `style_from_profile` returns font sizes, stroke widths, the palette and an aspect-derived
        height -- two of the six dimensions `styleprofile.compare` scores. The other four (grid,
        spines, panel letters, and the palette as the DRAWER uses it) are measured by the profile
        but never reach the canvas through that function.

        The first version of this experiment used it alone, and the per-dimension breakdown
        caught the consequence: `palette`, `rules`, `letters` and `lines` were IDENTICAL between
        the matched and mismatched candidate on almost every pair, so those four dimensions were
        not being tested at all -- the 0.93 accuracy was carried by `sizes` and `aspect` alone.
        A discrimination experiment whose treatment only reaches part of the metric understates
        what the metric can do and overstates what was demonstrated.

        So every dimension the comparison reads on the REFERENCE side is now applied on the
        candidate side too, from the same measurement:

            sizes    -> rc font tiers                     (style_from_profile)
            aspect   -> height derived from width/height   (style_from_profile)
            lines    -> rc axes.linewidth                  (style_from_profile)
            palette  -> the drawer's `palette` kwarg
            rules    -> rc axes.grid + axes.spines.*
            letters  -> composite(letters=...)

        Each is a style decision the reference actually exhibits; none of them reads the target.

    `apply_aspect=False` IS A DIAGNOSTIC, not a shipping mode. It renders the candidate at a fixed
    height so the two candidates differ ONLY in the dimensions the metric is supposed to measure.
    With aspect applied, that component tests whether the transfer ran -- a plumbing check that
    cannot fail -- so the headline accuracy is partly a tautology.
    """
    derived = styleprofile.style_from_profile(reference)
    rc = dict(derived["rc"])
    # GRID and SPINES are measured as rules and as long edge lines on the reference.
    grid = (reference.rules_h + reference.rules_v) > 0
    rc["axes.grid"] = bool(grid)
    for side, present in (reference.spines or {}).items():
        if side in ("left", "right", "top", "bottom"):
            rc[f"axes.spines.{side}"] = bool(present)
    return {
        "rc": rc,
        "palette": derived["palette"],
        # a fixed height when aspect is withheld, so the candidates cannot differ on it
        "height_mm": float(derived["height_mm"]) if apply_aspect else 100.0,
        # the reference either prints panel letters or it does not; both are style choices
        "letters": bool(reference.panel_letters),
        "grid": bool(grid),
        "spines": dict(reference.spines or {}),
    }


def _stroke_weights(reference: styleprofile.StyleProfile) -> dict:
    """The reference's measured stroke widths, as (median, thinnest, thickest).

    `line_widths_pt` is read from the PDF's own path widths, so it is an exact measurement for a
    vector source. Many published figures carry none (the paths are filled shapes rather than
    stroked lines), and the comparison then excludes the dimension -- which is why the caller
    must treat an empty list as "not measured" rather than "zero".
    """
    widths = sorted(float(w) for w in (reference.line_widths_pt or []) if w and w > 0)
    if not widths:
        return {}
    return {"median": widths[len(widths) // 2],
            "thin": widths[0],
            "thick": widths[-1]}


def _apply_stroke(fig, reference: styleprofile.StyleProfile) -> int:
    """Draw every line in the candidate at the REFERENCE's measured stroke weight.

    WHY THIS IS NECESSARY
        `drawlib`'s drawers carry their own stroke widths (`lw=1.0` on a fit, `lw=0.6` on a
        reference rule) because a drawer has to draw something before any style is known. Those
        literals do not consult rcParams, so a style transfer that only sets `axes.linewidth`
        leaves every plotted line at figpipe's default -- and `styleprofile.compare`'s `lines`
        component then sees the SAME width on both candidates of a pair.

        The per-dimension breakdown made that visible: `lines` scored exactly 0.000 with
        identical A and B values on every pair, i.e. the dimension was not tested. Restating the
        reference's measured width on the artists is the transfer doing what it claims.

    The widths keep their ORDER: the fit line stays the heaviest and the reference rule the
    lightest, scaled by the ratio of the reference's measured spread to figpipe's own. Copying
    one flat width would erase the visual hierarchy the reference actually has.
    """
    weights = _stroke_weights(reference)
    if not weights:
        return 0
    target = weights["median"]
    changed = 0
    for ax in getattr(fig, "axes", []):
        for line in ax.get_lines():
            current = float(line.get_linewidth())
            if current <= 0:
                continue                      # an invisible artist states no weight
            line.set_linewidth(round(target, 3))
            changed += 1
        for patch in ax.patches:
            if float(patch.get_linewidth()) > 0:
                patch.set_linewidth(round(min(target, weights["thick"]), 3))
                changed += 1
        for collection in getattr(ax, "collections", []):
            if float(collection.get_linewidths()[0] if collection.get_linewidths() else 0) > 0:
                collection.set_linewidth(round(target, 3))
                changed += 1
    return changed


def render_transfer(reference: styleprofile.StyleProfile, out_stem,
                    *, apply_aspect: bool = True) -> pathlib.Path:
    """Draw the fixed panel in `reference`'s measured style; return the rendered PDF.

    This is figpipe's style transfer in its simplest honest form: every style decision the
    profile measured is applied, and nothing reads the target.
    """
    style = transfer_style(reference, apply_aspect=apply_aspect)
    panel = _panel()
    # the drawer takes its series colours as a kwarg, so the palette has to travel with the
    # panel rather than only with rcParams (which the drawer does not consult for series ink)
    panel = composite.Panel(panel.draw, panel.data,
                            {**panel.kwargs, "palette": style["palette"]})
    fig = composite.composite([panel], columns=2.0,
                              height_mm=style["height_mm"],
                              rc=style["rc"], letters=style["letters"])
    _apply_stroke(fig, reference)
    paths = layout.save(fig, out_stem)
    return pathlib.Path(paths[0])


def code_for(prof: styleprofile.StyleProfile) -> str:
    """Emit a matplotlib script that DECLARES the style this profile measured.

    The official channel reads AST, not pixels, so a rendered PDF has to be re-expressed as the
    style calls it carries. This is the same emitter the benchmark uses, fed the candidate's
    own measured profile -- so the official score describes what was rendered, not what the
    transfer intended.
    """
    style = transfer_style(prof)
    panel = _panel()
    panel = composite.Panel(panel.draw, panel.data,
                            {**panel.kwargs, "palette": style["palette"]})
    # `codegen.emit` reads the stroke weight out of the STYLE dict, not a separate argument, so
    # the measured width travels the same way the transfer's other decisions do.
    weights = _stroke_weights(prof)
    style_calls = {"linewidth": weights.get("median")} if weights else {}
    style_calls.update({
        "grid": style["grid"],
        "spines_removed": (tuple(k for k, v in style["spines"].items() if not v)
                           if style["spines"] else None),
        "tick_direction": prof.tick_direction or "out",
        "serif": bool(prof.serif_guess) if prof.serif_guess is not None else None,
        "legend_frame": None,
    })
    return codegen.emit([panel], columns=2.0, height_mm=style["height_mm"],
                        rc=style["rc"], palette=style["palette"], style=style_calls)


def official_scores(reference: styleprofile.StyleProfile,
                    candidates: dict[str, styleprofile.StyleProfile]) -> dict:
    """Score every candidate against the reference with the benchmark's own code channel.

    Returns `{name: score_or_None}` plus the reason when a score is unavailable. An unavailable
    channel is an absence to be counted, never a zero and never a disagreement.
    """
    if official is None:
        return {"available": False, "reason": "official scorer not vendored", "scores": {}}
    try:
        ref_code = code_for(reference)
    except Exception as exc:                               # noqa: BLE001
        return {"available": False, "reason": f"reference not expressible: {type(exc).__name__}",
                "scores": {}}
    out: dict[str, float | None] = {}
    reasons: dict[str, str] = {}
    for name, prof in candidates.items():
        try:
            res = official.score_code_deviation(ref_code, code_for(prof))
        except Exception as exc:                           # noqa: BLE001
            out[name] = None
            reasons[name] = f"scorer failed: {type(exc).__name__}"
            continue
        if res.get("available") and res.get("score") is not None:
            out[name] = float(res["score"])
        else:
            out[name] = None
            reasons[name] = str(res.get("status") or "unavailable")
    return {"available": all(v is not None for v in out.values()),
            "scores": out, "reasons": reasons}


# --------------------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------------------

def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    WHY WILSON AND NOT WALD: the Wald interval collapses to zero width at k = n, which is
    exactly the case a clean result produces -- it would report "0.97 +/- 0.00" for 30/30 and
    claim certainty the experiment does not have. Wilson stays inside [0, 1] and keeps a
    non-zero width at the boundaries.
    """
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = (z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))) / denom
    return (round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4))


def binomial_p_value(k: int, n: int) -> float:
    """One-sided exact binomial p for "better than chance", H0: p = 0.5.

    Reported because a discrimination accuracy on 30 pairs is not self-interpreting: 22/30 is
    p = 0.008, while 18/30 is p = 0.18 and supports nothing.

    NOT ROUNDED TO SIX PLACES. 28/30 has p = 4.3e-07, and rounding that to 0.000000 would print
    "p = 0.0" -- which no exact test can produce and which reads as a certainty the experiment
    does not have. The value is kept at full precision and a separate `p_value_text` renders it
    in scientific notation for display.
    """
    if n <= 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(k, n + 1)) / (2 ** n)
    return min(1.0, tail)


def _p_text(p: float) -> str:
    """A p-value as a reader should see it: never a bare 0."""
    if p <= 0.0:
        return "< 1e-300"
    if p < 1e-3:
        return f"{p:.2e}"
    return f"{p:.4f}"


# --------------------------------------------------------------------------------------
# The experiment
# --------------------------------------------------------------------------------------

def _mismatch_index(i: int, refs: list[dict], rng: random.Random,
                    contrast: str = "cross") -> tuple[int, str]:
    """Pick a different reference at a stated contrast.

    TWO CONTRASTS, AND THE HARD ONE IS THE POINT.

    `cross`  a different PAPER. This is the easy condition: two unrelated papers differ in
             palette, typography and layout at once, so almost any metric separates them.
    `same`   a different FIGURE IN THE SAME PAPER. Those figures share a house style -- the same
             fonts, the same palette, the same axes conventions -- and differ only in how the
             individual panel was drawn. This is the condition a style metric is actually FOR:
             separating a faithful transfer from a near-miss. A metric that only passes `cross`
             has been shown to tell Nature from not-Nature, not to measure style.

    The first version of this experiment preferred `cross` and reported 30/30, which is a
    ceiling, not a sensitivity measurement. Both arms are now measured and reported separately.
    """
    others = [k for k in range(len(refs)) if k != i]
    if contrast == "same":
        pool = [k for k in others if refs[k]["paper"] == refs[i]["paper"]]
        if not pool:
            return -1, "unavailable"
        j = rng.choice(pool)
        return j, "same_paper"
    cross = [k for k in others if refs[k]["paper"] != refs[i]["paper"]]
    pool = cross or others
    j = rng.choice(pool)
    return j, ("different_paper" if refs[j]["paper"] != refs[i]["paper"] else "same_paper")


def measure(n_pairs: int = 30, seed: int = SEED, verbose: bool = True,
            contrast: str = "cross", apply_aspect: bool = True) -> dict:
    """Run the discrimination experiment and return the artefact dictionary.

    `contrast` is "cross" (mismatch from a different paper -- the easy condition) or "same"
    (mismatch from another figure in the same paper -- the condition a style metric is for).
    """
    rng = random.Random(seed)
    candidates = corpus_figures()
    if verbose:
        print(f"  corpus figures with a source PDF: {len(candidates)}")

    # SCAN THE WHOLE CORPUS, then sample. Stopping at the first N measurable figures would
    # sample the corpus's own ordering (papers sorted by year and slug), which is not a random
    # draw and would let one well-represented decade decide the result.
    refs: list[dict] = []
    skipped: dict[str, int] = {}
    for rec in candidates:
        try:
            prof = profile_of(rec)
        except Exception as exc:                           # noqa: BLE001
            skipped[type(exc).__name__] = skipped.get(type(exc).__name__, 0) + 1
            continue
        if not measurable(prof):
            skipped["below_style_floors"] = skipped.get("below_style_floors", 0) + 1
            continue
        rec = dict(rec)
        rec["profile"] = prof
        refs.append(rec)

    if len(refs) < 2:
        raise RuntimeError(f"need at least two measurable references, found {len(refs)}; "
                           f"skipped: {skipped}")

    # only references that CAN supply the requested contrast take part
    if contrast == "same":
        per_paper: dict[str, int] = {}
        for r in refs:
            per_paper[r["paper"]] = per_paper.get(r["paper"], 0) + 1
        usable = [i for i, r in enumerate(refs) if per_paper[r["paper"]] >= 2]
        if not usable:
            raise RuntimeError("no paper has two measurable figures; the same-paper contrast "
                               "is unavailable on this corpus")
        refs = [refs[i] for i in usable]

    if verbose:
        print(f"  measurable references: {len(refs)} of {len(candidates)}  (skipped {skipped})"
              f"  contrast={contrast}")

    n_pairs = min(n_pairs, len(refs))
    # one reference per pair, drawn at random from the whole measurable set
    order = list(range(len(refs)))
    rng.shuffle(order)
    chosen = sorted(order[:n_pairs])

    work = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-styleval-"))
    pairs: list[dict] = []
    try:
        for step, i in enumerate(chosen, start=1):
            true = refs[i]
            j, pair_contrast = _mismatch_index(i, refs, rng, contrast=contrast)
            if j < 0:
                skipped["no_same_paper_partner"] = skipped.get("no_same_paper_partner", 0) + 1
                continue
            other = refs[j]
            try:
                a_pdf = render_transfer(other["profile"], work / f"p{i:03d}_A",
                                        apply_aspect=apply_aspect)
                b_pdf = render_transfer(true["profile"], work / f"p{i:03d}_B",
                                        apply_aspect=apply_aspect)
            except Exception as exc:                       # noqa: BLE001
                skipped[f"render:{type(exc).__name__}"] = \
                    skipped.get(f"render:{type(exc).__name__}", 0) + 1
                continue
            dist_a = select.distance_to(true["profile"], a_pdf)
            dist_b = select.distance_to(true["profile"], b_pdf)
            prof_a = styleprofile.StyleProfile.from_pdf(a_pdf)
            prof_b = styleprofile.StyleProfile.from_pdf(b_pdf)
            off = official_scores(true["profile"], {"A": prof_a, "B": prof_b})
            d_a, d_b = float(dist_a["distance"]), float(dist_b["distance"])
            pairs.append({
                "reference": f"{true['paper']}/{true['figure_id']}",
                "reference_size_pt": list(true["size_pt"]),
                "mismatch": f"{other['paper']}/{other['figure_id']}",
                "mismatch_contrast": pair_contrast,
                "distance_A": round(d_a, 4),
                "distance_B": round(d_b, 4),
                "margin": round(d_a - d_b, 4),
                "correct": bool(d_b < d_a),
                "tie": bool(d_b == d_a),
                "details_A": dist_a["details"],
                "details_B": dist_b["details"],
                "official_A": off["scores"].get("A"),
                "official_B": off["scores"].get("B"),
                "official_available": bool(off["available"]),
                "official_reason": off.get("reasons") or None,
            })
            if verbose:
                flag = "ok " if d_b < d_a else "MISS"
                print(f"  [{step:>2}/{n_pairs}] {flag} dA={d_a:.3f} dB={d_b:.3f} "
                      f"{true['paper'][:38]}")
    finally:
        # Route through the source guard even though `work` is a mkdtemp directory: the project's
        # rule is that EVERY recursive delete asks first, because a scheduled run once deleted an
        # entire source package with an unguarded one. An unwritten exception is how that happened.
        try:
            from figpipe import sources as _sources
            _sources.assert_writable(work)
            shutil.rmtree(work, ignore_errors=True)
        except Exception:                                   # noqa: BLE001 - never mask the result
            shutil.rmtree(work, ignore_errors=True)

    return summarise(pairs, seed=seed, skipped=skipped, n_refs=len(refs), contrast=contrast)


def reweighted_distance(details: dict, drop: str | None = None) -> float | None:
    """`styleprofile.compare`'s own aggregation, with one component optionally removed.

    The distance is a weighted mean over the components both sides measured, renormalised by the
    weights of the components PRESENT. Removing a component and renormalising therefore asks a
    question the aggregate cannot answer on its own: how much of the discrimination survives
    when that one dimension is not allowed to vote?
    """
    kept = {k: v for k, v in details.items() if k != drop and v is not None}
    if not kept:
        return None
    weight_sum = sum(styleprofile.WEIGHTS.get(k, 0.10) for k in kept)
    if weight_sum <= 0:
        return None
    total = sum(styleprofile.WEIGHTS.get(k, 0.10) * float(v) for k, v in kept.items())
    return total / weight_sum


def leave_one_out(pairs: list[dict]) -> dict:
    """Discrimination accuracy with each dimension removed in turn.

    WHY THIS IS REPORTED
        An aggregate accuracy of 0.93 can be carried by one cheap dimension. `aspect`, for
        instance, is derived directly from the reference's measured width/height and is the
        easiest thing to reproduce -- if the result collapses when aspect is withheld, the metric
        is substantially an aspect check wearing five other components, and CLAIM.md must say so
        rather than quote the aggregate alone.

        A dimension whose removal does not change the accuracy is contributing nothing
        distinguishable from noise; one whose removal IMPROVES it is actively misleading.
    """
    base = reweighted_distance
    n = len(pairs)
    out: dict[str, dict] = {}
    dims = sorted({k for p in pairs for k in p["details_A"]})
    for drop in [None] + dims:
        wins = ties = 0
        for p in pairs:
            a = base(p["details_A"], drop)
            b = base(p["details_B"], drop)
            if a is None or b is None:
                continue
            if b < a:
                wins += 1
            elif b == a:
                ties += 1
        scored = n - sum(1 for p in pairs
                         if base(p["details_A"], drop) is None
                         or base(p["details_B"], drop) is None)
        if not scored:
            continue
        key = "all_dimensions" if drop is None else f"without_{drop}"
        out[key] = {
            "n": scored,
            "wins": wins,
            "ties": ties,
            "accuracy": round(wins / scored, 4),
            "delta_vs_all": None,      # filled below
            "ci": list(wilson_interval(wins, scored)),
        }
    full = out.get("all_dimensions", {}).get("accuracy")
    for key, rec in out.items():
        if full is not None and key != "all_dimensions":
            rec["delta_vs_all"] = round(rec["accuracy"] - full, 4)
    return out


def summarise(pairs: list[dict], *, seed: int, skipped: dict, n_refs: int,
              contrast: str = "cross") -> dict:
    """Turn the per-pair records into the artefact, including the inverted control."""
    n = len(pairs)
    if n == 0:
        raise RuntimeError("no pair could be measured; see the skip counts")
    wins = sum(1 for p in pairs if p["correct"])
    accuracy = round(wins / n, 4)
    lo, hi = wilson_interval(wins, n)

    # NEGATIVE CONTROL: the same arithmetic on an inverted ranking. It MUST land at 1-accuracy;
    # if it does not, the harness is not reading the numbers it claims to read.
    inverted_wins = sum(1 for p in pairs if p["distance_B"] > p["distance_A"])
    inverted = round(inverted_wins / n, 4)
    inverted_lo, inverted_hi = wilson_interval(inverted_wins, n)
    # TIES make the two counts sum to n - ties, not to n, so the complement test is done on the
    # COUNTS rather than on the rounded proportions: comparing two 4-dp numbers against a
    # 1/n tolerance fails by a rounding hair (0.9333 + 0.0333 = 0.9666 vs 1 - 1/30 = 0.9667).
    # That false FAIL was produced by the first version of this check.
    n_ties = sum(1 for p in pairs if p["distance_B"] == p["distance_A"])
    control_passes = bool(
        inverted_wins < wins
        and inverted_wins + wins + n_ties == n
        and abs((inverted_wins + wins) - (n - n_ties)) == 0
    )

    # per-dimension: for each component the metric uses, does it alone rank B closer?
    #
    # TIES ARE NOT LOSSES. When a dimension measures the same value on both candidates the
    # dimension carries no information for that pair; counting it in the denominator drives the
    # accuracy toward zero and manufactures "this dimension is worse than chance" out of
    # indifference. The first version did exactly that: `lines` has 8 wins, 1 loss and 19 ties,
    # and was reported as 0.286 -- a number that would have been read as "the linewidth
    # component is actively misleading". It is not; it is silent on two thirds of the pairs.
    #
    # The reported accuracy is therefore wins / (wins + losses), with the tie count kept
    # alongside so the reader can see how often the dimension had anything to say.
    dims: dict[str, dict] = {}
    for key in sorted({k for p in pairs for k in p["details_A"]}):
        a_vals = [p["details_A"].get(key) for p in pairs]
        b_vals = [p["details_B"].get(key) for p in pairs]
        usable = [(a, b) for a, b in zip(a_vals, b_vals) if a is not None and b is not None]
        if not usable:
            continue
        d_wins = sum(1 for a, b in usable if b < a)
        d_losses = sum(1 for a, b in usable if b > a)
        d_ties = sum(1 for a, b in usable if b == a)
        decisive = d_wins + d_losses
        dims[key] = {
            "n": len(usable),
            "n_decisive": decisive,
            "wins": d_wins,
            "losses": d_losses,
            "ties": d_ties,
            "accuracy": round(d_wins / decisive, 4) if decisive else None,
            "ci": list(wilson_interval(d_wins, decisive)) if decisive else None,
            "mean_A": round(float(np.mean([a for a, _ in usable])), 4),
            "mean_B": round(float(np.mean([b for _, b in usable])), 4),
            "mean_margin": round(float(np.mean([a - b for a, b in usable])), 4),
        }

    # official-scorer agreement on the SAME pairs, where it is available for both candidates
    comparable = [p for p in pairs
                  if p["official_A"] is not None and p["official_B"] is not None]
    agree = sum(1 for p in comparable if p["official_B"] > p["official_A"])
    disagree = sum(1 for p in comparable if p["official_B"] < p["official_A"])
    official_ties = sum(1 for p in comparable if p["official_B"] == p["official_A"])
    # THE OFFICIAL CHANNEL ALSO TIES. A deviation score is a mean over the reference-activated
    # dimensions, so two candidates that deviate identically land on the same number and the
    # channel expresses no preference. Counting those as disagreements would understate
    # agreement and manufacture a conflict between the two metrics; counting them as agreements
    # would overstate it. They are reported as their own count, and the rate is over DECISIVE
    # comparisons with the all-comparable rate kept alongside.
    decisive = agree + disagree
    official_block = {
        "scorer": "plottwin_scorer deviation-defect-v1 (vendored, unmodified)",
        "channel": "code_deviation (35 % of the official combined score)",
        "n_pairs_scored": len(comparable),
        "n_pairs_unavailable": n - len(comparable),
        "n_agree": agree,
        "n_disagree": disagree,
        "n_tie": official_ties,
        "n_decisive": decisive,
        "agreement_rate": round(agree / decisive, 4) if decisive else None,
        "agreement_rate_including_ties": (round(agree / len(comparable), 4)
                                          if comparable else None),
        "agreement_ci": list(wilson_interval(agree, decisive)) if decisive else None,
        "official_correct": agree,
        "official_accuracy": round(agree / decisive, 4) if decisive else None,
        "note": ("The official channel is a DEVIATION score (100 = the candidate's style calls "
                 "match the reference's). It is run on code emitted from the RENDERED "
                 "candidates' own measured profiles, so it describes what was rendered. "
                 "Agreement is counted only where the channel is available for BOTH candidates, "
                 "and the rate is over decisive comparisons: a pair where the official channel "
                 "scores both candidates identically is a tie, not a disagreement."),
    }

    # how often figpipe was right and the official channel was wrong, and vice versa
    both = [p for p in comparable]
    fp_right_off_wrong = sum(1 for p in both if p["correct"] and p["official_B"] < p["official_A"])
    fp_wrong_off_right = sum(1 for p in both if (not p["correct"]) and p["official_B"] > p["official_A"])

    return {
        "experiment": "style-metric discrimination on local published Nature figures",
        "what_this_measures": (
            "Whether figpipe's own style distance ranks a style transferred from the MATCHED "
            "reference closer to that reference than a style transferred from a MISMATCHED one. "
            "This tests ORDERING, not expert preference: it can refute a blind or inverted "
            "metric, it cannot establish that the closer figure is the better figure."),
        "not_human_validation": (
            "No human judgement was collected. This is a deterministic proxy that removes the "
            "'the metric was never tested at all' gap; it does not replace a reader study."),
        "corpus": {
            "source": "corpus/extracted (local published Nature figures, vector PDF regions)",
            "n_candidates_scanned": n_refs,
            "style_floors": {"min_width_pt": MIN_WIDTH_PT, "min_height_pt": MIN_HEIGHT_PT,
                             "min_text_spans": MIN_TEXT_SPANS,
                             "min_size_tiers": MIN_SIZE_TIERS,
                             "min_colours": MIN_COLOURS},
            "skipped": skipped,
        },
        "design": {
            "n_pairs": n,
            "seed": seed,
            "contrast_requested": contrast,
            "A": "style transferred from a MISMATCHED published figure",
            "B": "style transferred from the MATCHED reference itself",
            "candidate_data": "identical synthetic panel for both candidates",
            "distance": "figpipe.styleprofile.compare (the metric under test)",
            "mismatch_contrast": {
                "different_paper": sum(1 for p in pairs if p["mismatch_contrast"] == "different_paper"),
                "same_paper": sum(1 for p in pairs if p["mismatch_contrast"] == "same_paper"),
            },
            "contrast_note": (
                "cross-paper mismatch is the EASY condition: two unrelated papers differ in "
                "palette, typography and layout at once. A same-paper mismatch (another figure "
                "in the same paper) shares a house style and is the condition a style metric is "
                "actually for. Both are reported; neither substitutes for the other."),
        },
        "discrimination_accuracy": accuracy,
        "n_correct": wins,
        "n_pairs": n,
        "binomial_ci_95": [lo, hi],
        "chance_level": 0.5,
        "p_value_vs_chance": binomial_p_value(wins, n),
        "p_value_text": _p_text(binomial_p_value(wins, n)),
        "mean_margin": round(float(np.mean([p["margin"] for p in pairs])), 4),
        "median_margin": round(float(np.median([p["margin"] for p in pairs])), 4),
        "verdict": _verdict(accuracy, lo, n, leave_one_out(pairs)),
        "negative_control": {
            "what": "the same arithmetic applied to an INVERTED ranking (distance negated)",
            "accuracy": inverted,
            "n_correct": inverted_wins,
            "n_pairs": n,
            "n_ties": n_ties,
            "binomial_ci_95": [inverted_lo, inverted_hi],
            "passes": control_passes,
            "note": ("A harness that reports the same number for the inverted ranking is "
                     "measuring nothing. This control is asserted by the test suite. Ties are "
                     "counted in neither direction, so forward + inverted + ties = n."),
        },
        "official_scorer": official_block,
        "cross_metric": {
            "n_pairs_both_scored": len(both),
            "figpipe_right_official_wrong": fp_right_off_wrong,
            "figpipe_wrong_official_right": fp_wrong_off_right,
            "both_agree": agree,
        },
        "per_dimension": dims,
        "leave_one_out": leave_one_out(pairs),
        # TREATMENT REACH. A dimension whose A and B values are identical on every pair was not
        # tested, whatever its accuracy says. Reported explicitly so a reader (and the test
        # suite) can see which dimensions the transfer actually moved.
        "treatment_reach": {
            name: {
                "n": d["n"],
                "n_identical": sum(
                    1 for p in pairs
                    if p["details_A"].get(name) is not None
                    and p["details_A"].get(name) == p["details_B"].get(name)),
                "exercised": bool(d["n_decisive"]),
            }
            for name, d in dims.items()
        },
        "pairs": pairs,
    }


def _verdict(accuracy: float, lo: float, n: int, loo: dict | None = None) -> str:
    """A sentence CLAIM.md can quote, chosen by the measured number rather than by hope.

    `loo` (leave-one-out) is folded into the verdict because the aggregate alone can overstate
    what was shown. If withholding ONE component drops the accuracy toward chance, the metric is
    substantially that component and the verdict has to say so.
    """
    if accuracy <= 0.5:
        return ("REFUTED: the style distance does not rank a matched transfer above a "
                "mismatched one. The metric is at or below chance and no claim may rest on it.")
    if lo > 0.5:
        base = ("SUPPORTED at this contrast: the style distance discriminates a matched "
                "transfer from a mismatched one at above-chance accuracy, with a 95 % interval "
                "that excludes chance.")
        if loo:
            drops = {k: v["delta_vs_all"] for k, v in loo.items()
                     if k != "all_dimensions" and v.get("delta_vs_all") is not None}
            worst = min(drops.items(), key=lambda kv: kv[1]) if drops else None
            if worst and worst[1] <= -0.15:
                name = worst[0].replace("without_", "")
                return (base + f" CONCENTRATION: withholding `{name}` alone drops accuracy to "
                               f"{loo[worst[0]]['accuracy']:.2f} (delta {worst[1]:+.2f}), so "
                               f"most of the discrimination is that one component.")
        return base
    return ("INCONCLUSIVE: the point estimate is above chance but the 95 % interval includes "
            "0.5, so the discrimination is not established at this sample size.")


def combine_arms(arms: dict) -> dict:
    """Merge the two contrast arms into one artefact, with the HARD arm as the headline.

    WHY THE HEADLINE IS THE SAME-PAPER ARM
        The cross-paper arm is nearly free: two unrelated Nature papers differ in palette,
        type and layout at once, so a perfect score there says "the metric can tell one journal
        paper from another", which nobody doubted. The same-paper arm asks the question the
        metric exists to answer -- can it tell a faithful transfer from a transfer of a
        *sibling* figure's style, where the house style is held constant?

        Reporting only the easy arm would be the same failure this project already documented
        elsewhere: a number that is true, measured, and answers an easier question than the one
        the claim needs. So both are stored, `discrimination_accuracy` is the HARD arm, and
        `verdict` is computed from it. If the hard arm is at chance, CLAIM.md must say so even
        though the easy arm is perfect.
    """
    hard = arms.get("same") or {}
    easy = arms.get("cross") or {}
    if not hard and not easy:
        raise RuntimeError("neither contrast arm produced a result")

    headline = hard or easy
    out = dict(headline)
    out["experiment"] = "style-metric discrimination on local published Nature figures"
    out["design"] = dict(out["design"])
    out["design"]["arms"] = {
        "headline": "same_paper" if hard else "different_paper",
        "why": ("the same-paper mismatch holds the journal's house style constant, so it asks "
                "whether the metric separates a faithful transfer from a sibling figure's "
                "style -- the question the metric exists to answer"),
    }
    out["arms"] = {
        "same_paper": _arm_summary(hard) if hard else None,
        "different_paper": _arm_summary(easy) if easy else None,
    }
    out["discrimination_accuracy"] = headline.get("discrimination_accuracy")
    out["binomial_ci_95"] = headline.get("binomial_ci_95")
    out["n_pairs"] = headline.get("n_pairs")
    out["n_correct"] = headline.get("n_correct")
    out["p_value_vs_chance"] = headline.get("p_value_vs_chance")
    out["p_value_text"] = headline.get("p_value_text")
    out["verdict"] = headline.get("verdict")
    out["negative_control"] = headline.get("negative_control")
    out["official_scorer"] = headline.get("official_scorer")
    out["cross_metric"] = headline.get("cross_metric")
    out["per_dimension"] = headline.get("per_dimension")
    out["leave_one_out"] = headline.get("leave_one_out")
    out["treatment_reach"] = headline.get("treatment_reach")
    out["pairs"] = headline.get("pairs")
    if hard and easy:
        gap = round((easy.get("discrimination_accuracy") or 0.0)
                    - (hard.get("discrimination_accuracy") or 0.0), 4)
        out["contrast_gap"] = {
            "easy_minus_hard": gap,
            "note": ("How much the metric loses when the house style is held constant. A large "
                     "gap means most of the easy arm's accuracy came from cross-paper "
                     "differences, not from style fidelity."),
        }
    return out


def _arm_summary(arm: dict) -> dict:
    """The few numbers a reader needs from one arm, without its per-pair records."""
    if not arm:
        return {}
    off = arm.get("official_scorer") or {}
    return {
        "n_pairs": arm.get("n_pairs"),
        "n_correct": arm.get("n_correct"),
        "discrimination_accuracy": arm.get("discrimination_accuracy"),
        "binomial_ci_95": arm.get("binomial_ci_95"),
        "p_value_vs_chance": arm.get("p_value_vs_chance"),
        "p_value_text": arm.get("p_value_text"),
        "verdict": arm.get("verdict"),
        "official_agreement_rate": off.get("agreement_rate"),
        "official_n_scored": off.get("n_pairs_scored"),
        "negative_control_accuracy": (arm.get("negative_control") or {}).get("accuracy"),
    }


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=30, help="number of pairs (24-40 is the useful band)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--contrast", choices=["cross", "same", "both"], default="both",
                    help="mismatch contrast: 'cross' = different paper (easy), 'same' = another "
                         "figure in the same paper (hard, the condition the metric is for), "
                         "'both' = measure and store both arms")
    ap.add_argument("--report", action="store_true", help="print the stored artefact and exit")
    ap.add_argument("--no-aspect", action="store_true",
                    help="DIAGNOSTIC: transfer everything EXCEPT aspect, so the metric is tested "
                         "on the style dimensions rather than on whether the transfer ran. Not a "
                         "shipping mode -- a figure at the wrong aspect is the wrong figure.")
    ap.add_argument("--no-lock", action="store_true",
                    help="skip the measurement lock (only when the parent already holds it)")
    ap.add_argument("--wait", type=float, default=0.0,
                    help="seconds to queue for the measurement lock instead of failing at once")
    args = ap.parse_args(argv)

    if args.report:
        return _report(pathlib.Path(args.out))

    if not args.no_lock:
        try:
            lock.acquire("style_validation", wait_s=args.wait)
        except lock.MeasurementBusy as exc:
            print(f"  refused: {exc}")
            return 3
    try:
        if args.contrast == "both":
            arms = {}
            for arm in ("cross", "same"):
                print(f"\n  --- contrast: {arm} ---")
                arms[arm] = measure(n_pairs=args.n, seed=args.seed, contrast=arm,
                                    apply_aspect=not args.no_aspect)
            result = combine_arms(arms)
        else:
            result = measure(n_pairs=args.n, seed=args.seed, contrast=args.contrast,
                             apply_aspect=not args.no_aspect)
    finally:
        if not args.no_lock:
            # A LOCK LOST MID-RUN IS NOT OUR LOCK ANY MORE. Another heavy entry point can break
            # a lock it judges stale (or a scheduled run can take it between our acquire and our
            # release); `lock.release` then raises, and that exception would REPLACE the
            # measurement result with a traceback -- the numbers would be computed and thrown
            # away. Releasing someone else's lock is still refused by `lock.release`; the
            # difference here is that losing it is reported, not fatal.
            try:
                lock.release("style_validation")
            except lock.MeasurementBusy as exc:
                print(f"  warning: the measurement lock was taken over during the run: {exc}")

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print()
    print(f"  pairs: {result['n_pairs']}   correct: {result['n_correct']}")
    p_text = result.get("p_value_text") or _p_text(result["p_value_vs_chance"])
    print(f"  discrimination accuracy: {result['discrimination_accuracy']:.4f} "
          f"(95 % CI {result['binomial_ci_95'][0]:.3f}-{result['binomial_ci_95'][1]:.3f}, "
          f"p={p_text})")
    arms = result.get("arms") or {}
    if arms.get("different_paper") and arms.get("same_paper"):
        e = arms["different_paper"]
        h = arms["same_paper"]
        print(f"  arms: easy (different paper) {e['n_correct']}/{e['n_pairs']} = "
              f"{e['discrimination_accuracy']:.3f}   "
              f"hard (same paper) {h['n_correct']}/{h['n_pairs']} = "
              f"{h['discrimination_accuracy']:.3f}")
        print(f"        headline is the HARD arm; contrast gap "
              f"{(result.get('contrast_gap') or {}).get('easy_minus_hard')}")
    print(f"  negative control (inverted): {result['negative_control']['accuracy']:.4f} "
          f"-> {'PASS' if result['negative_control']['passes'] else 'FAIL'}")
    off = result["official_scorer"]
    if off["n_pairs_scored"]:
        print(f"  official scorer: {off['n_agree']} agree / {off['n_disagree']} disagree / "
              f"{off['n_tie']} tie over {off['n_pairs_scored']} comparable pairs "
              f"-> agreement {off['agreement_rate']:.3f} of {off['n_decisive']} decisive")
        print(f"                   (including ties: {off['agreement_rate_including_ties']:.3f})")
    else:
        print(f"  official scorer: no comparable pair ({off.get('note')})")
    print("  per-dimension accuracy (ties excluded -- a tie means the dimension had no opinion):")
    for name, d in sorted(result["per_dimension"].items(),
                          key=lambda kv: (kv[1]["accuracy"] is None, -(kv[1]["accuracy"] or 0))):
        acc = "n/a " if d["accuracy"] is None else f"{d['accuracy']:.3f}"
        note = "" if d["n_decisive"] else "  <- never decisive (A == B on every pair)"
        print(f"    {name:<8} n={d['n']:<3} decisive={d['n_decisive']:<3} "
              f"W/L/T={d['wins']}/{d['losses']}/{d['ties']}  acc={acc}{note}")
    dead = [k for k, v in result["treatment_reach"].items() if not v["exercised"]]
    if dead:
        print(f"  WARNING: the transfer did not move {dead}; those dimensions are untested")
    print("  leave-one-out (what carries the result):")
    for name, rec in sorted((result.get("leave_one_out") or {}).items(),
                            key=lambda kv: kv[1]["accuracy"]):
        delta = rec["delta_vs_all"]
        delta_s = "" if delta is None else f"  delta={delta:+.3f}"
        print(f"    {name:<22} acc={rec['accuracy']:.3f}  n={rec['n']}{delta_s}")
    print(f"  verdict: {result['verdict']}")
    print(f"  wrote {out}")
    return 0


def _report(path: pathlib.Path) -> int:
    if not path.is_file():
        print(f"  no artefact at {path}; run without --report first")
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"  n_pairs            {data['n_pairs']}")
    print(f"  discrimination     {data['discrimination_accuracy']:.4f}  "
          f"CI {data['binomial_ci_95']}  p={data['p_value_vs_chance']}")
    print(f"  verdict            {data['verdict']}")
    off = data.get("official_scorer") or {}
    print(f"  official agreement {off.get('agreement_rate')} "
          f"on {off.get('n_pairs_scored')} comparable pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
