"""Read a rendered figure's STRUCTURE from the PDF, without a model.

WHY THIS EXISTS
    The corpus's VLM labelling pass (`corpus/vlm_report.json`, model `gemma3:12b`, 40 figures) wrote
    ten fields every single time -- and a control experiment showed what that confidence was worth.
    On three images that contain no figure at all, the model asserted 20 specific values:

        control_blank.png     7 asserted,  2 fabricated   ("column_width": "single")
        control_noise.png    15 asserted,  9 fabricated   ("high_contrast": true on random strokes)
        control_textonly.png 12 asserted,  9 fabricated

    A model that reports `column_width: single` about a blank page cannot be the ground truth for
    column width. That is why this project does not use a VLM as a judge.

    But the FIELDS it was asked about are not all unknowable. Six of the ten can be measured
    deterministically, and this module measures the two that were still missing:

        figure_type          what kind of figure the file actually contains
        panel_labels_present whether the panels are lettered (a), (b), (c)

    Both come from the PDF's own text and page geometry, so they are reproducible: the same file
    gives the same answer on every machine, and a disagreement is a bug rather than a temperature.

WHAT THIS DELIBERATELY DOES NOT DO
    It does not decide whether a figure is GOOD. `arrow_style` and the aesthetic fields remain
    unmeasured, and `quality.UNMEASURABLE` says so with a reason. Guessing them would be the VLM's
    mistake with better manners.
"""
from __future__ import annotations

import pathlib
import re

#: Panel letters as they appear in a Nature figure: (a), (A), a, A at the start of a text run.
_PANEL_LETTER = re.compile(r"(?:^|\s)\(([a-zA-Z])\)(?:\s|$)")
#: A bare single letter used as a panel marker, which is the other common convention.
_BARE_LETTER = re.compile(r"(?:^|\s)([a-zA-Z])(?=\s)")

#: Minimum number of lettered runs before we call it a multi-panel figure.
_MIN_PANELS = 2


def _reader(pdf_path: pathlib.Path):
    """Open a PDF for reading, or raise with a message a caller can act on."""
    try:
        import pypdf
    except ImportError:                            # pragma: no cover - dependency present here
        try:
            import PyPDF2 as pypdf
        except ImportError:
            raise RuntimeError("no PDF reader available (need pypdf or PyPDF2)")
    return pypdf.PdfReader(str(pdf_path))


def page_text(pdf_path) -> str:
    """All extractable text on page 1, with whitespace normalised.

    Page 1 only: a Nature figure is one page, and a multi-page PDF is either a composite or a
    mistake -- reading further would describe a different object than the one being judged.
    """
    p = pathlib.Path(pdf_path)
    if not p.is_file():
        raise FileNotFoundError(f"no such file: {p}")
    reader = _reader(p)
    if not reader.pages:
        return ""
    return " ".join((reader.pages[0].extract_text() or "").split())


def text_items(pdf_path) -> list[tuple[str, float]]:
    """(text, font_size) for every text run on page 1.

    The font SIZE is what makes panel letters findable. In a figpipe figure the letters are drawn
    above every axis label and tick, so a single-letter run at the largest size present is a panel
    letter -- while the axis label `v` sits at a smaller size and is not. Matching on text alone
    could not tell those apart.
    """
    p = pathlib.Path(pdf_path)
    if not p.is_file():
        raise FileNotFoundError(f"no such file: {p}")
    reader = _reader(p)
    items: list[tuple[str, float]] = []

    def visitor(text, cm, tm, font_dict, font_size):
        if text and text.strip():
            items.append((text.strip(), round(float(font_size or 0.0), 1)))

    reader.pages[0].extract_text(visitor_text=visitor)
    return items


def panel_labels_from_sizes(items: list[tuple[str, float]]) -> list[str]:
    """Panel letters, found by size rather than by pattern.

    A single alphabetic character at the LARGEST font size on the page is a panel letter. Anything
    at a smaller size is an axis label or a tick, whatever it spells.
    """
    if not items:
        return []
    largest = max(size for _, size in items)
    letters = []
    for text, size in items:
        if size != largest:
            continue
        if len(text) == 1 and text.isalpha():
            letters.append(text)
    # keep first appearance order, no duplicates
    seen, out = set(), []
    for letter in letters:
        if letter not in seen:
            seen.add(letter)
            out.append(letter)
    return out if len(out) >= _MIN_PANELS else []


def panel_labels(text: str) -> list[str]:
    """The panel letters present, in order of appearance, without duplicates.

    Two conventions are recognised, in order of reliability:
        (a) (b) (c)   parenthesised, the Nature house style
        a  b  c       bare letters, only counted when the parenthesised form found fewer than two
    """
    paren = [m.group(1) for m in _PANEL_LETTER.finditer(text)]
    if len(set(paren)) >= _MIN_PANELS:
        seen, out = set(), []
        for letter in paren:
            if letter not in seen:
                seen.add(letter)
                out.append(letter)
        return out
    bare = [m.group(1) for m in _BARE_LETTER.finditer(text)]
    seen, out = set(), []
    for letter in bare:
        if letter not in seen:
            seen.add(letter)
            out.append(letter)
    return out if len(out) >= _MIN_PANELS else []


def figure_type(text: str, *, n_panels: int = 1) -> str:
    """A coarse classification from the axis text the figure actually printed.

    Deliberately coarse. `bar`, `line`, `scatter`, `heatmap`, `histogram`, `other` are the classes
    the corpus's VLM was asked for, and each maps to something visible in the text layer:

        a categorical axis of short labels plus a numeric axis  -> bar
        an ordered numeric axis with a fitted trend             -> line
        two numeric axes with many points and no categories     -> scatter
        a colour bar and a matrix of cells                      -> heatmap
        a single numeric axis with a count axis                 -> histogram

    When the text does not decide it, the answer is `other` -- not a guess. The VLM's mistake was
    answering anyway.
    """
    lowered = text.lower()
    if not lowered.strip():
        return "other"
    # `density` is an AXIS LABEL on a histogram or a KDE, NOT evidence of a heatmap -- the first
    # version of this function mislabelled a 4-facet histogram as a heatmap for exactly that reason.
    # A heatmap's distinguishing feature is a colour bar, which a text-only reader cannot see, so
    # the honest answer for a matrix figure is `other` rather than a confident wrong guess.
    if re.search(r"\b(frequency|count)\b", lowered):
        return "histogram"
    if re.search(r"\bdensity\b", lowered):
        return "histogram"
    # Two long numeric runs on the axes with no category words: a scatter or a line.
    numeric_tokens = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])", text)
    words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text)
    if len(numeric_tokens) >= 12 and len(words) <= 6:
        return "scatter"
    if n_panels >= 2:
        return "other"
    if len(words) <= 12:
        return "bar"
    return "other"


def describe(pdf_path) -> dict:
    """The deterministic structural description of one rendered figure."""
    text = page_text(pdf_path)
    labels = panel_labels_from_sizes(text_items(pdf_path))
    return {
        "figure_type": figure_type(text, n_panels=max(1, len(labels))),
        "panel_labels_present": bool(labels),
        "panel_labels": labels,
        "n_panels_inferred": max(1, len(labels)),
        "arrow_style": arrow_style(pdf_path),
        "text_chars": len(text),
    }


def compare_to_vlm(pdf_path, vlm_fields: dict) -> dict:
    """Where a deterministic reading and a VLM reading of the SAME file disagree.

    This is the only honest use for a model label here: as a second opinion to be checked, not as
    an answer key. A disagreement is reported; it is never silently resolved in either direction.
    """
    ours = describe(pdf_path)
    disagreements = []
    for field in ("figure_type", "panel_labels_present"):
        if field not in vlm_fields:
            continue
        mine, theirs = ours[field], vlm_fields[field]
        if mine != theirs:
            disagreements.append({"field": field, "deterministic": mine, "vlm": theirs})
    return {"ours": ours, "disagreements": disagreements,
            "agree": not disagreements}


#: An arrowhead is a SMALL FILLED TRIANGLE: three points, closed, filled, and small relative to the
#: page. Measured from the path operators in the PDF content stream, not from pixels.
_MAX_ARROW_SIDE_PT = 12.0
_MIN_ARROW_SIDE_PT = 1.0


def _path_groups(pdf_path) -> list[tuple[list[tuple[float, float]], bool, str]]:
    """Closed/filled subpaths as (points, closed, paint-op).

    A PDF draws with `m` (move) and `l` (line) between coordinates, then paints: `S` stroke,
    `f` fill, `B` both. `h` closes the subpath. An arrowhead is a closed FILLED subpath with
    exactly three points and a small bounding box -- a bar or a box is filled too, but far larger
    or has four points.
    """
    p = pathlib.Path(pdf_path)
    if not p.is_file():
        raise FileNotFoundError(f"no such file: {p}")
    reader = _reader(p)
    data = reader.pages[0].get_contents().get_data().decode("latin-1", "replace")
    out = []
    for m in re.finditer(r"((?:[\d.\-]+\s+[\d.\-]+\s+(?:m|l)\s*)+)\s*(h?)\s*(f\*?|S|B)", data):
        coords = re.findall(r"([\d.\-]+)\s+([\d.\-]+)\s+[ml]", m.group(1))
        if len(coords) < 3:
            continue
        out.append(([(float(a), float(b)) for a, b in coords], bool(m.group(2)), m.group(3)))
    return out


def arrow_style(pdf_path) -> str:
    """How the figure draws direction: `none`, `filled_triangle` or `other`.

    WHY THIS IS DETERMINISTIC: a direction arrow needs a head, a head is a closed FILLED subpath,
    and its size separates it from a bar or a panel border. figpipe's own drawers emit `B`/`S` for
    bars and `f` for background rectangles, and no small triangles -- so for its own output the
    answer is `none`, and that is measured rather than assumed.

    WHY IT IS NOT A VLM FIELD ANY MORE: `arrow_style` was one of the two fields left for a model
    last round. It is visually decidable, which is what made it a candidate -- but it is also
    expressible as a geometric test, which is better, because the answer is reproducible.
    """
    groups = _path_groups(pdf_path)
    heads = 0
    for points, closed, paint in groups:
        # `f` fills, `B` fills AND strokes -- an arrowhead is drawn with `B` by matplotlib.
        # Testing only for "f" excluded every arrowhead, which the positive control caught.
        if not closed or paint.lower() not in ("f", "f*", "b", "b*"):
            continue
        if len(points) != 3:
            continue
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        if _MIN_ARROW_SIDE_PT <= max(w, h) <= _MAX_ARROW_SIDE_PT:
            heads += 1
    if heads:
        return "filled_triangle"
    # a stroked open path with no filled head is an annotation line, not an arrow
    return "none"


def panel_layout(result: dict) -> str:
    """The panel arrangement, read from the pipeline's own layout record -- not from the PDF.

    `panel_layout` was the last field left for a VLM. It does not need one: the layout layer
    DECIDED the grid, so the answer is already known before the figure is drawn. Reading it from
    pixels would be re-deriving a fact the caller holds.

    Returns a shape name a reader can act on:
        "single"        one panel
        "1xN"           one row
        "Nx1"           one column
        "MxN"           a grid
    """
    n = int(result.get("panels") or 1)
    if n <= 1:
        return "single"
    columns = int(round(float((result.get("layout") or {}).get("columns") or 1.0)))
    columns = max(1, min(columns, n))
    rows = (n + columns - 1) // columns
    if rows == 1:
        return f"1x{n}"
    if columns == 1:
        return f"{n}x1"
    return f"{rows}x{columns}"


def all_fields(pdf_path, result: dict | None = None) -> dict:
    """Every field the corpus's VLM was asked for, measured deterministically.

    Ten fields were asked of `gemma3:12b`, which fabricated 20 values on three control images
    containing no figure at all. All ten now have a deterministic answer:

        column_width           audit.width          (already measured)
        font_uniform           audit.font_type      (already measured)
        min_font_legible       audit.font_size      (already measured)
        panel_count            result["panels"]     (already measured)
        high_contrast          colourcheck          (already measured)
        frame_restrained       styleprofile         (already measured)
        figure_type            structure            (this module)
        panel_labels_present   structure            (this module)
        arrow_style            structure            (this module)
        panel_layout           structure.panel_layout(result)   (this module)

    `result` is the dict from `skills.run()`. Without it, panel_layout falls back to what the PDF
    can tell us -- the number of lettered panels -- which is weaker but still not a guess.
    """
    d = describe(pdf_path)
    if result is not None:
        d["panel_layout"] = panel_layout(result)
        d["panel_count"] = int(result.get("panels") or 1)
    else:
        d["panel_layout"] = "single" if d["n_panels_inferred"] <= 1 else f"1x{d['n_panels_inferred']}"
        d["panel_count"] = d["n_panels_inferred"]
    return d
