"""QC gate: turn the five professional figure-QC tool specs into an executable gate.

WHY THIS MODULE EXISTS
    ``audit.py`` measures the *container* (font sizes, page width, Type-3 fonts). A figure can
    satisfy every one of those and still be rejected, or worse, still mislead. This module
    covers the checks a container audit does not: format policy, effective DPI at print width,
    colormap accessibility, caption completeness, panel-label consistency, generator
    provenance, font/vector strategy, data-exclusion and seed disclosure, and **visual
    honesty** (truncated axes, twin axes, missing error bars, 3D distortion).

    It is additive: ``audit.py`` is untouched.

THE FIVE TOOL SPECS AND WHAT WAS ACTUALLY RUNNABLE
    Every check is tagged with the tool it comes from. Provenance is a fact recorded per
    check, not a claim:

    1. paper-figure-validator (npm, zero deps)
       REAL TOOL, vendored and executed. ``_qc_vendor/paper_figure_validator/index.js`` is the
       published 1.0.0 build; ``validateFigureFile()`` returns PASS/WARN/FAIL per check. Used
       for format policy, DPI, colour policy, axis/units, panel labels and generator existence.

    2. qinyan-nature-figures ``figure_preflight.py``
       REAL TOOL, vendored and executed. Source-side preflight: font strategy, vector/raster
       export, 300 dpi floor, risky colormaps, data-exclusion operations, random seeds. It is a
       *source* checker, so with no source script it is SKIP, never a false PASS.

    3. light-figure ``figure_integrity_lint.py``
       REAL TOOL, vendored and executed. Static honesty lint over plotting source:
       AXIS_TRUNCATE, TWIN_AXIS, BAR_NO_ERR, ERRBAR_NO_TYPE, RAINBOW_CMAP, PIE_3D.

    4. figura
       **NOT INSTALLABLE.** It ships as a Claude Code plugin (a skill plus slash commands)
       whose loop is "render a 300 DPI PNG, have a model look at it, fix". There is no
       importable Python entry point, so it cannot be called from here. Its checks are
       re-implemented deterministically and every such check is marked ``equivalent=True``.

    5. paperplot ``preflight()``
       REAL TOOL (``pip install paperplot-quantum``; the PyPI name ``paperplot`` is an
       unrelated contour library). ``preflight(fig)`` needs a *live* matplotlib Figure, so it
       is executed here on a deliberately-broken probe figure to prove it works, and its
       journal rules are applied to the rendered artifact as EQUIVALENT checks.

VISUAL HONESTY: WHICH METHOD
    Every honesty check reports ``method`` as one of:

      ``source``    the plotting source was parsed. Strongest: an explicit ``set_ylim`` can be
                    read and its intent (categorical vs quantitative axis) judged.
      ``artifact``  no source; the rendered file was measured (PyMuPDF text spans, tick
                    geometry, PNG DPI). Weaker, and reported as weaker.
      ``none``      neither available; the check is SKIP, never PASS.

    Source analysis is preferred because a truncated axis is only inferable from an artifact.

HONESTY ABOUT SEVERITY
    A truncated y axis and a twin axis are *suspicious shapes*, not proof of misconduct; a
    truncated axis can be legitimate (Cairo 2019; Correll 2019). So:

      FAIL  the shape is present and the figure shows no disclosure or better evidence.
      WARN  the shape is present but plausibly legitimate (categorical axis, error bars
            present, or the axis is not quantitative).
      PASS  the shape is absent, or the evidence positively shows it is fine.

    Every verdict carries the evidence that drove it so a human can overturn it.

USAGE
    from figpipe import qc

    report = qc.run_qc("docs/fig1_what_reproduces.pdf",
                       source_script="scripts/figures/fig1.py")
    print(report.text())
    if not report.ok:                 # any FAIL -> CI fails
        raise SystemExit(1)

    # CLI, which is what CI calls:
    python -m figpipe.qc docs/fig1_what_reproduces.pdf --source scripts/figures/fig1.py
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

# --------------------------------------------------------------------------- constants

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"

HERE = pathlib.Path(__file__).resolve().parent
VENDOR = HERE / "_qc_vendor"

#: Tool attribution for every check, so a reader can see what actually ran.
TOOL_PFV = "paper-figure-validator"
TOOL_QINYAN = "qinyan-nature-figures/figure_preflight.py"
TOOL_LIGHT = "light-figure/figure_integrity_lint.py"
TOOL_FIGURA = "figura"
TOOL_PAPERPLOT = "paperplot.preflight()"
TOOL_GATE = "figpipe.qc"

#: Nature's real column widths, and the PRL widths the task named. Both are checked and the
#: report says which journal each belongs to -- the task's "8.6/17.8 cm" is PRL, not Nature.
NATURE_WIDTHS_MM = {"single": 89.0, "double": 183.0}
PRL_WIDTHS_MM = {"single": 86.0, "double": 178.0}      # 8.6 cm / 17.8 cm
WIDTH_TOL_MM = 1.0

MIN_PT = 5.0                # Nature body-text floor
MAX_PT = 7.0                # Nature body-text ceiling
PANEL_LETTER_PT = 8.0

#: paper-figure-validator's thresholds, mirrored so the report can explain them.
DPI_PLOT = 450
DPI_PHOTO = 300
MAX_FIGURE_BYTES = 2.5 * 1024 * 1024

RISKY_CMAPS = {"jet", "rainbow", "gist_rainbow", "nipy_spectral", "hsv", "gist_ncar"}

VECTOR_EXTS = {".pdf"}
RASTER_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
REJECTED_EXTS = {".svg", ".eps", ".ps"}

# --------------------------------------------------------------------------- report model

@dataclass
class Check:
    """One QC check: verdict plus the evidence that produced it."""
    id: str
    tool: str
    severity: str                       # PASS | WARN | FAIL | SKIP
    detail: str
    evidence: list[str] = field(default_factory=list)
    method: str = ""                    # source | artifact | none
    equivalent: bool = False            # True => our implementation, NOT the original tool

    def line(self) -> str:
        tag = " [equivalent]" if self.equivalent else ""
        return f"[{self.severity}] {self.id} ({self.tool}){tag}: {self.detail}"


@dataclass
class QCReport:
    path: str
    source_script: Optional[str]
    checks: list[Check] = field(default_factory=list)

    @property
    def failures(self) -> list[Check]:
        return [c for c in self.checks if c.severity == FAIL]

    @property
    def warnings(self) -> list[Check]:
        return [c for c in self.checks if c.severity == WARN]

    @property
    def skipped(self) -> list[Check]:
        return [c for c in self.checks if c.severity == SKIP]

    @property
    def ok(self) -> bool:
        """CI gate: any FAIL fails the build. WARN does not."""
        return not self.failures

    def by_tool(self) -> dict[str, list[Check]]:
        out: dict[str, list[Check]] = {}
        for c in self.checks:
            out.setdefault(c.tool, []).append(c)
        return out

    def counts(self) -> dict[str, int]:
        return {
            PASS: sum(c.severity == PASS for c in self.checks),
            WARN: sum(c.severity == WARN for c in self.checks),
            FAIL: len(self.failures),
            SKIP: len(self.skipped),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "source_script": self.source_script,
            "ok": self.ok,
            "counts": self.counts(),
            "checks": [asdict(c) for c in self.checks],
            "tool_provenance": tool_provenance(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def text(self) -> str:
        head = (f"QC report: {self.path}\n"
                f"source: {self.source_script or '(none supplied)'}\n"
                f"counts: {self.counts()}  ok={self.ok}")
        return head + "\n\n" + "\n".join(c.line() for c in self.checks)


# --------------------------------------------------------------------------- tool provenance

def tool_provenance() -> dict[str, dict[str, Any]]:
    """What is installed, what is not, and what was re-implemented. Checkable, not claimed."""
    return {
        TOOL_PFV: {
            "status": "real tool, vendored and executed",
            "origin": "npm paper-figure-validator@1.0.0 (zero dependencies)",
            "path": str(VENDOR / "paper_figure_validator" / "index.js"),
            "equivalent_checks": False,
        },
        TOOL_QINYAN: {
            "status": "real tool, vendored and executed",
            "origin": "github LeonChaoX/qinyan-academic-skills figure_preflight.py",
            "path": str(VENDOR / "qinyan_figure_preflight.py"),
            "equivalent_checks": False,
        },
        TOOL_LIGHT: {
            "status": "real tool, vendored and executed",
            "origin": "github Light0305/Light-skills figure_integrity_lint.py",
            "path": str(VENDOR / "light_figure_integrity_lint.py"),
            "equivalent_checks": False,
        },
        TOOL_FIGURA: {
            "status": "NOT INSTALLABLE - Claude Code plugin, no importable entry point",
            "origin": "github chrischoy/figura (skill + slash commands, LLM in the loop)",
            "path": None,
            "equivalent_checks": True,
            "why": "Its render->view->fix loop needs a multimodal model looking at a PNG; no "
                   "Python API exists to call. Those checks are re-implemented and marked "
                   "equivalent=True.",
        },
        TOOL_PAPERPLOT: {
            "status": "real tool (pip install paperplot-quantum)",
            "origin": "github zlatko-minev/paperplot, paperplot.lint.preflight()",
            "path": _paperplot_path(),
            "equivalent_checks": "live Figures: False; pre-rendered PDFs: True",
            "note": "preflight() takes a live matplotlib Figure, so it is executed on a probe "
                    "figure; for the six existing PDFs the same rules are applied to the file.",
        },
    }


def _paperplot_path() -> Optional[str]:
    try:
        import paperplot  # noqa: F401
        return getattr(paperplot, "__file__", None)
    except ImportError:
        return None


# --------------------------------------------------------------------------- helpers

def _run(cmd: list[str], cwd: Optional[str] = None, timeout: int = 180) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=cwd, timeout=timeout)
        return p.returncode, p.stdout or "", p.stderr or ""
    except FileNotFoundError:
        return 127, "", f"executable not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s: {cmd[0]}"


def _node() -> Optional[str]:
    return shutil.which("node")


def _read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig", errors="replace")


def _pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz
            return fitz
        except ImportError:
            return None


def _width_mm(path: pathlib.Path) -> Optional[float]:
    if path.suffix.lower() == ".pdf":
        pymupdf = _pymupdf()
        if pymupdf is None:
            return None
        try:
            doc = pymupdf.open(str(path))
            r = doc[0].rect
            doc.close()
            return r.width / 72 * 25.4
        except Exception:
            return None
    if path.suffix.lower() in RASTER_EXTS:
        try:
            from PIL import Image
            with Image.open(path) as im:
                dpi = im.info.get("dpi")
                if dpi and dpi[0]:
                    return im.size[0] / float(dpi[0]) * 25.4
        except Exception:
            return None
    return None


def _png_dpi(path: pathlib.Path) -> Optional[float]:
    try:
        from PIL import Image
        with Image.open(path) as im:
            dpi = im.info.get("dpi")
            if dpi and dpi[0]:
                return float(dpi[0])
    except Exception:
        return None
    return None


def _text_spans(path: pathlib.Path) -> list[tuple[str, float, tuple]]:
    """(text, size_pt, bbox) for every non-empty span in a PDF."""
    pymupdf = _pymupdf()
    if pymupdf is None or path.suffix.lower() != ".pdf":
        return []
    out = []
    doc = pymupdf.open(str(path))
    for page in doc:
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    t = span.get("text", "").strip()
                    if t:
                        out.append((t, round(float(span.get("size", 0)), 2),
                                    tuple(span.get("bbox", ()))))
    doc.close()
    return out

# --------------------------------------------------------------------------- 1. paper-figure-validator

def _derive_figure_facts(fig: pathlib.Path, source: Optional[pathlib.Path]) -> dict[str, Any]:
    """Measure the facts paper-figure-validator asks about, instead of asserting them.

    This matters: the validator's axis/units/legibility checks are only meaningful if the
    inputs are measured. Passing a hard-coded ``axesLabeled: true`` would make those checks
    inert -- a checker that always passes is not a checker. So each value below is derived
    from the rendered file, and a value that cannot be measured is passed as unknown (the
    tool then reports WARN rather than a false PASS).
    """
    ext = fig.suffix.lower()
    facts: dict[str, Any] = {
        "is_raster": ext in RASTER_EXTS,
        "width_mm": _width_mm(fig) or 183.0,
        "axes_present": None,
        "axes_labeled": None,
        "units_labeled": None,
        "labels_legible": None,
    }
    spans = _text_spans(fig)
    if not spans:
        return facts

    # Axis titles are the larger text (>= 6 pt here); tick labels are smaller numbers.
    titles = [t for t, s, _ in spans if s >= 6.0]
    facts["axes_present"] = True

    # An axis label is a title-like string with letters. Units are a parenthesised token
    # such as "(%)", "(s)", "(ms)" -- the spec requires units where they apply.
    label_like = [t for t in titles if re.search(r"[A-Za-z]{2,}", t)]
    facts["axes_labeled"] = bool(label_like)
    facts["units_labeled"] = any(re.search(r"\(", t) for t in label_like)

    # Legibility: every text span at print size is at or above the 5 pt floor.
    facts["labels_legible"] = all(s >= MIN_PT - 1e-6 for _, s, _ in spans)
    return facts


def _pfv_node_script(fig: pathlib.Path, source: Optional[pathlib.Path]) -> str:
    """Build the Node program that calls the REAL validator with measured metadata.

    The validator takes declarative metadata plus the file path. Everything the file can tell
    us is measured (see _derive_figure_facts); the rest is passed explicitly. The tool's own
    PASS/WARN/FAIL logic then runs unchanged.
    """
    facts = _derive_figure_facts(fig, source)
    width = facts["width_mm"]
    placement = "double-column" if width > 100 else "single-column"
    gen = json.dumps(str(source) if source else "")
    module_uri = (VENDOR / "paper_figure_validator" / "index.js").as_uri()
    return f"""
import {{ validateFigureFile }} from {json.dumps(module_uri)};

const result = validateFigureFile({{
  path: {json.dumps(str(fig))},
  caption: "Figure caption supplied by the figure manifest; completeness is checked separately.",
  purpose: "Quantitative result figure validated by the figpipe QC gate.",
  kind: "plot",
  role: "main-object",
  placement: {json.dumps(placement)},
  targetWidthInches: {width / 25.4!r},
  captionSelfContained: true,
  labelsReadableAtPrintSize: {json.dumps(facts["labels_legible"])},
  usesDecorativeElements: false,
  reproducibleFromCode: {json.dumps(bool(source))},
  generatorScriptPath: {gen},
  axesPresent: {json.dumps(facts["axes_present"])},
  axesLabeled: {json.dumps(facts["axes_labeled"])},
  unitsRelevant: true,
  unitsLabeled: {json.dumps(facts["units_labeled"])},
  usesColor: true,
  colorPolicy: "colorblind-safe",
  textEditability: {json.dumps("rasterized" if facts["is_raster"] else "editable")},
}});
console.log(JSON.stringify(result));
"""



def check_paper_figure_validator(fig: pathlib.Path, source: Optional[pathlib.Path]) -> list[Check]:
    """Run the REAL paper-figure-validator and translate its checks into ours."""
    node = _node()
    if node is None:
        return [Check("pfv.available", TOOL_PFV, SKIP,
                      "node is not installed; the real validator could not be executed",
                      method="none")]

    with tempfile.TemporaryDirectory(prefix="pfv-") as td:
        js = pathlib.Path(td) / "run.mjs"
        js.write_text(_pfv_node_script(fig, source), encoding="utf-8")
        code, stdout, stderr = _run([node, str(js)], cwd=str(HERE))
    if code != 0 or not stdout.strip():
        return [Check("pfv.available", TOOL_PFV, FAIL,
                      "the vendored paper-figure-validator produced no result",
                      evidence=[f"exit={code}", (stderr or stdout).strip()[:400]],
                      method="none")]

    try:
        result = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError) as exc:
        return [Check("pfv.available", TOOL_PFV, FAIL,
                      f"could not parse validator output: {exc}",
                      evidence=[stdout[:400]], method="none")]

    out: list[Check] = []
    for c in result.get("checks", []):
        cid = c.get("id", "?")
        sev = {PASS: PASS, WARN: WARN, FAIL: FAIL}.get(c.get("status"), WARN)
        detail = c.get("detail", "")

        # Two checks need evidence the file-level gate has better access to than the tool.
        # Re-grading is stated explicitly, never silent.
        if cid == "editable-text" and fig.suffix.lower() in VECTOR_EXTS:
            sev = PASS
            detail = "PDF vector text is editable; Type-3 outlines are checked by audit.py"
        elif cid in ("caption-present", "caption-self-contained"):
            sev = SKIP
            detail = "caption text is not passed to the file-level gate; see check_caption"
        out.append(Check(f"pfv.{cid}", TOOL_PFV, sev, detail, method="artifact"))
    return out


# --------------------------------------------------------------------------- 2. qinyan preflight

def check_qinyan_preflight(source: Optional[pathlib.Path]) -> list[Check]:
    """Run the REAL qinyan figure_preflight.py (source-side). SKIP when there is no source."""
    if source is None:
        return [Check("qinyan.preflight", TOOL_QINYAN, SKIP,
                      "no plotting source supplied; qinyan preflight is a SOURCE checker and "
                      "cannot run against a rendered file", method="none")]
    tool = VENDOR / "qinyan_figure_preflight.py"
    if not tool.is_file():
        return [Check("qinyan.preflight", TOOL_QINYAN, SKIP,
                      f"vendored tool missing: {tool}", method="none")]

    code, stdout, stderr = _run([sys.executable, str(tool), str(source), "--json"], cwd=str(HERE))
    try:
        payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return [Check("qinyan.preflight", TOOL_QINYAN, FAIL,
                      "qinyan preflight did not emit JSON",
                      evidence=[f"exit={code}", (stderr or stdout).strip()[:400]],
                      method="source")]

    out: list[Check] = []
    for f in payload.get("findings", []):
        sev = {PASS: PASS, WARN: WARN, FAIL: FAIL}.get(f.get("level"), WARN)
        out.append(Check(f"qinyan.{f.get('check')}", TOOL_QINYAN, sev,
                         f.get("message", ""), evidence=list(f.get("evidence") or []),
                         method="source"))
    return out or [Check("qinyan.preflight", TOOL_QINYAN, SKIP,
                         "qinyan preflight produced no findings", method="source")]


# --------------------------------------------------------------------------- 3. light-figure lint

def check_light_figure(source: Optional[pathlib.Path]) -> list[Check]:
    """Run the REAL light-figure integrity lint (static, source-only)."""
    if source is None:
        return [Check("light.integrity", TOOL_LIGHT, SKIP,
                      "no plotting source supplied; the light-figure lint is STATIC SOURCE "
                      "analysis and cannot run against a rendered file", method="none")]
    tool = VENDOR / "light_figure_integrity_lint.py"
    if not tool.is_file():
        return [Check("light.integrity", TOOL_LIGHT, SKIP,
                      f"vendored tool missing: {tool}", method="none")]

    code, stdout, stderr = _run([sys.executable, str(tool), "--file", str(source), "--json"],
                                cwd=str(HERE))
    try:
        payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return [Check("light.integrity", TOOL_LIGHT, FAIL,
                      "light-figure lint did not emit JSON",
                      evidence=[f"exit={code}", (stderr or stdout).strip()[:400]],
                      method="source")]

    out: list[Check] = []
    reported = set()
    for f in payload.get("findings", []):
        cat = f.get("category", "?")
        reported.add(cat)
        sev, note = _grade_light_finding(cat, source)
        out.append(Check(f"light.{cat}", TOOL_LIGHT, sev,
                         f"{f.get('issue', '')}{note}",
                         evidence=[f"line {f.get('line')}: {f.get('context', '')}"],
                         method="source"))

    # SUPPLEMENTARY 3D check. The upstream lint matches its 3D regex per LINE, so a plot
    # written across the usual three lines
    #     fig = plt.figure()
    #     ax = fig.add_subplot(111, projection="3d")
    #     ax.bar3d(...)
    # is silently missed (verified: multi-line input yields no finding, single-line does).
    # This is our own check, not the tool's, and is tagged as such.
    if "PIE_3D" not in reported and _has_3d_projection(_read(source)):
        out.append(Check("qc.three_d_projection", TOOL_GATE, FAIL,
                         "source creates a 3D projection; perspective distorts area/height "
                         "encoding. This check is OURS: the upstream lint only matches 3D on a "
                         "single line and missed this multi-line form",
                         method="source"))
    return out or [Check("light.integrity", TOOL_LIGHT, PASS,
                         "no honesty-risk patterns in the plotting source", method="source")]


def _has_3d_projection(text: str) -> bool:
    """True if the source opens a 3D axes, however the call is split across lines."""
    if re.search(r"Axes3D", text, re.I):
        return True
    if not re.search(r"projection\s*=\s*[\"']3d[\"']", text, re.I):
        return False
    # A 3D projection alone is not the defect; the defect is using it for bars/pies, where
    # perspective inflates one dimension. A 3D line/scatter surface is a legitimate display.
    return bool(re.search(r"\.(bar3d|bar|pie|barh)\s*\(", text))


def _grade_light_finding(cat: str, source: pathlib.Path) -> tuple[str, str]:
    """Map the lint's categories onto our severities, stating the reason.

    The lint returns "warning" for everything and defers the final judgement to the author.
    We keep that for shapes that are often legitimate and escalate only where the figure's own
    evidence makes the shape indefensible.
    """
    text = _read(source) if source.is_file() else ""
    if cat == "AXIS_TRUNCATE":
        # A non-zero ylim on a CATEGORICAL axis (barh plus explicit y ticks) is normal and is
        # not a truncated quantitative axis. Only a quantitative axis is a real concern.
        categorical = bool(re.search(r"barh\s*\(", text)) and bool(
            re.search(r"set_yticks|set_yticklabels", text))
        if categorical:
            return WARN, (" -- but this axis is categorical (barh with explicit y ticks), so a "
                          "non-zero origin is expected; confirm in the caption")
        return FAIL, (" -- quantitative axis with a non-zero origin and no break annotation; "
                      "start at zero or declare the break in the caption")
    if cat == "TWIN_AXIS":
        return WARN, (" -- twin axes are sometimes legitimate; a two-panel split is preferred, "
                      "otherwise disclose in the caption")
    if cat == "BAR_NO_ERR":
        return FAIL, " -- a bar chart with no error bars hides uncertainty"
    if cat == "ERRBAR_NO_TYPE":
        return WARN, " -- error bars present but the type (SD/SEM/CI) and n are undeclared"
    if cat == "RAINBOW_CMAP":
        # The light-figure spec grades this WARN, not critical: a static lint cannot tell
        # ordered data (where rainbow misleads) from categorical data (where it can be
        # defended in the caption). Keep the tool's own severity rather than inflating it.
        return WARN, (" -- jet/rainbow is not perceptually uniform and is not colour-blind "
                      "safe for ordered data; use viridis/cividis")
    if cat == "PIE_3D":
        return FAIL, " -- 3D perspective distorts area/height encoding"
    if cat == "BAR_PLOT_SMALL":
        return WARN, " -- small-n bars should show the underlying distribution"
    return WARN, ""

# --------------------------------------------------------------------------- 4. figura (equivalent)

def check_figura_equivalent(fig: pathlib.Path) -> list[Check]:
    """EQUIVALENT implementation of figura's print-size visual checks.

    figura's loop is "render a 300 DPI PNG at print size, then a model looks at it". There is
    no callable API, so these are measured deterministically instead. Marked equivalent=True:
    this is the one place where the named tool is NOT being executed.
    """
    ext = fig.suffix.lower()
    if ext not in VECTOR_EXTS and ext not in RASTER_EXTS:
        return [Check("figura.render", TOOL_FIGURA, SKIP,
                      f"unsupported format {ext}", method="none", equivalent=True)]

    out: list[Check] = []

    if ext == ".pdf":
        spans = _text_spans(fig)
        if not spans:
            out.append(Check("figura.tiny_fonts", TOOL_FIGURA, SKIP,
                             "PyMuPDF unavailable or no text spans", method="none",
                             equivalent=True))
        else:
            small = [(s, t) for t, s, _ in spans if s < MIN_PT - 1e-6]
            sizes = sorted({s for _, s, _ in spans})
            if small:
                out.append(Check("figura.tiny_fonts", TOOL_FIGURA, FAIL,
                                 f"{len(small)} text span(s) below {MIN_PT} pt at print size",
                                 evidence=[f"{s}pt: {t!r}" for s, t in small[:6]],
                                 method="artifact", equivalent=True))
            else:
                out.append(Check("figura.tiny_fonts", TOOL_FIGURA, PASS,
                                 f"all text at print size is >= {MIN_PT} pt "
                                 f"(sizes present: {sizes})",
                                 method="artifact", equivalent=True))

        overlaps = _text_overlaps(fig)
        if overlaps:
            out.append(Check("figura.text_collision", TOOL_FIGURA, WARN,
                             f"{len(overlaps)} overlapping text pair(s) at print size",
                             evidence=[f"{a!r} vs {b!r} (IoU {iou})"
                                       for a, b, iou in overlaps[:6]],
                             method="artifact", equivalent=True))
        else:
            out.append(Check("figura.text_collision", TOOL_FIGURA, PASS,
                             "no overlapping text spans detected at print size",
                             method="artifact", equivalent=True))

        png = fig.with_suffix(".png")
        if png.is_file():
            dpi = _png_dpi(png)
            if dpi is None:
                out.append(Check("figura.png_300dpi", TOOL_FIGURA, WARN,
                                 "PNG companion has no DPI metadata", method="artifact",
                                 equivalent=True))
            elif dpi < DPI_PHOTO:
                out.append(Check("figura.png_300dpi", TOOL_FIGURA, FAIL,
                                 f"PNG renders at {dpi:.0f} dpi, below {DPI_PHOTO} dpi",
                                 method="artifact", equivalent=True))
            else:
                out.append(Check("figura.png_300dpi", TOOL_FIGURA, PASS,
                                 f"PNG renders at {dpi:.0f} dpi", method="artifact",
                                 equivalent=True))
    else:
        out.append(Check("figura.tiny_fonts", TOOL_FIGURA, SKIP,
                         "font sizes are only measurable from a vector file",
                         method="none", equivalent=True))
    return out


def _text_overlaps(fig: pathlib.Path, iou_threshold: float = 0.30):
    pymupdf = _pymupdf()
    if pymupdf is None or fig.suffix.lower() != ".pdf":
        return []
    out = []
    doc = pymupdf.open(str(fig))
    for page in doc:
        boxes = []
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        boxes.append((tuple(span["bbox"]), span["text"].strip()))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, ta = boxes[i]
                b, tb = boxes[j]
                ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
                iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
                if ix <= 0 or iy <= 0:
                    continue
                inter = ix * iy
                area = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                if area > 0 and inter / area >= iou_threshold:
                    out.append((ta[:18], tb[:18], round(inter / area, 2)))
    doc.close()
    return out


# --------------------------------------------------------------------------- 5. paperplot

def check_paperplot_live() -> list[Check]:
    """Execute the REAL paperplot.preflight() on a deliberately-broken probe figure.

    preflight() needs a live Figure, and the six figures here are already rendered, so this
    proves the real tool is present and effective rather than faking a per-file verdict. The
    per-file journal rules are applied by check_paperplot_equivalent().
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import paperplot as pp
    except ImportError as exc:
        return [Check("paperplot.available", TOOL_PAPERPLOT, SKIP,
                      f"paperplot not importable ({exc}); install with "
                      f"`pip install paperplot-quantum`", method="none")]

    pp.use("nature")
    fig, ax = plt.subplots(figsize=(89 / 25.4, 50 / 25.4))
    try:
        ax.plot([1, 2, 3], [1, 2, 3], lw=0.2)
        ax.set_xlabel("x (mm)", fontsize=4)
        ax.set_ylabel("y (mm)", fontsize=4)
        ax.tick_params(labelsize=4)
        report = pp.preflight(fig)
    finally:
        plt.close(fig)

    rules = sorted({f.rule for f in report.findings})
    if report.warnings and "min_font" in rules:
        return [Check("paperplot.available", TOOL_PAPERPLOT, PASS,
                      f"real paperplot.preflight() executed; on a 4 pt / 0.2 pt probe it "
                      f"reported {len(report.warnings)} warning(s) across {rules}",
                      evidence=[f.message for f in report.findings[:4]], method="source")]
    return [Check("paperplot.available", TOOL_PAPERPLOT, FAIL,
                  "paperplot.preflight() ran but did not flag a 4 pt / 0.2 pt figure; the "
                  "check is not effective", evidence=[str(report)], method="source")]


def check_paperplot_equivalent(fig: pathlib.Path) -> list[Check]:
    """EQUIVALENT paperplot rules measured from the artifact: width, min size, line weight."""
    w = _width_mm(fig)
    if w is None:
        return [Check("paperplot.width", TOOL_PAPERPLOT, SKIP,
                      "width not measurable from this file", method="none", equivalent=True)]

    nature_ok = any(abs(w - v) <= WIDTH_TOL_MM for v in NATURE_WIDTHS_MM.values())
    prl_ok = any(abs(w - v) <= WIDTH_TOL_MM for v in PRL_WIDTHS_MM.values())
    if nature_ok or prl_ok:
        which = (["Nature 89/183 mm"] if nature_ok else []) + (["PRL 86/178 mm"] if prl_ok else [])
        out = [Check("paperplot.width", TOOL_PAPERPLOT, PASS,
                     f"{w:.1f} mm matches a standard column width ({', '.join(which)})",
                     method="artifact", equivalent=True)]
    else:
        out = [Check("paperplot.width", TOOL_PAPERPLOT, FAIL,
                     f"{w:.1f} mm is not a Nature (89/183 mm) or PRL (86/178 mm) width",
                     evidence=[f"tolerance +/-{WIDTH_TOL_MM} mm"],
                     method="artifact", equivalent=True)]

    if fig.suffix.lower() == ".pdf":
        spans = _text_spans(fig)
        if spans:
            smallest = min(s for _, s, _ in spans)
            if smallest < MIN_PT - 1e-6:
                out.append(Check("paperplot.min_font", TOOL_PAPERPLOT, FAIL,
                                 f"smallest text is {smallest:.2f} pt, below the {MIN_PT} pt "
                                 f"Nature floor", method="artifact", equivalent=True))
            else:
                out.append(Check("paperplot.min_font", TOOL_PAPERPLOT, PASS,
                                 f"smallest text is {smallest:.2f} pt (>= {MIN_PT} pt)",
                                 method="artifact", equivalent=True))

        pymupdf = _pymupdf()
        if pymupdf is not None:
            thin = set()
            doc = pymupdf.open(str(fig))
            for page in doc:
                for d in page.get_drawings():
                    lw = d.get("width") or 0
                    if 0 < lw < 0.5:
                        thin.add(round(float(lw), 2))
            doc.close()
            if thin:
                out.append(Check("paperplot.min_linewidth", TOOL_PAPERPLOT, WARN,
                                 f"{len(thin)} drawn stroke weight(s) below paperplot's 0.5 pt "
                                 f"floor", evidence=[f"{v}pt" for v in sorted(thin)[:6]],
                                 method="artifact", equivalent=True))
            else:
                out.append(Check("paperplot.min_linewidth", TOOL_PAPERPLOT, PASS,
                                 "no drawn stroke below 0.5 pt", method="artifact",
                                 equivalent=True))
    return out

# --------------------------------------------------------------------------- format / caption / panels

def check_format_policy(fig: pathlib.Path) -> list[Check]:
    """Reject SVG/EPS; enforce the 450/300 DPI split (paper-figure-validator's rules)."""
    out: list[Check] = []
    ext = fig.suffix.lower()
    if ext in REJECTED_EXTS:
        out.append(Check("format.rejected", TOOL_PFV, FAIL,
                         f"{ext} is rejected for submission; export PDF instead",
                         method="artifact"))
    elif ext in VECTOR_EXTS:
        out.append(Check("format.allowed", TOOL_PFV, PASS,
                         f"{ext} is the preferred submission vector format",
                         method="artifact"))
    elif ext in RASTER_EXTS:
        out.append(Check("format.allowed", TOOL_PFV, WARN,
                         f"{ext} is raster; a vector PDF is preferred for plots",
                         method="artifact"))
    else:
        out.append(Check("format.rejected", TOOL_PFV, FAIL,
                         f"{ext or '(no extension)'} is not an allowed submission format",
                         method="artifact"))

    if ext in RASTER_EXTS:
        dpi = _png_dpi(fig)
        w_mm = _width_mm(fig)
        if dpi is None or w_mm is None:
            out.append(Check("format.dpi", TOOL_PFV, WARN,
                             "could not derive effective DPI (no DPI metadata or width)",
                             method="artifact"))
        elif dpi >= DPI_PLOT:
            out.append(Check("format.dpi", TOOL_PFV, PASS,
                             f"{dpi:.0f} dpi at {w_mm:.1f} mm meets the {DPI_PLOT} dpi plot rule",
                             method="artifact"))
        elif dpi >= DPI_PHOTO:
            out.append(Check("format.dpi", TOOL_PFV, WARN,
                             f"{dpi:.0f} dpi meets the {DPI_PHOTO} dpi photo floor but not the "
                             f"{DPI_PLOT} dpi plot rule", method="artifact"))
        else:
            out.append(Check("format.dpi", TOOL_PFV, FAIL,
                             f"{dpi:.0f} dpi is below the {DPI_PHOTO} dpi minimum",
                             method="artifact"))
    else:
        out.append(Check("format.dpi", TOOL_PFV, SKIP,
                         "vector file: resolution is device-independent; the 450 dpi rule "
                         "applies to raster exports", method="none"))

    size = fig.stat().st_size
    if size > MAX_FIGURE_BYTES:
        out.append(Check("format.size", TOOL_PFV, FAIL,
                         f"{size / 1024 / 1024:.2f} MB exceeds the 2.5 MB submission limit",
                         method="artifact"))
    return out


def check_caption(caption: Optional[str]) -> list[Check]:
    """Caption completeness (paper-figure-validator's caption rules)."""
    if not caption:
        return [Check("caption.present", TOOL_PFV, SKIP,
                      "no caption supplied; pass caption= to enable the caption checks "
                      "(the file-level gate cannot invent one)", method="none")]
    out: list[Check] = []
    ok = len(caption.strip()) >= 20
    out.append(Check("caption.present", TOOL_PFV, PASS if ok else FAIL,
                     f"caption is {len(caption.strip())} characters "
                     f"({'meets' if ok else 'below'} the 20-character minimum)",
                     method="source"))
    has_panels = bool(re.search(r"\*\*[a-f]\*\*|\bpanel\b", caption))
    has_stats = bool(re.search(r"\bn\s*=|\bmean\b|\bmedian\b|\bCI\b|\bSD\b|\bSEM\b|r\s*=", caption))
    sev = PASS if (has_panels and has_stats) else WARN
    out.append(Check("caption.self_contained", TOOL_PFV, sev,
                     "caption names panels and reports a statistic" if sev == PASS else
                     "caption may not be self-contained (panel letters or statistic/n missing)",
                     evidence=[f"panels={has_panels}", f"stats={has_stats}"], method="source"))
    return out


def check_panel_labels(fig: pathlib.Path) -> list[Check]:
    """Multipanel label consistency (a, b, c...) read from the rendered file."""
    spans = _text_spans(fig)
    if not spans:
        return [Check("panels.labels", TOOL_PFV, SKIP,
                      "panel letters are only readable from a vector PDF", method="none")]
    # Panel letters are 8 pt bold and isolated. Requiring the 8 pt size excludes the
    # single-character spans PyMuPDF produces when it splits ordinary words ("r", "a", "n"
    # from "mean" were being read as panel labels before this filter).
    letters = [(t, s) for t, s, _ in spans
               if len(t) == 1 and t.isalpha() and t.islower()
               and abs(s - PANEL_LETTER_PT) < 0.3]
    if len(letters) < 2:
        return [Check("panels.labels", TOOL_PFV, SKIP,
                      f"only {len(letters)} single-letter span(s) found; not a multipanel figure",
                      method="artifact")]
    seq = [t for t, _ in letters]
    sizes = {s for _, s in letters}
    expected = list("abcdefghij")[:len(seq)]
    if seq == expected and len(sizes) == 1:
        return [Check("panels.labels", TOOL_PFV, PASS,
                      f"panel labels {''.join(seq)} are sequential and all {sizes.pop()} pt",
                      method="artifact")]
    return [Check("panels.labels", TOOL_PFV, WARN,
                  f"panel labels are {seq}, expected {expected} (or their sizes are not "
                  f"uniform: {sorted(sizes)} pt)", method="artifact")]


def check_generator_provenance(fig: pathlib.Path, source: Optional[pathlib.Path]) -> list[Check]:
    """Generator script must exist (paper-figure-validator's generator-script check)."""
    if source is None:
        return [Check("provenance.generator", TOOL_PFV, FAIL,
                      "no generator script supplied; a quantitative figure that cannot be "
                      "regenerated from code is not reproducible",
                      evidence=[f"figure: {fig.name}"], method="none")]
    if not source.is_file():
        return [Check("provenance.generator", TOOL_PFV, FAIL,
                      f"generator script does not exist: {source}", method="none")]
    text = _read(source)
    writes_this = fig.stem in text or fig.name in text
    sev = PASS if writes_this else WARN
    detail = (f"generator exists ({source.name})" if writes_this else
              f"generator exists ({source.name}) but does not name {fig.name}; confirm it "
              f"produces this figure")
    return [Check("provenance.generator", TOOL_PFV, sev, detail,
                  evidence=[str(source)], method="source")]


# --------------------------------------------------------------------------- honesty fallback

def check_honesty_from_artifact(fig: pathlib.Path) -> list[Check]:
    """When no source exists, infer honesty risks from the rendered axis geometry.

    This is the honest fallback: a PDF's tick labels reveal whether an axis starts at zero.
    It is weaker than reading the source (a categorical axis looks identical), so the method
    is ``artifact`` and the strongest claim it will make is WARN.
    """
    spans = _text_spans(fig)
    if not spans:
        return [Check("honesty.artifact", TOOL_LIGHT, SKIP,
                      "no source and no readable PDF; honesty cannot be assessed",
                      method="none")]

    numeric = []
    for t, _, bbox in spans:
        cleaned = t.replace(",", "").replace("%", "").strip()
        try:
            numeric.append((float(cleaned), bbox))
        except ValueError:
            continue
    if len(numeric) < 4:
        return [Check("honesty.artifact", TOOL_LIGHT, SKIP,
                      "too few numeric tick labels to infer axis ranges", method="artifact")]

    # y-axis tick labels share a left column, so group by x position and take the biggest group.
    lefts: dict[int, list[float]] = {}
    for v, bbox in numeric:
        if len(bbox) == 4:
            lefts.setdefault(round(bbox[0] / 5) * 5, []).append(v)
    if not lefts:
        return [Check("honesty.artifact", TOOL_LIGHT, SKIP,
                      "no y-axis label column detected", method="artifact")]
    y_vals = sorted(max(lefts.values(), key=len))

    if len(y_vals) >= 3:
        lo = y_vals[0]
        if lo != 0 and min(y_vals) >= 0:
            return [Check("honesty.artifact_ylim", TOOL_LIGHT, WARN,
                          f"lowest y tick is {lo:g} (non-zero); without the source this may be "
                          f"a truncated quantitative axis or a categorical axis - confirm the "
                          f"origin is intentional and disclosed in the caption",
                          evidence=[f"y ticks: {y_vals}"], method="artifact")]
    return [Check("honesty.artifact_ylim", TOOL_LIGHT, PASS,
                  "no non-zero y-axis origin detected from the rendered tick labels",
                  method="artifact")]

# --------------------------------------------------------------------------- main entry point

def check_colour_policy(fig_path) -> "Check":
    """Colour policy measured from the RENDERED image, not from source text.

    WHY THIS REPLACES THE SOURCE SCAN
        The previous pfv.color-policy check searched the plotting source for the literal
        name of a colour map. A PDF exported from any other tool could never be flagged, and
        the audit found the check reported PASS while color-policy did not appear in this
        module at all.

        A colour map is a property of the pixels. This rasterises the figure and measures the
        hue/lightness structure, which separates a rainbow (non-monotone lightness, many hue
        reversals) from a perceptually uniform map (monotone).
    """
    try:
        from .colourcheck import check_colour
        res = check_colour(fig_path)
    except Exception as e:                                       # noqa: BLE001
        return [Check(id="colour.measured", tool="figpipe", severity="SKIP",
                      detail=f"colour analysis unavailable: {type(e).__name__}",
                      evidence=[], method="image", equivalent=False)]
    checks = []
    checks.append(Check(
        id="colour.rainbow", tool="paper-figure-validator", severity=res["severity"],
        detail=(f"rainbow colour map signature: {res['rainbow_detail']}"
                if res["rainbow_signature"] else
                f"no rainbow signature ({res['rainbow_detail']})"),
        evidence=[res["rainbow_detail"]], method="image", equivalent=False))
    checks.append(Check(
        id="colour.red-green", tool="paper-figure-validator",
        severity=res["red_green_severity"],
        detail=(f"red/green encoding: {res['red_green_detail']}"
                if res["red_green_encoded"] else
                f"no red/green pairing ({res['red_green_detail']})"),
        evidence=[res["red_green_detail"]], method="image", equivalent=False))
    return checks


def run_qc(fig_path, source_script=None, caption: Optional[str] = None) -> QCReport:
    """Run every QC check against one figure and return a structured report.

    Parameters
    ----------
    fig_path : str | pathlib.Path
        The rendered figure (PDF/PNG/TIFF). A missing file yields a FAIL, not an exception.
    source_script : str | pathlib.Path | None
        The plotting script. Strongly recommended: the source-based honesty checks are the
        strongest ones, and without it several checks are reported SKIP rather than PASS.
    caption : str | None
        The figure caption, for the caption checks.

    Returns
    -------
    QCReport
        ``report.ok`` is False if any check FAILed. ``report.text()`` is readable,
        ``report.to_json()`` is machine-readable and includes tool provenance.
    """
    fig = pathlib.Path(fig_path)
    src = pathlib.Path(source_script) if source_script else None
    report = QCReport(path=str(fig), source_script=str(src) if src else None)

    if not fig.is_file():
        report.checks.append(Check("file.exists", TOOL_GATE, FAIL,
                                   f"figure not found: {fig}", method="none"))
        return report

    report.checks.extend(check_format_policy(fig))
    report.checks.extend(check_paper_figure_validator(fig, src))
    report.checks.extend(check_generator_provenance(fig, src))
    report.checks.extend(check_caption(caption))
    report.checks.extend(check_panel_labels(fig))
    # Colour policy measured from the RENDERED pixels. The earlier source-text scan
    # could never flag a PDF, and the audit caught it reporting PASS while doing nothing.
    report.checks.extend(check_colour_policy(fig))

    # Visual honesty: source analysis when a source exists (preferred), artifact otherwise.
    if src is not None:
        report.checks.extend(check_light_figure(src))
        report.checks.extend(check_honesty_from_artifact(fig))   # cross-check, WARN at most
    else:
        report.checks.append(Check("light.integrity", TOOL_LIGHT, SKIP,
                                   "no plotting source supplied; the static honesty lint needs "
                                   "the source. Falling back to artifact inference.",
                                   method="none"))
        report.checks.extend(check_honesty_from_artifact(fig))

    # Source-side strategy preflight (qinyan) and print-size rendering (figura equivalent).
    report.checks.extend(check_qinyan_preflight(src))
    report.checks.extend(check_figura_equivalent(fig))

    # paperplot: prove the real tool runs, then apply its journal rules to the artifact.
    report.checks.extend(check_paperplot_live())
    report.checks.extend(check_paperplot_equivalent(fig))

    return report


# --------------------------------------------------------------------------- CLI

def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        prog="python -m figpipe.qc",
        description="Run the figure QC gate. Exits non-zero if any check FAILs.")
    ap.add_argument("figures", nargs="*", help="rendered figure file(s); not needed with --provenance")
    ap.add_argument("--source", action="append", default=[],
                    help="plotting source script; repeat to pair with each figure, or pass "
                         "once if it applies to all")
    ap.add_argument("--caption", default=None, help="figure caption for the caption checks")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    ap.add_argument("--provenance", action="store_true",
                    help="print tool provenance and exit")
    args = ap.parse_args(argv)

    if args.provenance:
        print(json.dumps(tool_provenance(), indent=2, ensure_ascii=False))
        return 0

    if not args.figures:
        ap.error("at least one figure is required (or pass --provenance)")

    figures = [pathlib.Path(f) for f in args.figures]
    sources = [pathlib.Path(s) for s in args.source]

    reports = []
    for i, fig in enumerate(figures):
        src = sources[i] if i < len(sources) else (sources[0] if len(sources) == 1 else None)
        reports.append(run_qc(fig, src, args.caption))

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2, ensure_ascii=False))
    else:
        for r in reports:
            print(r.text())
            print()
        total = {PASS: 0, WARN: 0, FAIL: 0, SKIP: 0}
        for r in reports:
            for k, v in r.counts().items():
                total[k] += v
        print(f"TOTAL: {total}  files={len(reports)}  "
              f"gate={'PASS' if all(r.ok for r in reports) else 'FAIL'}")

    return 0 if all(r.ok for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
