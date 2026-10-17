"""Structured STYLE annotation of real Nature figures with a local VLM (Ollama gemma3).

WHAT THIS PRODUCES
    corpus/vlm_labels.jsonl      one record per annotation: labels, raw response, prompt, model,
                                 options, latency, image digest -- everything needed to replay it
    corpus/vlm_sources.json      the figure crops and the geometry measured from the PDF
    corpus/vlm_controls.json     the no-answer control images and whether the model declined
    corpus/vlm_consistency.json  the 10 % re-annotation and its per-field agreement
    corpus/vlm_report.json       the aggregate: parse rate, null ratios, control results

WHY THE UNIT IS A CROP AND NOT A PAGE
    A Nature page is mostly two columns of prose with one figure in it. A page image asks
    "what kind of figure is this?" about a page that is ~85 % text. The fields this corpus needs
    -- panel layout, line weight, colour count, caption structure -- are properties of the
    figure, and the caption is itself one of the fields, so the unit is figure + its caption.

THE ANTI-FABRICATION DESIGN, WHICH IS THE POINT OF THIS FILE
    A VLM asked "is this figure colourblind-safe?" will answer. It has no option to decline
    unless the prompt gives it one, and a 4 B model given no decline option returned a definite
    answer for every field on a synthetic test figure -- including `column_width`, which is not
    recoverable from a cropped image at all. So:

      1. The prompt states, for every field, that null is the correct answer when the image does
         not support a determination, and that a guess is worse than a null.
      2. Every field is nullable and null is recorded as data, not as failure. The null ratio is
         reported per field. A field at 0 % null over 30+ images is flagged as "possibly
         fabricated" -- these fields are genuinely hard to determine from a crop, so a model that
         is never uncertain is answering rather than seeing.
      3. CONTROL IMAGES are annotated that have no answer to give: blank, pure noise, and a
         text-only crop. On those, every figure field MUST come back null (or `other` for
         figure_type). A control that returns "heatmap" for white noise is the model telling us
         it guesses, and that makes the whole batch's confident answers untrustworthy. The
         control can FAIL and its result is reported rather than assumed.
      4. Where geometry can answer a field better than vision can -- column width is a fact from
         the PDF, not something a crop shows -- the measured width is GIVEN to the model as
         stated context and its answer is checked against that geometry. Agreement is reported.

DETERMINISM
    temperature=0 and seed=42 on every call, with the full options block recorded so a record can
    be replayed. Ollama is not bit-deterministic across restarts, so the 10 % re-annotation
    measures the agreement that actually holds; it is reported, not asserted to be 100 %.

RESUME
    The jsonl is the state. A record is keyed by (image, model, prompt digest) and skipped on a
    rerun, so an interrupted batch continues instead of restarting. `--force` redoes everything.
"""
from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import random
import re
import sys
import time
import urllib.error
import urllib.request

try:
    import pymupdf
except ImportError:  # noqa: BLE001
    pymupdf = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
IMAGES = CORPUS / "pages_for_vlm"
SOURCES = CORPUS / "vlm_sources.json"
LABELS = CORPUS / "vlm_labels.jsonl"
CONSISTENCY = CORPUS / "vlm_consistency.json"
REPORT = CORPUS / "vlm_report.json"

PDF_DIR = pathlib.Path(r"D:\2026-AI4S")
OLLAMA = "http://127.0.0.1:11434"
DEFAULT_MODEL = "gemma3:12b"
FALLBACK_MODEL = "gemma3:4b"

SEED = 42
TEMPERATURE = 0
NUM_CTX = 8192
NUM_PREDICT = 900
MAX_ATTEMPTS = 3
REQUEST_TIMEOUT = 600

# Rendering. 150 dpi keeps a 5 pt Nature label ~10 px tall (legible) while keeping a crop small.
DPI = 150
MIN_W_PT, MIN_H_PT = 60.0, 40.0

# Nature's own text geometry, in mm. Used to turn a measured crop width into the column field
# instead of asking a model to infer a page fact from a crop.
NATURE_SINGLE_COLUMN_MM = 89.0
NATURE_TEXT_WIDTH_MM = 183.0
# A crop is attributable to a column only when its width lands near that column's true value.
COLUMN_TOLERANCE_MM = 10.0


def column_from_caption(cap_rect, page_w: float) -> str:
    """Column implied by where the CAPTION was set, which is the stronger of the two signals.

    A Nature caption is set to the width of the block it belongs to, so the caption's own span
    survives even when the figure inside it is narrower. A caption ending near 295 pt on a 595 pt
    page is a one-column block; one running to ~560 pt spans the text measure. This is reported
    alongside the crop-width estimate because the two answer different questions -- how wide the
    figure is, and how wide the column it was set in is -- and a disagreement between them is
    itself informative.
    """
    w_mm = cap_rect.width * 25.4 / 72.0
    if abs(w_mm - NATURE_SINGLE_COLUMN_MM) <= COLUMN_TOLERANCE_MM:
        return "single"
    if abs(w_mm - NATURE_TEXT_WIDTH_MM) <= COLUMN_TOLERANCE_MM:
        return "double"
    return "ambiguous"

CAPTION_RE = re.compile(r"^\s*(?:Fig\.?|Figure)\s*\|?\s*(\d+)\s*[\|\.:]", re.I)

# ---------------------------------------------------------------------------------------------
# The schema. Every field is nullable; the enums are closed. `null` is a legitimate value.
# ---------------------------------------------------------------------------------------------
FIELDS: dict[str, dict] = {
    "figure_type": {
        "enum": ["mechanism", "flowchart", "scatter", "heatmap", "multi_panel", "micrograph",
                 "network", "tree", "bar", "line", "other"],
        "help": "the dominant visual form; multi_panel only if panels are the point"},
    "column_width": {
        "enum": ["single", "double", "full"],
        "help": "use the measured width given in the prompt; do not guess this from the crop"},
    "font_family": {
        "enum": ["sans_arial_helvetica", "serif", "monospace", "mixed", "other"],
        "help": "the typeface family of the axis labels and panel letters"},
    "font_uniform": {"type": "bool", "help": "all labels appear to share one size/weight scheme"},
    "min_font_legible": {
        "type": "bool", "help": "the smallest text is legible in this image as supplied"},
    "line_weight": {"enum": ["thin", "medium", "thick", "mixed"]},
    "arrow_style": {"enum": ["none", "plain", "filled_head", "open_head", "mixed"]},
    "frame_restrained": {
        "type": "bool", "help": "no heavy full boxes around panels; borders are minimal"},
    "high_contrast": {"type": "bool", "help": "foreground/background separation is strong"},
    "colorblind_safe": {
        "type": "bool",
        "help": "the palette appears to avoid red/green-only distinctions (deuteranopia)"},
    "saturated_color_count": {
        "type": "int", "min": 0, "max": 30,
        "help": "count of DISTINCT strongly saturated hues; 0 for greyscale"},
    "palette_description": {"type": "str", "maxlen": 120},
    "caption_overview_first": {"type": "bool", "help": "the caption opens with a summary sentence"},
    "caption_panel_by_panel": {"type": "bool", "help": "the caption then walks the panels"},
    "caption_has_stats": {
        "type": "bool", "help": "the caption states n, a test, or an error definition"},
    "caption_stats_last": {"type": "bool", "help": "that statistical material comes at the end"},
    "panel_count": {"type": "int", "min": 0, "max": 40, "help": "0 if the figure is unpanelled"},
    "panel_layout": {"enum": ["single", "row", "column", "grid", "irregular", "none"]},
    "panel_labels_present": {"type": "bool", "help": "panels are lettered a/b/c or A/B/C"},
    "whitespace_generous": {"type": "bool", "help": "panels are separated by visible whitespace"},
    "vector_or_bitmap": {
        "enum": ["vector", "bitmap", "mixed"],
        "help": "are the plotted elements crisp vector shapes or a raster image"},
}

PROMPT = """You are a figure-style annotator building a corpus of published journal figure \
conventions. You will see ONE figure cropped from a real Nature paper, together with its caption.

Answer about the FIGURE ONLY, from what is visible in the image.

CRITICAL RULE -- READ THIS FIRST
Some fields cannot be determined from this image. When that is the case, the value MUST be
null. Do NOT guess. Do NOT pick the most plausible option. A null is a correct, useful answer;
a confident guess is a wrong answer that corrupts the corpus. If you are unsure whether
something is true, use null.

MEASURED CONTEXT (facts, not things to infer)
- crop_width_mm: {crop_width_mm}
- page_text_width_mm: {text_width_mm}
- nature_single_column_mm: {single_mm}
- nature_double_column_mm: {text_width_mm}

`column_width` IS ALREADY MEASURED, so do not spend judgement on it. Report the value implied by
the numbers above, and nothing else: near {single_mm} mm -> "single"; near {text_width_mm} mm ->
"double"; wider than the text block -> "full"; a width that is neither is not attributable to a
column, so answer null. Do not read the column width off the image: the crop is a box around the
figure and its apparent size says nothing about the page grid.

FIELDS (all may be null)
{field_list}

Reply with ONLY a JSON object containing exactly these keys, nothing else. No prose, no code
fence. Use null for any field you cannot determine from the image.
"""


# ---------------------------------------------------------------------------------------------
# JSON handling: strict parse, tolerant extraction, schema validation with recorded repairs.
# ---------------------------------------------------------------------------------------------
def extract_json(text: str):
    """Parse a JSON object out of `text`; tolerate code fences and surrounding prose.

    `format: json` usually makes this trivial, but the fallback exists because a model that
    ignores the format constraint would otherwise score as a parse failure rather than as a
    response we can still salvage and record honestly.
    """
    if not isinstance(text, str):
        raise ValueError("response is not text")
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    try:
        obj = json.loads(t)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost balanced object.
    start = t.find("{")
    if start >= 0:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(t)):
            c = t[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        obj = json.loads(t[start:i + 1])
                        if isinstance(obj, dict):
                            return obj
                        break
    raise ValueError("no JSON object found in response")


def coerce_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes", "y", "1"):
            return True
        if s in ("false", "no", "n", "0"):
            return False
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v in (0, 1):
        return bool(v)
    return None


def validate(raw: dict):
    """(labels, repairs, unknown_keys): enforce the schema, recording every coercion.

    A value that cannot be coerced becomes null rather than being dropped: the field still
    appears in the record, so a field the model fumbled is visible in the null statistics
    instead of silently vanishing.
    """
    labels, repairs = {}, []
    for name, spec in FIELDS.items():
        if name not in raw:
            labels[name] = None
            repairs.append("%s: missing -> null" % name)
            continue
        v = raw[name]
        if v is None:
            labels[name] = None
            continue
        if "enum" in spec:
            if isinstance(v, str) and v.strip().lower() in spec["enum"]:
                labels[name] = v.strip().lower()
            else:
                labels[name] = None
                repairs.append("%s: %r not in enum -> null" % (name, v))
        elif spec.get("type") == "bool":
            b = coerce_bool(v)
            if b is None:
                repairs.append("%s: %r not a bool -> null" % (name, v))
            labels[name] = b
        elif spec.get("type") == "int":
            iv = None
            if isinstance(v, bool):
                iv = None
            elif isinstance(v, int):
                iv = v
            elif isinstance(v, float) and v.is_integer():
                iv = int(v)
            elif isinstance(v, str) and re.fullmatch(r"-?\d+", v.strip()):
                iv = int(v.strip())
            if iv is None:
                repairs.append("%s: %r not an int -> null" % (name, v))
            elif iv < spec.get("min", -10**9) or iv > spec.get("max", 10**9):
                repairs.append("%s: %r out of range -> null" % (name, v))
                iv = None
            labels[name] = iv
        elif spec.get("type") == "str":
            if isinstance(v, str):
                s = v.strip()
                labels[name] = s[: spec.get("maxlen", 10**6)] or None
            else:
                labels[name] = None
                repairs.append("%s: %r not a string -> null" % (name, v))
        else:
            labels[name] = v
    unknown = [k for k in raw if k not in FIELDS]
    return labels, repairs, unknown


# ---------------------------------------------------------------------------------------------
# Figure extraction from the PDFs (render subcommand).
# ---------------------------------------------------------------------------------------------
def page_graphics(page):
    rects, n_vec, n_img = [], 0, 0
    for d in page.get_drawings():
        r = d["rect"]
        if r.is_empty or r.width <= 0 or r.height <= 0:
            continue
        rects.append(r)
        n_vec += 1
    for info in page.get_image_info():
        r = pymupdf.Rect(info["bbox"])
        if r.is_empty or r.width <= 0 or r.height <= 0:
            continue
        rects.append(r)
        n_img += 1
    return rects, n_vec, n_img


def captions_on(page):
    out = []
    for b in page.get_text("blocks"):
        text = (b[4] or "").strip()
        m = CAPTION_RE.match(text)
        if m:
            out.append((int(m.group(1)), pymupdf.Rect(b[:4]), text))
    out.sort(key=lambda t: (round(t[1].y0), t[1].x0))
    return out


def find_graphic(cap_rect, band_top, rects):
    """The ink above this caption, within its column, below the previous caption."""
    inside = []
    for r in rects:
        if r.y1 > cap_rect.y0 + 1.0:
            continue
        if r.y0 < band_top - 1.0:
            continue
        if r.y1 < band_top - 1.0:
            continue
        if r.x1 < cap_rect.x0 - 2.0 or r.x0 > cap_rect.x1 + 2.0:
            continue
        inside.append(r)
    if not inside:
        return None, 0
    return pymupdf.Rect(min(r.x0 for r in inside), min(r.y0 for r in inside),
                        max(r.x1 for r in inside), max(r.y1 for r in inside)), len(inside)


def ink_fraction(pix):
    s = pix.samples
    n = len(s)
    if n == 0:
        return 0.0
    step = max(1, n // 60000) * 3
    sampled = nonwhite = 0
    for i in range(0, n - 2, step):
        sampled += 1
        if s[i] < 245 or s[i + 1] < 245 or s[i + 2] < 245:
            nonwhite += 1
    return nonwhite / sampled if sampled else 0.0


def render():
    """Render figure+caption crops for every NATURE-named PDF under PDF_DIR."""
    if pymupdf is None:
        print("  [FAIL] pymupdf is not installed, so nothing can be rendered")
        return 1
    IMAGES.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(p for p in PDF_DIR.rglob("*.pdf") if "NATURE" in p.name.upper())
    print("NATURE-named PDFs under %s: %d" % (PDF_DIR, len(pdfs)))
    if not pdfs:
        print("  [FAIL] no source PDFs, so there is nothing to render")
        return 1

    # THE SAME PAPER IS ON DISK MORE THAN ONCE. The 42 NATURE-named files hold only 34 distinct
    # documents: a paper and its SI copies live under several worktree/quarantine paths, and one
    # briefing is present seven times. Left in, the duplicates inflate "papers with figures" and,
    # worse, produce the same figure twice under the same truncated slug, so the second crop
    # silently overwrote the first and the manifest then described an image that no longer existed
    # on disk (133 records, 97 files). Deduplicating by content is the fix.
    unique, seen_sha, dup_paths = [], {}, []
    for pdf in pdfs:
        try:
            sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
        except OSError:
            continue
        if sha in seen_sha:
            dup_paths.append({"kept": str(seen_sha[sha]), "duplicate": str(pdf)})
            continue
        seen_sha[sha] = pdf
        unique.append((pdf, sha))
    print("distinct PDF contents: %d (from %d files, %d duplicates skipped)"
          % (len(unique), len(pdfs), len(dup_paths)))

    records, skipped = [], []
    for pdf, sha in unique:
        # The slug is capped for filesystem friendliness, so two long-titled papers can collide.
        # A short content hash keeps the name unique and still readable.
        slug = re.sub(r"[^a-z0-9]+", "-", pdf.stem.lower()).strip("-")[:48] + "-" + sha[:8]
        try:
            doc = pymupdf.open(pdf)
        except Exception as exc:  # noqa: BLE001
            skipped.append({"paper": pdf.name, "why": "cannot open: %s" % exc})
            continue
        page_w = 595.0
        for pno in range(len(doc)):
            page = doc[pno]
            page_w = page.rect.width
            caps = captions_on(page)
            if not caps:
                continue
            rects, n_vec, n_img = page_graphics(page)
            if not rects:
                continue
            for i, (num, cap_rect, cap_text) in enumerate(caps):
                band_top = caps[i - 1][1].y1 if i > 0 else 0.0
                graphic, n_ink = find_graphic(cap_rect, band_top, rects)
                if graphic is None:
                    skipped.append({"paper": pdf.name, "page": pno + 1, "fig": num,
                                    "why": "no graphic above the caption"})
                    continue
                crop = pymupdf.Rect(graphic.x0, graphic.y0, graphic.x1, cap_rect.y1) & page.rect
                if crop.width < MIN_W_PT or crop.height < MIN_H_PT:
                    skipped.append({"paper": pdf.name, "page": pno + 1, "fig": num,
                                    "why": "graphic too small (%.0fx%.0f pt)"
                                           % (crop.width, crop.height)})
                    continue
                crop = pymupdf.Rect(crop.x0 - 3, crop.y0 - 3,
                                    crop.x1 + 3, crop.y1 + 3) & page.rect
                pix = page.get_pixmap(clip=crop, dpi=DPI)
                ink = ink_fraction(pix)
                if ink < 0.002:
                    skipped.append({"paper": pdf.name, "page": pno + 1, "fig": num,
                                    "why": "blank crop (ink %.4f)" % ink})
                    continue
                name = "%s_p%03d_fig%d.png" % (slug, pno + 1, num)
                pix.save(str(IMAGES / name))
                width_mm = crop.width * 25.4 / 72.0
                # COLUMN WIDTH IS A PDF FACT, NOT A VISION TASK. The crop is a tight box around
                # the figure, so its width measures the FIGURE, not the column it was set in:
                # the median crop here is 118 mm, which is neither Nature column. Only widths
                # near the real 89 mm single or 183 mm double column are attributable; anything
                # between is a figure that happens to be that wide and has no column to report.
                # So geometry yields single/double/ambiguous, and the ambiguous band is reported
                # as unknown rather than forced into one of the two.
                if abs(width_mm - NATURE_SINGLE_COLUMN_MM) <= COLUMN_TOLERANCE_MM:
                    geom = "single"
                elif abs(width_mm - NATURE_TEXT_WIDTH_MM) <= COLUMN_TOLERANCE_MM:
                    geom = "double"
                elif width_mm > NATURE_TEXT_WIDTH_MM + COLUMN_TOLERANCE_MM:
                    geom = "full"
                else:
                    geom = "ambiguous"
                records.append({
                    "image": name, "paper": pdf.name, "page": pno + 1, "figure_number": num,
                    "crop_pt": [round(v, 1) for v in (crop.x0, crop.y0, crop.x1, crop.y1)],
                    "crop_px": [pix.width, pix.height],
                    "crop_width_mm": round(width_mm, 1),
                    "page_text_width_mm": round(page_w * 25.4 / 72.0, 1),
                    "dpi": DPI, "ink_fraction": round(ink, 4),
                    "caption_width_pt": round(cap_rect.width, 1),
                    "column_from_geometry": geom,
                    "column_from_caption_span": column_from_caption(cap_rect, page_w),
                    "caption_text": cap_text,
                    "graphic_objects": n_ink,
                    "page_vector_objects": n_vec,
                    "page_raster_images": n_img,
                })
        doc.close()

    # A COLLISION MUST FAIL THE RENDER, NOT OVERWRITE A FILE. The first run produced 133 records
    # over 97 images because two long-titled papers truncated to the same slug; the manifest then
    # pointed at images the last writer had replaced, and nothing in the output said so. Checking
    # the written file count against the record count turns that silent loss into a failure.
    names = [r["image"] for r in records]
    if len(set(names)) != len(names):
        from collections import Counter
        dup = {k: v for k, v in Counter(names).items() if v > 1}
        print("  [FAIL] %d image-name collisions -- crops overwrote each other: %s"
              % (len(dup), list(dup)[:4]))
        return 1
    missing_on_disk = [n for n in names if not (IMAGES / n).exists()]
    if missing_on_disk:
        print("  [FAIL] %d manifest images are not on disk" % len(missing_on_disk))
        return 1

    SOURCES.write_text(json.dumps(
        {"source_dir": str(PDF_DIR), "pdfs_scanned": len(pdfs),
         "pdfs_distinct": len(unique), "duplicates_skipped": dup_paths,
         "dpi": DPI, "figures": records, "skipped": skipped},
        indent=1, ensure_ascii=False), encoding="utf-8")
    print("figures rendered : %d" % len(records))
    print("distinct papers  : %d" % len({r["paper"] for r in records}))
    print("skipped          : %d" % len(skipped))
    from collections import Counter
    print("column geometry  : %s" % dict(Counter(r["column_from_geometry"] for r in records)))
    print("manifest         : %s" % SOURCES)
    for s in skipped[:6]:
        print("  [SKIP] %s p%s: %s" % (s["paper"][:40], s.get("page"), s["why"]))
    return 0 if records else 1


# ---------------------------------------------------------------------------------------------
# Control images: figures with no answer. The control that can fail.
# ---------------------------------------------------------------------------------------------
def make_controls():
    """Three images that have no figure to describe. Every figure field must come back null."""
    if pymupdf is None:
        return []
    ctl = CORPUS / "vlm_controls"
    ctl.mkdir(parents=True, exist_ok=True)
    made = []

    blank = pymupdf.open()
    p = blank.new_page(width=595, height=400)
    pix = p.get_pixmap(dpi=DPI)
    pix.save(str(ctl / "control_blank.png"))
    made.append({"image": "control_blank.png", "kind": "blank",
                 "why": "white page: nothing to annotate, so every field must be null"})
    blank.close()

    noise = pymupdf.open()
    p = noise.new_page(width=595, height=400)
    rnd = random.Random(SEED)
    for _ in range(9000):
        x, y = rnd.uniform(0, 595), rnd.uniform(0, 400)
        p.draw_line(pymupdf.Point(x, y), pymupdf.Point(x + rnd.uniform(1, 7), y),
                    color=(rnd.random(), rnd.random(), rnd.random()), width=0.7)
    pix = p.get_pixmap(dpi=DPI)
    pix.save(str(ctl / "control_noise.png"))
    made.append({"image": "control_noise.png", "kind": "noise",
                 "why": "random strokes: no figure type, no palette structure, no caption"})
    noise.close()

    textonly = pymupdf.open()
    p = textonly.new_page(width=595, height=400)
    body = ("The quick brown fox jumps over the lazy dog. " * 40)
    p.insert_textbox(pymupdf.Rect(40, 40, 555, 360), body, fontsize=10)
    pix = p.get_pixmap(dpi=DPI)
    pix.save(str(ctl / "control_textonly.png"))
    made.append({"image": "control_textonly.png", "kind": "text_only",
                 "why": "prose with no figure: a caption/structure answer here is invented"})
    textonly.close()
    return made


# ---------------------------------------------------------------------------------------------
# Ollama client.
# ---------------------------------------------------------------------------------------------
def field_list_text():
    lines = []
    for name, spec in FIELDS.items():
        if "enum" in spec:
            allowed = "|".join(spec["enum"])
            lines.append("- %s: one of %s" % (name, allowed))
        elif spec.get("type") == "bool":
            lines.append("- %s: true|false" % name)
        elif spec.get("type") == "int":
            lines.append("- %s: integer %s..%s" % (name, spec.get("min", 0), spec.get("max", 99)))
        else:
            lines.append("- %s: short string (<= %s chars)" % (name, spec.get("maxlen", 120)))
        if spec.get("help"):
            lines.append("    (%s)" % spec["help"])
    return "\n".join(lines)


def build_prompt(src: dict) -> str:
    return PROMPT.format(
        crop_width_mm=src.get("crop_width_mm", "unknown"),
        text_width_mm=NATURE_TEXT_WIDTH_MM,
        single_mm=NATURE_SINGLE_COLUMN_MM,
        field_list=field_list_text(),
    )


def ollama_generate(model: str, prompt: str, image_b64: str):
    body = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": TEMPERATURE,
            "seed": SEED,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(OLLAMA + "/api/generate", data=data,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
        out = json.loads(r.read().decode("utf-8"))
    return out, time.time() - t0, body


def annotate_one(model: str, image_path: pathlib.Path, src: dict):
    """Annotate one image with retries. Returns a record; never raises for a bad response."""
    raw_bytes = image_path.read_bytes()
    b64 = base64.b64encode(raw_bytes).decode("ascii")
    prompt = build_prompt(src)
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    image_sha = hashlib.sha256(raw_bytes).hexdigest()

    attempts, raw_responses, errors = [], [], []
    parsed, repairs, unknown, labels = None, [], [], None
    latency_total = 0.0
    for attempt in range(1, MAX_ATTEMPTS + 1):
        p = prompt
        if attempt > 1 and raw_responses:
            p = (prompt + "\n\nYour previous reply was not a valid JSON object. Reply with ONLY "
                          "the JSON object, no prose and no code fence.\nPrevious reply:\n"
                 + raw_responses[-1][:600])
        try:
            out, dt, _body = ollama_generate(model, p, b64)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            errors.append("attempt %d transport: %s" % (attempt, exc))
            attempts.append({"attempt": attempt, "ok": False, "error": "transport: %s" % exc})
            time.sleep(min(2.0 * attempt, 6.0))
            continue
        latency_total += dt
        raw = out.get("response", "")
        raw_responses.append(raw)
        try:
            obj = extract_json(raw)
            labels, repairs, unknown = validate(obj)
            attempts.append({"attempt": attempt, "ok": True, "latency_s": round(dt, 2),
                             "eval_count": out.get("eval_count"),
                             "response_sha256": hashlib.sha256(raw.encode()).hexdigest()[:16]})
            parsed = obj
            break
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append("attempt %d parse: %s" % (attempt, exc))
            attempts.append({"attempt": attempt, "ok": False, "parse_error": str(exc),
                             "latency_s": round(dt, 2)})

    return {
        "image": image_path.name,
        "image_sha256": image_sha,
        "kind": src.get("kind", "figure"),
        "paper": src.get("paper"),
        "page": src.get("page"),
        "figure_number": src.get("figure_number"),
        "model": model,
        "prompt_sha256": prompt_sha,
        "prompt": prompt,
        "options": {"temperature": TEMPERATURE, "seed": SEED, "num_ctx": NUM_CTX,
                    "num_predict": NUM_PREDICT, "format": "json"},
        "source_geometry": {
            "crop_width_mm": src.get("crop_width_mm"),
            "column_from_geometry": src.get("column_from_geometry"),
            "caption_text": src.get("caption_text"),
        },
        "parse_ok": parsed is not None,
        "attempts": attempts,
        "n_attempts": len(attempts),
        "errors": errors,
        "raw_responses": raw_responses,
        "parsed": parsed,
        "labels": labels,
        "repairs": repairs,
        "unknown_keys": unknown,
        "null_fields": sorted(k for k, v in (labels or {}).items() if v is None),
        "n_null": sum(1 for v in (labels or {}).values() if v is None),
        "latency_s": round(latency_total, 2),
        "annotated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


# ---------------------------------------------------------------------------------------------
# Batch driver with resume.
# ---------------------------------------------------------------------------------------------
def key_of(rec: dict) -> str:
    return "%s|%s|%s" % (rec["image"], rec["model"], rec["prompt_sha256"])


def load_done() -> dict[str, dict]:
    done = {}
    if LABELS.exists():
        for line in LABELS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue          # a torn final line from an interrupted write is expected
            if rec.get("parse_ok"):
                done[key_of(rec)] = rec
    return done


def label(model: str, limit: int | None, force: bool, per_paper: int):
    """Annotate every rendered figure, resuming from what is already in the jsonl."""
    if not IMAGES.exists():
        print("  [FAIL] no images at %s -- run the `render` subcommand first" % IMAGES)
        return 1
    if not SOURCES.exists():
        print("  [FAIL] no source manifest at %s -- run `render` first" % SOURCES)
        return 1
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))

    # One figure per paper by default: 42 papers, so a 30-figure batch is not 30 figures from
    # three papers, which would make every style statistic a statement about three papers.
    chosen, seen = [], {}
    for s in sources["figures"]:
        p = s["paper"]
        if seen.get(p, 0) >= per_paper:
            continue
        seen[p] = seen.get(p, 0) + 1
        chosen.append(s)
    chosen.sort(key=lambda s: (s["paper"], s["page"], s["figure_number"]))
    if limit:
        chosen = chosen[:limit]

    done = load_done() if not force else {}
    todo = []
    for s in chosen:
        rec_key = "%s|%s|" % (s["image"], model)
        if any(k.startswith(rec_key) for k in done):
            continue
        todo.append(s)

    print("model            : %s" % model)
    print("figures selected : %d (%d papers)" % (len(chosen), len(seen)))
    print("already labelled : %d" % (len(chosen) - len(todo)))
    print("to label         : %d" % len(todo))
    if not todo:
        print("nothing to do (resume found everything; use --force to redo)")
        return 0

    t_start = time.time()
    ok = fail = 0
    for i, s in enumerate(todo, 1):
        path = IMAGES / s["image"]
        if not path.exists():
            print("  [SKIP] %s: image missing" % s["image"])
            continue
        rec = annotate_one(model, path, s)
        with LABELS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if rec["parse_ok"]:
            ok += 1
            print("  [%2d/%2d] %-46s ok  nulls=%2d  %.1fs" % (
                i, len(todo), s["image"][:46], rec["n_null"], rec["latency_s"]))
        else:
            fail += 1
            print("  [%2d/%2d] %-46s PARSE FAILED after %d attempts" % (
                i, len(todo), s["image"][:46], rec["n_attempts"]))
    dt = time.time() - t_start
    print("annotated ok: %d   parse failures: %d   elapsed: %.0fs" % (ok, fail, dt))
    return 0 if fail == 0 else 1


def run_controls(model: str):
    """Annotate the no-answer control images and report whether the model declines.

    SCORING A CONTROL HONESTLY
    A first pass scored "any non-null field = fabricated" and that overstates the case: on a
    blank canvas `panel_count: 0` and `panel_layout: "none"` are TRUE, not invented. Calling them
    fabrication would be a false accusation, and a false accusation is as damaging to a control as
    a missed one -- it trains the reader to ignore the warning.

    So each asserted field is sorted into:
      trivially_true -- defensible on an empty canvas (0 panels, no arrows, no labels)
      fabricated     -- a claim about a figure that is not there: a figure type, a font family,
                        a line weight, a palette judgement, a caption structure, a column width.
    The control counts as DECLINED only when nothing was fabricated.

    `column_width` is scored separately and is the sharpest probe in the set: the prompt supplies
    `crop_width_mm: unknown` and states in as many words that this field is not to be read off the
    image. Any non-null column_width on a control is therefore a direct observation of the model
    ignoring an explicit instruction not to guess, which is the exact behaviour the corpus has to
    be protected from.
    """
    ctl_dir = CORPUS / "vlm_controls"
    if not ctl_dir.exists():
        make_controls()
    controls = [
        {"image": "control_blank.png", "kind": "blank",
         "why": "white page: nothing to annotate, so every field must be null"},
        {"image": "control_noise.png", "kind": "noise",
         "why": "random strokes: no figure type, no palette structure, no caption"},
        {"image": "control_textonly.png", "kind": "text_only",
         "why": "prose with no figure: a caption/structure answer here is invented"},
    ]
    # Values that are true of an empty canvas rather than invented about a figure.
    TRIVIAL = {
        "panel_count": {0},
        "panel_layout": {"none"},
        "panel_labels_present": {False},
        "arrow_style": {"none"},
        "saturated_color_count": {0},
        "whitespace_generous": {False},
        "frame_restrained": {True, False},   # an empty page has no heavy frames either way
    }
    results = []
    for c in controls:
        path = ctl_dir / c["image"]
        if not path.exists():
            continue
        rec = annotate_one(model, path, {"kind": "control", "caption_text": "",
                                         "crop_width_mm": "unknown"})
        labels = rec.get("labels") or {}
        asserted = {k: v for k, v in labels.items()
                    if v is not None and not (k == "figure_type" and v == "other")}
        trivial = {k: v for k, v in asserted.items()
                   if k in TRIVIAL and v in TRIVIAL[k]}
        fabricated = {k: v for k, v in asserted.items() if k not in trivial}
        results.append({
            "image": c["image"], "kind": c["kind"], "why": c["why"],
            "parse_ok": rec["parse_ok"], "n_null": rec["n_null"],
            "n_asserted": len(asserted), "asserted_fields": asserted,
            "n_trivially_true": len(trivial), "trivially_true_fields": trivial,
            "n_fabricated": len(fabricated), "fabricated_fields": fabricated,
            "column_width_asserted": labels.get("column_width"),
            "column_width_is_fabrication": labels.get("column_width") is not None,
            "raw_response": (rec["raw_responses"] or [""])[-1][:500],
            "declined": rec["parse_ok"] and len(fabricated) == 0,
        })
        r = results[-1]
        print("  %-26s nulls=%2d  asserted=%2d (trivial=%d)  FABRICATED=%2d  declined=%s"
              % (c["image"], r["n_null"], r["n_asserted"], r["n_trivially_true"],
                 r["n_fabricated"], r["declined"]))
        if r["fabricated_fields"]:
            print("      fabricated: %s" % json.dumps(r["fabricated_fields"], ensure_ascii=False)[:300])

    n_dec = sum(1 for r in results if r["declined"])
    cw_fab = sum(1 for r in results if r["column_width_is_fabrication"])
    total_fab = sum(r["n_fabricated"] for r in results)
    out = {
        "model": model,
        "controls": results,
        "n_controls": len(results),
        "n_declined": n_dec,
        "n_fabricated_total": total_fab,
        "n_column_width_guessed": cw_fab,
        "verdict": ("DECLINES -- the model abstains when there is nothing to see"
                    if n_dec == len(results) and results else
                    "FABRICATES -- the model asserts figure properties on images that have no "
                    "figure. Its confident answers on real figures are not evidence of seeing."),
    }
    out_path = CORPUS / "vlm_controls.json"
    out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("controls declined: %d of %d | fabricated assertions: %d | column_width guessed: %d"
          % (n_dec, len(results), total_fab, cw_fab))
    if n_dec < len(results):
        print("  [WARN] %s" % out["verdict"])
        print("         The per-field null ratios below are reported, but a null the model")
        print("         volunteers on hard fields is not proof it abstains when it could guess:")
        print("         it guessed here, where the right answer was impossible.")
    return 0


# ---------------------------------------------------------------------------------------------
# Consistency: re-annotate a deterministic 10 % sample and report per-field agreement.
# ---------------------------------------------------------------------------------------------
def consistency(model: str, fraction: float = 0.1):
    if not LABELS.exists():
        print("  [FAIL] no labels yet")
        return 1
    recs = []
    for line in LABELS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("parse_ok") and r.get("model") == model and r.get("kind") != "control":
            recs.append(r)
    # The latest record per image is the one that counts.
    latest = {}
    for r in recs:
        latest[r["image"]] = r
    pool = sorted(latest.values(), key=lambda r: r["image"])
    if not pool:
        print("  [FAIL] no figure annotations for model %s" % model)
        return 1
    n = max(1, int(round(len(pool) * fraction)))
    rnd = random.Random(SEED)
    sample = rnd.sample(pool, min(n, len(pool)))
    print("consistency sample: %d of %d figures (%.0f %%)" % (len(sample), len(pool), 100 * fraction))

    per_field: dict[str, list[bool]] = {f: [] for f in FIELDS}
    rows = []
    for r in sample:
        src = {"kind": "figure", "paper": r.get("paper"), "page": r.get("page"),
               "figure_number": r.get("figure_number"),
               "crop_width_mm": (r.get("source_geometry") or {}).get("crop_width_mm"),
               "caption_text": (r.get("source_geometry") or {}).get("caption_text")}
        again = annotate_one(model, IMAGES / r["image"], src)
        a, b = r.get("labels") or {}, again.get("labels") or {}
        agree = {f: (a.get(f) == b.get(f)) for f in FIELDS}
        for f, v in agree.items():
            per_field[f].append(v)
        both_null = sum(1 for f in FIELDS if a.get(f) is None and b.get(f) is None)
        rows.append({"image": r["image"], "first": a, "second": b,
                     "agreement": round(sum(agree.values()) / len(FIELDS), 4),
                     "both_null": both_null})
        print("  %-46s agreement=%.2f" % (r["image"][:46], rows[-1]["agreement"]))

    field_rate = {f: (round(sum(v) / len(v), 4) if v else None) for f, v in per_field.items()}
    overall = round(sum(r["agreement"] for r in rows) / len(rows), 4) if rows else None
    # Agreement that is only two nulls is not agreement about the figure; report it apart.
    informative = []
    for r in rows:
        decided = [f for f in FIELDS
                   if not (r["first"].get(f) is None and r["second"].get(f) is None)]
        if decided:
            informative.append(sum(1 for f in decided
                                   if r["first"].get(f) == r["second"].get(f)) / len(decided))
    informative_rate = round(sum(informative) / len(informative), 4) if informative else None
    out = {
        "model": model, "fraction": fraction, "n_sampled": len(sample), "n_pool": len(pool),
        "overall_field_agreement": overall,
        "agreement_excluding_both_null": informative_rate,
        "per_field_agreement": field_rate,
        "rows": rows,
        "note": ("overall_field_agreement counts a field where both runs said null as agreeing. "
                 "agreement_excluding_both_null counts only fields at least one run decided, so "
                 "it measures agreement about the figure rather than agreement to abstain."),
    }
    CONSISTENCY.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("overall field agreement        : %s" % overall)
    print("agreement excluding both-null  : %s" % informative_rate)
    print("written: %s" % CONSISTENCY)
    return 0


# ---------------------------------------------------------------------------------------------
# Report: the honest aggregate.
# ---------------------------------------------------------------------------------------------
def report():
    if not LABELS.exists():
        print("  [FAIL] no labels yet")
        return 1
    recs = []
    for line in LABELS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    figures = [r for r in recs if r.get("kind") != "control"]
    latest = {}
    for r in figures:
        latest[r["image"]] = r
    figures = list(latest.values())

    n = len(figures)
    parse_ok = sum(1 for r in figures if r.get("parse_ok"))
    per_field_null = {}
    for f in FIELDS:
        nulls = sum(1 for r in figures if (r.get("labels") or {}).get(f) is None)
        per_field_null[f] = round(nulls / n, 4) if n else None
    overall_null = (round(sum(r.get("n_null", 0) for r in figures) / (n * len(FIELDS)), 4)
                    if n else None)
    total_nulls = sum(r.get("n_null", 0) for r in figures)

    # COLUMN WIDTH: the model is scored against the geometry it was TOLD, and only where that
    # geometry actually determines an answer. Scoring against every figure compared the model with
    # an "ambiguous" bucket it had never been asked to produce, which understated the failure.
    geo_rows = []
    for r in figures:
        geom = (r.get("source_geometry") or {}).get("column_from_geometry")
        geo_rows.append({
            "image": r["image"],
            "model": (r.get("labels") or {}).get("column_width"),
            "geometry": geom,
            "width_mm": (r.get("source_geometry") or {}).get("crop_width_mm"),
        })
    attributable = [g for g in geo_rows if g["geometry"] in ("single", "double", "full")]
    geo_agree = sum(1 for g in attributable if g["model"] == g["geometry"])
    # The sharpest measure: the model was handed a width that maps to exactly one answer.
    unambiguous = [g for g in geo_rows if g["geometry"] in ("single", "double")]
    unamb_agree = sum(1 for g in unambiguous if g["model"] == g["geometry"])

    # A FIELD WITH ONE DOMINANT VALUE IS NOT A MEASUREMENT. If 37 of 40 figures are labelled
    # "single", the field is carrying almost no information about the corpus, whatever its null
    # ratio says. Reported next to the null ratios because the two failure modes look different
    # and both mean the same thing: the label cannot be used as evidence about style.
    from collections import Counter
    modal_share, distinct_values = {}, {}
    for f in FIELDS:
        vals = [(r.get("labels") or {}).get(f) for r in figures]
        c = Counter(v for v in vals if v is not None)
        distinct_values[f] = len(c)
        modal_share[f] = round(c.most_common(1)[0][1] / n, 4) if c and n else None
    degenerate = sorted(f for f, s in modal_share.items() if s is not None and s >= 0.9)

    controls = None
    if (CORPUS / "vlm_controls.json").exists():
        controls = json.loads((CORPUS / "vlm_controls.json").read_text(encoding="utf-8"))
    consistency_data = None
    if CONSISTENCY.exists():
        consistency_data = json.loads(CONSISTENCY.read_text(encoding="utf-8"))

    papers = sorted({r.get("paper") for r in figures if r.get("paper")})
    out = {
        "n_figures_labelled": n,
        "n_papers": len(papers),
        "models": sorted({r.get("model") for r in figures if r.get("model")}),
        "json_parse_rate": round(parse_ok / n, 4) if n else None,
        "n_parse_failures": n - parse_ok,
        "null_ratio_overall": overall_null,
        "n_null_values": total_nulls,
        "n_field_slots": n * len(FIELDS),
        "null_ratio_per_field": per_field_null,
        "fields_never_null": sorted(f for f, v in per_field_null.items() if v == 0.0),
        "distinct_values_per_field": distinct_values,
        "modal_share_per_field": modal_share,
        "degenerate_fields": degenerate,
        "column_width_vs_geometry": {
            "n_all": len(geo_rows),
            "n_attributable": len(attributable),
            "n_model_matches_geometry": geo_agree,
            "agreement_on_attributable": (round(geo_agree / len(attributable), 4)
                                          if attributable else None),
            "n_unambiguous": len(unambiguous),
            "n_unambiguous_agree": unamb_agree,
            "agreement_on_unambiguous": (round(unamb_agree / len(unambiguous), 4)
                                         if unambiguous else None),
            "note": ("agreement_on_unambiguous is the honest measure: it counts only figures whose "
                     "measured width maps to exactly one column under the instruction the model "
                     "was given. The other figures have no column to be right or wrong about."),
        },
        "controls": controls,
        "consistency": consistency_data,
        "elapsed_s_total": round(sum(r.get("latency_s", 0) for r in figures), 1),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    # A field at 0 % null over a real batch is the fabrication smell: these fields are genuinely
    # hard to determine from a crop, so a model that is never uncertain is not seeing, it is
    # answering. Flag it rather than let it pass as data.
    suspect = [f for f, v in per_field_null.items() if v == 0.0]
    out["fabrication_watch"] = {
        "fields_at_zero_null": suspect,
        "degenerate_fields": degenerate,
        "interpretation": (
            "A field with 0 nulls over %d figures was answered every time; a field whose modal "
            "value covers >=90 %% of figures carries almost no information even when it does "
            "abstain sometimes. Together with the control result these say whether the model was "
            "seeing or answering. Check `controls` before using these labels as evidence." % n),
    }
    REPORT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    print("figures labelled      : %d  (%d papers)" % (n, len(papers)))
    print("models                : %s" % ", ".join(out["models"]))
    print("JSON parse rate       : %.1f %%  (%d failures)"
          % (100 * out["json_parse_rate"], n - parse_ok))
    print("null ratio overall    : %.1f %%  (%d of %d field slots)"
          % (100 * overall_null, total_nulls, n * len(FIELDS)))
    print("fields never null     : %s" % (suspect or "none"))
    print("degenerate fields     : %s" % (degenerate or "none"))
    print("column width          : %s/%s on unambiguous widths (%s)"
          % (out["column_width_vs_geometry"]["n_unambiguous_agree"],
             out["column_width_vs_geometry"]["n_unambiguous"],
             out["column_width_vs_geometry"]["agreement_on_unambiguous"]))
    if consistency_data:
        print("consistency (10%%)     : overall %s | decided-only %s"
              % (consistency_data["overall_field_agreement"],
                 consistency_data["agreement_excluding_both_null"]))
    if controls:
        n_dec = sum(1 for c in controls["controls"] if c["declined"])
        print("controls declined     : %d/%d" % (n_dec, len(controls["controls"])))
    print("written: %s" % REPORT)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        print("subcommands: render | controls | label | consistency | report | all")
        return 0
    cmd = argv[1]
    model = DEFAULT_MODEL
    if "--model" in argv:
        model = argv[argv.index("--model") + 1]
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else None
    force = "--force" in argv
    per_paper = int(argv[argv.index("--per-paper") + 1]) if "--per-paper" in argv else 1

    if cmd == "render":
        return render()
    if cmd == "controls":
        made = make_controls()
        print("control images: %d" % len(made))
        for m in made:
            print("  %-26s %s" % (m["image"], m["why"]))
        return 0
    if cmd == "label":
        return label(model, limit, force, per_paper)
    if cmd == "consistency":
        return consistency(model)
    if cmd == "report":
        return report()
    if cmd == "all":
        rc = render()
        if rc:
            return rc
        make_controls()
        rc = label(model, limit, force, per_paper)
        run_controls(model)
        consistency(model)
        return report()
    print("unknown subcommand: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
