# Tooling Protocol

## Purpose

Use strong local tools when they materially improve course extraction, image quality, OCR, note generation, validation, or reliability.

## Rule

Do not silently downgrade to a weaker workflow just because a preferred package or tool is missing. If a better tool would materially improve the result, ask the user for permission to install it. After the user approves, install and use it.

## When To Ask

Ask for installation approval when a missing tool would improve:

- PDF rendering or precise figure cropping
- PPT/PDF image extraction
- OCR accuracy
- Table extraction
- Formula extraction or rendering
- Diagram generation or validation
- Markdown or note processing
- Large-file indexing

## Request Shape

Be concrete and short:

```text
PyMuPDF is not installed. It would improve PDF rendering and precise figure cropping for note images. May I install it with `pip install pymupdf`?
```

## Fallback

If the user declines, approval is unavailable, or installation fails:

1. Use the best available fallback.
2. Keep the original quality rules, such as three-pass image validation.
3. State the limitation in plain language.
4. Do not pretend the fallback is equivalent when it is not.

## Examples

- Prefer PyMuPDF for PDF page rendering and crop extraction when available.
- Prefer OCR tooling when slide images contain important text that normal PDF text extraction misses.
- Prefer structured parsers for tables, formulas, and metadata when plain text extraction would be fragile.
