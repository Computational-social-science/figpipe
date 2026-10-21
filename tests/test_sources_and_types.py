"""Source PDFs are read-only, and figure types must be a partition that can evolve.

WHY THESE TWO THINGS SIT TOGETHER
    Both are about the same mistake: treating an assumption as a guarantee.

    * The published PDFs are the project's INPUT. An audit found no script currently writes to
      them, but "no script does it today" is not protection -- one `shutil.rmtree(root)` in a
      future edit would destroy a library that git cannot restore.
    * "Nature has one figure standard" is the other assumption, and it has already done damage
      twice: H02's ink band was measured on six line plots and generalised to "figures"; the
      owner's instruction is explicit that there is NO single absolute standard and the
      classification must be scientific and iterable.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

sources = pytest.importorskip("figpipe.sources", reason="source guard absent")
ftypes = pytest.importorskip("figpipe.figuretypes", reason="type classifier absent")

TYPES = ROOT / "corpus" / "figure_types.json"


# ---------------------------------------------------------------- source protection

def test_a_source_pdf_path_cannot_be_written():
    """THE HARD RULE: nothing may write inside the read-only roots."""
    for probe in (pathlib.Path("D:/2026-AI4S/paper.pdf"),
                  pathlib.Path("D:/anything/x.pdf"),
                  pathlib.Path("C:/keystroke-corpus/f.txt")):
        with pytest.raises(sources.SourceProtectionError):
            sources.assert_writable(probe)


def test_project_paths_remain_writable():
    """The guard must not be so eager that the pipeline cannot run."""
    ok = sources.assert_writable(ROOT / "corpus" / "extracted" / "x.json")
    assert str(ok).startswith(str(ROOT))


def test_no_script_deletes_inside_a_source_root():
    """A static check: the destructive helpers must route through the guard.

    Reading the source is weaker than running it, but it catches the case that matters -- a
    new `shutil.rmtree(...)` added without the guard.
    """
    offenders = []
    for p in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "figpipe").glob("*.py")):
        text = p.read_text(encoding="utf-8", errors="replace")
        if "rmtree" not in text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "rmtree" in line and "_assert_writable" not in text and "assert_writable" not in text:
                offenders.append(f"{p.name}:{i}")
    assert not offenders, (
        "these files call rmtree without routing through the source guard: "
        + ", ".join(offenders))


def test_fingerprint_detects_a_change():
    """The fingerprint must actually notice a modification, or it proves nothing."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        (d / "a.pdf").write_bytes(b"one")
        # full=True hashes content. Metadata alone can miss a same-length rewrite inside one
        # filesystem timestamp tick -- this test caught exactly that, which is why the content
        # hash, not the size, is what the guarantee rests on.
        before = sources.fingerprint(d, full=True)
        (d / "a.pdf").write_bytes(b"two")
        after = sources.fingerprint(d, full=True)
        diff = sources.compare_fingerprints(before, after)
        assert diff["modified"], "a modified PDF was not detected"
        assert not diff["unchanged"]


# ---------------------------------------------------------------- figure typing

def test_classification_is_a_partition_not_a_guess():
    """Every figure gets exactly one type, and 'unclassified' is a real bucket.

    Forcing an unknown figure into a plausible bucket is how a distribution silently absorbs
    the cases that do not fit. 105 of 275 figures are unclassified -- reported, not hidden.
    """
    if not TYPES.is_file():
        pytest.skip("figure types not computed")
    d = json.loads(TYPES.read_text(encoding="utf-8"))
    assigns = d["assignments"]
    assert len(assigns) == d["summary"]["n"] > 100
    for a in assigns:
        assert a["figure_type"], "a figure has no type"
        assert a["confidence"] in ("caption", "geometry", "none")
    # and the types must not all be one bucket
    assert len(d["summary"]["by_type"]) >= 5, "classification collapsed into one type"


def test_caption_evidence_is_stronger_than_geometry():
    """Confidence must reflect WHAT decided it, so a reader can weigh the labels."""
    if not TYPES.is_file():
        pytest.skip("figure types not computed")
    d = json.loads(TYPES.read_text(encoding="utf-8"))
    for a in d["assignments"]:
        if a["confidence"] == "caption":
            assert a["evidence"] and a["figure_type"] != "unclassified"
        elif a["confidence"] == "geometry":
            assert "aspect" in a["evidence"]
        else:
            assert a["figure_type"] == "unclassified"


def test_rules_are_ordered_and_micrograph_wins_over_scatter():
    """Order matters: a micrograph caption often mentions axes and statistics."""
    got = ftypes.classify("Electron micrograph with a scale bar; error bars show s.d.", 90, 90)
    assert got["figure_type"] == "micrograph", (
        f"a micrograph was classified as {got['figure_type']}; the type rules must check "
        f"imaging before plotting or every micrograph becomes a scatter")


def test_unclassified_is_reachable():
    """A caption with no signal must land in unclassified, not in the nearest-looking bucket."""
    got = ftypes.classify("A photograph of the authors at the conference.", 100, 100)
    assert got["figure_type"] == "unclassified"
    assert got["confidence"] == "none"


def test_types_are_split_by_document_kind():
    """Main text, Extended Data and supplements follow different conventions.

    This is the correction of E01/E02, which averaged over all three and then reported the
    result as "Nature figures".
    """
    if not TYPES.is_file():
        pytest.skip("figure types not computed")
    d = json.loads(TYPES.read_text(encoding="utf-8"))
    kinds = d["summary"]["by_kind"]
    assert len(kinds) >= 2, (
        "types are not split by document kind; a single pooled distribution is what went "
        "wrong with E01/E02")
    for kind, dist in kinds.items():
        assert sum(dist.values()) > 0
