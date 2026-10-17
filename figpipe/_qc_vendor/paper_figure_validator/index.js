import { existsSync, readFileSync, statSync } from 'node:fs';
import { basename, extname, resolve } from 'node:path';
export const FIGURE_KINDS = [
    'plot',
    'comparison',
    'heatmap',
    'diagram',
    'schematic',
    'flowchart',
    'proof',
    'photo',
    'screenshot',
    'scan',
    'other',
];
export const FIGURE_ROLES = [
    'main-object',
    'comparison',
    'method',
    'phenomenon',
    'proof',
    'parameter-dependence',
    'summary',
    'other',
];
export const FIGURE_PLACEMENTS = ['single-column', 'double-column', 'full-width', 'unknown'];
export const COLOR_POLICIES = ['not-applicable', 'monochrome', 'colorblind-safe', 'redundant-encoding', 'unknown'];
export const TEXT_EDITABILITY_OPTIONS = ['editable', 'rasterized', 'unknown'];
export const VALIDATION_STATUSES = ['PASS', 'WARN', 'FAIL'];
const MAX_FIGURE_BYTES = 2.5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = new Set(['.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff']);
const RASTER_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.tif', '.tiff']);
const VECTOR_EXTENSIONS = new Set(['.pdf']);
const VECTOR_PREFERRED_KINDS = new Set(['plot', 'comparison', 'heatmap', 'diagram', 'schematic', 'flowchart', 'proof']);
const AXES_EXPECTED_KINDS = new Set(['plot', 'comparison', 'heatmap']);
const QUANTITATIVE_REPRODUCIBLE_KINDS = new Set(['plot', 'comparison', 'heatmap']);
const DEFAULT_TARGET_WIDTH_INCHES = {
    'single-column': 3.5,
    'double-column': 7.2,
    'full-width': 7.2,
    unknown: undefined,
};
function stripToolAtPrefix(value) {
    return String(value || '').trim().replace(/^@+/, '');
}
function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes < 0)
        return 'unknown size';
    if (bytes < 1024)
        return `${bytes} B`;
    if (bytes < 1024 * 1024)
        return `${(bytes / 1024).toFixed(bytes < 10 * 1024 ? 1 : 0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(bytes < 10 * 1024 * 1024 ? 2 : 1)} MB`;
}
function addCheck(checks, id, label, status, detail) {
    checks.push({ id, label, status, detail });
}
function finalizeResult(result) {
    const failures = result.checks.filter((check) => check.status === 'FAIL').map((check) => `${check.label}: ${check.detail}`);
    const warnings = result.checks.filter((check) => check.status === 'WARN').map((check) => `${check.label}: ${check.detail}`);
    const verdict = failures.length > 0 ? 'FAIL' : warnings.length > 0 ? 'WARN' : 'PASS';
    return {
        ...result,
        verdict,
        ok: failures.length === 0,
        failures,
        warnings,
    };
}
function isRasterExtension(extension) {
    return RASTER_EXTENSIONS.has(extension);
}
function isVectorExtension(extension) {
    return VECTOR_EXTENSIONS.has(extension);
}
function targetWidthInches(input) {
    if (Number.isFinite(input.targetWidthInches) && Number(input.targetWidthInches) > 0) {
        return Number(input.targetWidthInches);
    }
    return DEFAULT_TARGET_WIDTH_INCHES[input.placement || 'unknown'];
}
function effectiveDpiThreshold(kind) {
    if (kind === 'photo' || kind === 'scan' || kind === 'screenshot')
        return 300;
    if (kind === 'heatmap' || kind === 'comparison')
        return 450;
    return 450;
}
function readPngDimensions(filePath) {
    const buffer = readFileSync(filePath);
    if (buffer.length < 24)
        return undefined;
    if (buffer.readUInt32BE(0) !== 0x89504e47)
        return undefined;
    if (buffer.toString('ascii', 12, 16) !== 'IHDR')
        return undefined;
    return {
        widthPx: buffer.readUInt32BE(16),
        heightPx: buffer.readUInt32BE(20),
    };
}
function readJpegDimensions(filePath) {
    const buffer = readFileSync(filePath);
    if (buffer.length < 4 || buffer[0] !== 0xff || buffer[1] !== 0xd8)
        return undefined;
    let offset = 2;
    while (offset + 9 < buffer.length) {
        while (offset < buffer.length && buffer[offset] === 0xff)
            offset += 1;
        if (offset >= buffer.length)
            break;
        const marker = buffer[offset];
        offset += 1;
        if (marker === 0xd8 || marker === 0xd9)
            continue;
        if (marker >= 0xd0 && marker <= 0xd7)
            continue;
        if (offset + 1 >= buffer.length)
            break;
        const segmentLength = buffer.readUInt16BE(offset);
        if (segmentLength < 2 || offset + segmentLength > buffer.length)
            break;
        const isStartOfFrame = (marker >= 0xc0 && marker <= 0xc3)
            || (marker >= 0xc5 && marker <= 0xc7)
            || (marker >= 0xc9 && marker <= 0xcb)
            || (marker >= 0xcd && marker <= 0xcf);
        if (isStartOfFrame) {
            if (offset + 7 >= buffer.length)
                break;
            return {
                heightPx: buffer.readUInt16BE(offset + 3),
                widthPx: buffer.readUInt16BE(offset + 5),
            };
        }
        offset += segmentLength;
    }
    return undefined;
}
function readRasterDimensions(filePath, extension) {
    if (extension === '.png')
        return readPngDimensions(filePath);
    if (extension === '.jpg' || extension === '.jpeg')
        return readJpegDimensions(filePath);
    return undefined;
}
export function validateFigureFile(input, cwd = process.cwd()) {
    const normalizedPath = stripToolAtPrefix(input.path);
    const resolvedPath = resolve(cwd, normalizedPath);
    const checks = [];
    const extension = extname(resolvedPath).toLowerCase();
    const generatorScriptPath = input.generatorScriptPath ? stripToolAtPrefix(input.generatorScriptPath) : undefined;
    const resolvedGeneratorScriptPath = generatorScriptPath ? resolve(cwd, generatorScriptPath) : undefined;
    if (!existsSync(resolvedPath)) {
        addCheck(checks, 'exists', 'Figure file exists', 'FAIL', `Could not find ${normalizedPath}.`);
        return finalizeResult({
            figurePath: resolvedPath,
            normalizedPath,
            generatorScriptPath: resolvedGeneratorScriptPath,
            fileExists: false,
            fileExtension: extension || undefined,
            checks,
        });
    }
    const stat = statSync(resolvedPath);
    const sizeLabel = formatBytes(stat.size);
    const isRaster = isRasterExtension(extension);
    const isVector = isVectorExtension(extension);
    const prefersVector = VECTOR_PREFERRED_KINDS.has(input.kind);
    const axesExpected = AXES_EXPECTED_KINDS.has(input.kind);
    const targetWidth = targetWidthInches(input);
    const dimensions = isRaster ? readRasterDimensions(resolvedPath, extension) : undefined;
    const dpi = dimensions && targetWidth ? dimensions.widthPx / targetWidth : undefined;
    addCheck(checks, 'allowed-format', 'Figure format is submission-safe', ALLOWED_EXTENSIONS.has(extension) ? 'PASS' : 'FAIL', ALLOWED_EXTENSIONS.has(extension)
        ? `${extension || '(no extension)'} is accepted by the paper workflow.`
        : `${extension || '(no extension)'} is not supported. Use PDF for vector figures or PNG/JPEG/TIFF for raster figures.`);
    addCheck(checks, 'non-empty', 'Figure file is non-empty', stat.size > 0 ? 'PASS' : 'FAIL', stat.size > 0 ? `File size is ${sizeLabel}.` : 'File is empty.');
    addCheck(checks, 'size-limit', 'Figure file is ≤ 2.5 MB', stat.size <= MAX_FIGURE_BYTES ? 'PASS' : 'FAIL', stat.size <= MAX_FIGURE_BYTES
        ? `${sizeLabel} is within the 2.5 MB submission limit.`
        : `${sizeLabel} exceeds the 2.5 MB submission limit. Compress the file or convert it to PDF.`);
    if (prefersVector) {
        if (isVector) {
            addCheck(checks, 'vector-format', 'Technical figure uses vector output', 'PASS', 'PDF is the preferred format for technical diagrams and plots.');
        }
        else if (isRaster) {
            const justification = String(input.rasterJustification || '').trim();
            addCheck(checks, 'vector-format', 'Technical figure uses vector output', justification ? 'WARN' : 'FAIL', justification
                ? `Raster output is justified: ${justification}`
                : 'Plots, diagrams, schematics, proof figures, and flowcharts should be PDF unless raster output is genuinely unavoidable.');
        }
    }
    else if (isRaster) {
        addCheck(checks, 'format-fit', 'Figure format matches figure kind', 'PASS', `${input.kind} figures may use raster output when appropriate.`);
    }
    if (dimensions) {
        addCheck(checks, 'dimensions', 'Raster figure dimensions are known', 'PASS', `${dimensions.widthPx}×${dimensions.heightPx} px.`);
    }
    else if (isRaster) {
        addCheck(checks, 'dimensions', 'Raster figure dimensions are known', 'WARN', `Could not infer pixel dimensions for ${extension}.`);
    }
    if (isRaster && dpi && targetWidth) {
        const threshold = effectiveDpiThreshold(input.kind);
        addCheck(checks, 'dpi', 'Raster figure has adequate effective DPI', dpi >= threshold ? 'PASS' : 'FAIL', `${dpi.toFixed(0)} DPI at ${targetWidth.toFixed(2)} in target width (required ≥ ${threshold} DPI).`);
    }
    else if (isRaster && targetWidth && !dpi) {
        addCheck(checks, 'dpi', 'Raster figure has adequate effective DPI', 'WARN', `Could not compute effective DPI at ${targetWidth.toFixed(2)} in target width.`);
    }
    const caption = String(input.caption || '').trim();
    addCheck(checks, 'caption-present', 'Caption is present', caption.length >= 20 ? 'PASS' : 'FAIL', caption.length >= 20 ? `Caption length is ${caption.length} characters.` : 'Caption is too short to be self-contained.');
    addCheck(checks, 'caption-self-contained', 'Caption is self-contained', input.captionSelfContained ? 'PASS' : 'FAIL', input.captionSelfContained
        ? 'Caption can be understood without surrounding text.'
        : 'Captions must explain what is shown and how to read the figure without forcing the reader to search the paper.');
    const purpose = String(input.purpose || '').trim();
    addCheck(checks, 'purpose', 'Figure has a clear purpose', purpose.length >= 16 ? 'PASS' : 'FAIL', purpose.length >= 16
        ? `Purpose: ${purpose}`
        : 'State the figure’s main message or role in the paper. Decorative figures are not allowed.');
    addCheck(checks, 'decorative', 'Figure is technical, not decorative', input.usesDecorativeElements ? 'FAIL' : 'PASS', input.usesDecorativeElements
        ? 'Remove decorative or cosmetic elements that do not carry mathematical or explanatory meaning.'
        : 'No decorative-only elements were declared.');
    addCheck(checks, 'legibility', 'Labels are legible at print size', input.labelsReadableAtPrintSize ? 'PASS' : 'FAIL', input.labelsReadableAtPrintSize
        ? 'Labels are readable at the intended paper size.'
        : 'Increase font sizes, simplify the figure, or change layout until labels remain readable at final print size.');
    if (axesExpected) {
        addCheck(checks, 'axes-present', 'Expected axes are present', input.axesPresent === true ? 'PASS' : 'FAIL', input.axesPresent === true
            ? 'Axes and tick marks are present.'
            : `${input.kind} figures should expose the coordinate system clearly.`);
        addCheck(checks, 'axes-labeled', 'Axes are labeled', input.axesLabeled === true ? 'PASS' : 'FAIL', input.axesLabeled === true
            ? 'Axes labels are present.'
            : 'Axes should be labeled clearly.');
        if (input.unitsRelevant !== false) {
            addCheck(checks, 'units-labeled', 'Units are labeled when relevant', input.unitsLabeled === true ? 'PASS' : 'FAIL', input.unitsLabeled === true
                ? 'Units are present where relevant.'
                : 'Quantities with units should include them in axis labels or annotations.');
        }
        if (input.directLabelingOrClearLegend === false) {
            addCheck(checks, 'legend-clarity', 'Legend or direct labeling is clear', 'WARN', 'Prefer direct labeling or a clear legend order that matches the data.');
        }
    }
    if (input.multipanel) {
        addCheck(checks, 'panel-labels', 'Multipanel labels are consistent', input.panelLabelsConsistent === true ? 'PASS' : 'FAIL', input.panelLabelsConsistent === true
            ? 'Panels are labeled consistently (for example a, b, c).'
            : 'Multipanel figures should use consistent panel labels and ordering.');
    }
    if (input.usesRainbowOrJet) {
        addCheck(checks, 'colormap', 'Colormap avoids rainbow/jet defaults', 'FAIL', 'Rainbow/jet-style colormaps are misleading and should be replaced with perceptually safer alternatives.');
    }
    if (input.usesRedGreenOnly) {
        addCheck(checks, 'red-green', 'Color encoding avoids red/green-only distinctions', 'FAIL', 'Do not rely on red/green-only distinctions in paper figures.');
    }
    if (input.usesColor === true) {
        const colorPolicy = input.colorPolicy || 'unknown';
        addCheck(checks, 'color-policy', 'Color use is accessible', colorPolicy === 'colorblind-safe' || colorPolicy === 'redundant-encoding' || colorPolicy === 'monochrome' ? 'PASS' : 'FAIL', colorPolicy === 'colorblind-safe' || colorPolicy === 'redundant-encoding' || colorPolicy === 'monochrome'
            ? `Declared color policy: ${colorPolicy}.`
            : 'If the figure uses color, declare a colorblind-safe or redundantly encoded color policy.');
    }
    if (prefersVector) {
        const editability = input.textEditability || 'unknown';
        addCheck(checks, 'editable-text', 'Text remains editable/non-rasterized', editability === 'editable' ? 'PASS' : editability === 'rasterized' ? 'FAIL' : 'WARN', editability === 'editable'
            ? 'Text is declared editable.'
            : editability === 'rasterized'
                ? 'Vector exports should keep text editable instead of rasterizing or outlining it into unreadable shapes.'
                : 'Text editability was not confirmed.');
    }
    if (QUANTITATIVE_REPRODUCIBLE_KINDS.has(input.kind)) {
        addCheck(checks, 'reproducibility', 'Quantitative figure is reproducible from code', input.reproducibleFromCode === true ? 'PASS' : 'FAIL', input.reproducibleFromCode === true
            ? 'A reproducible code path was declared.'
            : 'Quantitative figures should be reproducible from code and tracked in the paper repository.');
    }
    else if (input.reproducibleFromCode === false) {
        addCheck(checks, 'reproducibility', 'Figure reproducibility is documented', 'WARN', 'Programmatic generation is preferred when possible; document why manual production was necessary.');
    }
    if (resolvedGeneratorScriptPath) {
        addCheck(checks, 'generator-script', 'Generator script path exists', existsSync(resolvedGeneratorScriptPath) ? 'PASS' : 'FAIL', existsSync(resolvedGeneratorScriptPath)
            ? `Found ${generatorScriptPath}.`
            : `Generator script ${generatorScriptPath} was declared but not found.`);
    }
    else if (input.reproducibleFromCode === true) {
        addCheck(checks, 'generator-script', 'Generator script path exists', 'WARN', 'Provide the generator script path so future runs can reproduce the figure directly.');
    }
    if (input.requiresScaleBar) {
        addCheck(checks, 'scale-bar', 'Required scale bar is present', input.scaleBarPresent === true ? 'PASS' : 'FAIL', input.scaleBarPresent === true
            ? 'Scale bar is present.'
            : 'This figure type requires a scale bar; add one before submission.');
    }
    return finalizeResult({
        figurePath: resolvedPath,
        normalizedPath,
        generatorScriptPath: resolvedGeneratorScriptPath,
        fileExists: true,
        fileExtension: extension || undefined,
        fileSizeBytes: stat.size,
        fileSizeLabel: sizeLabel,
        widthPx: dimensions?.widthPx,
        heightPx: dimensions?.heightPx,
        effectiveDpi: dpi,
        targetWidthInches: targetWidth,
        checks,
    });
}
export function formatFigureValidationResult(result) {
    const lines = [];
    lines.push(`${result.verdict} validate_figure: ${basename(result.normalizedPath || result.figurePath)}`);
    const meta = [];
    if (result.fileExtension)
        meta.push(`format ${result.fileExtension}`);
    if (result.fileSizeLabel)
        meta.push(`size ${result.fileSizeLabel}`);
    if (result.widthPx && result.heightPx)
        meta.push(`${result.widthPx}×${result.heightPx}px`);
    if (result.effectiveDpi && result.targetWidthInches)
        meta.push(`${result.effectiveDpi.toFixed(0)} DPI @ ${result.targetWidthInches.toFixed(2)}in`);
    if (meta.length > 0)
        lines.push(`Metadata: ${meta.join(' • ')}`);
    if (result.failures.length > 0) {
        lines.push('');
        lines.push('Failures:');
        for (const failure of result.failures)
            lines.push(`- ${failure}`);
    }
    if (result.warnings.length > 0) {
        lines.push('');
        lines.push('Warnings:');
        for (const warning of result.warnings)
            lines.push(`- ${warning}`);
    }
    lines.push('');
    lines.push('Checklist:');
    for (const check of result.checks) {
        const marker = check.status === 'PASS' ? '✓' : check.status === 'WARN' ? '!' : '✗';
        lines.push(`${marker} ${check.label} — ${check.detail}`);
    }
    return lines.join('\n');
}
//# sourceMappingURL=index.js.map