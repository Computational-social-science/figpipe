"""Build a blind A/B reader study: the one claim no script can settle.

WHY THIS EXISTS
    `corpus/e2e/style_validation.json` says, in its own words:

        No human judgement was collected. This is a deterministic proxy that removes the "the metric
        was never tested at all" gap; IT DOES NOT REPLACE A READER STUDY.

    and

        This tests ORDERING, not expert preference: it can refute a blind or inverted metric, it cannot
        establish that the closer figure is the better figure.

    So the style metric's central claim -- that the figure figpipe picks is the BETTER figure -- has
    never been tested by a reader. That is not a coding gap; it is a missing experiment.

WHAT THIS SCRIPT IS
    A study HARNESS, not a study. It builds the material a reader needs and the file they fill in, and
    it scores the result. **It cannot run itself**: the judgement is the input.

    For each of N pairs it renders, from the SAME synthetic data:
        A  a panel in a MISMATCHED published figure's style
        B  a panel in the MATCHED reference's style
    and shows them side by side, UNLABELLED, with the reference above them.

    The rater answers one question per pair: which of A and B is closer to the reference?
    The answer key is written to a SEPARATE file so the sheet a rater fills in carries no answer.

WHAT THE RESULT MEANS
    If raters agree with the metric more often than chance, the metric's ordering is corroborated by
    expert preference. If they do not, the metric ranks something other than what a reader sees -- and
    that is the more valuable outcome, because it invalidates the claim rather than decorating it.

USAGE
    python scripts/reader_study.py --build            # writes the study into corpus/study/
    python scripts/reader_study.py --score            # scores the completed answer sheet
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

STUDY = ROOT / "corpus" / "study"
ANSWERS = STUDY / "answers.csv"
KEY = STUDY / "key.json"
SHEET = STUDY / "README.txt"


def _pairs(n: int, seed: int) -> list[dict]:
    """The pairs the metric already measured, with their distances."""
    data = json.loads((ROOT / "corpus" / "e2e" / "style_validation.json").read_text(encoding="utf-8"))
    same = [p for p in (data.get("pairs") or []) if p.get("mismatch_contrast") == "same_paper"]
    rng = random.Random(seed)
    rng.shuffle(same)
    return same[:n]


def build(n: int = 30, seed: int = 20261025) -> int:
    """Render the study material and write the answer sheet with NO answers in it."""
    import validate_style_metric as V
    from figpipe import layout, styleprofile

    pairs = _pairs(n, seed)
    if not pairs:
        print("  no same_paper pairs in style_validation.json; run validate_style_metric.py first")
        return 2
    STUDY.mkdir(parents=True, exist_ok=True)
    (STUDY / "figures").mkdir(exist_ok=True)

    key: dict[str, dict] = {}
    for i, pair in enumerate(pairs, 1):
        try:
            ref_prof = _profile(_resolve(pair["reference"]))
            mis_prof = _profile(_resolve(pair["mismatch"]))
        except Exception as exc:                    # noqa: BLE001 - a missing source is not fatal
            print(f"  pair {i}: cannot profile a source ({type(exc).__name__}); skipped")
            continue
        try:
            a_pdf = V.render_transfer(mis_prof, STUDY / "figures" / f"p{i:02d}A")
            b_pdf = V.render_transfer(ref_prof, STUDY / "figures" / f"p{i:02d}B")
        except Exception as exc:                    # noqa: BLE001
            print(f"  pair {i}: cannot render ({type(exc).__name__}); skipped")
            continue
        # RANDOMISE THE PRESENTATION SIDE so a rater cannot learn "B is always the good one".
        flip = random.Random(seed + i).random() < 0.5
        left, right = (b_pdf, a_pdf) if flip else (a_pdf, b_pdf)
        # RASTERISE, DO NOT RENAME. `render_transfer` returns a PDF; copying it to a `.png` name gives a
        # rater a file no viewer opens (measured: PIL raises UnidentifiedImageError on `%PDF-1.4`).
        _rasterise(left, STUDY / "figures" / f"p{i:02d}_left.png")
        _rasterise(right, STUDY / "figures" / f"p{i:02d}_right.png")
        shutil.copy(_resolve(pair["reference"]),
                    STUDY / "figures" / f"p{i:02d}_reference{_resolve(pair['reference']).suffix}")
        key[f"p{i:02d}"] = {
            "reference": pair["reference"],
            "mismatch": pair["mismatch"],
            "matched_side": "left" if flip else "right",
            # WHICH SIDE, NOT WHICH LETTER. `metric_picks` used to be "A" or "B", and because A is
            # always the mismatched candidate that field was "A" on 27 of 30 pairs -- a value that
            # could not be wrong. The side is what a rater's answer is actually compared with.
            "metric_prefers": ("right" if flip else "left")
                              if pair["distance_B"] < pair["distance_A"]
                              else ("left" if flip else "right"),
            "distance_A": pair["distance_A"],
            "distance_B": pair["distance_B"],
        }

    KEY.write_text(json.dumps(key, indent=2), encoding="utf-8")
    rows = ["pair,your_choice  # 'left' or 'right'"]
    rows += [f"{pid}," for pid in key]
    ANSWERS.write_text("\n".join(rows) + "\n", encoding="utf-8")
    SHEET.write_text(_sheet_text(len(key)), encoding="utf-8")
    print(f"  built {len(key)} pairs in {STUDY}")
    print(f"    figures/   {len(key) * 3} PNG files (reference, left, right)")
    print(f"    {ANSWERS.name}   <- the rater fills this in")
    print(f"    {KEY.name}       <- DO NOT show this to the rater")
    print(f"    {SHEET.name}      <- instructions")
    return 0


def _rasterise(pdf: pathlib.Path, out_png: pathlib.Path, dpi: int = 200) -> pathlib.Path:
    """Render page 1 of `pdf` to a real PNG.

    A study is looked at, not parsed. `fitz` (pymupdf) is already a dependency of the package.
    """
    import fitz
    doc = fitz.open(str(pdf))
    try:
        page = doc[0]
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(out_png))
    finally:
        doc.close()
    return out_png


def _profile(path: pathlib.Path):
    """A StyleProfile from either a PDF or a PNG -- the study accepts whatever the corpus has."""
    from figpipe import styleprofile
    if path.suffix.lower() == ".pdf":
        return styleprofile.StyleProfile.from_pdf(path)
    return styleprofile.StyleProfile.from_image(path)


def _resolve(rel: str) -> pathlib.Path:
    """Resolve a study source.

    MEASURED: the stems in style_validation.json are `<paper>/fig_001` and the files on disk are
    `corpus/extracted/<paper>/figures/fig_001.png` -- PNG, not PDF. A study only needs the STYLE, and
    `StyleProfile.from_image` reads a raster, so the extension is not a limitation here.
    """
    base = ROOT / "corpus" / "extracted"
    stem = pathlib.Path(rel)
    candidates = [
        base / rel,
        base / f"{rel}.png",
        base / f"{rel}.pdf",
        base / stem.parent / "figures" / f"{stem.name}.png",
        base / stem.parent / "figures" / f"{stem.name}.pdf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[3]


def _need_k(n: int, alpha: float = 0.05) -> int:
    """Smallest k with P(X >= k | p = 0.5) <= alpha, for a one-sided binomial test."""
    from math import comb
    for k in range(n + 1):
        if sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n <= alpha:
            return k
    return n + 1


def _power(n: int, k: int, p_true: float) -> float:
    """P(reject chance | the true agreement rate is p_true)."""
    from math import comb
    return sum(comb(n, i) * p_true ** i * (1 - p_true) ** (n - i) for i in range(k, n + 1))


def _sheet_text(n: int) -> str:
    return f"""READER STUDY: does the figure figpipe picks look closer to the reference?

WHAT YOU ARE JUDGING
    For each pair you get three images:
        pNN_reference   the published figure whose style is the target
        pNN_left        a candidate rendered in SOME published figure's style
        pNN_right       a candidate rendered in ANOTHER published figure's style

    The two candidates use IDENTICAL data and layout. ONLY the style differs: typography, palette,
    stroke weight, spines, aspect. One of them was styled from the reference itself; the other from a
    different figure in the same paper.

YOUR TASK
    For each pair, answer ONE question: WHICH CANDIDATE LOOKS CLOSER TO THE REFERENCE?
    Fill in {ANSWERS.name}:

        pair,your_choice
        p01,left
        p02,right
        ...

    Answer every row. If a pair is a genuine coin-flip, write `tie` -- a tie is data, and guessing
    destroys the signal.

WHAT HAPPENS WITH YOUR ANSWERS
    `python scripts/reader_study.py --score` compares your choices with the answer key. The interesting
    number is not your raw accuracy -- it is whether your choices AGREE WITH THE METRIC. If the metric
    ranks a figure better than a reader does, the metric is measuring something other than what a reader
    sees, and that invalidates a claim this project has been making.

    {n} pairs. At chance you would agree with the metric on about half.

WHAT THIS STUDY CAN AND CANNOT DETECT
    One-sided binomial, chance 0.5, alpha 0.05, with {n} pairs you must agree on
    {_need_k(n)}/{n} = {_need_k(n)/n:.2f} to reject chance. If the true agreement is 0.70 the study
    detects it with power {_power(n, _need_k(n), 0.70):.2f}; at 0.80, {_power(n, _need_k(n), 0.80):.2f}.

    THIS IS A LIMIT OF THE CORPUS, NOT OF THE HARNESS: there are 30 same-paper pairs, and a study
    cannot be made stronger by running it on pairs that do not exist.

PLEASE DO NOT
    * open {KEY.name}
    * compare the candidates by guessing which one "looks like figpipe"
    * spend more than ~15 seconds per pair
"""


def score() -> int:
    """Compare the rater's choices with the answer key."""
    if not ANSWERS.is_file() or not KEY.is_file():
        print("  no study to score; run --build first")
        return 2
    key = json.loads(KEY.read_text(encoding="utf-8"))
    choices: dict[str, str] = {}
    for line in ANSWERS.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        parts = [p.strip().lower() for p in line.split(",")]
        if len(parts) >= 2 and parts[0] in key:
            choices[parts[0]] = parts[1]
    # A ROW THAT PARSES IS NOT AN ANSWER. `p01,` yields `("p01", "")`, so a sheet with the right ids and
    # no judgements looked non-empty and scored 0 % -- a claim about the metric from no data.
    answered = {pid: v for pid, v in choices.items() if v in ("left", "right", "tie")}
    if not answered:
        print("  the answer sheet has no judgements; a study with no judgements measures nothing")
        return 2
    choices = answered

    agree = disagree = tie = 0
    rows = []
    for pid, meta in key.items():
        choice = choices.get(pid)
        if choice is None:
            continue
        matched_side = meta["matched_side"]
        if choice == "tie":
            tie += 1
            rows.append((pid, "tie", "-"))
            continue
        picked_matched = (choice == matched_side)
        # THE METRIC'S PREFERENCE IS A SIDE, NOT A LETTER. `metric_picks` was "A"/"B" and A is always
        # the mismatched candidate, so that field was a tautology -- it said "the metric was right".
        metric_prefers = meta.get("metric_prefers")
        if metric_prefers is None:                  # a key written before the fix
            metric_prefers = matched_side if meta.get("metric_picks") == "B" else \
                ("right" if matched_side == "left" else "left")
        metric_picks_matched = (metric_prefers == matched_side)
        agrees = picked_matched == metric_picks_matched
        if agrees:
            agree += 1
        else:
            disagree += 1
        rows.append((pid, choice, "agrees" if agrees else "DISAGREES"))

    n = agree + disagree
    print(f"  answered: {n + tie} of {len(key)}  (ties: {tie})")
    if n == 0:
        print("  every answer was a tie; no discrimination to measure")
        return 2
    rate = agree / n
    print(f"  rater agrees with the metric on {agree}/{n} = {rate:.3f}")
    print()
    for pid, choice, verdict in rows:
        print(f"    {pid}  {choice:<6} {verdict}")
    print()
    if rate >= 0.70:
        print("  VERDICT: the metric's ordering is CORROBORATED by this reader.")
    elif rate <= 0.55:
        print("  VERDICT: the metric's ordering is NOT corroborated -- it ranks something a reader does "
              "not see. This invalidates the style claim rather than decorating it.")
    else:
        print("  VERDICT: inconclusive at this sample size. More pairs, or more raters.")
    out = STUDY / "scored.json"
    out.write_text(json.dumps({"agree": agree, "disagree": disagree, "tie": tie,
                               "agreement_rate": round(rate, 4), "rows": rows}, indent=2),
                   encoding="utf-8")
    # A STUDY DIRECTORY IS A PARAMETER, SO THE OUTPUT MAY NOT BE UNDER THE REPO. Printing a path is
    # not a reason to crash after the scoring already succeeded.
    try:
        shown = out.relative_to(ROOT)
    except ValueError:
        shown = out
    print(f"  wrote {shown}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", action="store_true", help="render the study material")
    ap.add_argument("--score", action="store_true", help="score the completed answer sheet")
    # 30, NOT 20, AND THE REASON IS MEASURED. One-sided binomial at alpha 0.05:
    #     N=20 needs 15/20 (power 0.80 at a true 0.80, only 0.42 at 0.70)
    #     N=30 needs 20/30 (power 0.97 at 0.80, 0.73 at 0.70)
    # The corpus has exactly 30 same-paper pairs, so this is the largest study the data supports.
    ap.add_argument("-n", type=int, default=30,
                    help="how many pairs (default 30: the corpus maximum, and the smallest N with "
                         "acceptable power at alpha 0.05)")
    ap.add_argument("--seed", type=int, default=20261025)
    args = ap.parse_args(argv)
    if args.build:
        return build(args.n, args.seed)
    if args.score:
        return score()
    ap.print_help()
    return 2


if __name__ == "__main__":                          # pragma: no cover
    raise SystemExit(main())
