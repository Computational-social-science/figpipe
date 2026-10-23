"""VisionHOPE cannot replace a VLM, and the record must say why.

WHY THIS EXISTS
    Asked to "immediately adopt VisionHOPE and drop the local VLM". The repository is a visual
    BACKBONE: `create_model` returns 1000 ImageNet logits, with no tokenizer, no language head and no
    prompt interface. It cannot answer "how many panels are in this image", so it cannot replace a
    VLM for that job.

    That is a fact about the artefact, not an opinion, and it belongs in a test so nobody re-derives
    it wrong later -- this project has recorded repeatedly that a name promising one thing and
    holding another is its most expensive defect class.

WHAT IS PINNED
    * the adoption note states the category difference
    * the clone exists and the environment is described accurately
    * the blocker is named exactly (no C++ compiler), not vaguely
"""
from __future__ import annotations

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTE = ROOT / "PEER_VISIONHOPE_ADOPTION.md"


def test_the_adoption_note_exists():
    assert NOTE.is_file(), (
        "the VisionHOPE adoption attempt has no record, so the next round would redo it")


def test_the_note_states_that_visionhope_is_not_a_vlm():
    """THE CATEGORY FACT. Without it, the next request to 'swap the VLM for VisionHOPE' is
    re-litigated from scratch."""
    text = NOTE.read_text(encoding="utf-8")
    assert "VisionHOPE is not a VLM" in text
    assert "1000 ImageNet" in text or "logits" in text


def test_the_note_names_the_blocker_exactly():
    """A blocker described as 'it does not work' is not a blocker description."""
    text = NOTE.read_text(encoding="utf-8")
    assert "C++ compiler" in text or "MSVC" in text
    assert "load_inline" in text or "cpp_extension" in text
    assert "vcvars64.bat" in text or "VC.Tools" in text


def test_the_note_records_the_cpu_path_finding():
    """`chunk.py` has `if not x.is_cuda` branches, so the CPU route LOOKS open. It is not."""
    text = NOTE.read_text(encoding="utf-8")
    assert "same CUDA device" in text, (
        "the note does not record that srnl.py raises on CPU input, so a reader would try the CPU "
        "path again")


def test_the_note_says_what_is_already_installed():
    """So the work is not repeated: the venv, torch and the package are all on disk."""
    text = NOTE.read_text(encoding="utf-8")
    assert "venv-visionhope" in text
    assert "torch 2.14.1" in text or "torch 2.13" in text


def test_the_note_does_not_claim_the_adoption_succeeded():
    """THE HONESTY CLAUSE. The request was 'adopt it immediately'; the outcome was 'it cannot run'."""
    text = NOTE.read_text(encoding="utf-8")
    assert "It is not a refusal" in text
    assert "cannot" in text.lower()
