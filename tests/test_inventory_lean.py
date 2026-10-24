"""A tracked file must not carry fields nothing reads.

WHY THIS EXISTS
    `corpus/extracted/pdf_inventory.json` was 1893 KB and 793 KB of it was `page0_text_head` -- a
    600-character preview of each PDF's first page. Two scripts WROTE it
    (`classify_corpus.py:61`, `extract_corpus.py:265`) and no code anywhere READ it.

    The tracked-size budget then failed at 80.09 MB against a limit of 80.0 -- by 90 KB. **The budget
    was doing its job**: a tracked file carrying 38 % dead weight is exactly what it exists to surface,
    and trimming a real field is the honest fix rather than raising the limit.

THE RULE
    A field that is written and never read is dead weight in a TRACKED file. The inventory is
    regenerable, so a preview kept "for debugging" costs every clone forever.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "corpus" / "extracted" / "pdf_inventory.json"


def test_the_inventory_has_no_unread_preview_field():
    """THE DEFECT. `page0_text_head` was written twice and read nowhere."""
    if not INVENTORY.is_file():
        pytest.skip("inventory absent")
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    records = data.get("kept") or []
    if not records:
        pytest.skip("no kept records")
    offenders = [r.get("path", "?") for r in records if "page0_text_head" in r]
    assert not offenders, (
        f"{len(offenders)} inventory records carry `page0_text_head`, which no code reads; "
        f"it is ~790 KB of a tracked file. First: {offenders[0]}")


def test_the_inventory_is_smaller_than_it_was():
    """A REGRESSION GUARD. The file was 1893 KB with the preview and 1100 KB without."""
    if not INVENTORY.is_file():
        pytest.skip("inventory absent")
    kb = INVENTORY.stat().st_size / 1024
    assert kb < 1300, (
        f"the inventory grew back to {kb:.0f} KB; the unread preview is probably back")


def test_no_tracked_json_carries_a_large_unread_string_field():
    """THE GENERAL FORM, bounded so it does not scan the whole repo on every run.

    Only the two inventory files are checked -- they are the ones built by scanning a corpus, which is
    where a preview field is most likely to accumulate.
    """
    for candidate in (INVENTORY, ROOT / "corpus" / "pdf_inventory.json"):
        if not candidate.is_file():
            continue
        data = json.loads(candidate.read_text(encoding="utf-8"))
        records = data.get("kept") or data if isinstance(data, list) else data.get("kept") or []
        if not isinstance(records, list) or not records:
            continue
        sample = records[0]
        for field, value in (sample.items() if isinstance(sample, dict) else []):
            if isinstance(value, str) and len(value) > 400:
                pytest.fail(
                    f"{candidate.name} carries a {len(value)}-character string in {field!r}; "
                    f"if nothing reads it, it is dead weight in a tracked file")
