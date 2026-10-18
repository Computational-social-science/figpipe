"""Search template variants against a measured reference style, deterministically.

WHAT IT DOES
    Loads one panel of the seed's Fig. 7 data (Core -> Core), the measured profile of the
    published figure's PDF region, and searches the template's style knobs for the variant with
    the smallest distance to that reference -- keeping every evaluated variant in a trace.

WHY IT MATTERS
    This is the peer loop (render -> compare -> refine) with the model removed: the reference is
    a measured profile, the comparison is an exact distance, and the search is the vendored MIT
    tree search used only as an exploration policy. The output is auditable: every number in the
    trace can be re-derived by rendering the variant again.

USAGE
    python scripts/search_style.py --budget 12
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import tempfile

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import search, sources, styleprofile  # noqa: E402

DATA = ROOT / "corpus" / "seed" / "derived" / "fig7_mimicry.csv"
REFERENCE = ROOT / "corpus" / "style" / "published_fig7.json"
OUT = ROOT / "templates" / "search"


def pane_data(paper="Core", receiver="Core") -> pd.DataFrame:
    df = pd.read_csv(DATA, encoding="utf-8")
    part = df[(df["sender_cp"] == paper) & (df["receiver_cp"] == receiver)]
    return part[["Year", "mean"]].sort_values("Year").reset_index(drop=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    if not DATA.is_file() or not REFERENCE.is_file():
        print("  derived data or reference profile missing; run reproduce_seed.py first")
        return 1
    reference = styleprofile.StyleProfile.load(REFERENCE)
    df = pane_data()
    work = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-search-"))
    try:
        result = search.search(df, reference, budget=args.budget, seed=args.seed,
                               out_dir=work)
        OUT.mkdir(parents=True, exist_ok=True)
        payload = {k: v for k, v in result.items()}
        (OUT / "style_search_trace.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        best_pdf = work / pathlib.Path(result["best"]["pdf"]).name
        if best_pdf.is_file():
            shutil.copy2(best_pdf, OUT / "style_best_variant.pdf")
            prof = styleprofile.StyleProfile.from_pdf(OUT / "style_best_variant.pdf")
            prof.save(ROOT / "corpus" / "style" / "best_variant_profile.json")
        print(f"  baseline: {result['baseline'].get('state')}  "
              f"reward={result['baseline'].get('reward')}")
        print(f"  best    : {result['best']['state']}  reward={result['best']['reward']}  "
              f"improvement={result['improvement']}")
        for row in result["trace"][:6]:
            print(f"    {row['state']:<38} reward={row['reward']:<7} "
                  f"distance={row['distance']}")
        print(f"  wrote {OUT / 'style_search_trace.json'}")
    finally:
        # the temporary variant directory must never resolve inside a read-only source root,
        # whatever TMPDIR is set to; the guard makes that an error instead of a silent delete
        sources.assert_writable(work)
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
