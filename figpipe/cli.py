"""The command line: `figpipe audit`, `figpipe render`, `figpipe style`.

WHY A CLI AT ALL
    The five README entry points are all `import`-first, which is right for a library and wrong for the
    one thing most users need first: **check a PDF I already made**. A researcher holding a rejected
    figure does not want to open a REPL; they want

        figpipe audit figure.pdf --expect-width 183

    and an exit code they can put in a Makefile.

WHAT EACH COMMAND IS, AND IS NOT
    `audit`   wraps `audit.audit` and sets the exit code from `report["ok"]`. It measures the rendered
              file, so it is the only check that can catch the defects the README lists.
    `render`  wraps `skills.run` on a CSV, because "make a figure from your own CSV" is a README
              promise that currently needs Python.
    `style`   wraps `styleprofile` + `select`, so a reference figure can be measured and a candidate
              ranked without writing a script.

    None of them re-implements anything. **A CLI that reimplements the library is a second
    implementation to keep in sync**, which is the defect this project records most often.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def _cmd_audit(args) -> int:
    """Audit a rendered PDF. Exit 1 when the report says not ok."""
    from figpipe import audit

    pdf = pathlib.Path(args.pdf)
    if not pdf.is_file():
        print(f"figpipe audit: no such file: {pdf}", file=sys.stderr)
        return 2
    report = audit.audit(pdf, min_pt=args.min_pt, max_pt=args.max_pt,
                         expect_width_mm=args.expect_width,
                         check_overlap=not args.no_overlap)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        width = report.get("width_mm")
        print(f"{pdf.name}: {'OK' if report['ok'] else 'NOT SUBMITTABLE'}")
        if width is not None:
            print(f"  width: {width:.1f} mm")
        findings = report.get("findings") or []
        if findings:
            print(f"  {len(findings)} finding(s):")
            for f in findings:
                print(f"    [{f.get('severity', '?')}] {f.get('check', '?')}: "
                      f"{str(f.get('detail', ''))[:120]}")
        else:
            print("  no findings")
    return 0 if report.get("ok") else 1


def _cmd_render(args) -> int:
    """Render a figure from a CSV using a named skill."""
    import pandas as pd

    from figpipe import skills

    csv = pathlib.Path(args.csv)
    if not csv.is_file():
        print(f"figpipe render: no such file: {csv}", file=sys.stderr)
        return 2
    df = pd.read_csv(csv)
    params = {}
    if args.x:
        params["x"] = args.x
    if args.y:
        params["y"] = args.y
    out = pathlib.Path(args.out) if args.out else pathlib.Path("figpipe_out")
    try:
        result = skills.run(args.skill, df, out_stem=out, **params)
    except Exception as exc:                       # noqa: BLE001 - a CLI reports, it does not raise
        print(f"figpipe render: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"{result['skill']}: {result['panels']} panel(s)")
    print(f"  pdf: {result['pdf']}")
    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "trace"}, indent=2, default=str))
    hard = result.get("hard_failures") or 0
    if hard:
        print(f"  {hard} HARD failure(s) -- the figure is not submittable", file=sys.stderr)
    return 0 if hard == 0 else 1


def _cmd_style(args) -> int:
    """Measure a reference's style and rank candidate figures against it."""
    from figpipe import select, styleprofile

    ref = pathlib.Path(args.reference)
    if not ref.is_file():
        print(f"figpipe style: no such reference: {ref}", file=sys.stderr)
        return 2
    try:
        profile = styleprofile.StyleProfile.from_pdf(ref, page=args.page)
    except Exception as exc:                       # noqa: BLE001
        print(f"figpipe style: cannot profile {ref.name}: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    if not args.candidates:
        print(json.dumps({"source": str(ref), "sizes_pt": sorted(set(profile.sizes_pt)),
                          "colours": [c["hex"] for c in profile.colours[:12]],
                          "spines": profile.spines,
                          "line_widths_pt": sorted(set(profile.line_widths_pt))},
                         indent=2, default=str))
        return 0
    candidates = {}
    for path in args.candidates:
        p = pathlib.Path(path)
        if p.is_file():
            candidates[p.stem] = str(p)
    if not candidates:
        print("figpipe style: no readable candidate", file=sys.stderr)
        return 2
    picked = select.select(profile, candidates)
    print(json.dumps(picked, indent=2, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="figpipe",
        description="Publication-figure compliance: measure the rendered file, not the source.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {_version()}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="check a rendered PDF against the compliance floor")
    p_audit.add_argument("pdf", help="the rendered figure")
    p_audit.add_argument("--expect-width", type=float, default=None, metavar="MM",
                         help="the column width the figure must match (e.g. 183 for double column)")
    p_audit.add_argument("--min-pt", type=float, default=5.0, help="minimum text size (default 5.0)")
    p_audit.add_argument("--max-pt", type=float, default=7.0, help="maximum text size (default 7.0)")
    p_audit.add_argument("--no-overlap", action="store_true", help="skip the glyph-overlap check")
    p_audit.add_argument("--json", action="store_true", help="print the full report as JSON")
    p_audit.set_defaults(func=_cmd_audit)

    p_render = sub.add_parser("render", help="render a figure from a CSV using a named skill")
    p_render.add_argument("csv", help="the data")
    p_render.add_argument("--skill", default="trend_with_uncertainty", help="which recipe")
    p_render.add_argument("--x", help="column for the x axis")
    p_render.add_argument("--y", help="column for the y axis")
    p_render.add_argument("--out", help="output stem (default figpipe_out)")
    p_render.add_argument("--json", action="store_true")
    p_render.set_defaults(func=_cmd_render)

    p_style = sub.add_parser("style", help="measure a reference figure's style, optionally rank candidates")
    p_style.add_argument("reference", help="the reference PDF")
    p_style.add_argument("candidates", nargs="*", help="candidate PDFs to rank against it")
    p_style.add_argument("--page", type=int, default=1)
    p_style.set_defaults(func=_cmd_style)

    return parser


def _version() -> str:
    from figpipe import __version__
    return __version__


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":                          # pragma: no cover
    raise SystemExit(main())
