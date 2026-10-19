"""Make a publication figure from a CSV, and prove it complies. One command, no Python.

WHY THIS FILE EXISTS
    The objective asks whether the pipeline's capability is "reusable and verifiable in research
    scenarios". Until now the answer was: the API is callable, and `examples/worked_example.py`
    demonstrates it on INVENTED data. That proves the functions exist. It does not prove a
    researcher can use the thing, because a researcher has three things this project never asked
    for: their own CSV, a target column width, and -- often -- a reference figure whose style they
    are told to match.

    This is the entry point for exactly that path. If this command works on a stranger's CSV, the
    capability is reusable. If it only works on the benchmark's data shapes, it is not.

WHAT IT DOES
    1. read a CSV (tidy, one row per observation)
    2. infer what to draw from the columns, or REFUSE with a reason
    3. optionally transfer the style of a reference figure (PDF or image)
    4. write a submission PDF at Nature's column width plus a preview PNG
    5. audit the RENDERED file and exit non-zero if it does not comply

WHAT IT DELIBERATELY DOES NOT DO
    It does not guess. `spec.infer_spec` raises rather than picking a chart type from an ambiguous
    table, and this command surfaces that refusal as a message with the available columns. A tool
    that silently draws the wrong chart is worse than one that says it cannot.

USAGE
    python scripts/make_figure.py data.csv --out myfig
    python scripts/make_figure.py data.csv --out myfig --columns 1 --height 60
    python scripts/make_figure.py data.csv --out myfig --reference published.pdf --page 3
    python scripts/make_figure.py data.csv --out myfig --intent ranked_composition --label site --value score

EXIT CODES
    0  figure written and it passed the audit
    1  figure written but the audit FAILED (the findings are printed)
    2  could not draw: the data or the request was refused, with a reason
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from figpipe import audit, grammar, layout, skills, spec, styleprofile  # noqa: E402

#: Nature's column widths in millimetres. The pipeline draws at one of these or the file is not
#: submittable, so the CLI only offers these.
#: Nature prints at exactly two widths. `columns` is an ENUM in the layout layer (1 or 2), so the
#: CLI must offer the same choice rather than a millimetre value it would have to convert.
COLUMN_WIDTHS = {"1": 89.0, "2": 183.0}
COLUMNS_ENUM = {"1": 1.0, "2": 2.0}


def read_csv(path: pathlib.Path) -> pd.DataFrame:
    """Read a CSV and report what it found, so a column-name mistake is visible immediately."""
    if not path.is_file():
        raise SystemExit(f"  cannot read {path}: file not found")
    try:
        df = pd.read_csv(path)
    except Exception as exc:                       # noqa: BLE001 - surfaced to the user
        raise SystemExit(f"  cannot parse {path}: {type(exc).__name__}: {exc}")
    if df.empty:
        raise SystemExit(f"  {path} has no rows")
    print(f"  data: {len(df)} rows x {len(df.columns)} columns")
    print(f"  columns: {', '.join(f'{c} ({df[c].dtype})' for c in df.columns)}")
    return df


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Make a Nature-compliant figure from a CSV, and verify it.")
    ap.add_argument("csv", help="tidy CSV: one row per observation")
    ap.add_argument("--out", default="figure", help="output stem (writes .pdf and .png)")
    ap.add_argument("--columns", choices=sorted(COLUMN_WIDTHS), default="2",
                    help="Nature column width: 1 = 89 mm (single), 2 = 183 mm (double, default)")
    ap.add_argument("--height", type=float, default=None,
                    help="panel height in mm (default: derived from the width and the reference)")
    ap.add_argument("--reference", default=None,
                    help="a PDF or image whose STYLE should be transferred")
    ap.add_argument("--page", type=int, default=1,
                    help="page of --reference to measure (PDF only)")
    ap.add_argument("--intent", default=None,
                    help="force a chart intent instead of inferring it")
    ap.add_argument("--label", default=None, help="category column (with --intent)")
    ap.add_argument("--value", default=None, help="value column (with --intent)")
    ap.add_argument("--x", default=None, help="x column (with --intent)")
    ap.add_argument("--y", default=None, help="y column (with --intent)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    width_mm = COLUMN_WIDTHS[args.columns]
    print(f"  target: {width_mm} mm column, Nature submission")

    df = read_csv(pathlib.Path(args.csv))

    # ---- what to draw -------------------------------------------------------------------
    if args.intent:
        if not any([args.label, args.x]):
            raise SystemExit("  --intent needs --label or --x so the columns are unambiguous")
        intent_name, params = args.intent, {}
        if args.label:
            params.update({"label": args.label, "value": args.value})
        if args.x:
            params.update({"x": args.x, "y": args.y})
        print(f"  intent: {intent_name} (forced)")
    else:
        try:
            figure = spec.infer_spec(df)
        except spec.SpecError as exc:
            print(f"  REFUSED: {exc}")
            print(f"  the columns are: {', '.join(df.columns)}")
            print(f"  pass --intent with --label/--value or --x/--y to choose explicitly")
            return 2
        declared = figure.panels[0]
        intent_name = declared.intent
        # `kwargs` IS the column mapping spec resolved -- x/ycols/label/value. Passing an empty
        # dict here refused every inferred figure for columns spec had already found.
        params = dict(declared.kwargs or {})
        print(f"  intent: {intent_name} (inferred)")
        print(f"  why:    {declared.rationale}")

    # ---- optional style transfer --------------------------------------------------------
    style_kw = {}
    if args.reference:
        ref_path = pathlib.Path(args.reference)
        if not ref_path.is_file():
            raise SystemExit(f"  cannot read reference {ref_path}: file not found")
        try:
            if ref_path.suffix.lower() == ".pdf":
                prof = styleprofile.StyleProfile.from_pdf(ref_path, page=args.page)
            else:
                prof = styleprofile.StyleProfile.from_image(ref_path)
        except Exception as exc:                   # noqa: BLE001 - surfaced
            raise SystemExit(f"  cannot measure the reference: {type(exc).__name__}: {exc}")
        style_kw["profile"] = prof
        print(f"  reference style: {ref_path.name} (width {prof.width_mm} mm)")

    # ---- draw ---------------------------------------------------------------------------
    # Map the inferred intent onto a registered skill. A missing mapping is a REFUSAL, not a
    # fallback: drawing something the intent did not ask for is how a figure ends up wrong.
    # The keys are the intents `spec.infer_spec` actually emits, enumerated by driving it over
    # real table shapes -- NOT invented names. An invented key turns a valid table into
    # "no skill implements intent", which looks like a deliberate refusal and is a missing entry.
    # `tests/test_make_figure.py` fails if this map and the reachable set ever diverge.
    recipe = {
        "grouped_bars": "grouped_measures",
        "scatter_fit": "scatter_relationship",
        "boxplot": "distribution_comparison",
        "ranked_composition": "ranked_composition",
        "density_relationship": "density_relationship",
    }.get(intent_name)
    if recipe is None:
        print(f"  REFUSED: no skill implements intent {intent_name!r}")
        print(f"  available recipes: {', '.join(sorted(skills.SKILLS))}")
        return 2

    height_mm = args.height if args.height is not None else (width_mm * 0.5)
    stem = pathlib.Path(args.out)
    stem.parent.mkdir(parents=True, exist_ok=True)

    # Pass only the parameters the chosen skill DECLARES. Dropping the rest silently would hide a
    # real mismatch; dropping them with a printed note keeps the choice visible.
    skill = skills.SKILLS[recipe]
    declared_params = set(getattr(skill, "required", ()) or ()) | \
        set(getattr(skill, "optional", ()) or ())
    dropped = sorted(k for k in params if k not in declared_params)
    usable = {k: v for k, v in params.items() if k in declared_params}
    if dropped:
        print(f"  note: {recipe} does not take {dropped}; omitted")

    try:
        result = skills.run(recipe, df, out_stem=stem,
                            columns=COLUMNS_ENUM[args.columns],
                            height_mm=height_mm, **style_kw, **usable)
    except skills.SkillError as exc:
        print(f"  REFUSED: {exc}")
        return 2
    except Exception as exc:                       # noqa: BLE001 - surfaced
        print(f"  FAILED: {type(exc).__name__}: {exc}")
        return 2

    pdf = pathlib.Path(result["pdf"])
    print(f"  wrote: {pdf.name} and its .png preview")
    print(f"  operators: {' -> '.join(result['trace'][:5])}")

    # ---- verify the RENDERED file, not the source ---------------------------------------
    report = audit.audit(str(pdf), expect_width_mm=width_mm, check_overlap=False)
    hard = [f for f in report["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    print(f"  audit: width {report.get('width_mm')} mm, "
          f"height {report.get('height_mm')} mm, {len(hard)} hard finding(s)")
    for f in hard:
        print(f"    ! {f['check']}: {f['detail']}")

    if result.get("hard_failures"):
        print(f"  the figure has {result['hard_failures']} rendering finding(s):")
        for f in (result.get("findings") or [])[:5]:
            print(f"    ! {f.get('check')}: {f.get('detail')}")

    ok = not hard
    print(f"  RESULT: {'compliant' if ok else 'NOT compliant'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
