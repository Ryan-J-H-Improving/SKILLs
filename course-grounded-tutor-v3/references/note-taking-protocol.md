# Note-Taking Protocol

## Contents

- [Four Note Types](#four-note-types)
- [Course Map](#course-map)
- [Study Notes](#study-notes)
- [Exam Review Notes](#exam-review-notes)
- [Personalized Mistake Handling](#personalized-mistake-handling)
- [Note Language](#note-language)
- [Formula Stability](#formula-stability)
- [Figure Register And Delivery](#figure-register-and-delivery)
- [Warning Lifecycle](#warning-lifecycle)
- [Read-Only Note Audit](#read-only-note-audit)
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

`course-map.md` is the learner-facing navigation layer. It answers "which lecture covered this concept?" and helps future chats retrieve relevant sources quickly. Derive its lesson order and totals from the validated `indexes/teaching-blueprint.md`; do not maintain a competing point order.

`notes/course-map.md` is the only canonical learner-facing map. A weekly or alternate map is permitted only as a derived view and must state `Derived from: notes/course-map.md`; it must not define a competing point order, status, or total.

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

For each lecture or lesson, mirror the blueprint's ordered knowledge-point list so progress can be displayed numerically. The list must include the validated total and current point number. A mismatch blocks further teaching until repaired.

## Study Notes

Study notes are personalized course notes, not a generic summary.

Use this top-level structure:

1. Contents
2. Knowledge Points
3. Mistake Review

A temporary `Restart Status` or `Migration Status` section may appear during reconciliation. Other top-level sections should be folded under the three canonical sections or moved to the dedicated concept-map, exam-review, or progress surface.

`notes/study-notes.md` is the canonical study-note index. It may hold the detailed notes directly or link one or more local Markdown files as learner-facing detailed-note surfaces. When detailed weekly notes are used:

- link every active detailed note from the `Contents` section in `notes/study-notes.md` in the same update that creates it;
- keep linked note files inside the course project;
- treat the central file plus its explicitly linked Markdown files as one learner-facing note set for figure delivery, formula inventory, warning lifecycle, and freshness checks;
- do not duplicate a detailed weekly note back into the central index merely to satisfy the audit;
- do not count an unlinked or external Markdown file as delivered learner notes.

Rules:

- Write in `note_language`.
- Be concise, but do not omit non-key content entirely.
- Explain high-priority content more fully.
- Record every formula with course notation.
- Explain every symbol and every non-obvious operation or transformation in each formula.
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
- Keep formulas, symbol explanations, and operation meanings complete.
- Record trigger words and conditions for selecting methods.
- Record expected answer structures and marking points.
- Emphasize the user's recurring exam-style errors.
- During ordinary learning, incrementally copy complete course formulas, symbol meanings, method trigger conditions, and explicit must-memorize items into the Formula Sheet. Label them `Evidence status: course formula; exam frequency unknown` until a past paper, sample exam, marking guide, or teacher statement supplies exam-frequency evidence.
- Do not populate High-Frequency Topics, Question Patterns, marking points, or school-style claims from ordinary lecture presence alone.

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

## Figure Register And Delivery

`notes/figure-notes.md` is the validation and delivery register; it is not a second copy of study notes and must not be generated by deleting every figure absent from `study-notes.md`.

Every registered figure must record exactly one delivery status:

- `embedded`: a working image link is present at the related concept in `notes/study-notes.md` or in a local detailed-note surface explicitly linked from its `Contents` section.
- `pending_insertion`: validation passed, but insertion is unfinished; record the target note anchor and next action.
- `reference_only`: the figure is valid but deliberately omitted because it is redundant or low-value for the learner-facing notes; record the reason.
- `archived`: the figure was superseded or removed; record the replacement or reason.

An image embedded in study notes must have a matching figure-register entry. A register entry marked `embedded` without a study-note image is inconsistent. A `Saved file` line without an embedded register preview is incomplete and should be repaired when the figure is next touched.

## Warning Lifecycle

Do not delete a personal warning merely because a point later becomes `mastered`; relapse protection can remain useful. Give each personal warning one status:

- `active`: the misconception is unresolved or recently repeated.
- `monitor`: corrected, but still worth checking during spaced review.
- `resolved`: repeated independent evidence shows the old mental model no longer recurs; retain a concise historical note or archive it during note maintenance.

Change warning status only from learner evidence. Tutor confidence, point position, or a legacy `mastered` label is insufficient.

## Read-Only Note Audit

`scripts/audit_course_workspace.py` reports note health without rewriting learner notes. It checks:

- required and unexpected central study-note top-level sections;
- missing or out-of-project detailed-note links declared by the central index;
- template-only exam notes and missing formula inventory;
- images across the central index and linked detailed-note surfaces that are absent from the figure register;
- registered figures with unknown, pending, or contradictory delivery state;
- broken Markdown image links and register entries without previews;
- approximate study-note-set lag, using the newest central or linked surface, against session and practice evidence;
- personal warnings without lifecycle status;
- course-map companion files without a declared canonical source.

Note warnings do not by themselves block formal teaching. Show a compact health signal at session start when warnings exist, repair low-risk metadata at the next safe boundary, and use a separately reviewed migration for large content moves.

## Update Policy

Update notes when:

- The user asks to organize, save, or write notes.
- The user says a figure or explanation is useful.
- A figure, chart, diagram, table, or generated teaching image has passed validation and would make the note clearer.
- A visually dependent concept was taught with a validated figure that the user would otherwise need to reopen the source to inspect.
- The user has a misconception that should be protected against future relapse.
- A substantial knowledge point has been completed.
- Exam review identifies a high-frequency topic, formula, or question pattern.
- A substantial point introduces a course formula, symbol set, method trigger, or explicit must-memorize item; update the exam Formula Sheet incrementally while leaving exam frequency unknown.
- A figure's delivery state changes among embedded, pending, reference-only, or archived.
- A personal warning receives evidence that changes it from active to monitor or resolved.

When uncertain whether to overwrite, merge, or create a separate entry, ask the user with clear options.
