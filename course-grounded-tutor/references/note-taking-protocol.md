# Note-Taking Protocol

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
- Lecture or week
- Slide pages
- Transcript range when known
- Related concepts
- Relevant formulas or symbols
- Note anchors
- Exam relevance

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
- Prefer updating existing entries over appending duplicates.
- Preserve useful course figures or AI teaching aids only when they help the user.

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
- The user has a misconception that should be protected against future relapse.
- A substantial knowledge point has been completed.
- Exam review identifies a high-frequency topic, formula, or question pattern.

When uncertain whether to overwrite, merge, or create a separate entry, ask the user with clear options.

