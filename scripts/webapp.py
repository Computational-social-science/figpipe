"""A local web interface: upload a CSV, get an audited publication figure.

WHY THIS EXISTS
    AutoFigure (ResearAI/AutoFigure, ICLR 2026) ships a Next.js frontend and a Flask API. A
    researcher uses it without a terminal. figpipe had `scripts/make_figure.py` -- a command line --
    and its README led with a shell command.

    For a tool whose stated objective is "reusable in research scenarios", that is a barrier
    AutoFigure decided was worth removing and this project had not. `PEER_AUTOFIGURE.md` names it as
    the one thing figpipe should be embarrassed about. This file removes it.

WHAT IT IS
    A single-process FastAPI app serving one HTML page and a small JSON API:

        GET  /                  the page
        GET  /api/health        liveness, so a script can wait for it
        POST /api/inspect       upload a CSV, get the inferred intent and the column list
        POST /api/make          upload a CSV + options, get the PDF and a quality report
        GET  /api/file/{name}   fetch a generated file (PDF or PNG preview)

WHAT IT DELIBERATELY DOES NOT DO
    * No accounts, no database, no cloud. It binds to 127.0.0.1 and is meant for one researcher on
      one machine.
    * No LLM. Every number it shows comes from the same deterministic code the CLI runs, so the web
      page cannot claim anything the pipeline cannot prove.
    * It does not hide a refusal. An ambiguous table returns the reason and the column list, exactly
      as the CLI does -- a web page that swallows a refusal is worse than no web page.

USAGE
    python scripts/webapp.py                 # http://127.0.0.1:8099
    python scripts/webapp.py --port 9000
"""
from __future__ import annotations

import argparse
import base64
import io
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse  # noqa: E402
import pandas as pd  # noqa: E402

from figpipe import audit, quality, skills, spec, styleprofile  # noqa: E402

#: Generated figures live here for the process lifetime. A temp dir, not the repo: a web session
#: must not leave artefacts in a git working tree.
OUT_DIR = pathlib.Path(tempfile.mkdtemp(prefix="figpipe-web-"))

COLUMN_WIDTHS = {"1": 89.0, "2": 183.0}
COLUMNS_ENUM = {"1": 1.0, "2": 2.0}

app = FastAPI(title="figpipe", docs_url=None, redoc_url=None)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>figpipe - publication figures from your data</title>
<style>
 body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:880px;margin:40px auto;
      padding:0 20px;color:#1a1a1a}
 h1{font-size:24px;margin-bottom:4px} .sub{color:#666;margin-bottom:28px}
 fieldset{border:1px solid #ddd;border-radius:8px;padding:16px 18px;margin-bottom:18px}
 legend{font-weight:600;padding:0 6px}
 label{display:block;margin:10px 0 4px;font-weight:500;font-size:14px}
 input,select{font:inherit;padding:7px 9px;border:1px solid #ccc;border-radius:6px;width:100%;
              box-sizing:border-box}
 button{font:inherit;font-weight:600;padding:10px 20px;border:0;border-radius:7px;
        background:#1f6feb;color:#fff;cursor:pointer;margin-top:6px}
 button:disabled{background:#9db8dd;cursor:default}
 pre{background:#f6f8fa;padding:14px;border-radius:8px;overflow-x:auto;font-size:13px;white-space:pre-wrap}
 .ok{color:#127a2e;font-weight:600} .bad{color:#b3261e;font-weight:600}
 img{max-width:100%;border:1px solid #e5e5e5;border-radius:8px;margin-top:12px}
 .hint{color:#666;font-size:13px;margin-top:2px}
</style></head><body>
<h1>figpipe</h1>
<div class="sub">Upload a tidy CSV. Get a Nature-width figure, verified by reading the rendered file
back. Nothing is sent anywhere &mdash; this runs on your machine.</div>

<form id="f">
 <fieldset><legend>1. Your data</legend>
  <label for="csv">CSV (one row per observation)</label>
  <input type="file" id="csv" name="csv" accept=".csv" required>
  <div class="hint">Any column names. The pipeline infers what to draw, or tells you why it cannot.</div>
 </fieldset>

 <fieldset><legend>2. The figure</legend>
  <label for="columns">Nature column width</label>
  <select id="columns" name="columns">
   <option value="2" selected>183 mm (double column)</option>
   <option value="1">89 mm (single column)</option>
  </select>

  <label for="facet">Facet column (optional &mdash; one panel per level)</label>
  <input type="text" id="facet" name="facet" placeholder="e.g. condition">

  <label for="value">Value column (needed with a facet)</label>
  <input type="text" id="value" name="value" placeholder="e.g. score">

  <label for="reference">Reference figure (optional &mdash; transfer its style)</label>
  <input type="file" id="reference" name="reference" accept=".pdf,.png,.jpg,.jpeg">
 </fieldset>

 <button id="go" type="submit">Make the figure</button>
</form>

<div id="out"></div>

<script>
const f = document.getElementById('f'), out = document.getElementById('out'),
      go = document.getElementById('go');
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  go.disabled = true; out.innerHTML = '<p>Working...</p>';
  const fd = new FormData();
  fd.append('csv', document.getElementById('csv').files[0]);
  fd.append('columns', document.getElementById('columns').value);
  fd.append('facet', document.getElementById('facet').value);
  fd.append('value', document.getElementById('value').value);
  const ref = document.getElementById('reference').files[0];
  if (ref) fd.append('reference', ref);
  try {
    const r = await fetch('/api/make', {method: 'POST', body: fd});
    const j = await r.json();
    out.innerHTML = '';
    if (j.refused) {
      out.innerHTML = '<h3 class="bad">Refused</h3><pre>' + esc(j.reason) +
        '\\n\\ncolumns: ' + esc((j.columns||[]).join(', ')) + '</pre>';
    } else {
      let h = '<h3 class="' + (j.compliant ? 'ok' : 'bad') + '">' +
              (j.compliant ? 'Compliant' : 'Not compliant') + '</h3>';
      h += '<pre>' + esc(j.summary) + '</pre>';
      if (j.preview) h += '<img src="/api/file/' + j.preview + '" alt="figure preview">';
      if (j.pdf) h += '<p><a href="/api/file/' + j.pdf + '" download>Download the PDF</a></p>';
      out.innerHTML = h;
    }
  } catch (err) {
    out.innerHTML = '<h3 class="bad">Error</h3><pre>' + esc(String(err)) + '</pre>';
  } finally { go.disabled = false; }
});
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
</script>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


@app.get("/api/health")
def health() -> dict:
    """Liveness, so a script (or the test suite) can wait instead of sleeping."""
    return {"ok": True, "service": "figpipe", "out_dir": str(OUT_DIR)}


def _read_upload(data: bytes, name: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.BytesIO(data))
    except Exception as exc:                       # noqa: BLE001 - surfaced to the browser
        raise HTTPException(400, f"cannot parse {name}: {type(exc).__name__}: {exc}")
    if df.empty:
        raise HTTPException(400, f"{name} has no rows")
    return df


@app.post("/api/inspect")
async def inspect(csv: UploadFile = File(...)) -> JSONResponse:
    """What would be drawn, before drawing it. A user should see the decision, not just the result."""
    df = _read_upload(await csv.read(), csv.filename or "upload.csv")
    try:
        figure = spec.infer_spec(df)
    except spec.SpecError as exc:
        return JSONResponse({"refused": True, "reason": str(exc),
                             "columns": [str(c) for c in df.columns]})
    declared = figure.panels[0]
    return JSONResponse({"refused": False, "intent": declared.intent,
                         "rationale": declared.rationale,
                         "columns": [str(c) for c in df.columns]})


@app.post("/api/make")
async def make(csv: UploadFile = File(...), columns: str = Form("2"),
               facet: str = Form(""), value: str = Form(""),
               reference: UploadFile | None = File(None)) -> JSONResponse:
    """Draw the figure and return a VERIFIED result: the same audit the CLI runs.

    A web page that reports success without verifying is the defect this project exists to prevent,
    with a nicer font.
    """
    df = _read_upload(await csv.read(), csv.filename or "upload.csv")
    width_mm = COLUMN_WIDTHS.get(columns, 183.0)
    stem = OUT_DIR / f"fig_{len(list(OUT_DIR.glob('*.pdf'))) + 1:03d}"

    style_kw: dict = {}
    if reference is not None and reference.filename:
        ref_bytes = await reference.read()
        ref_path = OUT_DIR / f"ref_{stem.stem}{pathlib.Path(reference.filename).suffix or '.pdf'}"
        ref_path.write_bytes(ref_bytes)
        try:
            if ref_path.suffix.lower() == ".pdf":
                style_kw["profile"] = styleprofile.StyleProfile.from_pdf(ref_path, page=1)
            else:
                style_kw["profile"] = styleprofile.StyleProfile.from_image(ref_path)
        except Exception as exc:                   # noqa: BLE001 - surfaced
            return JSONResponse({"refused": True,
                                 "reason": f"cannot measure the reference: "
                                           f"{type(exc).__name__}: {exc}",
                                 "columns": [str(c) for c in df.columns]})

    # ---- facet path -------------------------------------------------------------------
    if facet:
        if facet not in df.columns:
            return JSONResponse({"refused": True,
                                 "reason": f"{facet!r} is not a column",
                                 "columns": [str(c) for c in df.columns]})
        if not value or value not in df.columns:
            return JSONResponse({"refused": True,
                                 "reason": "a facet needs a value column that exists",
                                 "columns": [str(c) for c in df.columns]})
        try:
            result = skills.run("faceted_distribution", df, out_stem=stem,
                                columns=COLUMNS_ENUM.get(columns, 2.0), height_mm=60.0,
                                value=value, by=facet, of="hist", **style_kw)
        except skills.SkillError as exc:
            return JSONResponse({"refused": True, "reason": str(exc),
                                 "columns": [str(c) for c in df.columns]})
        return _verified(result, width_mm)

    # ---- single-panel path ------------------------------------------------------------
    try:
        figure = spec.infer_spec(df)
    except spec.SpecError as exc:
        return JSONResponse({"refused": True, "reason": str(exc),
                             "columns": [str(c) for c in df.columns]})
    declared = figure.panels[0]
    recipe = spec.recipe_for(declared.intent)
    if recipe is None:
        return JSONResponse({"refused": True,
                             "reason": f"no recipe implements intent {declared.intent!r}",
                             "columns": [str(c) for c in df.columns]})

    skill = skills.SKILLS[recipe]
    declared_params = set(getattr(skill, "required", ()) or ()) | \
        set(getattr(skill, "optional", ()) or ())
    usable = {k: v for k, v in (declared.kwargs or {}).items() if k in declared_params}
    try:
        result = skills.run(recipe, df, out_stem=stem,
                            columns=COLUMNS_ENUM.get(columns, 2.0),
                            height_mm=width_mm * 0.5, **style_kw, **usable)
    except skills.SkillError as exc:
        return JSONResponse({"refused": True, "reason": str(exc),
                             "columns": [str(c) for c in df.columns]})
    except ValueError as exc:
        return JSONResponse({"refused": True,
                             "reason": f"this table cannot be drawn as "
                                       f"{declared.intent!r}: {exc}",
                             "columns": [str(c) for c in df.columns]})
    return _verified(result, width_mm)


def _verified(result: dict, width_mm: float) -> JSONResponse:
    """Audit the RENDERED file and report named dimensions. The same checks the CLI runs."""
    pdf = pathlib.Path(result["pdf"])
    report = audit.audit(str(pdf), expect_width_mm=width_mm, check_overlap=False)
    hard = [f for f in report["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type")]
    qrep = quality.for_skill_result(result, figure=str(pdf))

    lines = [
        f"panels: {result.get('panels', 1)}",
        f"width: {report.get('width_mm')} mm, height: {report.get('height_mm')} mm",
        f"hard findings: {len(hard)}",
    ]
    for f in hard:
        lines.append(f"  ! {f['check']}: {f['detail']}")
    if qrep["dimensions"]:
        lines.append("dimensions (worst first):")
        for d in qrep["dimensions"]:
            lines.append(f"  {d['name']:<12} {d['score']:<6} {d['band']}")
    if qrep["unmeasured"]:
        lines.append("unmeasured: " + ", ".join(f"{u['name']} ({u['why']})"
                                                for u in qrep["unmeasured"]))

    png = result.get("png")
    return JSONResponse({
        "refused": False,
        "compliant": not hard,
        "summary": "\n".join(lines),
        "pdf": pdf.name,
        "preview": pathlib.Path(png).name if png else "",
        "quality": qrep,
    })


@app.get("/api/file/{name}")
def get_file(name: str) -> FileResponse:
    """Serve a generated file. The name is resolved INSIDE OUT_DIR and must stay there.

    A path that escapes the output directory would let a crafted request read arbitrary files; the
    check is explicit rather than relying on the framework, because this is the one place a web
    surface adds an attack the CLI does not have.
    """
    safe = pathlib.Path(name).name              # strip any directory component
    path = (OUT_DIR / safe).resolve()
    if OUT_DIR.resolve() not in path.parents:
        raise HTTPException(400, "invalid file name")
    if not path.is_file():
        raise HTTPException(404, "no such file")
    return FileResponse(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Local web interface for figpipe.")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8099)
    args = ap.parse_args(argv)
    import uvicorn
    print(f"  figpipe web interface: http://{args.host}:{args.port}")
    print(f"  outputs: {OUT_DIR}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
