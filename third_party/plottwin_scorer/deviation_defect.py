"""Deviation-from-default + defect-ledger scorer.

This is the production, single-sample form of the exploratory
``experiments/deviation_defect_scorer`` scripts. It keeps the deterministic
code channel and the VLM defect ledger separately auditable.
"""

from __future__ import annotations

import ast
import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.colors as mcolors

from .color import ciede2000


DEVIATION_DEFECT_SCORE_VERSION = "deviation-defect-v1"
DEFAULT_CODE_WEIGHT = 0.35
DEFAULT_PENALTIES: dict[str, int] = {
    "minor": 5,
    "major": 10,
    "critical": 25,
}
SEVERITIES = tuple(DEFAULT_PENALTIES)

# Activation thresholds inherited from the accepted prototype. They are part
# of this versioned scorer behaviour rather than adapter configuration knobs.
COLOR_DEVIATION_THRESHOLD = 4.0
LINEWIDTH_DEVIATION_LOG_THRESHOLD = 0.15
ASPECT_DEVIATION_LOG_THRESHOLD = 0.10

_COLOR_KEYWORDS = frozenset({"color", "c", "colors", "edgecolor", "ec"})
_LINE_CALLS = frozenset(
    {
        "plot",
        "errorbar",
        "step",
        "hlines",
        "vlines",
        "axhline",
        "axvline",
        "semilogx",
        "semilogy",
        "loglog",
    }
)
_SPINE_SIDES = ("top", "right", "left", "bottom")
_UNKNOWN = object()


DEFECT_SYSTEM_PROMPT = """You are a strict style-transfer auditor for scientific figures.
Image 1 is the REFERENCE style target. Image 2 is the CANDIDATE rendered from
different data. This is CONTENT-BLIND evaluation: differences in data values,
data distributions, labels or text content, series count, panel count, axis
ranges, and axis values are correct by design and must never be logged as a
defect. Do not infer missing style defects from those content differences.

Audit only deliberate visual style choices made by the reference that the
candidate failed to reproduce. Focus on perceptual/layout choices code cannot
reliably establish: panel alignment and spacing, whitespace/compactness, spine
weight/color, gridline restraint, legend/colorbar craft and placement,
typographic hierarchy, emphasis/accent structure, signature motifs, clipping,
overlap, and mark collisions. Be demanding: a faithful transfer has zero or a
small number of misses. Return one JSON object only, with no prose or Markdown."""

DEFECT_USER_PROMPT = """List every deliberate REFERENCE style choice the CANDIDATE failed to reproduce.

Each miss must have:
- "choice": a concise description of the missed reference style choice;
- "severity": exactly one of "minor", "major", or "critical";
- "bbox": exactly four numeric candidate-image coordinates [x0, y0, x1, y1]
  on a 0..1000 normalized canvas, with x0 < x1 and y0 < y1.

Severity guide: use "critical" ONLY for objective render-integrity failures that
make the figure wrong or unreadable — content drawn outside the axes or off the
canvas, a legend/label/title/tick clipped or cut off at an edge, or text/marks
overlapping so they become unreadable. Use "major" for clearly visible
layout/spacing/emphasis choices that were not reproduced but do not break the
figure, and "minor" for subtle spacing, margin, or restraint differences.

Do not log data, label/text content, series/panel count, axis-value, or range
differences. If the transfer is stylistically faithful, return an empty list.

Output exactly this JSON shape and no additional keys:
{"misses": [{"choice": "...", "severity": "minor", "bbox": [0, 0, 1000, 1000]}]}"""


def validate_code_weight(code_weight: Any) -> float:
    """Return a finite blend weight in ``[0, 1]`` or fail loudly."""
    if isinstance(code_weight, bool):
        raise ValueError("code_weight must be a numeric value in [0, 1]")
    try:
        value = float(code_weight)
    except (TypeError, ValueError) as exc:
        raise ValueError("code_weight must be a numeric value in [0, 1]") from exc
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"code_weight must be finite and in [0, 1], got {code_weight!r}")
    return value


def validate_penalties(penalties: Mapping[str, Any] | None = None) -> dict[str, float]:
    """Validate and normalize a severity ledger.

    Defaults are frozen to ``minor=5``, ``major=10``, and ``critical=25``.
    Adapter config may explicitly carry the values so fingerprints document
    runtime semantics. A separately versioned release may use another ledger,
    but it must preserve strict severity ordering.
    """
    if penalties is None:
        return {name: float(value) for name, value in DEFAULT_PENALTIES.items()}
    if not isinstance(penalties, Mapping):
        raise ValueError("penalties must be a mapping with minor, major, and critical")
    expected = set(SEVERITIES)
    actual = set(penalties)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            "penalties must contain exactly minor, major, critical "
            f"(missing={missing}, extra={extra})"
        )
    normalized: dict[str, float] = {}
    for severity in SEVERITIES:
        raw = penalties[severity]
        if isinstance(raw, bool):
            raise ValueError(f"penalties.{severity} must be a positive finite number")
        try:
            value = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"penalties.{severity} must be a positive finite number"
            ) from exc
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"penalties.{severity} must be a positive finite number")
        normalized[severity] = value
    if not (
        normalized["minor"] < normalized["major"] < normalized["critical"]
    ):
        raise ValueError("penalties must satisfy minor < major < critical")
    return normalized


def _json_number(value: float) -> float | int:
    return int(value) if float(value).is_integer() else float(value)


def _serializable_penalties(penalties: Mapping[str, float]) -> dict[str, float | int]:
    return {severity: _json_number(penalties[severity]) for severity in SEVERITIES}


def _normalise_color(value: Any) -> str | None:
    try:
        return mcolors.to_hex(value, keep_alpha=False).lower()
    except (TypeError, ValueError):
        return None


def _coerce_pair(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    try:
        first, second = float(value[0]), float(value[1])
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(first) and math.isfinite(second) and first > 0 and second > 0):
        return None
    return first, second


def _font_is_serif(value: Any) -> bool | None:
    if isinstance(value, str):
        families = [value]
    elif isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        families = list(value)
    else:
        return None
    lowered = {family.strip().lower() for family in families}
    if "serif" in lowered:
        return True
    if lowered & {"sans-serif", "sans", "monospace", "mono"}:
        return False
    return None


def matplotlib_default_style() -> dict[str, Any]:
    """Read immutable Matplotlib defaults, not process-wide current rcParams."""
    defaults = matplotlib.rcParamsDefault
    cycle = defaults.get("axes.prop_cycle")
    colors = []
    if cycle is not None:
        try:
            colors = [_normalise_color(c) for c in cycle.by_key().get("color", [])]
        except Exception:  # pragma: no cover - defensive against exotic rcParams
            colors = []
    colors = [color for color in colors if color is not None]
    figsize = _coerce_pair(defaults.get("figure.figsize"))
    return {
        "palette": colors,
        "background": _normalise_color(defaults.get("axes.facecolor")) or "#ffffff",
        "figure_aspect": (figsize[0] / figsize[1]) if figsize else (6.4 / 4.8),
        "linewidth": float(defaults.get("lines.linewidth", 1.5)),
        "grid": bool(defaults.get("axes.grid", False)),
        "spines_removed": [],
        "tick_direction": str(defaults.get("xtick.direction", "out")),
        "serif": _font_is_serif(defaults.get("font.family")),
        "legend_frame": bool(defaults.get("legend.frameon", True)),
        "matplotlib_version": matplotlib.__version__,
    }


def _literal(node: ast.AST | None) -> Any:
    if node is None:
        return _UNKNOWN
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return _UNKNOWN


def _const_env(tree: ast.AST) -> dict[str, ast.expr]:
    """Names bound exactly once, to an expression, anywhere in the module.

    Candidates open with a named style block -- ``COL_CURVE = "#4c72b0"``,
    ``FIGSIZE = (11.2, 6.5)``, ``DENDRO_LINEWIDTH = 0.34`` -- which is the idiom this
    corpus rewards, and then pass the name rather than the literal. Reading only the
    call site therefore discards a value the source states plainly.

    A name qualifies only when the module leaves no doubt about it: a single plain
    assignment, never rebound, never a parameter, loop target, comprehension target,
    ``with``/``except`` alias, walrus, augmented assignment, import alias, or a
    function/class name, and never declared ``global``/``nonlocal``. Anything else is
    dropped, so a value that genuinely depends on data stays unreadable.
    """
    bindings: dict[str, list[ast.expr]] = {}
    disqualified: set[str] = set()

    def bind(target: ast.AST, value: ast.expr | None) -> None:
        if isinstance(target, ast.Name):
            if value is None:
                disqualified.add(target.id)
            else:
                bindings.setdefault(target.id, []).append(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            elts = list(target.elts)
            if (isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(elts)
                    and not any(isinstance(e, ast.Starred) for e in elts)):
                for t, v in zip(elts, value.elts):
                    bind(t, v)
            else:
                for t in elts:
                    bind(t, None)
        else:
            for name in (n.id for n in ast.walk(target) if isinstance(n, ast.Name)):
                disqualified.add(name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                bind(t, node.value)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
            bind(node.target, None)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            bind(node.target, None)
        elif isinstance(node, ast.comprehension):
            bind(node.target, None)
        elif isinstance(node, ast.withitem):
            if node.optional_vars is not None:
                bind(node.optional_vars, None)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                disqualified.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                disqualified.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            disqualified.add(node.name)
            a = node.args
            for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg]:
                if arg is not None:
                    disqualified.add(arg.arg)
        elif isinstance(node, ast.Lambda):
            a = node.args
            for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg]:
                if arg is not None:
                    disqualified.add(arg.arg)
        elif isinstance(node, ast.ClassDef):
            disqualified.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            disqualified.update(node.names)

    return {n: v[0] for n, v in bindings.items()
            if len(v) == 1 and n not in disqualified}


def _loop_env(tree: ast.AST, env: Mapping[str, ast.expr]) -> dict[str, list[Any]]:
    """Values a loop target can take when the loop runs over a literal table.

    ``for treatment, label, colour in LINE_MAP:`` states every colour the figure can
    draw; only which row is current depends on the data. This is the same statement the
    spine recogniser already unrolls, applied to values rather than to sides.

    A name bound by more than one loop, or by a loop over something that does not fold,
    is dropped -- the set of values would not be known.
    """
    choices: dict[str, list[Any]] = {}
    dropped: set[str] = set()

    def bind(target: ast.AST, values: list[Any]) -> None:
        if isinstance(target, ast.Name):
            if target.id in choices or target.id in env:
                dropped.add(target.id)
            else:
                choices[target.id] = values
        elif isinstance(target, (ast.Tuple, ast.List)):
            arity = len(target.elts)
            if any(isinstance(e, ast.Starred) for e in target.elts):
                for element in target.elts:
                    for name in (n.id for n in ast.walk(element) if isinstance(n, ast.Name)):
                        dropped.add(name)
                return
            rows = [v for v in values if isinstance(v, (list, tuple)) and len(v) == arity]
            if len(rows) != len(values) or not rows:
                for element in target.elts:
                    for name in (n.id for n in ast.walk(element) if isinstance(n, ast.Name)):
                        dropped.add(name)
                return
            for index, element in enumerate(target.elts):
                bind(element, [row[index] for row in rows])

    generators: list[tuple[ast.AST, ast.expr]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.AsyncFor)):
            generators.append((node.target, node.iter))
        elif isinstance(node, ast.comprehension):
            generators.append((node.target, node.iter))

    for target_node, iter_node in generators:
        iterable = _resolve(iter_node, env)
        if isinstance(iterable, dict):
            iterable = list(iterable.keys())
        if not isinstance(iterable, (list, tuple)) or not iterable:
            for name in (n.id for n in ast.walk(target_node) if isinstance(n, ast.Name)):
                dropped.add(name)
            continue
        bind(target_node, list(iterable))

    return {n: v for n, v in choices.items() if n not in dropped}


def _param_env(tree: ast.AST, env: Mapping[str, ast.expr],
                loop_env: Mapping[str, list[Any]]) -> dict[str, list[Any]]:
    """Values a helper's parameter can take, read off its call sites.

    Candidates factor drawing into helpers -- ``def draw_edge(ax, p0, p1, colour, lw)``
    called as ``draw_edge(ax, a, b, COL_EDGE, 1.2)``. Inside the helper the value is a
    parameter name and looks non-local, but the module states every argument it is ever
    called with, so the set of values is known.

    A parameter is dropped unless EVERY call site supplies a value that folds. A helper
    called once with a computed colour therefore stays unreadable, as it must.
    """
    definitions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    duplicated: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in definitions:
                duplicated.add(node.name)
            definitions[node.name] = node
    for name in duplicated:
        definitions.pop(name, None)

    call_sites: dict[str, list[ast.Call]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in definitions:
            call_sites.setdefault(node.func.id, []).append(node)

    resolved: dict[str, list[Any]] = {}
    conflicted: set[str] = set()
    for name, definition in definitions.items():
        arguments = definition.args
        if arguments.vararg is not None or arguments.kwarg is not None:
            continue
        positional = [*arguments.posonlyargs, *arguments.args]
        defaults: dict[str, ast.expr] = {}
        for parameter, default in zip(positional[len(positional) - len(arguments.defaults):],
                                      arguments.defaults):
            defaults[parameter.arg] = default
        for parameter, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
            if default is not None:
                defaults[parameter.arg] = default

        for index, parameter in enumerate([*positional, *arguments.kwonlyargs]):
            key = parameter.arg
            if key in env or key in loop_env:
                conflicted.add(key)
                continue
            values: list[Any] = []
            usable = True
            for call in call_sites.get(name, []):
                supplied = None
                if index < len(call.args) and parameter in positional:
                    supplied = call.args[index]
                else:
                    for keyword in call.keywords:
                        if keyword.arg == key:
                            supplied = keyword.value
                            break
                if supplied is None:
                    supplied = defaults.get(key)
                if supplied is None:
                    usable = False
                    break
                folded = _resolve_choices(supplied, env, loop_env)
                if not folded:
                    usable = False
                    break
                values.extend(folded)
            if not call_sites.get(name) and key in defaults:
                values = _resolve_choices(defaults[key], env, loop_env)
                usable = bool(values)
            if usable and values:
                if key in resolved and resolved[key] != values:
                    conflicted.add(key)
                else:
                    resolved[key] = values

    return {n: v for n, v in resolved.items() if n not in conflicted}


_RESOLVE_DEPTH = 6


def _resolve(node: ast.AST | None, env: Mapping[str, ast.expr], _seen: frozenset = frozenset()) -> Any:
    """``_literal`` plus names bound unambiguously and constant arithmetic."""
    if node is None or len(_seen) > _RESOLVE_DEPTH:
        return _UNKNOWN
    value = _literal(node)
    if value is not _UNKNOWN:
        return value
    if isinstance(node, ast.Name):
        if node.id in _seen or node.id not in env:
            return _UNKNOWN
        return _resolve(env[node.id], env, _seen | {node.id})
    if isinstance(node, (ast.Tuple, ast.List)):
        out = [_resolve(e, env, _seen) for e in node.elts]
        if any(v is _UNKNOWN for v in out):
            return _UNKNOWN
        return tuple(out) if isinstance(node, ast.Tuple) else out
    if isinstance(node, ast.Dict):
        keys = [_resolve(k, env, _seen) for k in node.keys]
        vals = [_resolve(v, env, _seen) for v in node.values]
        if any(k is _UNKNOWN for k in keys) or any(v is _UNKNOWN for v in vals):
            return _UNKNOWN
        try:
            return dict(zip(keys, vals))
        except TypeError:
            return _UNKNOWN
    if isinstance(node, ast.Call):
        # A style table is as often built with a constructor as with a display --
        # ``COLORS = OrderedDict([("ctrl", "#4c72b0"), ...])``. These are pure, so folding
        # them reads a value the source states; any other call stays unknown.
        constructor = _call_name(node.func)
        if constructor in {"dict", "OrderedDict"}:
            folded: dict[Any, Any] = {}
            for argument in node.args:
                value = _resolve(argument, env, _seen)
                if isinstance(value, dict):
                    folded.update(value)
                    continue
                if not isinstance(value, (list, tuple)):
                    return _UNKNOWN
                try:
                    folded.update({key: item for key, item in value})
                except (TypeError, ValueError):
                    return _UNKNOWN
            for keyword in node.keywords:
                value = _resolve(keyword.value, env, _seen)
                if keyword.arg is None:
                    if not isinstance(value, dict):
                        return _UNKNOWN
                    folded.update(value)
                elif value is _UNKNOWN:
                    return _UNKNOWN
                else:
                    folded[keyword.arg] = value
            return folded
        if constructor in {"items", "values", "keys"} and isinstance(node.func, ast.Attribute) \
                and not node.args and not node.keywords:
            mapping = _resolve(node.func.value, env, _seen)
            if not isinstance(mapping, dict):
                return _UNKNOWN
            if constructor == "items":
                return [(k, v) for k, v in mapping.items()]
            return list(mapping.values() if constructor == "values" else mapping.keys())
        if constructor == "get" and isinstance(node.func, ast.Attribute) and not node.keywords \
                and 1 <= len(node.args) <= 2:
            mapping = _resolve(node.func.value, env, _seen)
            key = _resolve(node.args[0], env, _seen)
            if not isinstance(mapping, dict) or key is _UNKNOWN:
                return _UNKNOWN
            if key in mapping:
                return mapping[key]
            return _resolve(node.args[1], env, _seen) if len(node.args) == 2 else None
        if constructor in {"enumerate", "zip", "sorted", "reversed"} and not node.keywords:
            folded = [_resolve(a, env, _seen) for a in node.args]
            if not folded or any(v is _UNKNOWN or not isinstance(v, (list, tuple)) for v in folded):
                return _UNKNOWN
            try:
                if constructor == "enumerate":
                    return list(enumerate(folded[0]))
                if constructor == "zip":
                    return list(zip(*folded))
                if constructor == "reversed":
                    return list(reversed(folded[0]))
                return sorted(folded[0])
            except TypeError:
                return _UNKNOWN
        if constructor in {"list", "tuple", "set"} and not node.keywords and len(node.args) <= 1:
            if not node.args:
                return {"list": [], "tuple": (), "set": []}[constructor]
            value = _resolve(node.args[0], env, _seen)
            if not isinstance(value, (list, tuple)):
                return _UNKNOWN
            return tuple(value) if constructor == "tuple" else list(value)
        return _UNKNOWN
    if isinstance(node, ast.Subscript):
        container = _resolve(node.value, env, _seen)
        index = _resolve(node.slice, env, _seen)
        if container is _UNKNOWN or index is _UNKNOWN:
            return _UNKNOWN
        try:
            return container[index]
        except (KeyError, IndexError, TypeError):
            return _UNKNOWN
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        inner = _resolve(node.operand, env, _seen)
        if isinstance(inner, (int, float)) and not isinstance(inner, bool):
            return -inner if isinstance(node.op, ast.USub) else inner
        return _UNKNOWN
    if isinstance(node, ast.BinOp):
        left, right = _resolve(node.left, env, _seen), _resolve(node.right, env, _seen)
        if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
            return _UNKNOWN
        if isinstance(left, bool) or isinstance(right, bool):
            return _UNKNOWN
        try:
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        except ZeroDivisionError:
            return _UNKNOWN
    return _UNKNOWN


def _resolve_choices(node: ast.AST | None, env: Mapping[str, ast.expr],
                     loop_env: Mapping[str, list[Any]] | None = None,
                     _seen: frozenset = frozenset()) -> list[Any]:
    """Every value an expression can provably take, or [] when that is not knowable.

    ``lw=0.85 if is_bottom else 0.55`` states both widths in the source; which one
    applies to which artist is data-dependent, and the dimensions that consume this
    already aggregate over a pool, so both belong in it.
    """
    if node is None or len(_seen) > _RESOLVE_DEPTH:
        return []
    value = _resolve(node, env, _seen)
    if value is not _UNKNOWN:
        return [value]
    if isinstance(node, ast.IfExp):
        out = _resolve_choices(node.body, env, loop_env, _seen) + _resolve_choices(node.orelse, env, loop_env, _seen)
        return out if all(o is not _UNKNOWN for o in out) and out else []
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        out: list[Any] = []
        for v in node.values:
            got = _resolve_choices(v, env, loop_env, _seen)
            if not got:
                return []
            out.extend(got)
        return out
    if isinstance(node, ast.Name) and node.id not in _seen:
        if node.id in env:
            return _resolve_choices(env[node.id], env, loop_env, _seen | {node.id})
        if loop_env and node.id in loop_env:
            return list(loop_env[node.id])
    if isinstance(node, ast.Subscript):
        # ``style = condition_style[condition]`` then ``color=style["color"]``: which row
        # is picked depends on the data, but the table is written out in full, so the set
        # of colours the figure can draw is known even though the choice is not.
        out = []
        for container in _resolve_choices(node.value, env, loop_env, _seen) or []:
            index = _resolve(node.slice, env, _seen)
            if index is not _UNKNOWN:
                try:
                    out.append(container[index])
                    continue
                except (KeyError, IndexError, TypeError):
                    return []
            if isinstance(container, dict):
                out.extend(container.values())
            elif isinstance(container, (list, tuple)):
                out.extend(container)
            else:
                return []
        return out
    return []


def _call_name(func: ast.AST) -> str:
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _attribute_chain(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return _attribute_chain(node.value) + [node.attr]
    return []


def _keyword_value(node: ast.Call, *names: str) -> ast.AST | None:
    for keyword in node.keywords:
        if keyword.arg in names:
            return keyword.value
    return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


class _StyleVisitor(ast.NodeVisitor):
    """Conservative literal-only extractor for accepted code dimensions.

    Dynamic configuration is deliberately surfaced as unavailable. This avoids
    fabricating a default value for a candidate and hiding it by shrinking a
    reference-defined denominator.
    """

    def __init__(self, env: Mapping[str, ast.expr] | None = None,
                 loop_env: Mapping[str, list[Any]] | None = None) -> None:
        self.env: Mapping[str, ast.expr] = env or {}
        self.loop_env: Mapping[str, list[Any]] = loop_env or {}
        self.colors: list[str] = []
        self.colors_unreadable = 0
        self.facecolors: list[str] = []
        self.figsize: tuple[float, float] | None = None
        self.linewidths: list[float] = []
        self.grid: bool | None = None
        self.grid_by_axes: dict[str, bool] = {}
        self.spines_removed: set[str] = set()
        self.tick_direction: str | None = None
        self.font_serif: bool | None = None
        self.has_legend = False
        self.legend_frame: bool | None = None
        self.line_call_count = 0
        self.line_calls_missing_width = 0
        self.dynamic_dimensions: set[str] = set()
        self.global_style_unknown = False
        self.events: dict[str, list[str]] = {
            "palette": [],
            "background": [],
            "figure_aspect": [],
            "linewidth": [],
            "grid": [],
            "spines_removed": [],
            "tick_direction": [],
            "serif": [],
            "legend_frame": [],
            "global": [],
        }

    def _value(self, node: ast.AST | None) -> Any:
        return _resolve(node, self.env)

    def _choices(self, node: ast.AST | None) -> list[Any]:
        return _resolve_choices(node, self.env, self.loop_env)

    def _event(self, feature: str, message: str) -> None:
        self.events.setdefault(feature, []).append(message)

    def _dynamic(self, feature: str, message: str) -> None:
        self.dynamic_dimensions.add(feature)
        self._event(feature, message)

    def _global_unknown(self, message: str) -> None:
        self.global_style_unknown = True
        self._event("global", message)

    def _add_color(self, value: Any, *, background: bool = False, event: str) -> None:
        color = _normalise_color(value)
        if color is None:
            if background:
                self._dynamic("background", event)
                return
            # A palette is a SET, and its score is the mean distance from each reference
            # colour to the NEAREST candidate colour. Dropping a colour we cannot read can
            # only move that distance up, never down, so scoring the readable subset
            # cannot inflate a candidate -- while discarding the dimension threw away
            # every colour the file did state.
            self.colors_unreadable += 1
            self._event("palette", f"{event} unreadable colour")
            return
        target = self.facecolors if background else self.colors
        target.append(color)
        self._event("background" if background else "palette", event)

    def _set_figsize(self, value: Any, event: str) -> None:
        pair = _coerce_pair(value)
        if pair is None:
            self._dynamic("figure_aspect", event)
            return
        if self.figsize is not None and self.figsize != pair:
            self._dynamic("figure_aspect", f"conflicting explicit figsize ({event})")
            return
        self.figsize = pair
        self._event("figure_aspect", event)

    _NO_LINE_STYLES = frozenset({"none", "", " "})

    def _draws_no_line(self, node: ast.Call) -> bool:
        """True when this artist provably renders no connecting segment."""
        for names in (("linestyle", "ls"), ("fmt",)):
            value = self._value(_keyword_value(node, *names))
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in self._NO_LINE_STYLES:
                    return True
                if names == ("fmt",) and not any(c in value for c in "-:"):
                    return True
        # A positional matplotlib format string with no line-style character.
        for argument in node.args[2:4]:
            value = self._value(argument)
            if isinstance(value, str) and value and not any(c in value for c in "-:"):
                return True
        # A single point has no segment between two points, whatever the style says.
        if len(node.args) >= 2:
            resolved = [self._value(a) for a in node.args[:2]]
            if all(
                (isinstance(v, (int, float)) and not isinstance(v, bool))
                or (isinstance(v, (list, tuple)) and len(v) == 1)
                for v in resolved
            ):
                return True
        return False

    def _add_linewidths(self, node: ast.AST | None, event: str) -> None:
        """Feed every width the source states for this artist into the pool."""
        value = self._value(node)
        if isinstance(value, (list, tuple)) and value:
            for item in value:
                self._add_linewidth(item, event)
            return
        if value is _UNKNOWN:
            choices = self._choices(node)
            if choices:
                for item in choices:
                    self._add_linewidth(item, event)
                return
        self._add_linewidth(value, event)

    def _add_linewidth(self, value: Any, event: str) -> None:
        if isinstance(value, bool):
            self._dynamic("linewidth", event)
            return
        try:
            linewidth = float(value)
        except (TypeError, ValueError):
            self._dynamic("linewidth", event)
            return
        if not math.isfinite(linewidth):
            self._dynamic("linewidth", event)
            return
        if linewidth <= 0:
            # ``set_linewidth(0)`` states that this artist has no stroke. That is a
            # known fact, not an unreadable one, and a zero does not belong in a pool
            # of stroke widths.
            self._event("linewidth", f"{event} zero width")
            return
        self.linewidths.append(linewidth)
        self._event("linewidth", event)

    def _set_grid(self, value: Any, event: str, axis: Any = "both", receiver: str = "") -> None:
        if not isinstance(value, bool):
            self._dynamic("grid", event)
            return
        # Grid visibility is per-Axes: a figure that draws gridlines on its main
        # panel and clears them on a companion Axes (residual strip, twin axis,
        # colorbar) still shows gridlines. Track each receiver separately and let
        # "any Axes gridded" decide the figure-level feature.
        if value:
            self.grid_by_axes[receiver] = True
        elif axis in (None, "both"):
            # Only an unqualified grid(False) clears that Axes; a per-axis
            # grid(False, axis="x") must not cancel a prior grid(True, axis="y").
            self.grid_by_axes[receiver] = False
        # else: partial per-axis off — leave this Axes' state alone.
        self.grid = any(self.grid_by_axes.values()) if self.grid_by_axes else None
        self._event("grid", event)
        # else: grid(False, axis=<specific/unknown>) is a partial off — leave state.
        self._event("grid", event)

    def _set_tick_direction(self, value: Any, event: str) -> None:
        if not isinstance(value, str) or value not in {"in", "out", "inout"}:
            self._dynamic("tick_direction", event)
            return
        self.tick_direction = value
        self._event("tick_direction", event)

    def _set_font_family(self, value: Any, event: str) -> None:
        serif = _font_is_serif(value)
        if serif is None:
            self._dynamic("serif", event)
            return
        self.font_serif = serif
        self._event("serif", event)

    def _set_legend_frame(self, value: Any, event: str) -> None:
        if not isinstance(value, bool):
            self._dynamic("legend_frame", event)
            return
        self.legend_frame = value
        self._event("legend_frame", event)

    def _apply_rcparam(self, key: Any, value: Any, event: str) -> None:
        if not isinstance(key, str):
            self._global_unknown(event)
            return
        handlers = {
            "axes.grid": lambda: self._set_grid(value, event),
            "axes.facecolor": lambda: self._add_color(value, background=True, event=event),
            "figure.facecolor": lambda: self._add_color(value, background=True, event=event),
            "figure.figsize": lambda: self._set_figsize(value, event),
            "lines.linewidth": lambda: self._add_linewidth(value, event),
            "xtick.direction": lambda: self._set_tick_direction(value, event),
            "ytick.direction": lambda: self._set_tick_direction(value, event),
            "font.family": lambda: self._set_font_family(value, event),
            "legend.frameon": lambda: self._set_legend_frame(value, event),
        }
        handler = handlers.get(key)
        if handler is not None:
            handler()
            return
        # Only unknown rcParams that can alter a registered code feature make
        # its fallback unreliable. A harmless setting such as figure.dpi must
        # not throw every unrelated dimension away.
        if key == "axes.prop_cycle":
            self._dynamic("palette", event)
        elif key.startswith("axes.spine"):
            self._dynamic("spines_removed", event)
        else:
            self._event("global", f"ignored unscored rcParam {key!r}")

    def _rcparam_key(self, target: ast.AST) -> str | None:
        if not isinstance(target, ast.Subscript):
            return None
        chain = _attribute_chain(target.value)
        if not chain or chain[-1] != "rcParams":
            return None
        key = self._value(target.slice)
        return key if isinstance(key, str) else None

    def visit_Assign(self, node: ast.Assign) -> None:
        value = self._value(node.value)
        for target in node.targets:
            key = self._rcparam_key(target)
            if key is not None:
                self._apply_rcparam(key, value, f"rcParams[{key!r}] assignment")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        key = self._rcparam_key(node.target)
        if key is not None:
            self._apply_rcparam(key, self._value(node.value), f"rcParams[{key!r}] assignment")
        self.generic_visit(node)

    def _record_color_keyword(self, key: str, value_node: ast.AST, event: str) -> None:
        value = self._value(value_node)
        if value is _UNKNOWN:
            # A colour chosen by a branch or read out of a literal table states every
            # colour the figure can draw, even when which one applies is data-dependent.
            choices = self._choices(value_node)
            if choices:
                for item in choices:
                    self._add_color(item, event=event)
                return
        if key == "colors" and isinstance(value, (list, tuple)):
            for item in value:
                self._add_color(item, event=event)
            return
        # ``tick_params(colors="#222222")`` is a scalar, which matplotlib accepts;
        # rejecting it for being spelled plural discarded a literal colour.
        self._add_color(value, event=event)

    def _record_prop_cycle(self, node: ast.Call, event: str) -> None:
        color_node = _keyword_value(node, "color", "colors")
        if color_node is None:
            self._dynamic("palette", event)
            return
        self._record_color_keyword("colors", color_node, event)

    def _record_grid_call(self, node: ast.Call, chain: list[str] | None = None) -> None:
        axis_node = _keyword_value(node, "axis")
        if axis_node is not None:
            axis = self._value(axis_node)
        elif chain and len(chain) >= 2 and chain[-2] in ("xaxis", "yaxis"):
            # ``ax.xaxis.grid(False)`` / ``ax.yaxis.grid(True, ...)`` control a
            # single axis; the receiver carries the axis the axis= kwarg would.
            axis = "x" if chain[-2] == "xaxis" else "y"
        else:
            axis = "both"
        # Receiver identity ("ax", "ax2", "axr", ...) so per-Axes grid state is
        # tracked separately; strip the xaxis/yaxis hop and the grid call itself.
        parts = [p for p in (chain or []) if p not in ("grid", "xaxis", "yaxis")]
        receiver = ".".join(parts)
        value_node = _keyword_value(node, "visible", "b")
        if value_node is None and node.args:
            first = self._value(node.args[0])
            if isinstance(first, bool):
                self._set_grid(first, "grid()", axis, receiver)
                return
            if first is _UNKNOWN:
                self._dynamic("grid", "dynamic grid() visibility")
                return
        if value_node is not None:
            self._set_grid(self._value(value_node), "grid()", axis, receiver)
        else:
            # ``Axes.grid()`` switches grid on if no visibility flag is given.
            self._set_grid(True, "grid()", axis, receiver)

    def _record_despine(self, node: ast.Call) -> None:
        for side in ("top", "right"):
            raw = self._value(_keyword_value(node, side))
            if raw is _UNKNOWN:
                raw = True
            if isinstance(raw, bool):
                if raw:
                    self.spines_removed.add(side)
                    self._event("spines_removed", f"despine({side}=True)")
            else:
                self._dynamic("spines_removed", f"dynamic despine({side}=...)")

    def _record_rc_call(self, node: ast.Call) -> None:
        group = self._value(node.args[0]) if node.args else _UNKNOWN
        if not isinstance(group, str):
            self._global_unknown("dynamic matplotlib.rc() group")
            return
        for keyword in node.keywords:
            if keyword.arg is None:
                self._global_unknown("matplotlib.rc() unpacked kwargs")
                continue
            key = f"{group}.{keyword.arg}"
            self._apply_rcparam(key, self._value(keyword.value), f"matplotlib.rc({key!r})")

    def _record_rc_update(self, node: ast.Call) -> None:
        if len(node.args) != 1 or node.keywords:
            self._global_unknown("dynamic rcParams.update()")
            return
        argument = node.args[0]
        if isinstance(argument, ast.Dict):
            # ``_apply_rcparam`` already scopes an unreadable value to the single
            # dimension its key touches. Literal-evaluating the whole mapping instead
            # escalated one non-literal colour constant into a global unknown, which
            # erased every dimension in the file -- including ones stated literally
            # in the same dict.
            for key_node, value_node in zip(argument.keys, argument.values):
                if key_node is None:
                    self._global_unknown("rcParams.update() unpacked mapping")
                    continue
                key = self._value(key_node)
                if not isinstance(key, str):
                    self._global_unknown("rcParams.update() non-string key")
                    continue
                self._apply_rcparam(key, self._value(value_node), f"rcParams.update({key!r})")
            return
        payload = self._value(argument)
        if not isinstance(payload, dict):
            self._global_unknown("dynamic rcParams.update()")
            return
        for key, value in payload.items():
            self._apply_rcparam(key, value, f"rcParams.update({key!r})")

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        chain = _attribute_chain(node.func)
        event = f"{'.'.join(chain) or name}()"

        if len(chain) >= 2 and chain[-2:] == ["style", "use"]:
            self._global_unknown("style.use()")
        elif name in {"set_theme", "set_style", "set_context"} and chain:
            self._global_unknown(f"{name}()")
        elif name == "update" and len(chain) >= 2 and chain[-2] == "rcParams":
            self._record_rc_update(node)
        elif name == "rc":
            self._record_rc_call(node)

        if name == "grid":
            self._record_grid_call(node, chain)
        elif name == "set_facecolor":
            if node.args:
                self._add_color(self._value(node.args[0]), background=True, event=event)
            else:
                self._dynamic("background", event)
        elif name == "set_size_inches":
            if len(node.args) >= 2:
                self._set_figsize((self._value(node.args[0]), self._value(node.args[1])), event)
            elif node.args:
                self._set_figsize(self._value(node.args[0]), event)
            else:
                self._dynamic("figure_aspect", event)
        elif name == "tick_params":
            direction = _keyword_value(node, "direction")
            if direction is not None:
                self._set_tick_direction(self._value(direction), event)
        elif name == "legend":
            self.has_legend = True
            frameon = _keyword_value(node, "frameon")
            if frameon is not None:
                self._set_legend_frame(self._value(frameon), event)
            else:
                self._event("legend_frame", event)
        elif name == "despine":
            self._record_despine(node)
        elif name in {"set_prop_cycle", "cycler"}:
            self._record_prop_cycle(node, event)
        elif name == "set_fontfamily":
            if node.args:
                self._set_font_family(self._value(node.args[0]), event)
            else:
                self._dynamic("serif", event)

        if name in _LINE_CALLS and isinstance(node.func, ast.Attribute):
            # A bare ``plot()`` is the script's own entry point, not an artist: a
            # matplotlib line call always has a receiver.
            if self._draws_no_line(node):
                # ``errorbar(..., fmt="none")``, ``plot(..., linestyle="none")``, a
                # positional ``"o"`` format, a one-point overlay: no segment is drawn, so
                # a linewidth would have no effect. Demanding one here vetoed every width
                # the script did state.
                self._event("linewidth", f"{event} draws no line")
            else:
                self.line_call_count += 1
                linewidth_node = _keyword_value(node, "linewidth", "lw")
                if linewidth_node is None:
                    self.line_calls_missing_width += 1
                else:
                    self._add_linewidths(linewidth_node, event)
        elif isinstance(node.func, ast.Attribute) or name not in _LINE_CALLS:
            # A stroke width is a stroke width wherever the script states it. The pool
            # already mixes ``set_linewidth`` on spines with line widths, and a patch
            # edge -- ``ax.add_patch(Wedge(..., linewidth=2.0))``, ``bar(..., lw=1.2)``,
            # ``pie(wedgeprops={"linewidth": 1.15})`` -- is one too. Only the veto below
            # stays tied to calls that actually draw a line.
            stroke = _keyword_value(node, "linewidth", "lw")
            if stroke is not None:
                self._add_linewidths(stroke, event)
            for keyword in node.keywords:
                if not (keyword.arg or "").endswith("props"):
                    continue
                props = self._value(keyword.value)
                if isinstance(props, dict):
                    for key in ("linewidth", "lw"):
                        if key in props:
                            self._add_linewidth(props[key], f"{event}[{keyword.arg}]")
                            break

        if name == "set_linewidth":
            if node.args:
                self._add_linewidths(node.args[0], event)
            else:
                self._dynamic("linewidth", event)

        if name in {"figure", "subplots", "subplot_mosaic"}:
            figsize = _keyword_value(node, "figsize")
            if figsize is not None:
                self._set_figsize(self._value(figsize), event)
            facecolor = _keyword_value(node, "facecolor")
            if facecolor is not None:
                self._add_color(self._value(facecolor), background=True, event=event)

        for keyword in node.keywords:
            if keyword.arg in _COLOR_KEYWORDS:
                self._record_color_keyword(keyword.arg, keyword.value, event)
            elif keyword.arg in {"fontfamily", "fontname"}:
                self._set_font_family(self._value(keyword.value), event)

        self.generic_visit(node)


def _feature_value(
    value: Any,
    known: bool,
    origin: str,
    reason: str = "",
    events: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "value": value,
        "known": bool(known),
        "origin": origin,
        "reason": reason,
        "events": list(events or []),
    }


def _spine_sides_hidden_in_loops(tree: ast.AST) -> set[str]:
    """Sides hidden by ``for <var> in (<sides>): ...spines[<var>].set_visible(False)``.

    Only literal string tuples/lists bound to a simple loop variable are
    unrolled, and only ``set_visible(False)`` on a ``spines[<var>]`` subscript
    counts -- the same evidence the lexical recognizer accepts for a literal
    index, just written as a loop.
    """
    hidden: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
            continue
        sides = _literal(node.iter)
        if not isinstance(sides, (list, tuple)):
            continue
        sides = [s for s in sides if isinstance(s, str) and s in _SPINE_SIDES]
        if not sides:
            continue
        var = node.target.id
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            func = inner.func
            if not isinstance(func, ast.Attribute) or func.attr != "set_visible":
                continue
            if len(inner.args) != 1 or _literal(inner.args[0]) is not False:
                continue
            target = func.value
            if not isinstance(target, ast.Subscript):
                continue
            chain = _attribute_chain(target.value)
            if not chain or chain[-1] != "spines":
                continue
            index = target.slice
            if isinstance(index, ast.Name) and index.id == var:
                hidden.update(sides)
    return hidden


def extract_style_features(code: str) -> dict[str, Any]:
    """Extract only code dimensions this scorer can defend reliably.

    Unknown styles, dynamic values, or syntax failures become ``known: false``.
    The scoring layer then preserves unavailable activated dimensions instead
    of silently changing the reference-defined denominator.
    """
    visitor = _StyleVisitor()
    parse_error = ""
    try:
        tree = ast.parse(code)
        const_env = _const_env(tree)
        choice_env = _loop_env(tree, const_env)
        choice_env.update(_param_env(tree, const_env, choice_env))
        visitor = _StyleVisitor(const_env, choice_env)
        visitor.visit(tree)
    except SyntaxError as exc:
        parse_error = f"syntax error: {exc.msg}"

    # Side-specific ``spines[...]`` forms are easier to audit with a narrow
    # lexical recognizer than with AST receiver reconstruction.
    for side in _SPINE_SIDES:
        quoted = re.escape(side)
        patterns = (
            rf"spines\s*\[\s*['\"]{quoted}['\"]\s*\]\s*\.\s*set_visible\s*\(\s*False\s*\)",
            rf"spines\s*\.\s*{quoted}\s*\.\s*set_visible\s*\(\s*False\s*\)",
        )
        if any(re.search(pattern, code, flags=re.IGNORECASE) for pattern in patterns):
            visitor.spines_removed.add(side)
            visitor._event("spines_removed", f"{side} spine hidden")

    # The lexical form above only sees literal indices. Hiding spines by looping
    # over a literal tuple of side names -- ``for side in ("top", "right"):
    # ax.spines[side].set_visible(False)`` -- is the same statement written once,
    # so unroll that loop and credit the same sides.
    if not parse_error:
        for side in _spine_sides_hidden_in_loops(tree):
            if side not in visitor.spines_removed:
                visitor.spines_removed.add(side)
                visitor._event("spines_removed", f"{side} spine hidden (loop)")

    defaults = matplotlib_default_style()

    def fallback_allowed(feature: str) -> bool:
        return not parse_error and not visitor.global_style_unknown and feature not in visitor.dynamic_dimensions

    def literal_or_default(
        feature: str,
        explicit_value: Any,
        default_value: Any,
        *,
        explicit_origin: str,
    ) -> dict[str, Any]:
        if parse_error:
            return _feature_value(
                value=None,
                known=False,
                origin="unavailable",
                reason=parse_error,
                events=visitor.events.get(feature),
            )
        if explicit_value is not None:
            return _feature_value(
                value=explicit_value,
                known=True,
                origin=explicit_origin,
                events=visitor.events.get(feature),
            )
        if fallback_allowed(feature):
            return _feature_value(
                value=default_value,
                known=True,
                origin="matplotlib_default",
                events=visitor.events.get(feature),
            )
        reason = "dynamic style value" if feature in visitor.dynamic_dimensions else "unsupported global style mutation"
        return _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason=reason,
            events=visitor.events.get(feature),
        )

    if parse_error:
        palette = _feature_value(None, False, "unavailable", parse_error, visitor.events["palette"])
    elif not visitor.colors and visitor.colors_unreadable:
        # Every colour this file draws with is computed. Falling through to the default
        # cycle would invent a value the candidate never stated.
        palette = _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason="every candidate colour is computed",
            events=visitor.events["palette"],
        )
    elif visitor.colors and "palette" not in visitor.dynamic_dimensions and fallback_allowed("palette"):
        palette = _feature_value(
            value=_dedupe(visitor.colors),
            known=True,
            origin="explicit",
            events=visitor.events["palette"],
        )
    elif fallback_allowed("palette"):
        palette = _feature_value(
            value=defaults["palette"],
            known=True,
            origin="matplotlib_default",
            events=visitor.events["palette"],
        )
    else:
        palette = _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason="dynamic palette value" if "palette" in visitor.dynamic_dimensions else "unsupported global style mutation",
            events=visitor.events["palette"],
        )

    if parse_error:
        background = _feature_value(None, False, "unavailable", parse_error, visitor.events["background"])
    elif visitor.facecolors and "background" not in visitor.dynamic_dimensions:
        background = _feature_value(
            value=visitor.facecolors[-1],
            known=True,
            origin="explicit",
            events=visitor.events["background"],
        )
    elif fallback_allowed("background"):
        background = _feature_value(
            value=defaults["background"],
            known=True,
            origin="matplotlib_default",
            events=visitor.events["background"],
        )
    else:
        background = _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason="dynamic background value" if "background" in visitor.dynamic_dimensions else "unsupported global style mutation",
            events=visitor.events["background"],
        )

    aspect_value = (
        visitor.figsize[0] / visitor.figsize[1]
        if visitor.figsize is not None and "figure_aspect" not in visitor.dynamic_dimensions
        else None
    )
    figure_aspect = literal_or_default(
        "figure_aspect",
        aspect_value,
        defaults["figure_aspect"],
        explicit_origin="explicit",
    )

    if visitor.linewidths and not visitor.line_calls_missing_width and "linewidth" not in visitor.dynamic_dimensions:
        ordered_linewidths = sorted(visitor.linewidths)
        linewidth = _feature_value(
            value=ordered_linewidths[len(ordered_linewidths) // 2],
            known=True,
            origin="explicit",
            events=visitor.events["linewidth"],
        )
    elif visitor.line_call_count > 0 and not visitor.linewidths:
        linewidth = literal_or_default(
            "linewidth", None, defaults["linewidth"], explicit_origin="explicit"
        )
    elif visitor.linewidths and fallback_allowed("linewidth"):
        # Some artists state a width and the rest are left alone. What the figure draws
        # is not ambiguous: the ones left alone render at the matplotlib default. Put
        # them in the pool at that width rather than discarding every width the script
        # did state.
        pool = sorted(visitor.linewidths + [float(defaults["linewidth"])] * visitor.line_calls_missing_width)
        linewidth = _feature_value(
            value=pool[len(pool) // 2],
            known=True,
            origin="explicit",
            events=visitor.events["linewidth"],
        )
    else:
        reason = "no reliably identified line primitive" if visitor.line_call_count == 0 else "mixed explicit/default line widths"
        linewidth = _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason=reason,
            events=visitor.events["linewidth"],
        )

    grid = literal_or_default("grid", visitor.grid, defaults["grid"], explicit_origin="explicit")

    if parse_error:
        spines_removed = _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason=parse_error,
            events=visitor.events["spines_removed"],
        )
    elif fallback_allowed("spines_removed"):
        spines_removed = _feature_value(
            value=sorted(visitor.spines_removed),
            known=True,
            origin="explicit" if visitor.spines_removed else "matplotlib_default",
            events=visitor.events["spines_removed"],
        )
    else:
        spines_removed = _feature_value(
            value=None,
            known=False,
            origin="unavailable",
            reason="dynamic spine visibility" if "spines_removed" in visitor.dynamic_dimensions else "unsupported global style mutation",
            events=visitor.events["spines_removed"],
        )

    tick_direction = literal_or_default(
        "tick_direction", visitor.tick_direction, defaults["tick_direction"], explicit_origin="explicit"
    )
    serif = literal_or_default("serif", visitor.font_serif, defaults["serif"], explicit_origin="explicit")

    if not visitor.has_legend:
        legend_frame = _feature_value(
            value=None,
            known=False,
            origin="not_applicable",
            reason="no legend call found",
            events=visitor.events["legend_frame"],
        )
    else:
        legend_frame = literal_or_default(
            "legend_frame", visitor.legend_frame, defaults["legend_frame"], explicit_origin="explicit"
        )

    return {
        "parse_ok": not bool(parse_error),
        "parse_error": parse_error or None,
        "global_style_unknown": visitor.global_style_unknown,
        "global_style_events": visitor.events["global"],
        "matplotlib_defaults": defaults,
        "features": {
            "palette": palette,
            "background": background,
            "figure_aspect": figure_aspect,
            "linewidth": linewidth,
            "grid": grid,
            "spines_removed": spines_removed,
            "tick_direction": tick_direction,
            "serif": serif,
            "legend_frame": legend_frame,
        },
    }


def directed_mean_nearest_delta_e(reference_colors: list[str], candidate_colors: list[str]) -> float:
    """Mean nearest CIEDE2000 distance from reference colors to candidates.

    It deliberately has no cardinality reward: extra arbitrary candidate colors
    cannot improve the score. The function calls the repository's calibrated
    :func:`ciede2000`, never an RGB proxy or a local reimplementation.
    """
    if not reference_colors or not candidate_colors:
        raise ValueError("directed color distance requires non-empty color lists")
    return sum(
        min(ciede2000(reference, candidate) for candidate in candidate_colors)
        for reference in reference_colors
    ) / len(reference_colors)


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def _feature_snapshot(feature: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": feature.get("value"),
        "known": bool(feature.get("known")),
        "origin": feature.get("origin"),
        "reason": feature.get("reason", ""),
        "events": feature.get("events", []),
    }


def _inactive_dimension(
    *,
    default: Any,
    reference: dict[str, Any],
    candidate: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "active": False,
        "status": "inactive",
        "score": None,
        "reason": reason,
        "default": default,
        "reference": _feature_snapshot(reference),
        "candidate": _feature_snapshot(candidate) if candidate is not None else None,
        "evidence": {},
    }


def _unavailable_dimension(
    *,
    default: Any,
    reference: dict[str, Any],
    candidate: dict[str, Any],
    reason: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "active": True,
        "status": "unavailable",
        "score": None,
        "reason": reason,
        "default": default,
        "reference": _feature_snapshot(reference),
        "candidate": _feature_snapshot(candidate),
        "evidence": evidence or {},
    }


def _scored_dimension(
    *,
    default: Any,
    reference: dict[str, Any],
    candidate: dict[str, Any],
    score: float,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "active": True,
        "status": "scored",
        "score": _clamp_unit(float(score)),
        "reason": "",
        "default": default,
        "reference": _feature_snapshot(reference),
        "candidate": _feature_snapshot(candidate),
        "evidence": evidence,
    }


def _categorical_dimension(
    default: Any,
    reference: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    if not reference["known"]:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference feature unavailable; activation cannot be determined",
        )
    if reference["value"] == default:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference matches Matplotlib default",
        )
    if not candidate["known"]:
        return _unavailable_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="candidate feature is not reliably extractable",
        )
    match = candidate["value"] == reference["value"]
    return _scored_dimension(
        default=default,
        reference=reference,
        candidate=candidate,
        score=1.0 if match else 0.0,
        evidence={"match": match},
    )


def _continuous_dimension(
    *,
    default: float,
    reference: dict[str, Any],
    candidate: dict[str, Any],
    distance: Any,
    activation_threshold: float,
) -> dict[str, Any]:
    if not reference["known"]:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference feature unavailable; activation cannot be determined",
        )
    reference_value = float(reference["value"])
    deviation = float(distance(default, reference_value))
    if deviation <= activation_threshold:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference deviation from Matplotlib default is below activation threshold",
        )
    if not candidate["known"]:
        return _unavailable_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="candidate feature is not reliably extractable",
            evidence={"reference_default_distance": deviation, "activation_threshold": activation_threshold},
        )
    candidate_value = float(candidate["value"])
    candidate_distance = float(distance(reference_value, candidate_value))
    score = _clamp_unit(1.0 - candidate_distance / deviation)
    return _scored_dimension(
        default=default,
        reference=reference,
        candidate=candidate,
        score=score,
        evidence={
            "reference_default_distance": deviation,
            "reference_candidate_distance": candidate_distance,
            "activation_threshold": activation_threshold,
        },
    )


def _palette_dimension(
    default: list[str], reference: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    if not reference["known"]:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference palette unavailable; activation cannot be determined",
        )
    reference_colors = list(reference["value"])
    default_distance = directed_mean_nearest_delta_e(reference_colors, default)
    if default_distance <= COLOR_DEVIATION_THRESHOLD:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference palette is not sufficiently different from Matplotlib default cycle",
        )
    if not candidate["known"]:
        return _unavailable_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="candidate palette is not reliably extractable",
            evidence={
                "reference_default_mean_delta_e": default_distance,
                "activation_threshold": COLOR_DEVIATION_THRESHOLD,
            },
        )
    candidate_colors = list(candidate["value"])
    candidate_distance = directed_mean_nearest_delta_e(reference_colors, candidate_colors)
    score = _clamp_unit(1.0 - candidate_distance / default_distance)
    return _scored_dimension(
        default=default,
        reference=reference,
        candidate=candidate,
        score=score,
        evidence={
            "metric": "directed_mean_nearest_ciede2000",
            "reference_default_mean_delta_e": default_distance,
            "reference_candidate_mean_delta_e": candidate_distance,
            "activation_threshold": COLOR_DEVIATION_THRESHOLD,
            "reference_color_count": len(reference_colors),
            "candidate_color_count": len(candidate_colors),
        },
    )


def _background_dimension(
    default: str, reference: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    if not reference["known"]:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference background unavailable; activation cannot be determined",
        )
    reference_value = str(reference["value"])
    default_distance = ciede2000(default, reference_value)
    if default_distance <= COLOR_DEVIATION_THRESHOLD:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference background is not sufficiently different from Matplotlib default",
        )
    if not candidate["known"]:
        return _unavailable_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="candidate background is not reliably extractable",
            evidence={
                "reference_default_delta_e": default_distance,
                "activation_threshold": COLOR_DEVIATION_THRESHOLD,
            },
        )
    candidate_distance = ciede2000(reference_value, str(candidate["value"]))
    score = _clamp_unit(1.0 - candidate_distance / default_distance)
    return _scored_dimension(
        default=default,
        reference=reference,
        candidate=candidate,
        score=score,
        evidence={
            "metric": "ciede2000",
            "reference_default_delta_e": default_distance,
            "reference_candidate_delta_e": candidate_distance,
            "activation_threshold": COLOR_DEVIATION_THRESHOLD,
        },
    )


def _spines_dimension(
    default: list[str], reference: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    if not reference["known"]:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference spine visibility unavailable; activation cannot be determined",
        )
    reference_removed = set(reference["value"])
    if not reference_removed:
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference keeps Matplotlib default full box spines",
        )
    if not candidate["known"]:
        return _unavailable_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="candidate spine visibility is not reliably extractable",
        )
    candidate_removed = set(candidate["value"])
    matched = reference_removed & candidate_removed
    return _scored_dimension(
        default=default,
        reference=reference,
        candidate=candidate,
        score=len(matched) / len(reference_removed),
        evidence={
            "reference_removed": sorted(reference_removed),
            "candidate_removed": sorted(candidate_removed),
            "matched_removed": sorted(matched),
        },
    )


def _legend_frame_dimension(
    default: bool, reference: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    if reference.get("origin") == "not_applicable":
        return _inactive_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            reason="reference has no legend; frame style has no content-blind code target",
        )
    if candidate.get("origin") == "not_applicable":
        # "This candidate draws no legend" is something the extractor established, not
        # something it failed to read. The reference styles its legend frame away from
        # the matplotlib default and this candidate does not reproduce that, so the
        # dimension is scored as the miss it is instead of discarding the whole sample.
        return _scored_dimension(
            default=default,
            reference=reference,
            candidate=candidate,
            score=0.0,
            evidence={"match": False, "candidate_has_no_legend": True},
        )
    return _categorical_dimension(default, reference, candidate)


def score_code_deviation(reference_code: str, candidate_code: str) -> dict[str, Any]:
    """Score one code pair against reference-defined Matplotlib deviations.

    The denominator is the number of activated reference dimensions. If a
    candidate is not reliably extractable for any activated dimension, the code
    channel is unavailable and ``score`` is ``None``. ``observed_partial_score``
    remains audit-only and is never sent into the final blend.
    """
    if not isinstance(reference_code, str) or not isinstance(candidate_code, str):
        raise TypeError("reference_code and candidate_code must be strings")

    reference_extraction = extract_style_features(reference_code)
    candidate_extraction = extract_style_features(candidate_code)
    defaults = matplotlib_default_style()
    reference = reference_extraction["features"]
    candidate = candidate_extraction["features"]

    dimensions = {
        "palette": _palette_dimension(defaults["palette"], reference["palette"], candidate["palette"]),
        "background": _background_dimension(defaults["background"], reference["background"], candidate["background"]),
        "figure_aspect": _continuous_dimension(
            default=float(defaults["figure_aspect"]),
            reference=reference["figure_aspect"],
            candidate=candidate["figure_aspect"],
            distance=lambda left, right: abs(math.log(left / right)),
            activation_threshold=ASPECT_DEVIATION_LOG_THRESHOLD,
        ),
        "linewidth": _continuous_dimension(
            default=float(defaults["linewidth"]),
            reference=reference["linewidth"],
            candidate=candidate["linewidth"],
            distance=lambda left, right: abs(math.log(left / right)),
            activation_threshold=LINEWIDTH_DEVIATION_LOG_THRESHOLD,
        ),
        "grid": _categorical_dimension(defaults["grid"], reference["grid"], candidate["grid"]),
        "spines_removed": _spines_dimension(
            defaults["spines_removed"], reference["spines_removed"], candidate["spines_removed"]
        ),
        "tick_direction": _categorical_dimension(
            defaults["tick_direction"], reference["tick_direction"], candidate["tick_direction"]
        ),
        "serif": _categorical_dimension(defaults["serif"], reference["serif"], candidate["serif"]),
        "legend_frame": _legend_frame_dimension(
            defaults["legend_frame"], reference["legend_frame"], candidate["legend_frame"]
        ),
    }

    activated = [name for name, item in dimensions.items() if item["active"]]
    scored = [name for name in activated if dimensions[name]["status"] == "scored"]
    unavailable = [name for name in activated if dimensions[name]["status"] == "unavailable"]
    observed_scores = [float(dimensions[name]["score"]) for name in scored]
    observed_partial_score = (100.0 * sum(observed_scores) / len(observed_scores)) if observed_scores else None

    if not activated:
        available = False
        status = "reference_has_no_activated_dimensions"
        score: float | None = None
    elif unavailable:
        available = False
        status = "candidate_feature_unavailable"
        score = None
    else:
        available = True
        status = "ok"
        score = 100.0 * sum(observed_scores) / len(observed_scores)

    return {
        "version": DEVIATION_DEFECT_SCORE_VERSION,
        "channel": "code_deviation",
        "available": available,
        "valid": available,
        "status": status,
        "score": score,
        "S_code": score,
        "formula": "mean(reference-activated dimension scores) * 100",
        "n_activated": len(activated),
        "n_scored": len(scored),
        "n_unavailable": len(unavailable),
        "coverage": (len(scored) / len(activated)) if activated else 0.0,
        "activated_dimensions": activated,
        "scored_dimensions": scored,
        "unavailable_dimensions": unavailable,
        "observed_partial_score": observed_partial_score,
        "dimensions": dimensions,
        "reference_extraction": reference_extraction,
        "candidate_extraction": candidate_extraction,
    }


def _normalise_bbox(value: Any) -> list[float | int]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("miss.bbox must be a list of exactly four coordinates")
    normalized: list[float] = []
    for coordinate in value:
        if isinstance(coordinate, bool):
            raise ValueError("miss.bbox coordinates must be numeric values in 0..1000")
        try:
            number = float(coordinate)
        except (TypeError, ValueError) as exc:
            raise ValueError("miss.bbox coordinates must be numeric values in 0..1000") from exc
        if not math.isfinite(number) or not 0.0 <= number <= 1000.0:
            raise ValueError("miss.bbox coordinates must be finite values in 0..1000")
        normalized.append(number)
    x0, y0, x1, y1 = normalized
    if not x0 < x1 or not y0 < y1:
        raise ValueError("miss.bbox must satisfy x0 < x1 and y0 < y1")
    return [_json_number(number) for number in normalized]


def parse_defect_response(
    raw_response: str,
    *,
    penalties: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Strictly parse and locally score one VLM defect-ledger response.

    Invalid JSON, Markdown wrappers, extra keys, unsupported severities, and
    malformed bboxes raise ``ValueError`` so the adapter retry wrapper can call
    the model again rather than caching a malformed score.
    """
    ledger = validate_penalties(penalties)
    if not isinstance(raw_response, str):
        raise ValueError("VLM response must be a string containing one JSON object")
    try:
        payload = json.loads(raw_response.strip())
    except json.JSONDecodeError as exc:
        raise ValueError(f"VLM response is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("VLM response must be a JSON object")
    if set(payload) != {"misses"}:
        raise ValueError("VLM response must contain exactly the top-level key 'misses'")
    misses_raw = payload["misses"]
    if not isinstance(misses_raw, list):
        raise ValueError("VLM response field 'misses' must be a list")

    misses: list[dict[str, Any]] = []
    for index, raw_miss in enumerate(misses_raw):
        if not isinstance(raw_miss, dict):
            raise ValueError(f"misses[{index}] must be an object")
        if set(raw_miss) != {"choice", "severity", "bbox"}:
            raise ValueError(
                f"misses[{index}] must contain exactly choice, severity, bbox"
            )
        choice = raw_miss["choice"]
        if not isinstance(choice, str) or not choice.strip():
            raise ValueError(f"misses[{index}].choice must be a non-empty string")
        severity = raw_miss["severity"]
        if severity not in SEVERITIES:
            raise ValueError(
                f"misses[{index}].severity must be one of {list(SEVERITIES)}, got {severity!r}"
            )
        bbox = _normalise_bbox(raw_miss["bbox"])
        misses.append(
            {
                "choice": choice.strip(),
                "severity": severity,
                "bbox": bbox,
                "penalty": _json_number(ledger[severity]),
            }
        )

    total_penalty = sum(float(miss["penalty"]) for miss in misses)
    return {
        "misses": misses,
        "n_misses": len(misses),
        "penalty": _json_number(total_penalty),
        "score": max(0.0, 100.0 - total_penalty),
        "parameters": {"penalties": _serializable_penalties(ledger)},
    }


def _require_file(label: str, path: Path | str) -> Path:
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} not found: {resolved}")
    return resolved


def score_vlm_defects(
    source_png: Path | str,
    candidate_png: Path | str,
    client: Any,
    *,
    penalties: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a VLM once and return a strict, fully auditable defect ledger."""
    source = _require_file("source_png", source_png)
    candidate = _require_file("candidate_png", candidate_png)
    if client is None or not callable(getattr(client, "complete_with_image", None)):
        raise TypeError("client must provide a callable complete_with_image method")
    ledger = validate_penalties(penalties)
    raw_response = client.complete_with_image(
        system=DEFECT_SYSTEM_PROMPT,
        user=DEFECT_USER_PROMPT,
        image_path=[source, candidate],
        response_format={"type": "json_object"},
    )
    parsed = parse_defect_response(raw_response, penalties=ledger)
    return {
        "version": DEVIATION_DEFECT_SCORE_VERSION,
        "channel": "vlm_defect_ledger",
        "available": True,
        "valid": True,
        "status": "ok",
        "score": parsed["score"],
        "S_vlm": parsed["score"],
        "formula": "max(0, 100 - sum(severity penalties))",
        "n_misses": parsed["n_misses"],
        "penalty": parsed["penalty"],
        "misses": parsed["misses"],
        "parameters": {"penalties": _serializable_penalties(ledger)},
        "model": str(getattr(client, "model", "") or ""),
        "raw_response": raw_response,
        "evidence": {
            "system_prompt": DEFECT_SYSTEM_PROMPT,
            "user_prompt": DEFECT_USER_PROMPT,
            "image_order": ["reference", "candidate"],
            "source_png": str(source),
            "candidate_png": str(candidate),
            "raw_response": raw_response,
            "misses": parsed["misses"],
        },
    }


def _channel_score(channel: Mapping[str, Any]) -> float | None:
    if not bool(channel.get("available")):
        return None
    raw_score = channel.get("score")
    if isinstance(raw_score, bool):
        return None
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(score) or not 0.0 <= score <= 100.0:
        return None
    return score


def combine_channels(
    code_channel: Mapping[str, Any],
    vlm_channel: Mapping[str, Any],
    *,
    code_weight: Any = DEFAULT_CODE_WEIGHT,
) -> dict[str, Any]:
    """Blend only available channels and renormalize effective weights."""
    nominal_code_weight = validate_code_weight(code_weight)
    nominal_vlm_weight = 1.0 - nominal_code_weight
    code_score = _channel_score(code_channel)
    vlm_score = _channel_score(vlm_channel)

    available: list[tuple[str, float, float]] = []
    if code_score is not None:
        available.append(("code", code_score, nominal_code_weight))
    if vlm_score is not None:
        available.append(("vlm", vlm_score, nominal_vlm_weight))
    if not available:
        return {
            "version": DEVIATION_DEFECT_SCORE_VERSION,
            "available": False,
            "valid": False,
            "status": "no_available_channels",
            "score": None,
            "S": None,
            "formula": "renormalized weighted mean of available channels",
            "parameters": {
                "code_weight": nominal_code_weight,
                "vlm_weight": nominal_vlm_weight,
            },
            "effective_weights": {"code": 0.0, "vlm": 0.0},
        }

    nominal_mass = sum(weight for _, _, weight in available)
    if nominal_mass == 0.0:
        # If config deliberately assigns an unavailable channel all weight,
        # retain the sample with the available evidence rather than 0/0.
        effective = {name: 1.0 / len(available) for name, _, _ in available}
    else:
        effective = {name: weight / nominal_mass for name, _, weight in available}
    score = sum(value * effective[name] for name, value, _ in available)
    return {
        "version": DEVIATION_DEFECT_SCORE_VERSION,
        "available": True,
        "valid": True,
        "status": "ok",
        "score": score,
        "S": score,
        "formula": "renormalized weighted mean of available channels",
        "parameters": {
            "code_weight": nominal_code_weight,
            "vlm_weight": nominal_vlm_weight,
        },
        "effective_weights": {
            "code": effective.get("code", 0.0),
            "vlm": effective.get("vlm", 0.0),
        },
        "channel_scores": {"code": code_score, "vlm": vlm_score},
    }


def score_deviation_defect(
    source_py: Path | str,
    source_png: Path | str,
    candidate_py: Path | str,
    candidate_png: Path | str,
    client: Any,
    *,
    code_weight: Any = DEFAULT_CODE_WEIGHT,
    penalties: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Score one reference/candidate pair with the production scorer.

    The keyword parameters are deliberately explicit so evaluator YAML and its
    fingerprint can document runtime behaviour. Defaults freeze the accepted
    release setting: ``code_weight=0.35`` and ``minor/major/critical=5/10/25``.
    """
    source_code_path = _require_file("source_py", source_py)
    source_image_path = _require_file("source_png", source_png)
    candidate_code_path = _require_file("candidate_py", candidate_py)
    candidate_image_path = _require_file("candidate_png", candidate_png)
    normalized_weight = validate_code_weight(code_weight)
    normalized_penalties = validate_penalties(penalties)

    code_channel = score_code_deviation(
        source_code_path.read_text(encoding="utf-8", errors="replace"),
        candidate_code_path.read_text(encoding="utf-8", errors="replace"),
    )
    vlm_channel = score_vlm_defects(
        source_image_path,
        candidate_image_path,
        client,
        penalties=normalized_penalties,
    )
    combined = combine_channels(code_channel, vlm_channel, code_weight=normalized_weight)
    # The VLM parser either returns a valid ledger or raises ValueError for
    # adapter retry. Therefore an unavailable code channel never drops a row.
    if not combined["available"]:  # pragma: no cover - defensive future change
        raise RuntimeError("deviation-defect scorer has no available channel")

    parameters = {
        "code_weight": normalized_weight,
        "vlm_weight": 1.0 - normalized_weight,
        "penalties": _serializable_penalties(normalized_penalties),
    }
    formula = (
        "renormalized "
        f"{normalized_weight:g} code / {1.0 - normalized_weight:g} "
        "VLM defect-ledger blend"
    )
    return {
        "version": DEVIATION_DEFECT_SCORE_VERSION,
        "valid": True,
        "status": "ok",
        "score": combined["score"],
        "S": combined["score"],
        "S_code": code_channel["score"],
        "S_vlm": vlm_channel["score"],
        "formula": formula,
        "parameters": parameters,
        "channels": {"code": code_channel, "vlm": vlm_channel},
        "code": code_channel,
        "vlm": vlm_channel,
        "combination": combined,
        "raw_response": vlm_channel["raw_response"],
        "evidence": {
            "code_dimensions": code_channel["dimensions"],
            "defect_ledger": vlm_channel["misses"],
            "raw_vlm_response": vlm_channel["raw_response"],
        },
        "paths": {
            "source_py": str(source_code_path),
            "source_png": str(source_image_path),
            "candidate_py": str(candidate_code_path),
            "candidate_png": str(candidate_image_path),
        },
    }


__all__ = [
    "ASPECT_DEVIATION_LOG_THRESHOLD",
    "COLOR_DEVIATION_THRESHOLD",
    "DEFAULT_CODE_WEIGHT",
    "DEFAULT_PENALTIES",
    "DEFECT_SYSTEM_PROMPT",
    "DEFECT_USER_PROMPT",
    "DEVIATION_DEFECT_SCORE_VERSION",
    "LINEWIDTH_DEVIATION_LOG_THRESHOLD",
    "SEVERITIES",
    "combine_channels",
    "directed_mean_nearest_delta_e",
    "extract_style_features",
    "matplotlib_default_style",
    "parse_defect_response",
    "score_code_deviation",
    "score_deviation_defect",
    "score_vlm_defects",
    "validate_code_weight",
    "validate_penalties",
]
