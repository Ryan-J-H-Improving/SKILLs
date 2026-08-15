# Figure Selection Rules

## Contents

- [Figure Types](#figure-types)
- [Proactive Visual Dependency Gate](#proactive-visual-dependency-gate)
- [When To Show A Course Figure](#when-to-show-a-course-figure)
- [Figure Quality](#figure-quality)
- [Tooling](#tooling)
- [Three-Pass Image Validation](#three-pass-image-validation)
- [Saving Figures To Notes](#saving-figures-to-notes)
- [Asking The User](#asking-the-user)

## Figure Types

Use two labels:

- `Course figure`: extracted from course slides, exam papers, handouts, or official materials.
- `AI-generated teaching aid`: created by AI to support explanation and not part of the course source.

Never let the user confuse the two.

## Proactive Visual Dependency Gate

Before composing each new teaching unit, inspect the relevant source pages and transcript for visual dependency. Do this proactively; the user does not need to ask for a picture.

Treat a visual as required before explanation or questioning when the learner must reason from:

- a graph, plot shape, axis, legend, trend, residual pattern, or geometric relationship;
- a diagram, process flow, hierarchy, spatial arrangement, interface, or annotated object;
- code output, software output, a layout-dependent table, or a visual comparison;
- an example whose meaning depends on relative position, color, line style, region, or movement.

Prefer a validated course figure that directly carries the course's notation and emphasis. If the course source is absent, incomplete, or visually unsuitable, create a clearly labeled and validated `AI-generated teaching aid`. Show the visual before asking the user to identify, compare, diagnose, or interpret its features.

Do not force an image into a topic that text or a short formula explains better. The decision is based on learning value, not decoration.

## When To Show A Course Figure

Show or save a course figure when it:

- Contains a definition, diagram, formula structure, data display, code output, model, graph, table, or worked example.
- Is explicitly discussed in the transcript.
- Helps explain a concept more clearly than text alone.
- Is likely to be examinable.
- Is requested by the user.

When any proactive visual-dependency trigger applies, showing the best validated visual is mandatory even if the user has not requested it.

Do not show decorative images, title-page artwork, vague backgrounds, or screenshots with unreadable content.

## Figure Quality

Before using a figure:

- Ensure text and labels are readable.
- Prefer cropping to the key content rather than saving a full slide or page. Use a full-page screenshot only when surrounding context is necessary for understanding.
- Ensure the crop keeps all labels, axes, legends, formulas, captions, and surrounding context needed to understand the selected content.
- Keep a source citation.
- Add a short caption explaining why the figure matters.

If a figure is complex, break the explanation into parts rather than describing everything at once.

## Tooling

Use the best available extraction tool for the task. For PDF/PPT figure extraction and precise cropping, prefer tools that preserve resolution and layout fidelity, such as PyMuPDF when available.

If the preferred tool is missing, ask the user for permission to install it instead of silently switching to a weaker fallback. Explain what the tool improves, for example:

```text
PyMuPDF is not installed. It would improve PDF page rendering and precise figure cropping for notes. May I install it with `pip install pymupdf`?
```

If the user approves, install and use the tool. If the user declines or installation fails, use the best available fallback, keep the three-pass validation requirement, and note any limitation.

## Three-Pass Image Validation

Images are fragile. Before showing, saving, inserting into notes, or relying on an extracted screenshot or AI-generated teaching aid, complete at least three independent validation passes in one validation cycle. Each pass must start from a different checking question, not from the original creation rationale. All passes must pass before the image can be used.

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

All three passes belong to one release decision. Do not use an image after two passes and plan to inspect it later.

For PPT/PDF screenshots, prefer the smallest crop that preserves the effective educational content. Remove unrelated slide headings, decorative elements, surrounding text blocks, and neighboring examples unless they are required context.

Record the validation result briefly when saving to notes:

```md
Validation: passed relevance, fidelity, and usability checks
```

When a validated image is used in user-facing notes, embed it directly:

```md
![Sampling distribution diagram](../extracted/figures/week03-p12-sampling-distribution.png)
```

Do not replace the image with a source-only note such as "see Week 3 slides p. 12". A source citation is necessary, but it is not a substitute for the embedded image.

## Saving Figures To Notes

When a figure is saved, update `notes/figure-notes.md`:

```md
## Sampling Distribution Diagram

![Sampling distribution diagram](../extracted/figures/week03-p12-sampling-distribution.png)

Type: Course figure
Source: Week 3 slides p. 12
Saved file: ../extracted/figures/week03-p12-sampling-distribution.png
Used for: Understanding how sample means vary across repeated samples.
Related note: study-notes.md#sampling-distribution
```

For AI-generated aids:

```md
![Standard error teaching aid](../extracted/figures/standard-error-ai-aid.png)

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

Do not ask before saving a clearly high-value validated figure that the notes need to be self-contained. Embed it directly with its source and type. Asking is reserved for marginal, duplicative, or cluttering figures.
