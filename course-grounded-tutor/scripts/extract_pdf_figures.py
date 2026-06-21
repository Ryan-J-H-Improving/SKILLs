#!/usr/bin/env python3
"""Render selected PDF pages or rectangular crops as PNG files.

Requires PyMuPDF (`fitz`). The script is intentionally small because the
selection decision belongs to the tutoring protocol, not to image heuristics.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_pages(spec: str) -> list[int]:
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(piece) for piece in part.split("-", 1)]
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return pages


def parse_rect(spec: str | None):
    if not spec:
        return None
    values = [float(piece.strip()) for piece in spec.split(",")]
    if len(values) != 4:
        raise ValueError("--rect must be x0,y0,x1,y1")
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--pages", required=True, help="1-based pages, e.g. 1,3-5")
    parser.add_argument("--rect", help="Optional crop rectangle x0,y0,x1,y1 in PDF points")
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required. Install package `pymupdf` to use this script.") from exc

    pdf_path = Path(args.pdf)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rect_values = parse_rect(args.rect)

    document = fitz.open(pdf_path)
    matrix = fitz.Matrix(args.dpi / 72, args.dpi / 72)
    outputs: list[Path] = []

    for page_number in parse_pages(args.pages):
        page = document[page_number - 1]
        clip = fitz.Rect(*rect_values) if rect_values else None
        pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
        suffix = "crop" if clip else "page"
        output = out_dir / f"{pdf_path.stem}-p{page_number:03d}-{suffix}.png"
        pixmap.save(output)
        outputs.append(output)

    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
