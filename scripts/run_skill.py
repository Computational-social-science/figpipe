"""Run one named skill on a CSV, from the command line.

WHAT IT IS FOR
    `figpipe/skills.py` defines named recipes over classic operators. This is the thin CLI that
    makes one usable without writing Python, and prints the verification findings so a failure is
    visible rather than a "looks fine" PNG.

USAGE
    python scripts/run_skill.py --skill trend_with_uncertainty --data data.csv \
        --x year --y mean --out templates/skills/demo
    python scripts/run_skill.py --skill ranked_composition --data shares.csv \
        --label country --value share --top 20 --percent
    python scripts/run_skill.py --list
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import skills  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skill", help="skill name")
    ap.add_argument("--data", help="CSV file")
    ap.add_argument("--out", help="output stem (default templates/skills/<skill>)")
    ap.add_argument("--list", action="store_true", help="list skills and operators")
    ap.add_argument("--x")
    ap.add_argument("--y")
    ap.add_argument("--lo")
    ap.add_argument("--hi")
    ap.add_argument("--label")
    ap.add_argument("--value")
    ap.add_argument("--group")
    ap.add_argument("--ycols")
    ap.add_argument("--profile")
    ap.add_argument("--top", type=int)
    ap.add_argument("--percent", action="store_true")
    ap.add_argument("--param", nargs="*", default=[], metavar="KEY=VALUE")
    args = ap.parse_args(argv)

    if args.list or not args.skill:
        cat = skills.catalogue()
        print("skills:")
        for s in cat["skills"]:
            print(f"  {s['name']:<24} {s['description']}")
        print("\noperators:")
        for o in cat["operators"]:
            print(f"  {o['kind']:<6} {o['name']:<22} {o['doc']}")
        return 0

    if not args.data:
        print("  --data is required")
        return 2
    data = pd.read_csv(args.data, encoding="utf-8")
    params = {k: v for k, v in vars(args).items()
              if k in {"x", "y", "lo", "hi", "label", "value", "group", "ycols",
                       "profile", "top"} and v is not None}
    if args.percent:
        params["percent"] = True
    for item in args.param:
        key, _, value = item.partition("=")
        if not key:
            raise SystemExit(f"bad --param {item!r}; expected KEY=VALUE")
        params[key] = value
    out = args.out or str(ROOT / "templates" / "skills" / args.skill)
    result = skills.run(args.skill, data, out_stem=out, **params)
    print(json.dumps({k: v for k, v in result.items() if k != "trace"},
                     indent=2, ensure_ascii=False))
    return 0 if result["hard_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
