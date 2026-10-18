# NOTICE — PlotTwin-Bench scorer, deterministic code channel

## Origin

- Dataset / benchmark: **figmirror/PlotTwin-Bench**
  <https://huggingface.co/datasets/figmirror/PlotTwin-Bench>
- Paper: *FigMirror: Ground It, Code It, Plot It* (arXiv:2608.28814)
- Files copied **unmodified** from `scorer/plottwin_scorer/`:
  - `color.py` (sRGB → CIELAB → CIEDE2000)
  - `deviation_defect.py` (the code channel: `score_code_deviation`, `extract_style_features`)

## What was NOT copied

The upstream package also contains:

- `vlm.py` and `score_vlm_defects()` — the vision channel (65 % of the official score), which
  requires an OpenAI-compatible client and a model the upstream chose.
- `cli.py` — the end-to-end runner, which drives both channels.

figpipe vendors **only the deterministic code channel**. Reasons, in order:

1. It is the part this project can actually run and reproduce offline.
2. It is 35 % of the official score, and the official formula is documented upstream
   (`S = 0.35 · S_code + 0.65 · S_vision`), so a code-channel number can be reported **as a code
   channel number** without implying the combined score.
3. Vendoring the vision half would imply a score we cannot recompute; the project's standing rule is
   that a control which cannot be re-run is not a control.

## Licence

The benchmark artefact (dataset card and scorer) is **CC BY-NC 4.0 — non-commercial**.
Consequences applied in this repository:

- the vendored files are used for **local evaluation only** and are **not** part of the published
  wheel (`pyproject.toml` excludes `third_party/`);
- no benchmark data (reference images, target tables) is redistributed — only metric reports;
- `__init__.py` here is written by figpipe and exposes only the two deterministic functions.

If you reuse this repository commercially, delete `third_party/plottwin_scorer/` first: nothing
else in figpipe depends on it, and the benchmark report degrades to the project's own
`styleprofile` metric.

## Modification status

`color.py` and `deviation_defect.py` are byte-identical to upstream. The only file authored here is
`__init__.py`, which omits the vision imports so the package can be imported without `openai`.
