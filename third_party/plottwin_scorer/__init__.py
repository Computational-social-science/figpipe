"""PlotTwin-Bench scorer -- DETERMINISTIC CODE CHANNEL ONLY.

WHY THIS VENDORED SUBSET
The upstream package ships two channels: a code channel
(deterministic, 35% of the official score) and a VLM defect-ledger channel (65%, needs an
OpenAI-compatible client). figpipe vendors ONLY the code channel: it is the part this project
can run and defend, and shipping the VLM half would imply a score we cannot reproduce.

The files are unmodified copies from the benchmark repository:
  https://huggingface.co/datasets/figmirror/PlotTwin-Bench  (scorer/plottwin_scorer/)
Licence of the benchmark artefact: CC BY-NC 4.0 -- NON-COMMERCIAL. This package is therefore
not redistributed in the wheel and is used for local evaluation only; see NOTICE.md.
"""
from .deviation_defect import (
    DEVIATION_DEFECT_SCORE_VERSION,
    score_code_deviation,
    extract_style_features,
)

__all__ = [
    "DEVIATION_DEFECT_SCORE_VERSION",
    "extract_style_features",
    "score_code_deviation",
]
