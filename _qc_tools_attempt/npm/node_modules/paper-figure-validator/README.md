# paper-figure-validator

Validate academic paper figures for journal submission quality.

Zero external dependencies. Only uses `node:fs` and `node:path`.

## What it checks

- **Format** — PDF, PNG, JPEG, TIFF only (SVG/EPS rejected)
- **File size** — must be ≤ 2.5 MB
- **Vector vs raster** — plots, heatmaps, diagrams prefer PDF; raster requires justification
- **DPI** — raster figures must meet minimum DPI at declared target width (450 DPI for plots/heatmaps, 300 DPI for photos)
- **PNG/JPEG dimensions** — read directly from binary headers, no image library needed
- **Caption** — must be present and self-contained (≥ 20 chars)
- **Purpose** — must state a clear purpose (no decorative figures)
- **Color policy** — must declare colorblind-safe, redundant-encoding, or monochrome policy when color is used
- **Rainbow/jet colormaps** — rejected
- **Red/green-only encoding** — rejected
- **Axis labels** — required for plots, comparisons, heatmaps
- **Units** — required when relevant
- **Reproducibility** — quantitative figures must be reproducible from code
- **Generator script** — if declared, must exist on disk
- **Multipanel labels** — must be consistent when `multipanel: true`
- **Scale bar** — required when `requiresScaleBar: true`

Each check returns `PASS`, `WARN`, or `FAIL` with a human-readable detail message.

## Install

```bash
npm install paper-figure-validator
```

## Usage

```typescript
import { validateFigureFile, formatFigureValidationResult } from 'paper-figure-validator';

const result = validateFigureFile({
  path: 'figures/fig-01-convergence.pdf',
  caption: 'Convergence of the iterative solver as a function of iteration count for three regularization values.',
  purpose: 'Shows that the method converges within 50 iterations for all tested parameters.',
  kind: 'plot',
  role: 'main-object',
  placement: 'single-column',
  captionSelfContained: true,
  labelsReadableAtPrintSize: true,
  usesDecorativeElements: false,
  reproducibleFromCode: true,
  generatorScriptPath: 'scripts/fig01.py',
  axesPresent: true,
  axesLabeled: true,
  unitsRelevant: true,
  unitsLabeled: true,
});

if (!result.ok) {
  console.error(formatFigureValidationResult(result));
  process.exit(1);
}
```

### Result structure

```typescript
{
  verdict: 'PASS' | 'WARN' | 'FAIL',
  ok: boolean,            // true when no FAIL checks
  fileExists: boolean,
  fileSizeBytes?: number,
  widthPx?: number,       // PNG/JPEG only
  heightPx?: number,
  effectiveDpi?: number,
  checks: Array<{
    id: string,
    label: string,
    status: 'PASS' | 'WARN' | 'FAIL',
    detail: string,
  }>,
  failures: string[],     // FAIL check labels + details
  warnings: string[],     // WARN check labels + details
}
```

### Input reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | `string` | ✓ | Path to the figure file (relative to `cwd` or absolute) |
| `caption` | `string` | ✓ | Full figure caption |
| `purpose` | `string` | ✓ | What the figure shows and why it matters |
| `kind` | `FigureKind` | ✓ | `plot`, `heatmap`, `diagram`, `photo`, `screenshot`, … |
| `role` | `FigureRole` | ✓ | `main-object`, `comparison`, `method`, … |
| `placement` | `FigurePlacement` | — | `single-column`, `double-column`, `full-width` |
| `targetWidthInches` | `number` | — | Override default width for DPI check |
| `captionSelfContained` | `boolean` | ✓ | Caption can be understood without reading the paper |
| `labelsReadableAtPrintSize` | `boolean` | ✓ | All text is legible at final print size |
| `usesDecorativeElements` | `boolean` | ✓ | Has cosmetic elements that carry no information |
| `reproducibleFromCode` | `boolean` | — | Figure can be regenerated from a script |
| `generatorScriptPath` | `string` | — | Path to the generator script |
| `axesPresent` | `boolean` | — | Required for `plot`, `comparison`, `heatmap` |
| `axesLabeled` | `boolean` | — | Required for `plot`, `comparison`, `heatmap` |
| `unitsRelevant` | `boolean` | — | Whether units apply |
| `unitsLabeled` | `boolean` | — | Axes include units |
| `usesColor` | `boolean` | — | Figure uses color |
| `colorPolicy` | `ColorPolicy` | — | `colorblind-safe`, `redundant-encoding`, `monochrome`, … |
| `usesRainbowOrJet` | `boolean` | — | Uses rainbow/jet colormap (always FAIL) |
| `usesRedGreenOnly` | `boolean` | — | Uses red/green-only color encoding (always FAIL) |
| `multipanel` | `boolean` | — | Figure has multiple panels |
| `panelLabelsConsistent` | `boolean` | — | Panel labels follow a consistent scheme (a, b, c…) |
| `requiresScaleBar` | `boolean` | — | A scale bar is required (e.g. microscopy) |
| `scaleBarPresent` | `boolean` | — | Scale bar is present |
| `rasterJustification` | `string` | — | Why raster is used instead of vector (converts FAIL → WARN) |
| `textEditability` | `TextEditability` | — | `editable`, `rasterized`, `unknown` |

## License

MIT
