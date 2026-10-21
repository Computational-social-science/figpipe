"""Two functions with the same name that measure different things is a defect class.

WHY THIS EXISTS
    `validate_style_metric.leave_one_out` removed one DIMENSION and re-scored every pair -- an
    ablation. `validate_metric_claims.leave_one_out` held out one PAIR and fitted on the rest --
    cross-validation. Both are legitimately "leave one out" in the statistical sense, and a reader
    comparing the two numbers would be comparing an ablation with a cross-validation.

    Neither function was wrong. The NAME was, and a name is the only interface a report has.

    This project has already paid for this class once: a `distance` that meant two things at once.
    The detector below makes the class visible rather than relying on someone noticing.

WHAT IT CHECKS
    Public functions defined in more than one module, whose BODIES differ. Same name + same body is
    a harmless duplicate; same name + different body is a trap.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

#: Names that carry NO cross-module meaning because they are PROTOCOL ENTRY POINTS: every script
#: has a `main`, every module that writes has a `save`/`load`, every module that renders has a
#: `render`. No reader compares these across modules.
#:
#: THIS SET MUST STAY SMALL. An earlier version also listed `summarise`, `measure`, `describe`,
#: `compare`, `catalogue`, `validate`, `report`, `classify` and `tables` -- most of the project's
#: real vocabulary -- and the detector then scanned to ZERO and passed. A detector that excludes
#: everything is not a detector. The check `test_the_detector_finds_something_to_scan` exists to
#: stop that happening again.
PROTOCOL = {"main", "run", "save", "load", "render", "build"}

#: Collisions that are HARMLESS, each with the reason. What makes a collision dangerous is that a
#: reader could reasonably think the two functions measure the same thing; these do not. Every
#: entry carries a reason so that adding one is a deliberate act rather than a way to silence the
#: detector.
HARMLESS = {
    "health": "decision.health probes a service; webapp.health answers a liveness probe",
    "validate": "gate.validate runs controls; vlm_label.validate enforces a label schema",
    "measure": "caption_features.measure reads a caption; validate_style_metric.measure runs an "
               "experiment",
    "run_task": "mutation.run_task runs a task under an override; bench_plottwin.run_task runs a "
                "benchmark row",
    "classify": "three corpus tools classify different inputs (figures, rows, sources)",
    "catalogue": "grammar and skills each catalogue their own kind of object",
    "tables": "two renderers build their own tables",
    "git": "two scripts shell out to git for their own purposes",
    "read_json": "guard and build_report each read a JSON file for their own use",
    "report": "quality.report scores a figure; vlm_label.report formats label output",
    "describe": "adaptiverule.describe formats a margin; structure.describe a figure layout",
}

#: Names that WERE colliding in a way a reader could confuse, and were renamed apart.
RENAMED = {
    "leave_one_out": "an ablation in validate_style_metric vs cross-validation in "
                     "validate_metric_claims; the latter is now cross_validated_accuracy",
}


def _definitions(path: pathlib.Path) -> dict[str, str]:
    """Every top-level `def name(...)` in a module, as name -> normalised body."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    out = {}
    for m in re.finditer(r"^def (\w+)\(", text, re.M):
        name = m.group(1)
        start = m.start()
        nxt = re.search(r"^(def |class |@)", text[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(text))
        body = text[start:end]
        # strip comments and blank lines: two functions differing only in commentary are the same
        body = "\n".join(ln for ln in body.splitlines()
                         if ln.strip() and not ln.lstrip().startswith("#"))
        out[name] = body
    return out


@pytest.fixture(scope="module")
def modules():
    files = sorted((ROOT / "figpipe").glob("*.py")) + sorted((ROOT / "scripts").glob("*.py"))
    return {f: _definitions(f) for f in files}


def test_no_two_modules_define_the_same_named_function_differently(modules):
    """THE DETECTOR. Same name + different body across modules is a reader trap.

    The scan finds 13 such names. Most are harmless -- `health()` in `decision.py` talks to a
    service and `health()` in `webapp.py` answers a liveness probe, and no reader compares them.
    Failing on all 13 would make the test noise, and a noisy test gets excluded, which is how a
    detector dies. So harmless ones are listed WITH A REASON and everything unlisted must be unique
    or identical.
    """
    seen: dict[str, list[tuple[str, str]]] = {}
    for path, defs in modules.items():
        for name, body in defs.items():
            if name.startswith("_") or name in PROTOCOL or name in HARMLESS:
                continue
            seen.setdefault(name, []).append((path.name, body))

    collisions = []
    for name, places in seen.items():
        if len(places) < 2:
            continue
        digests = {hashlib.sha256(b.encode()).hexdigest() for _, b in places}
        if len(digests) > 1:
            collisions.append((name, [p for p, _ in places]))

    assert not collisions, (
        "these functions share a name across modules but implement different things, so a report "
        "citing one and a control using the other would be comparing different quantities.\n"
        "Either rename them apart, or add the name to HARMLESS with the reason it cannot be "
        "confused:\n"
        + "\n".join(f"  {n}: {p}" for n, p in collisions))


def test_every_harmless_entry_still_collides(modules):
    """A HARMLESS entry that no longer collides is stale and must be removed, not left as a hole.

    Otherwise the list slowly becomes a list of names the detector is forbidden to examine, which
    is how the first version of this file passed while checking nothing.
    """
    seen: dict[str, int] = {}
    for path, defs in modules.items():
        for name in defs:
            if name.startswith("_") or name in PROTOCOL:
                continue
            seen[name] = seen.get(name, 0) + 1
    stale = [n for n in HARMLESS if seen.get(n, 0) < 2]
    assert not stale, (
        f"these HARMLESS entries no longer collide anywhere, so they only blind the detector: "
        f"{stale}")


def test_the_detector_can_fire(modules, tmp_path):
    """A detector that cannot fail is not a detector."""
    fake = tmp_path / "fake.py"
    fake.write_text("def measure_thing():\n    return 1\n", encoding="utf-8")
    other = tmp_path / "other.py"
    other.write_text("def measure_thing():\n    return 2\n", encoding="utf-8")
    seen = {}
    for f in (fake, other):
        for name, body in _definitions(f).items():
            seen.setdefault(name, []).append((f.name, body))
    digests = {hashlib.sha256(b.encode()).hexdigest() for _, b in seen["measure_thing"]}
    assert len(digests) > 1, "the detector did not notice two different bodies under one name"


def test_the_two_leave_one_out_concepts_are_named_apart(modules):
    """THE CASE THAT PROMPTED THIS FILE, pinned so it cannot silently return."""
    import validate_metric_claims as claims
    import validate_style_metric as style

    assert hasattr(style, "leave_one_out"), (
        "the ablation function was renamed; if that is deliberate, update this test")
    assert not hasattr(claims, "leave_one_out"), (
        "cross-validation was renamed back to `leave_one_out`, colliding with the ablation again")
    assert hasattr(claims, "cross_validated_accuracy")

    # and they must genuinely measure different things
    import inspect
    a = inspect.getsource(style.leave_one_out)
    b = inspect.getsource(claims.cross_validated_accuracy)
    assert "dimension" in a.lower() or "reweighted" in a.lower(), (
        "the ablation no longer removes a dimension")
    assert "held-out" in b.lower() or "train" in b.lower(), (
        "cross-validation no longer holds out a pair")


def test_the_detector_finds_something_to_scan(modules):
    """A detector whose exclusion set swallows the corpus passes while checking nothing.

    This is the failure this test exists to prevent: the first version of the exclusion set listed
    most of the project's vocabulary, so the scan found ZERO candidate collisions and the suite went
    green. Green because nothing was examined is worse than red.
    """
    scanned = 0
    for path, defs in modules.items():
        for name in defs:
            if name.startswith("_") or name in PROTOCOL:
                continue
            scanned += 1
    assert scanned >= 50, (
        f"the detector only scanned {scanned} function definitions; the exclusion set has grown "
        f"until it swallows the corpus")
