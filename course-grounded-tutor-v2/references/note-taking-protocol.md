# Note-Taking Protocol

## Contents

- [Four Note Types](#four-note-types)
- [Course Map](#course-map)
- [Study Notes](#study-notes)
- [Exam Review Notes](#exam-review-notes)
- [Personalized Mistake Handling](#personalized-mistake-handling)
- [Note Language](#note-language)
- [Formula Stability](#formula-stability)
- [Update Policy](#update-policy)

## Four Note Types

Maintain four user-visible note surfaces:

```text
notes/course-map.md
notes/study-notes.md
notes/exam-review-notes.md
notes/figure-notes.md
```

Maintain AI continuity separately in `memory/`.

## Course Map

`course-map.md` is the navigation layer. It answers "which lecture covered this concept?" and helps future chats retrieve relevant sources quickly.

Each entry should include:

- Concept name
- Registered source IDs
- Lecture or week
- Position within the lecture, such as `2/10`
- Slide pages
- Transcript range when known
- Related concepts
- Relevant formulas or symbols
- Note anchors
- Exam relevance

For each lecture or lesson, maintain an ordered knowledge-point list so progress can be displayed numerically. The list should include the total number of knowledge points for that lecture and the current point number.

## Study Notes

Study notes are personalized course notes, not a generic summary.

Use this top-level structure:

1. Contents
2. Knowledge Points
3. Mistake Review

Rules:

- Write in `note_language`.
- Be concise, but do not omit non-key content entirely.
- Explain high-priority content more fully.
- Record every formula with course notation.
- Explain every symbol in each formula.
- Include user-specific clarifications for prior misunderstandings.
- Proactively insert useful images when they materially improve review; do not wait for the user to request them. Every image must first pass the three-pass validation in `figure-selection-rules.md`.
- Crop PPT/PDF screenshots to effective content only. Do not include unrelated slide text, decorations, or neighboring examples unless they are needed to understand the image.
- A `Useful Figure` section must contain an embedded image link. Do not make the user return to the original PPT/PDF just to see the figure.
- Do not write source-only placeholders such as "Course figure: PDF p. 10" as the full content of a useful-figure note.
- Prefer updating existing entries over appending duplicates.
- Preserve useful course figures or AI teaching aids only when they help the user.

Use this shape:

```md
#### Useful Figure

![<short descriptive alt text>](../extracted/figures/<validated-crop>.png)

- Caption: <why this figure helps>
- Type: Course figure
- Source: <slides or PDF page>
- Source ID: <registered source ID>
- Validation: passed relevance, fidelity, and usability checks
```

If extraction is temporarily impossible, use a temporary pending block instead of pretending the note is complete:

```md
#### Useful Figure

Image pending: <reason extraction could not be completed>.
Source candidate: <slides or PDF page>.
Next action: extract the key figure only, validate it, then replace this block with an embedded image.
```

## Exam Review Notes

Exam review notes are for fast recall and exam performance.

Use this top-level structure:

1. Contents
2. High-Frequency Topics
3. Formula Sheet
4. Question Patterns
5. Mistake Review

Rules:

- Keep topic explanations compact.
- Keep formulas and symbol explanations complete.
- Record trigger words and conditions for selecting methods.
- Record expected answer structures and marking points.
- Emphasize the user's recurring exam-style errors.

## Personalized Mistake Handling

When the user has misunderstood a concept, notes must include:

- The user's previous incorrect thinking
- Why it is wrong
- The correct course-based explanation
- A short future warning or trigger pattern

This is required because users often return to their original intuition during revision.

## Note Language

Default notes to `reply_language`. Change note language only on explicit user request. A temporary user message in another language does not change note language.

## Formula Stability

Use LaTeX-style display math for important formulas:

```text
\[
SE(\bar{X}) = \frac{\sigma}{\sqrt{n}}
\]
```

Then explain symbols:

```text
- `SE(\bar{X})`: standard error of the sample mean
- `\sigma`: population standard deviation
- `n`: sample size
```

If the course uses a different symbol, use the course symbol, not the generic symbol.

## Update Policy

Update notes when:

- The user asks to organize, save, or write notes.
- The user says a figure or explanation is useful.
- A figure, chart, diagram, table, or generated teaching image has passed validation and would make the note clearer.
- A visually dependent concept was taught with a validated figure that the user would otherwise need to reopen the source to inspect.
- The user has a misconception that should be protected against future relapse.
- A substantial knowledge point has been completed.
- Exam review identifies a high-frequency topic, formula, or question pattern.

When uncertain whether to overwrite, merge, or create a separate entry, ask the user with clear options.
