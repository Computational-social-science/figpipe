"""Render the caption-anchored figure regions so they can be LOOKED AT.

WHY RENDERING IS PART OF THE PIPELINE
    The adversarial audit caught the previous detector by rendering its output and looking at
    it: half the "figures" were pages of prose. Numbers alone did not reveal that. So rendering
    is not a convenience here, it is the verification step -- a detector that has never been
    looked at is a detector that has never been checked.
"""
from __future__ import annotations

import pathlib
import sys

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from figpipe.figdetect import extract_paper  # noqa: E402

OUT = ROOT / "corpus" / "rendered"
DPI = 200


def render_paper(pdf_path: pathlib.Path, max_figs: int = 8) -> list[pathlib.Path]:
    info = extract_paper(pdf_path)
    stem = "".join(ch if ch.isalnum() else "_" for ch in pdf_path.stem)[:52]
    outdir = OUT / stem
    outdir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf_path))
    written = []
    for i, f in enumerate(info["figures"][:max_figs]):
        page = doc[f["page"] - 1]
        clip = pymupdf.Rect(f["bbox"])
        if clip.is_empty or clip.width < 10 or clip.height < 10:
            continue
        pix = page.get_pixmap(dpi=DPI, clip=clip)
        p = outdir / (f"fig{i+1:02d}_p{f['page']:02d}_n{f['figure_number']}.png")
        pix.save(str(p))
        written.append(p)
    doc.close()
    return written


def main() -> int:
    root = pathlib.Path(r"D:\2026-AI4S")
    pdfs = [p for p in root.glob("*.pdf") if "NATURE" in p.name.upper()]
    BAD = ("national science review", "natl sci rev", "nature communications",
           "npj", "scientific reports")
    pdfs = [p for p in pdfs if not any(b in p.name.lower() for b in BAD)]
    print(f"  candidate Nature PDFs: {len(pdfs)}")
    total = 0
    for p in pdfs[:12]:
        try:
            written = render_paper(p)
        except Exception as e:                                   # noqa: BLE001
            print(f"  {p.name[:50]:<50} FAILED {str(e)[:40]}")
            continue
        if written:
            total += len(written)
            print(f"  {p.name[:50]:<50} {len(written)} figure(s)")
    print(f"\n  rendered {total} figure regions to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
