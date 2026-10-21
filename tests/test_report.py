"""The HTML report is the only report format: English, self-contained, and generated from evidence.

WHY THESE TESTS
    The owner asked for an HTML progress report and for scientific work to be in English. A report
    that is generated is only useful if it stays self-contained (no broken local links / external
    CDNs) and stays in the required language. These checks are cheap and they fail loudly.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

report = None
try:
    import build_report as report  # noqa: F401
except Exception:                                      # pragma: no cover - optional deps
    report = None


def test_report_is_english_self_contained_and_has_the_key_evidence(tmp_path):
    if report is None:
        import pytest
        pytest.skip("report builder unavailable in this environment")
    out = report.build(tmp_path / "figpipe_report.html", live_tests=False)
    text = pathlib.Path(out).read_text(encoding="utf-8")
    assert text.startswith("<!DOCTYPE html>")
    assert "PlotTwin-Bench" in text
    bench = json.loads((ROOT / "corpus/e2e/plottwin_report.json").read_text(encoding="utf-8"))
    assert f'{bench["mean_distance"]:.3f}' in text
    assert "Progress overview" in text and "Research deliverables" in text
    assert not re.search(r"[\u4e00-\u9fff]", text), "report must be English-only"
    # Forbid Python's None leaking into the page as a VALUE. The bare word "None" is also ordinary
    # English ("None is counted as passing"), so match the shapes a leaked value takes: a standalone
    # cell, a metric value, or a label position.
    leaked = re.findall(r"(?:>|: |\| )None(?:<|,|\s*$)", text)
    assert not leaked, f"Python's None leaked into the report: {leaked[:3]}"
    assert 'src="http' not in text and "<script src=" not in text
