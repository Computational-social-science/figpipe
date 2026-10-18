"""A deterministic implementation of the metric dimensions a peer benchmark uses.

WHY THIS MODULE EXISTS
    NaturePanelForge's SciFigure2Code evaluator (MIT) publishes an explicit dimension list for
    scoring a reconstructed scientific panel: execution, visual fidelity, chart type, layout,
    data pattern, text labels, axes, legends/colorbars, components, clarity/overlap, notation,
    code validity, plus two invalidity rates. That list is a good description of what a figure
    reproduction SHOULD be judged on, and it is the first thing adoptable from the peer work
    without any model: the taxonomy.

    What cannot be adopted is the judge. Their dimensions are filled by VLMs (0/1/2 rubrics) and
    by code execution with model-generated code. figpipe's position is that most of these
    dimensions have a MEASURABLE definition on the artefact, and that the ones which do not
    should be reported as N/A with a reason rather than guessed. So this module implements the
    subset that figpipe can measure exactly, records the evidence for each score, and leaves the
    rest explicitly missing -- a blank that says "not measured" is more useful than a number
    invented by a model.

WHAT IS MEASURED (per rendered PDF)
    execution_pass_rate        the PDF exists and the compliance audit has no hard finding
    visual_fidelity            (1 - style distance) to a measured reference profile, 0-100
    clarity_overlap            glyph-level text collisions: 0 -> 2, 1 -> 1, more -> 0
    layout_consistency         page width in {89,183} mm, height <= 170, one letter per panel
    text_label_fidelity        panel letters present and the expected number of text runs
    component_completeness     caller-declared components (band, fit, reference line) detected
    data_pattern_fidelity      published vs computed statistics: |delta| <= .01 -> 2, <= .05 -> 1
    chart_type_consistency     caller-declared expected vs actual intent sets
    invalidity                 direct image use and pixel painting are structurally 0 here, and
                               the module says so instead of claiming a measurement

NOT MEASURED (reported null, with a reason)
    axis_fidelity, legend_colorbar_completeness, scientific_notation_fidelity,
    code_validity_editability -- each needs either the reference panel or an interpretation,
    and fabricating them would repeat the mistake this project already documented about a VLM.
"""
from __future__ import annotations

import pathlib

from figpipe import audit, styleprofile


def _detect_components(pdf_path) -> dict:
    """Presence of declarable component classes, from the PDF's own drawing objects."""
    pymupdf = audit._require_pymupdf()
    doc = pymupdf.open(str(pdf_path))
    found = {"band": False, "fit_line": False, "reference": False, "colorbar": False}
    try:
        for page in doc:
            rect = page.rect
            page_area = rect.width * rect.height
            for path in page.get_drawings():
                r = path.get("rect")
                if r is None:
                    continue
                fill = path.get("fill")
                stroke = path.get("color")
                area = r.width * r.height
                if fill is not None and area > 0.02 * page_area:
                    found["band"] = True
                if stroke is not None and r.width > 0.35 * rect.width and r.height < 0.05 * rect.height:
                    # a long coloured horizontal stroke: a fit line or a reference line
                    if path.get("dashes") and path.get("dashes") != "[] 0":
                        found["reference"] = True
                    else:
                        found["fit_line"] = True
                if path.get("fill") is not None and r.width < 0.08 * rect.width \
                        and r.height > 0.4 * rect.height:
                    found["colorbar"] = True
    finally:
        doc.close()
    return found


def _rubric(value, scale=(0, 1, 2)) -> dict:
    return {"value": value, "scale": [scale[0], scale[-1]]}


def score_panel(pdf_path, *, reference_profile: styleprofile.StyleProfile | None = None,
                published: dict | None = None, computed: dict | None = None,
                expected_panels: int | None = 1, expect_components=None,
                expected_intents=None, actual_intents=None) -> dict:
    """Score one rendered panel. `None` in a dimension means NOT MEASURED, never guessed."""
    pdf = pathlib.Path(pdf_path)
    dimensions: dict[str, dict] = {}
    na: dict[str, str] = {}
    if not pdf.is_file():
        raise FileNotFoundError(pdf)

    a = audit.audit(pdf, check_overlap=False)
    hard = [f for f in a["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    dimensions["execution_pass_rate"] = {
        **_rubric(1.0 if not hard else 0.0),
        "evidence": [f["check"] for f in hard] or "rendered and audit-clean"}

    glyph = audit.overlapping_glyphs(pdf)
    clarity = 2 if not glyph else (1 if len(glyph) == 1 else 0)
    dimensions["clarity_overlap"] = {
        **_rubric(clarity), "evidence": {"collisions": glyph[:3]}}

    prof = styleprofile.StyleProfile.from_pdf(pdf)
    if reference_profile is not None:
        dist = styleprofile.compare(reference_profile, prof)
        dimensions["visual_fidelity"] = {
            "value": round(100.0 * (1.0 - dist["distance"]), 1), "scale": [0, 100],
            "evidence": {"style_distance": dist["distance"], "details": dist["details"]}}
    else:
        na["visual_fidelity"] = "no reference style profile supplied"

    layout = 0
    ok_width = abs(prof.width_mm - 89.0) < 0.6 or abs(prof.width_mm - 183.0) < 0.6
    if ok_width and prof.height_mm <= 170.0:
        layout = 1
        if expected_panels is None or len(prof.panel_letters) == expected_panels:
            layout = 2
    dimensions["layout_consistency"] = {
        **_rubric(layout), "evidence": {"width_mm": prof.width_mm,
                                        "height_mm": prof.height_mm,
                                        "panel_letters": len(prof.panel_letters),
                                        "expected": expected_panels}}

    letters_ok = (expected_panels is None or len(prof.panel_letters) == expected_panels)
    text_ok = prof.n_text_spans >= 4
    dimensions["text_label_fidelity"] = {
        **_rubric(2 if letters_ok and text_ok else (1 if text_ok else 0)),
        "evidence": {"n_text_spans": prof.n_text_spans, "letters_ok": letters_ok}}

    if expect_components:
        found = _detect_components(pdf)
        hit = [c for c in expect_components if found.get(c)]
        miss = [c for c in expect_components if not found.get(c)]
        dimensions["component_completeness"] = {
            **_rubric(2 if not miss else (1 if hit else 0)),
            "evidence": {"expected": list(expect_components), "found": hit, "missing": miss}}
    else:
        na["component_completeness"] = "no expected component list supplied"

    if published and computed:
        deltas = []
        for k, v in published.items():
            if isinstance(v, dict):
                continue
            got = computed.get(k)
            if got is not None:
                deltas.append(abs(got - v))
        if deltas:
            worst = max(deltas)
            dimensions["data_pattern_fidelity"] = {
                **_rubric(2 if worst <= 0.01 else (1 if worst <= 0.05 else 0)),
                "evidence": {"worst_abs_delta": round(worst, 4), "n": len(deltas)}}
        else:
            na["data_pattern_fidelity"] = "no overlapping statistic keys"
    else:
        na["data_pattern_fidelity"] = "no published/computed statistics supplied"

    if expected_intents is not None:
        exp = set(expected_intents)
        act = set(actual_intents or [])
        dimensions["chart_type_consistency"] = {
            **_rubric(2 if exp == act else (1 if exp & act else 0)),
            "evidence": {"expected": sorted(exp), "actual": sorted(act)}}
    else:
        na["chart_type_consistency"] = "no expected intent supplied"

    for name in ("axis_fidelity", "legend_colorbar_completeness",
                 "scientific_notation_fidelity", "code_validity_editability"):
        na[name] = "needs the reference panel or an interpretation; not measured"

    invalidity = {
        "direct_image_dependency_rate": {"value": 0.0,
                                         "evidence": "template pipeline never loads a target image"},
        "pixel_painting_or_raster_tracing_rate": {"value": 0.0,
                                                  "evidence": "all marks are vector primitives"},
    }
    values = [d["value"] for d in dimensions.values() if isinstance(d.get("value"), (int, float))]
    return {"pdf": str(pdf), "dimensions": dimensions, "invalidity": invalidity,
            "not_measured": na,
            "n_measured": len(values), "n_not_measured": len(na),
            "note": ("dimensions are reported separately, as the peer protocol requires; a "
                     "weighted total is optional and deliberately not computed here")}


if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(score_panel(sys.argv[1]), indent=2, ensure_ascii=False))
