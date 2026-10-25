"""Every module-level import must be a declared dependency.

WHY THIS EXISTS
    `pip install -e .` in a clean venv exited 0, and the user's FIRST line failed:

        ModuleNotFoundError: No module named 'pandas'

    `pyproject.toml` declared matplotlib and pymupdf only, while the package imports numpy and pandas
    at module level. **`pip install` reporting success and the package failing on first use is the
    worst kind of broken**, because nothing in the install tells the user.

THE RULE
    A module-level import is part of the install contract. A GUARDED import (inside try/except) is an
    optional feature and belongs in `[project.optional-dependencies]` with its reason. The two are
    different promises and must be checked differently.
"""
from __future__ import annotations

import ast
import pathlib
import sys
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "figpipe"

#: Import names that are not the distribution name on PyPI.
IMPORT_TO_DIST = {
    "PIL": "pillow",
    "fitz": "pymupdf",
    "pymupdf": "pymupdf",
    "PyPDF2": "pypdf2",
    "pypdf": "pypdf",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "pandas": "pandas",
    "scienceplots": "scienceplots",
    "mcts": "mcts",
    "paperplot": "paperplot",
}

#: Vendored or in-repo modules -- they ship with the package and need no declaration.
#:
#: `mcts` lives in `third_party/mcts` and is reached by a `sys.path.insert` in search.py, so it is as
#: vendored as harness2_ledger is -- the only difference is that it is imported by bare name after the
#: path insert rather than as a subpackage.
VENDORED = {"harness2_ledger", "plottwin_scorer", "decision_service", "figpipe", "mcts"}


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _declared() -> set[str]:
    project = _pyproject().get("project", {})
    names: set[str] = set()
    for spec in project.get("dependencies") or []:
        names.add(spec.split(">")[0].split("<")[0].split("=")[0].split("[")[0].strip().lower())
    for group in (project.get("optional-dependencies") or {}).values():
        for spec in group:
            names.add(spec.split(">")[0].split("<")[0].split("=")[0].split("[")[0].strip().lower())
    return names


def _module_level_imports() -> dict[str, set[str]]:
    """Third-party names imported at module level (indent 0), mapped to the files that do it."""
    found: dict[str, set[str]] = {}
    for path in PACKAGE.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in tree.body:                      # ONLY module level, not inside try/except
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in sys.stdlib_module_names or name in VENDORED or name == "__future__":
                    continue
                found.setdefault(name, set()).add(path.name)
    return found


def test_every_module_level_import_is_declared():
    """THE DEFECT. This is the check that would have caught the clean-venv failure."""
    declared = _declared()
    missing = {}
    for name, files in _module_level_imports().items():
        dist = IMPORT_TO_DIST.get(name, name).lower()
        if dist not in declared:
            missing[name] = sorted(files)
    assert not missing, (
        f"these module-level imports are not declared in pyproject.toml, so `pip install` will "
        f"succeed and the package will fail on first use: {missing}. Declared: {sorted(declared)}")


def test_the_core_data_dependencies_are_required_not_optional():
    """pandas and numpy are used by the ENTRY POINTS the README advertises; they are not extras."""
    declared = _declared()
    required = set()
    for spec in (_pyproject().get("project", {}).get("dependencies") or []):
        required.add(spec.split(">")[0].split("<")[0].split("=")[0].strip().lower())
    for name in ("pandas", "numpy", "matplotlib", "pymupdf"):
        assert name in required, (
            f"{name} is imported at module level but is not a REQUIRED dependency; a user following "
            f"the README's entry points would hit ImportError")


def test_optional_features_are_extras():
    """THE OTHER DIRECTION. A guarded import must be an extra, not a hard requirement -- otherwise the
    package refuses to install for someone who never uses that feature."""
    project = _pyproject().get("project", {})
    extras = project.get("optional-dependencies") or {}
    flat = {spec.split(">")[0].split("<")[0].split("=")[0].strip().lower()
            for group in extras.values() for spec in group}
    # these are guarded in the source and must be extras
    for name in ("pillow", "scienceplots"):
        assert name in flat, (
            f"{name} is imported inside a try/except and should be an optional dependency")


def test_the_version_is_declared():
    """A package that installs as 0.1.0 while reporting 0.6.0 at runtime is two packages."""
    import figpipe
    declared = _pyproject()["project"]["version"]
    runtime = getattr(figpipe, "__version__", None)
    assert runtime is not None, "figpipe has no __version__"
    assert declared == runtime, (
        f"pyproject says version {declared!r} but figpipe.__version__ is {runtime!r}; an installed "
        f"package would report a version nobody published")
