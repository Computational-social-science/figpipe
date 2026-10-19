"""The logical audit must stay true as the pipeline changes.

WHY THIS TEST
    LOGICAL_AUDIT.md claims, entry by entry, that a specific class of logical defect was found and
    fixed. A claim like that rots silently: the fix stays, someone refactors, and the document keeps
    asserting something no longer true. These tests check the claims that are mechanically
    checkable, so the audit cannot become a fossil.

    The ones that are NOT mechanically checkable (measurement validity, residual risk) are stated
    as residual risk in the document itself -- that is the honest way to leave them.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "LOGICAL_AUDIT.md"


def test_the_audit_document_exists_and_names_the_sections():
    if not AUDIT.is_file():
        pytest.skip("LOGICAL_AUDIT.md absent")
    text = AUDIT.read_text(encoding="utf-8")
    for heading in ("Measurement validity", "Reference class", "Input assumptions",
                    "Verification completeness", "State and timing", "What is NOT audited"):
        assert heading in text, f"the audit dropped the {heading!r} section"


def test_the_audit_states_residual_risk_rather_than_claiming_perfection():
    """An audit that concludes "no defects" is not an audit."""
    if not AUDIT.is_file():
        pytest.skip("LOGICAL_AUDIT.md absent")
    text = AUDIT.read_text(encoding="utf-8").lower()
    assert "residual risk" in text, "the audit must state what remains unvalidated"
    assert "no known logical defect" in text
    # and it must NOT ASSERT the absence of all defects. Check for an assertive form only:
    # "the pipeline has no defects", "there are no defects" -- the document legitimately says
    # "the honest summary is therefore not 'no defects'", which is the opposite of a claim.
    import re
    for pattern in (r"pipeline has no defects", r"there are no defects",
                    r"has no logical defect\b(?!s)", r"contains no defects"):
        assert not re.search(pattern, text), (
            f"the audit asserts the absence of defects: /{pattern}/")


def test_the_fixes_the_audit_claims_are_actually_present():
    """Each 'Fixed' claim in the audit must correspond to code that exists now."""
    sys.path.insert(0, str(ROOT))
    from figpipe import codegen, skills, styleprofile
    # 1. Wasserstein size distance, not a 1-pt histogram
    assert hasattr(styleprofile, "_size_distance")
    # 2. three-valued freshness lives in the benchmark harness
    sys.path.insert(0, str(ROOT / "scripts"))
    import bench_plottwin as bench
    assert hasattr(bench, "freshness")
    # 3. non-finite aspect is refused
    import numpy as np
    import pandas as pd
    from figpipe import composite
    df = pd.DataFrame({"x": np.arange(8.0), "y": np.linspace(0, 1, 8)})
    panel = composite.Panel("trend_band", df, {"x": "x", "y": "y", "fit": "lm"})
    with pytest.raises(codegen.CodegenError):
        codegen.emit([panel], style={"figure_aspect": float("nan")})
    # 4. a bar axis has a category budget
    src = (ROOT / "figpipe" / "skills.py").read_text(encoding="utf-8")
    assert "MAX_BARS" in src, "the bar category budget is gone"
    # 5. a long table is pivoted before being drawn as a matrix
    assert "encode.matrix.pivot" in src
    # 6. edge-corrected rule detection
    prof_src = (ROOT / "figpipe" / "styleprofile.py").read_text(encoding="utf-8")
    assert "EDGE CORRECTION IS MANDATORY" in prof_src


def test_the_audit_does_not_overstate_what_was_compared():
    """The pipeline was NOT compared head-to-head with any other system."""
    if not AUDIT.is_file():
        pytest.skip("LOGICAL_AUDIT.md absent")
    text = AUDIT.read_text(encoding="utf-8").lower()
    assert "head-to-head" in text
    assert "no comparison" in text or "not claimed" in text
