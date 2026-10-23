"""The OFFICIAL scorer must run, and our emitted code must score against it.

WHY THESE TESTS
    PlotTwin-Bench's official score is `S = 0.35 * S_code + 0.65 * S_vision`. This project can only
    run the deterministic code channel, so the honest claim is "code channel", never "combined
    score". These tests pin three things:

      1. the vendored scorer is the real one and gives 100 for identical code, <100 for deviations
      2. figpipe can EMIT code that the scorer accepts (otherwise the official channel is
         unreachable, which was the actual state before this module)
      3. the emitted code actually renders -- a script the scorer accepts but matplotlib rejects
         would be a score for a figure that does not exist
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "third_party"))

scorer = pytest.importorskip("plottwin_scorer", reason="official scorer not vendored")
codegen = pytest.importorskip("figpipe.codegen", reason="codegen absent")
from figpipe import composite  # noqa: E402

TREND = pd.DataFrame({"year": np.arange(1990, 2014),
                      "value": 0.1 + 0.008 * np.arange(24)})


def _panel():
    return composite.Panel("trend_band", TREND,
                           {"x": "year", "y": "value", "fit": "lm", "reference": 0.5,
                            "xlabel": "Year", "ylabel": "z-score"})


def test_the_vendored_scorer_is_the_real_one():
    assert scorer.DEVIATION_DEFECT_SCORE_VERSION == "deviation-defect-v1"
    code = ("import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots(figsize=(3.6, 2.4))\n"
            "ax.plot([1, 2, 3], [1, 2, 3], color='#0072b2', linewidth=1.2)\n"
            "ax.grid(False)\n")
    same = scorer.score_code_deviation(code, code)
    assert same["available"] is True
    assert same["score"] == pytest.approx(100.0)
    worse = scorer.score_code_deviation(
        code, code.replace("#0072b2", "#d55e00").replace("linewidth=1.2", "linewidth=0.4"))
    assert worse["score"] < 100.0


def test_figpipe_can_emit_code_the_official_scorer_accepts(tmp_path):
    script = codegen.write([_panel()], tmp_path / "candidate.py", columns=2.0,
                           height_mm=90.0)
    text = script.read_text(encoding="utf-8")
    assert "matplotlib" in text and "savefig" in text
    reference = text                      # a perfect candidate is its own reference
    res = scorer.score_code_deviation(reference, text)
    assert res["available"] is True
    assert res["score"] == pytest.approx(100.0)


def test_the_emitted_script_actually_runs(tmp_path):
    """A score for a script that cannot render is a score for a figure that does not exist."""
    script = codegen.write([_panel()], tmp_path / "run_me.py", columns=2.0, height_mm=90.0)
    cp = subprocess.run([sys.executable, str(script)], cwd=tmp_path,
                        capture_output=True, text=True, timeout=180)
    assert cp.returncode == 0, cp.stderr[-2000:]
    assert (tmp_path / "figure.png").is_file()


def test_an_unknown_drawer_is_refused_rather_than_emitted():
    panel = composite.Panel("polar_profile", TREND,
                            {"theta": "year", "value": "value"})
    with pytest.raises(codegen.CodegenError, match="cannot be emitted"):
        codegen.emit([panel])


def test_deviating_code_scores_lower_than_matching_code(tmp_path):
    base = codegen.emit([_panel()], columns=2.0, height_mm=90.0)
    deviating = base.replace("ax.grid(False)", "ax.grid(True)")
    deviating = deviating.replace("color='#0072b2'", "color='#d55e00'")
    res = scorer.score_code_deviation(base, deviating)
    assert res["available"] is True
    assert res["score"] < 100.0
    assert "grid" in res["scored_dimensions"] or "palette" in res["scored_dimensions"]


def test_the_official_aggregate_covers_the_whole_report_not_a_slice():
    """A per-slice aggregate changes whenever a new window is measured.

    The first version computed the mean over the CURRENT slice only: it reported 97.87 over 6
    scored tasks while the report held 20. This is the same defect as the raw mean over a growing
    set, so the aggregate must be computed after the merge.
    """
    import json
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        import pytest
        pytest.skip("benchmark harness unavailable")
    report = ROOT / "corpus" / "e2e" / "plottwin_report.json"
    if not report.is_file():
        import pytest
        pytest.skip("report absent")
    data = json.loads(report.read_text(encoding="utf-8"))
    ok = [t for t in data["tasks"] if t.get("status") == "ok"]
    agg = bench._official_summary(ok)
    stored = data.get("official_code_channel") or {}
    assert agg["n_scored"] == stored.get("n_scored"), (
        f"stored aggregate covers {stored.get('n_scored')} tasks, report holds "
        f"{agg['n_scored']} scored")


def test_the_emitter_reproduces_every_scored_dimension():
    """The official score is only meaningful if the candidate can reach 100 by construction.

    Two dimensions were silently failing: `background` was never emitted at all, and `linewidth`
    used a hard-coded 1.0 while the reference said 1.1. Both were invisible because the aggregate
    mean (85) looked healthy -- one task scoring 33 does not move a mean much.
    """
    import json
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        pytest.skip("benchmark harness unavailable")
    import pandas as pd
    import numpy as np
    from figpipe import composite

    found = None
    for off in range(bench.POOL):
        try:
            row = bench.fetch_row(off)
        except Exception:                # noqa: BLE001 - offline is not a test failure
            break
        if row.get("reference_code"):
            found = row
            break
    if not found:
        pytest.skip("no reference code reachable")

    features = scorer.extract_style_features(found["reference_code"])["features"]
    style = codegen.style_from_features(features)
    df = pd.DataFrame({"x": np.arange(20.0), "y": np.linspace(0.1, 0.9, 20)})
    panel = composite.Panel("trend_band", df, {"x": "x", "y": "y", "fit": "lm"})
    candidate = codegen.emit([panel], columns=2.0, height_mm=100.0, style=style,
                             palette=style.get("palette"))
    res = scorer.score_code_deviation(found["reference_code"], candidate)
    assert res["available"] is True
    for dim in res["scored_dimensions"]:
        assert res["dimensions"][dim]["score"] == pytest.approx(1.0), (
            f"dimension {dim} scores {res['dimensions'][dim]['score']}, expected 1.0")
    assert res["score"] == pytest.approx(100.0, abs=0.01)


def test_the_two_style_sources_cannot_overwrite_each_other():
    """The honest number and the tautological ceiling are different measurements.

    Writing both to one path silently destroyed the honest result with the ceiling. Output identity
    must follow input identity.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import score_official as so
    except Exception:                    # pragma: no cover
        pytest.skip("scoring script unavailable")
    assert so.OUT_IMAGE != so.OUT_CODE
    assert so.OUT_IMAGE.name == "official_scores.json"
    assert so.OUT_CODE.name == "official_scores_code.json"


def test_an_image_inferred_style_leaves_code_only_dimensions_undetermined():
    """A raster cannot tell us the tick direction; pretending otherwise would be fabrication."""
    import sys
    sys.path.insert(0, str(ROOT))
    from figpipe import codegen, styleprofile
    imgs = list((ROOT / "corpus" / "e2e" / "images").glob("*.png"))
    if not imgs:
        pytest.skip("no cached reference images")
    prof = styleprofile.StyleProfile.from_image_detailed(imgs[0])
    style = codegen.style_from_image_profile(prof)
    assert style["inferred_from"] == "image"
    for dim in ("tick_direction", "serif", "legend_frame", "linewidth"):
        assert style[dim] is None, f"{dim} must be undetermined from pixels"
        assert dim in style["undetermined_dimensions"]
    # palette and aspect ARE recoverable
    assert style["figure_aspect"] is not None


def test_the_palette_estimate_comes_from_real_pixels():
    """Adaptive quantisation reported light blues for a figure whose ink is near-black.

    The official palette dimension is a directed nearest-distance over the REFERENCE's colours, so
    an estimate that misses them scores ~0 while looking like a measurement. This pins the fix:
    the dominant colours must be actual pixel values, and the cap must be large enough to cover
    references that carry up to 28 colours.
    """
    import sys
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))
    from figpipe import styleprofile
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        pytest.skip("benchmark harness unavailable")
    imgs = list(bench.IMAGES.glob("*.png"))
    if not imgs:
        pytest.skip("no cached reference images")
    prof = styleprofile.StyleProfile.from_image_detailed(imgs[0])
    hexes = [c["hex"] for c in prof.colours]
    assert hexes, "no colours extracted"
    assert len(hexes) <= 24
    # every reported colour must be a real colour in the image
    from PIL import Image
    import numpy as np
    arr = np.asarray(Image.open(imgs[0]).convert("RGB")).reshape(-1, 3)
    present = {f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r, g, b in arr[::37]}
    hits = sum(1 for h in hexes if h in present)
    assert hits >= len(hexes) // 2, (
        f"only {hits}/{len(hexes)} reported colours occur in the image: {hexes}")


def test_an_undetermined_linewidth_is_not_guessed():
    """Stroke width is not recoverable: the reference renders carry no dpi and vary 104-343 dpi.

    A fixed conversion produced 0.36 pt against true widths of 0.42-1.38 pt and made the official
    linewidth dimension WORSE (0.432 -> 0.244). Undetermined must stay undetermined.
    """
    import sys
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))
    from figpipe import codegen, styleprofile
    try:
        import bench_plottwin as bench
    except Exception:                    # pragma: no cover
        pytest.skip("benchmark harness unavailable")
    imgs = list(bench.IMAGES.glob("*.png"))
    if not imgs:
        pytest.skip("no cached reference images")
    prof = styleprofile.StyleProfile.from_image_detailed(imgs[0])
    style = codegen.style_from_image_profile(prof)
    assert style["linewidth"] is None
    assert "linewidth" in style["undetermined_dimensions"]


def test_the_claim_has_a_baseline_and_a_ceiling():
    """A score with no referent supports no claim.

    75.41 alone cannot say whether the pipeline beats anything. The three measured points must
    exist together: baseline (matplotlib defaults), pipeline (image-inferred), ceiling (code-copied).
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import score_official as so
    except Exception:                    # pragma: no cover
        pytest.skip("scoring script unavailable")
    cmp = so.comparison()
    for label in ("baseline", "pipeline", "ceiling"):
        assert label in cmp
        if cmp[label] is None:
            pytest.skip(f"{label} not measured yet")
        assert cmp[label]["mean"] is not None
        assert cmp[label]["n"] >= 5
    # the ordering must be baseline < pipeline < ceiling, or the "improvement" is not an improvement
    assert cmp["baseline"]["mean"] < cmp["pipeline"]["mean"] < cmp["ceiling"]["mean"]
    assert cmp["improvement"]["absolute"] > 0
    # THE THREE MUST BE COMPARED ON THE SAME TASK SET, and the per-pass counts can differ because a
    # pass drops a task it cannot fetch. `intersection` is the comparison that holds the set fixed;
    # it must exist and must cover most of the pool.
    ix = cmp.get("intersection")
    assert ix is not None, (
        "no fixed-set comparison: the three means cover different task sets, so the improvement is "
        "the difference between two different measurements")
    assert ix["n"] >= 100, f"the fixed-set comparison covers only {ix['n']} tasks"
    assert set(ix["means"]) == {"baseline", "pipeline", "ceiling"}
    assert ix["means"]["baseline"] < ix["means"]["pipeline"] < ix["means"]["ceiling"]
    assert ix["improvement"]["absolute"] > 0
    # and each must declare where its style came from
    assert cmp["baseline"]["source"] == "naive"
    assert cmp["pipeline"]["source"] == "image"
    assert cmp["ceiling"]["source"] == "code"
