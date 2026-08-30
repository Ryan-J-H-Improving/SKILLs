#!/usr/bin/env python3
"""Render selected PDF pages or rectangular crops as PNG files.

Requires PyMuPDF (`pymupdf`). The script is intentionally small because the
selection decision belongs to the tutoring protocol, not to image heuristics.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_pages(spec: str) -> list[int]:
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(piece) for piece in part.split("-", 1)]
            if start > end:
                raise ValueError(f"page range must be ascending: {part}")
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    if not pages or any(page < 1 for page in pages):
        raise ValueError("--pages must contain positive 1-based page numbers")
    return list(dict.fromkeys(pages))


def parse_rect(spec: str | None):
    if not spec:
        return None
    values = [float(piece.strip()) for piece in spec.split(",")]
    if len(values) != 4:
        raise ValueError("--rect must be x0,y0,x1,y1")
    if values[0] >= values[2] or values[1] >= values[3]:
        raise ValueError("--rect requires x0 < x1 and y0 < y1")
    return values


def coordinate_token(value: float) -> str:
    return f"{value:g}".replace("-", "m").replace(".", "p")


def output_name(pdf_path: Path, page_number: int, rect_values, custom_name: str) -> str:
    if custom_name:
        return f"{custom_name}-p{page_number:03d}.png"
    if rect_values:
        coords = "-".join(coordinate_token(value) for value in rect_values)
        return f"{pdf_path.stem}-p{page_number:03d}-crop-{coords}.png"
    return f"{pdf_path.stem}-p{page_number:03d}-page.png"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--pages", required=True, help="1-based pages, e.g. 1,3-5")
    parser.add_argument("--rect", help="Optional crop rectangle x0,y0,x1,y1 in PDF points")
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--name", default="", help="Optional safe output-name prefix")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.dpi < 72 or args.dpi > 600:
        parser.error("--dpi must be between 72 and 600")
    if args.name and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.name):
        parser.error("--name may contain only letters, digits, dot, underscore, and hyphen")

    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required. Install package `pymupdf` to use this script.") from exc

    pdf_path = Path(args.pdf)
    if not pdf_path.is_file():
        parser.error(f"PDF not found: {pdf_path}")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        rect_values = parse_rect(args.rect)
        page_numbers = parse_pages(args.pages)
    except ValueError as exc:
        parser.error(str(exc))

    matrix = pymupdf.Matrix(args.dpi / 72, args.dpi / 72)
    outputs: list[Path] = []

    with pymupdf.open(pdf_path) as document:
        for page_number in page_numbers:
            if page_number > document.page_count:
                parser.error(
                    f"page {page_number} is outside the PDF page range 1-{document.page_count}"
                )
            page = document[page_number - 1]
            clip = pymupdf.Rect(*rect_values) if rect_values else None
            if clip and not page.rect.contains(clip):
                parser.error(f"--rect is outside page {page_number}: page bounds are {page.rect}")
            output = out_dir / output_name(pdf_path, page_number, rect_values, args.name)
            if output.exists() and not args.overwrite:
                parser.error(f"output already exists; use --overwrite to replace it: {output}")
            pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
            pixmap.save(output)
            outputs.append(output)

    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
