# Figure Selection Rules

## Figure Types

Use two labels:

- `Course figure`: extracted from course slides, exam papers, handouts, or official materials.
- `AI-generated teaching aid`: created by AI to support explanation and not part of the course source.

Never let the user confuse the two.

## When To Show A Course Figure

Show or save a course figure when it:

- Contains a definition, diagram, formula structure, data display, code output, model, graph, table, or worked example.
- Is explicitly discussed in the transcript.
- Helps explain a concept more clearly than text alone.
- Is likely to be examinable.
- Is requested by the user.

Do not show decorative images, title-page artwork, vague backgrounds, or screenshots with unreadable content.

## Figure Quality

Before using a figure:

- Ensure text and labels are readable.
- Prefer cropping to the key content rather than saving a full slide or page. Use a full-page screenshot only when surrounding context is necessary for understanding.
- Ensure the crop keeps all labels, axes, legends, formulas, captions, and surrounding context needed to understand the selected content.
- Keep a source citation.
- Add a short caption explaining why the figure matters.

If a figure is complex, break the explanation into parts rather than describing everything at once.

## Three-Pass Image Validation

Images are fragile. Before showing, saving, or relying on an extracted screenshot or AI-generated teaching aid, complete at least three independent validation passes. Each pass must start from a different checking question, not from the original creation rationale. All passes must pass.

Pass 1: educational relevance

- Does this image directly support the current knowledge point, misconception, formula, example, or exam pattern?
- Is it better than a short text explanation alone?
- Would saving it help the user review later?

Pass 2: source and content fidelity

- For a course figure, does the image faithfully represent the selected slide, exam paper, handout, or official source?
- Are no key labels, formulas, axes, legends, captions, data values, or surrounding assumptions missing from the crop?
- For an AI-generated teaching aid, are the concept, formula, notation, labels, and relationships consistent with the course materials?
- Are AI-added elements clearly marked as not from the course source?

Pass 3: visual usability

- Is the image readable at chat and note size?
- Is the crop focused on the key content without unnecessary margins or unrelated slide material?
- Are text, symbols, colors, arrows, and graph elements clear enough to support learning?
- Is the image free from obvious generation artifacts, distorted text, impossible geometry, or misleading visual emphasis?

If any pass fails, do not use the image as-is. Re-crop, regenerate, replace with a text explanation, or ask the user which option they prefer.

Record the validation result briefly when saving to notes:

```md
Validation: passed relevance, fidelity, and usability checks
```

## Saving Figures To Notes

When a figure is saved, update `notes/figure-notes.md`:

```md
## Sampling Distribution Diagram

Type: Course figure
Source: Week 3 slides p. 12
Saved file: ../extracted/figures/week03-p12-sampling-distribution.png
Used for: Understanding how sample means vary across repeated samples.
Related note: study-notes.md#sampling-distribution
```

For AI-generated aids:

```md
Type: AI-generated teaching aid
Source status: Not from course slides
Related course source: Week 3 slides p. 12
```

## Asking The User

Ask before saving when:

- The figure is only mildly useful.
- The same concept already has several saved figures.
- The user may prefer a cleaner AI-generated aid.
- Saving would clutter notes.

If the user says a figure is useful or asks to keep it, save it.
