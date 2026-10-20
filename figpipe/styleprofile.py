"""Measure a figure's GRAPHIC STYLE from its own vector objects, without a vision model.

WHY THIS EXISTS
    The peer projects in this space (FigMirror, NaturePanelForge, ChartCoder, DeTi*k*Zify)
    all reconstruct a figure from its RASTER: a model looks at a picture and guesses fonts,
    colours, line weights and positions. That is the only option for a screenshot, and it is
    why those systems need a second model as judge, an "aesthetic library", a preserve list
    and an iteration cap -- the measurement itself is uncertain and not reproducible.

    A published PDF does not have that problem. It carries the type sizes, fonts, stroke
    widths, fill colours and geometry as objects. figpipe already audits a rendered PDF for
    compliance; this module turns the same source into a measured style PROFILE that a
    template can be generated from and scored against. Same input, same numbers, no GPU, no
    API call, no judge model.

WHAT IS MEASURED
    page size and aspect, the text-size histogram, font names, panel letters (8 pt single
    glyphs), stroke/fill palette (named against Okabe-Ito with an RGB distance), line widths,
    full-span horizontal/vertical rules (grid and spines).

    Deliberately NOT measured: anything requiring interpretation ("is this elegant", "which
    panel is the key panel"). Those stay judgement calls; this module only measures.

HONEST LIMITS
    * RGB Euclidean distance is not a perceptual delta-E; it is labelled as RGB distance.
    * A figure region inside a journal page can be located only approximately: pass an
      explicit bbox when exactness matters (the corpus's caption-anchored records have them).
    * A raster-only source cannot be profiled this way; `from_pdf` reads text and vector
      objects, so the numbers are exact for vector sources and undefined for images.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import asdict, dataclass, field

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: The Okabe-Ito palette, as RGB triples. Used to NAME the colours a figure uses; a colour that
#: is not near any of them keeps its hex and is reported as off-palette.
OKABE_RGB = {
    "black": (0, 0, 0),
    "orange": (230, 159, 0),
    "sky_blue": (86, 180, 233),
    "bluish_green": (0, 158, 115),
    "yellow": (240, 228, 66),
    "blue": (0, 114, 178),
    "vermillion": (213, 94, 0),
    "reddish_purple": (204, 121, 167),
}

MM_PER_PT = 25.4 / 72.0


def _require_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:  # pragma: no cover
        try:
            import fitz
            return fitz
        except ImportError:  # pragma: no cover
            return None


def _rgb(value):
    """Accept '#rrggbb', a 3-sequence of 0-1 floats, or a packed int; return 0-255 triple."""
    if value is None:
        return None
    if isinstance(value, str) and value.startswith("#"):
        h = value.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    if isinstance(value, (tuple, list)) and len(value) == 3:
        return tuple(int(round(float(c) * 255)) for c in value)
    if isinstance(value, int):
        return ((value >> 16) & 255, (value >> 8) & 255, value & 255)
    return None


def _hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _nearest_okabe(rgb):
    best, best_d = None, 1e9
    for name, ref in OKABE_RGB.items():
        d = math.dist(rgb, ref)
        if d < best_d:
            best, best_d = name, d
    return best, round(best_d, 1)


@dataclass
class StyleProfile:
    """A measured graphic style. Every field is a number read from the source PDF."""
    source: str = ""
    region: str = "page"
    width_mm: float = 0.0
    height_mm: float = 0.0
    n_text_spans: int = 0
    sizes_pt: list[float] = field(default_factory=list)
    fonts: dict[str, int] = field(default_factory=dict)
    panel_letters: list[dict] = field(default_factory=list)
    colours: list[dict] = field(default_factory=list)
    line_widths_pt: list[float] = field(default_factory=list)
    rules_h: int = 0
    rules_v: int = 0
    spines: dict[str, bool] = field(default_factory=dict)
    #: "vector" profiles carry exact type sizes; "image" profiles (raster references from a
    #: benchmark) carry only palette, aspect and ink density. The comparison renormalises over
    #: whatever both sides actually measured instead of pretending a size distribution exists.
    modality: str = "vector"
    ink_density: float = 0.0
    #: Raster-only measurements: a picture shows tick marks, stroke thickness and glyph shapes.
    tick_direction: str | None = None
    serif_guess: bool | None = None
    stroke_px: float | None = None

    # ---- construction -------------------------------------------------------------
    @classmethod
    def from_pdf(cls, pdf_path, page: int = 1, bbox_pt=None, caption_prefix=None,
                 source: str | None = None) -> "StyleProfile":
        """Profile a page region.

        `bbox_pt` is (x0, y0, x1, y1) in PDF points. Without it, `caption_prefix` finds the
        caption and profiles the column area above it; without either, the whole page.
        """
        pymupdf = _require_pymupdf()
        if pymupdf is None:
            raise RuntimeError("PyMuPDF is required to profile a PDF: pip install pymupdf")
        doc = pymupdf.open(str(pdf_path))
        try:
            page_obj = doc[page - 1]
            rect, label = _resolve_region(page_obj, bbox_pt, caption_prefix)
            prof = cls._extract(page_obj, rect)
            prof.source = source or str(pdf_path)
            prof.region = label
            return prof
        finally:
            doc.close()

    @classmethod
    def _extract(cls, page, rect) -> "StyleProfile":
        prof = cls()
        prof.width_mm = round(rect.width * MM_PER_PT, 1)
        prof.height_mm = round(rect.height * MM_PER_PT, 1)
        sizes: list[float] = []
        fonts: dict[str, int] = {}
        for block in page.get_text("dict", clip=rect).get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    size = round(float(span.get("size", 0)), 2)
                    sizes.append(size)
                    name = span.get("font", "?")
                    fonts[name] = fonts.get(name, 0) + 1
                    # a panel letter is a BOLD 8 pt single glyph. Without the bold test the
                    # axis label "y" (7 pt, regular) is indistinguishable from a panel letter,
                    # and the profile would claim letters a figure does not have.
                    font = span.get("font", "")
                    bold = bool(int(span.get("flags", 0)) & 16) or "bold" in font.lower()
                    if len(text) == 1 and text.isalpha() and 7.0 <= size <= 9.5 and bold:
                        x0, y0, _x1, _y1 = span["bbox"]
                        prof.panel_letters.append({
                            "char": text, "size_pt": size,
                            "x_mm": round((x0 - rect.x0) * MM_PER_PT, 1),
                            "y_mm": round((y0 - rect.y0) * MM_PER_PT, 1)})
        prof.sizes_pt = sizes
        prof.fonts = dict(sorted(fonts.items(), key=lambda kv: -kv[1]))
        prof.n_text_spans = len(sizes)

        colour_counts: dict[str, int] = {}
        widths: list[float] = []
        rules_h = rules_v = 0
        drawings = page.get_drawings()
        # Spines are judged against the INK extent, not the page edge: profiling a full page
        # would otherwise report no spines at all, because the axes sit inside the margins.
        _ink = _union_rect([d["rect"] for d in drawings if d.get("rect") and _intersects(d["rect"], rect)])
        for path in drawings:
            r = path.get("rect")
            if r is None or not _intersects(r, rect):
                continue
            for key in ("color", "fill"):
                rgb = _rgb(path.get(key))
                if rgb is not None:
                    colour_counts[_hex(rgb)] = colour_counts.get(_hex(rgb), 0) + 1
            w = path.get("width")
            if w:
                widths.append(round(float(w), 2))
            for item in path.get("items", []):
                if item[0] == "l":
                    p1, p2 = item[1], item[2]
                    dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                    # a long line ON the region edge is a spine, not a grid rule; counting it
                    # as a rule would report every matplotlib axes as "has gridlines"
                    if dx > 0.8 * rect.width and dy < 1.0:
                        if not (abs(p1.y - rect.y0) < 1.5 or abs(p1.y - rect.y1) < 1.5):
                            rules_h += 1
                    if dy > 0.8 * rect.height and dx < 1.0:
                        if not (abs(p1.x - rect.x0) < 1.5 or abs(p1.x - rect.x1) < 1.5):
                            rules_v += 1
        prof.line_widths_pt = widths
        prof.rules_h, prof.rules_v = rules_h, rules_v
        prof.spines = _spine_flags(drawings, rect)
        prof.colours = []
        for h, n in sorted(colour_counts.items(), key=lambda kv: -kv[1]):
            name, dist = _nearest_okabe(_rgb(h))
            prof.colours.append({"hex": h, "count": n, "okabe": name,
                                 "rgb_distance": dist})
        return prof

    @classmethod
    def from_image(cls, image_path, max_colours: int = 24) -> "StyleProfile":
        """Profile a RASTER reference (PNG/JPEG): palette, aspect, ink density.

        Exact type sizes and stroke widths cannot be recovered from pixels without OCR/vision,
        so this profile is explicitly `modality="image"` and `compare()` only uses the shared
        components. It exists because authoritative benchmarks such as PlotTwin-Bench publish
        their references as images; measuring palette and aspect is still deterministic.
        """
        try:
            from PIL import Image
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Pillow is required to profile an image: pip install Pillow") from exc
        im = Image.open(str(image_path)).convert("RGB")
        w, h = im.size
        arr = np.asarray(im)
        ink = float(np.any(arr < 245, axis=2).mean())
        # DOMINANT COLOURS, taken from the actual pixels. Adaptive palette quantisation was
        # scrambling them: it reported light blues and greys for a figure whose ink is #262626,
        # #000000 and #2a7ab9, so nothing matched the reference palette and the official palette
        # dimension scored 0.47 while looking "measured".
        flat = arr.reshape(-1, 3)
        uniq, counts = np.unique(flat, axis=0, return_counts=True)
        # collapse near-duplicates: antialiasing produces thousands of shades of the same ink
        keep_idx = np.argsort(-counts)
        chosen: list[np.ndarray] = []
        for i in keep_idx:
            rgb = uniq[i].astype(int)
            if all(c > 245 for c in rgb):
                continue                       # page white
            if any(int(np.abs(rgb - c).sum()) < 24 for c in chosen):
                continue                       # within a rounding step of an already-kept colour
            chosen.append(rgb)
            if len(chosen) >= max_colours * 3:
                break
        colours = np.array(chosen, dtype=int) if chosen else np.zeros((0, 3), dtype=int)
        counts = np.array([counts[keep_idx[i]] for i in range(len(chosen))], dtype=int)
        order = np.argsort(-counts)
        total = float(w * h)
        out = []
        for i in order:
            rgb = tuple(int(c) for c in colours[i])
            n = int(counts[i])
            if n < 0.004 * total:
                continue
            if all(c > 240 for c in rgb):        # page white
                continue
            name, dist = _nearest_okabe(rgb)
            out.append({"hex": _hex(rgb), "count": n, "okabe": name,
                        "rgb_distance": dist})
            if len(out) >= max_colours:
                break
        prof = cls(source=str(image_path), region="image", modality="image",
                   ink_density=round(ink, 4), colours=out)
        # width/height in PIXELS: only their ratio is used, and compare() documents the unit
        prof.width_mm = float(w)
        prof.height_mm = float(h)
        return prof

    @classmethod
    def from_image_detailed(cls, image_path, max_colours: int = 24) -> "StyleProfile":
        """Profile a raster reference, including the LINE structure a picture still shows.

        WHY THIS EXISTS
            `from_image` recovers palette and aspect only. The official PlotTwin-Bench code channel
            also scores grid, spines, tick direction, serif and legend frame, which are code
            constructs -- but a rendered picture still shows GRID LINES and SPINES as long straight
            runs of ink. Detecting them is ordinary image analysis, not vision-model guessing, and
            it is the difference between a candidate that can only copy colours and one that can
            reproduce the reference's structure.

        Method (deterministic):
            * binarise to ink
            * find rows/columns whose ink fraction exceeds a threshold and whose run is long:
              those are horizontal/vertical RULES
            * rules near the ink bounding box edge are SPINES; interior rules are GRID
        """
        try:
            from PIL import Image
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Pillow is required: pip install Pillow") from exc
        prof = cls.from_image(image_path, max_colours=max_colours)
        im = Image.open(str(image_path)).convert("L")
        arr = np.asarray(im, dtype=np.uint8)
        ink = arr < 200
        h, w = ink.shape
        if h < 8 or w < 8 or not ink.any():
            prof.rules_h = prof.rules_v = 0
            prof.spines = {}
            return prof
        ys, xs = np.where(ink)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        span_h, span_v = max(1, x1 - x0), max(1, y1 - y0)

        # A RULE is not "a dense row": a dense skymap or heatmap has almost every row dense, so a
        # density threshold finds hundreds of "rules". A rule is a row that is dense while its
        # NEIGHBOURS are not -- local contrast. Measured on real references: a dense field gives
        # 2 rows / 0 cols above 0.25 contrast, a sparse line figure gives 0.40 / 0.36.
        def _rules(profile_1d, min_contrast: float = 0.25) -> list[int]:
            """Rows/columns that are locally denser than their neighbourhood.

            EDGE CORRECTION IS MANDATORY. `np.convolve(mode="same")` divides by the FULL kernel
            even where it runs off the ends, so the first and last few entries of a UNIFORM signal
            come out as large "contrast" (measured: 0.444 on a solid black image). Without this
            correction a blank or noisy image reports edge "rules", and therefore four spines it
            does not have -- a fabricated structural claim.
            """
            n = len(profile_1d)
            if n < 9:
                return []
            kernel = np.ones(9) / 9.0
            local = np.convolve(profile_1d, kernel, mode="same")
            # recompute the edges with the truncated window that actually applies there
            half = 4
            for i in range(min(half, n)):
                local[i] = profile_1d[max(0, i - half):i + half + 1].mean()
                local[n - 1 - i] = profile_1d[n - 1 - i - half:
                                              min(n, n - i + half)].mean()
            contrast = profile_1d - local
            return [int(i) for i in np.where(contrast > min_contrast)[0]]

        row_ink = ink.mean(axis=1)
        col_ink = ink.mean(axis=0)
        h_rules = _rules(row_ink)
        v_rules = _rules(col_ink)
        edge = max(2, int(round(0.02 * max(span_h, span_v))))
        spines = {"left": False, "right": False, "top": False, "bottom": False}
        interior_h = interior_v = 0
        for y in h_rules:
            if abs(y - y0) <= edge:
                spines["top"] = True
            elif abs(y - y1) <= edge:
                spines["bottom"] = True
            else:
                interior_h += 1
        for x in v_rules:
            if abs(x - x0) <= edge:
                spines["left"] = True
            elif abs(x - x1) <= edge:
                spines["right"] = True
            else:
                interior_v += 1
        prof.rules_h, prof.rules_v = interior_h, interior_v
        prof.spines = spines

        # TICK DIRECTION: with a detected spine, ticks outside it put ink in the margin beyond,
        # inside it put ink in the plot area. Compared on the left spine only, where the margin is
        # usually clean.
        direction = None
        if spines.get("left"):
            band = max(2, int(round(0.01 * span_h)))
            outside = float(ink[y0:y1 + 1, max(0, x0 - band):x0].mean()) if x0 > band else 0.0
            inside = float(ink[y0:y1 + 1, x0 + 1:min(w, x0 + 1 + band)].mean())
            if max(outside, inside) > 0.01:
                direction = "out" if outside > inside else "in"
        prof.tick_direction = direction

        # STROKE WIDTH: the modal run length of a thin horizontal ink run, in pixels. This is a
        # PIXEL measurement and must be converted at the image's own dpi to become points; the
        # conversion is deliberately left to the caller, which knows the dpi.
        # A stroke is THIN. Filled areas (a heatmap cell, a bar) produce runs of hundreds of
        # pixels; including them makes the "stroke width" a measure of the densest region, which
        # is why the first attempt reported 688 px on a skymap. Only runs under 12 px are strokes.
        widths = []
        for y in np.where(row_ink > 0.15)[0][:60]:
            run = 0
            for v in ink[y]:
                if v:
                    run += 1
                elif run:
                    if run <= 12:
                        widths.append(run)
                    run = 0
            if 0 < run <= 12:
                widths.append(run)
        prof.stroke_px = float(np.median(widths)) if widths else None
        return prof

    # ---- serialisation ------------------------------------------------------------
    def to_dict(self) -> dict:
        d = asdict(self)
        d["summary"] = self.summary()
        return d

    def save(self, path) -> pathlib.Path:
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
                     encoding="utf-8")
        return p

    @classmethod
    def load(cls, path) -> "StyleProfile":
        d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        d.pop("summary", None)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    # ---- description --------------------------------------------------------------
    def summary(self) -> dict:
        s = np.asarray(self.sizes_pt) if self.sizes_pt else np.array([])
        return {
            "width_mm": self.width_mm, "height_mm": self.height_mm,
            "n_text_spans": self.n_text_spans,
            "size_min_pt": round(float(s.min()), 2) if s.size else None,
            "size_median_pt": round(float(np.median(s)), 2) if s.size else None,
            "size_max_pt": round(float(s.max()), 2) if s.size else None,
            "n_sizes": int(len(set(self.sizes_pt))),
            "panel_letters": "".join(sorted(lt["char"] for lt in self.panel_letters)),
            "dominant_colours": [c["hex"] for c in self.colours[:5]],
            "line_width_median_pt": round(float(np.median(self.line_widths_pt)), 2)
            if self.line_widths_pt else None,
            "rules_h": self.rules_h, "rules_v": self.rules_v,
            "spines": self.spines,
        }


def _intersects(a, b) -> bool:
    return not (a.x1 < b.x0 or a.x0 > b.x1 or a.y1 < b.y0 or a.y0 > b.y1)


def _union_rect(rects):
    if not rects:
        return None
    x0 = min(r.x0 for r in rects); y0 = min(r.y0 for r in rects)
    x1 = max(r.x1 for r in rects); y1 = max(r.y1 for r in rects)
    class _R:  # minimal duck-typed rect
        pass
    r = _R(); r.x0, r.y0, r.x1, r.y1 = x0, y0, x1, y1
    r.width, r.height = x1 - x0, y1 - y0
    return r


def _spine_flags(drawings, region) -> dict[str, bool]:
    """Which sides of the region carry a long axis line.

    Judged by LENGTH and by which quarter of the region the line sits in, not by coincidence
    with the region edge: a full page profile puts the axes inside the margins, and a bar panel
    starts its first bar to the right of the y axis, so an edge-match test finds nothing.
    """
    v_lines, h_lines = [], []
    for path in drawings:
        r = path.get("rect")
        if r is None or not _intersects(r, region):
            continue
        for item in path.get("items", []):
            if item[0] != "l":
                continue
            p1, p2 = item[1], item[2]
            if abs(p2.x - p1.x) < 1.0 and abs(p2.y - p1.y) > 0.5 * region.height:
                v_lines.append(p1.x)
            if abs(p2.y - p1.y) < 1.0 and abs(p2.x - p1.x) > 0.5 * region.width:
                h_lines.append(p1.y)
    w, h = region.width, region.height
    return {
        "left": any(x <= region.x0 + 0.25 * w for x in v_lines),
        "right": any(x >= region.x0 + 0.75 * w for x in v_lines),
        "top": any(y <= region.y0 + 0.25 * h for y in h_lines),
        "bottom": any(y >= region.y0 + 0.75 * h for y in h_lines),
    }


def _resolve_region(page, bbox_pt, caption_prefix):
    """Figure region: an explicit bbox, or the column above a caption."""
    pymupdf = _require_pymupdf()
    if bbox_pt is not None:
        return pymupdf.Rect(*bbox_pt), f"bbox:{tuple(round(v, 1) for v in bbox_pt)}"
    if not caption_prefix:
        return page.rect, "page"
    found = None
    for block in page.get_text("dict").get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if caption_prefix in span.get("text", "") and found is None:
                    found = span["bbox"]
    if found is None:
        raise ValueError(f"caption {caption_prefix!r} not found on this page; pass bbox_pt")
    x0, _, x1, _ = found
    return pymupdf.Rect(x0, page.rect.y0, x1, found[1] - 2), \
        f"above:{caption_prefix!r}"


# --------------------------------------------------------------------------------------
# From measurement to template: turning a profile into style settings
# --------------------------------------------------------------------------------------

#: The submission band. A measured reference may sit outside it (journals render larger); the
#: transfer clamps into the band rather than copying the reference out of spec.
BAND = (5.0, 7.0)


def palette_from_profile(profile: "StyleProfile", n: int = 4) -> list[str]:
    """The reference's own colours, most-used first, without white/background greys.

    Used for series colours when the target style is a specific paper. The colours are copied
    from the measurement, not invented: that is the whole point of profiling a vector source.
    """
    out: list[str] = []
    for c in profile.colours:
        rgb = _rgb(c["hex"])
        if rgb is None:
            continue
        r, g, b = rgb
        if r > 240 and g > 240 and b > 240:        # page white
            continue
        if abs(r - g) < 6 and abs(g - b) < 6 and r > 200:   # light grey band
            continue
        if c["hex"] in out:
            continue
        out.append(c["hex"])
        if len(out) >= n:
            break
    return out


def style_from_profile(profile: "StyleProfile", columns: float = 2.0,
                       height_mm: float | None = None,
                       canvas_mm: float | None = None) -> dict:
    """Derive a compliant, ready-to-use style from a measured profile.

    Returns `rc` (matplotlib rcParams), `palette`, and `height_mm` (the reference's own aspect,
    clamped into 120-170 mm). Every number is traceable: the font tier comes from the measured
    median clamped into 5-7 pt, the palette from the measured colours, the height from the
    measured width/height. This is the step that turns "we measured a style" into "we can use it".
    """
    import numpy as np
    sizes = sorted(profile.sizes_pt)
    median = float(np.median(sizes)) if sizes else 6.0
    base = min(max(round(median * 2) / 2, BAND[0]), BAND[1])     # half-point tier
    label = min(max(round((median + 0.25) * 2) / 2, BAND[0]), BAND[1])
    tick = min(max(base - 0.5, BAND[0]), BAND[1])
    widths = sorted(profile.line_widths_pt)
    lw = float(np.median(widths)) if widths else 0.5
    rc = {"font.size": base, "axes.labelsize": label, "axes.titlesize": BAND[1],
          "xtick.labelsize": tick, "ytick.labelsize": tick,
          "legend.fontsize": tick, "axes.linewidth": round(lw, 2),
          "xtick.major.width": round(lw, 2), "ytick.major.width": round(lw, 2)}
    height = height_mm
    if height is None and profile.width_mm and profile.height_mm:
        # THE CANVAS MATTERS. The reference's aspect is a property of the reference; the height
        # that reproduces it depends on the width the CANDIDATE will be drawn at. Deriving the
        # height from a hard-coded 183 mm and then drawing a 89 mm single-column figure makes the
        # aspect wrong by ~2x -- which is exactly what the benchmark caught on Field 2D tasks
        # (aspect component 0.75 for every one of them, vs 0.001 for two-column Line tasks).
        width = canvas_mm if canvas_mm is not None else (183.0 if columns == 2.0 else 89.0)
        aspect = profile.width_mm / profile.height_mm
        height = min(max(round(width / aspect, 1), 60.0), 170.0)
    return {"rc": rc, "palette": palette_from_profile(profile),
            "height_mm": height, "source": profile.source}


# --------------------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------------------

#: Weights of the style distance. Explicit, because a single blended "style score" hides which
#: property is off -- the per-property details are always returned alongside it.
WEIGHTS = {"sizes": 0.30, "palette": 0.25, "letters": 0.15, "lines": 0.10,
           "rules": 0.10, "aspect": 0.10}


def _size_distance(a: "StyleProfile", b: "StyleProfile") -> float:
    """Wasserstein-1 between the two size distributions, normalised by 2 pt.

    WHY NOT A HISTOGRAM: a 1-pt bin cannot see a 6.0 -> 6.5 change (both fall in [6,7)), so the
    first style-transfer run improved six pages to an identical distance -- the metric, not the
    figure, was blind to the difference. A continuous CDF distance is monotone in the shift and
    does not depend on where the bin boundaries happen to land.
    """
    if not a.sizes_pt or not b.sizes_pt:
        raise ValueError("both profiles need text sizes to be comparable")
    grid = np.linspace(4.0, 12.0, 401)
    ca = np.searchsorted(np.sort(a.sizes_pt), grid, side="right") / len(a.sizes_pt)
    cb = np.searchsorted(np.sort(b.sizes_pt), grid, side="right") / len(b.sizes_pt)
    w1 = float(np.sum(np.abs(ca - cb)) * (grid[1] - grid[0]))
    return min(1.0, w1 / 2.0)


def _size_hist(profile, bins=None) -> np.ndarray:
    # ONE-POINT BINS, deliberately. Half-point bins made a 6.44 pt reference and a 6.0 pt
    # candidate look almost disjoint (total variation 0.84), which is a property of the bin
    # boundaries rather than of the styles. The distance should be readable as "these are close".
    if bins is None:
        bins = np.arange(4.0, 12.01, 1.0)
    return np.histogram(profile.sizes_pt, bins=bins)[0].astype(float)


def compare(a: StyleProfile, b: StyleProfile) -> dict:
    """A zero-to-one style distance (0 = identical distributions) with its components.

    The components are deliberately simple and monotone rather than learned: a score whose
    direction cannot be explained is useless for driving a template, and driving templates is
    what this module exists for.
    """
    details: dict[str, float] = {}
    if a.sizes_pt and b.sizes_pt:
        details["sizes"] = _size_distance(a, b)

    def _palette(a, b):
        ca = [(c["hex"], c["count"]) for c in a.colours]
        cb = [(c["hex"], c["count"]) for c in b.colours]
        if not ca or not cb:
            return 1.0
        total = sum(n for _, n in ca)
        acc = 0.0
        for hex_a, n in ca:
            ra = _rgb(hex_a)
            d = min(math.dist(ra, _rgb(hex_b)) for hex_b, _ in cb)
            acc += (n / total) * (d / 441.67)             # max RGB distance normalised
        return acc

    if a.panel_letters or b.panel_letters:
        la = [lt["size_pt"] for lt in a.panel_letters]
        lb = [lt["size_pt"] for lt in b.panel_letters]
        letter_sizes = abs((np.mean(la) if la else 0.0) - (np.mean(lb) if lb else 0.0)) / 4.0
        letter_counts = abs(len(la) - len(lb)) / max(len(la), len(lb), 1)
        details["letters"] = min(1.0, 0.5 * letter_sizes + 0.5 * letter_counts)

    if a.line_widths_pt and b.line_widths_pt:
        wa = float(np.median(a.line_widths_pt))
        wb = float(np.median(b.line_widths_pt))
        details["lines"] = min(1.0, abs(math.log((wa + 0.1) / (wb + 0.1)))
                               / math.log(5.0))

    if a.spines and b.spines:
        grid_a = (a.rules_h > 0) or (a.rules_v > 0)
        grid_b = (b.rules_h > 0) or (b.rules_v > 0)
        spine_mismatch = sum(1 for k in a.spines
                             if a.spines.get(k) != b.spines.get(k)) / 4.0
        details["rules"] = min(1.0, 0.7 * float(grid_a ^ grid_b) + 0.3 * spine_mismatch)

    if a.colours and b.colours:
        details["palette"] = _palette(a, b)

    if a.width_mm and a.height_mm and b.width_mm and b.height_mm:
        # the SHAPE, not the width: two figures of the same width but 183x168 vs 184x154 have
        # visibly different compositions
        ra = a.width_mm / a.height_mm
        rb = b.width_mm / b.height_mm
        details["aspect"] = min(1.0, abs(math.log(ra / rb)))

    if a.ink_density > 0 and b.ink_density > 0:
        details["ink"] = min(1.0, abs(a.ink_density - b.ink_density) / 0.5)

    if not details:
        raise ValueError("profiles share no measurable component")
    weight_sum = sum(WEIGHTS.get(k, 0.10) for k in details)
    score = sum(WEIGHTS.get(k, 0.10) * v for k, v in details.items()) / weight_sum
    return {"distance": round(float(score), 3),
            "details": {k: round(float(v), 3) for k, v in details.items()},
            "a": a.summary(), "b": b.summary()}
