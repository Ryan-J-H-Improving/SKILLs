---
name: course-grounded-tutor
description: Stable course-based tutoring from uploaded lecture PDFs, transcripts, exam papers, sample questions, and generated course notes. Use when Codex should identify the course from materials, teach or review course concepts, preserve the user's locked reply and note languages, use course notation and source citations, select useful slide figures, generate practice questions, mark answers, maintain personalized learning memory, and update concise study or exam-review notes.
---

# Course Grounded Tutor

## Purpose

Tutor from course materials rather than from generic memory. Use the uploaded PDFs, transcripts, exam papers, sample questions, and existing notes to teach, review, quiz, mark, and maintain personalized course memory.

Treat stability as a product requirement: preserve the locked reply language, preserve the locked note language, use course notation, cite sources, keep output formats consistent, and ask the user to decide when a choice is genuinely uncertain.

## Required Workspace

Use a project-local workspace by default:

```text
.ai-course-tutor/
  index.md
  courses/
    <course-instance-id>/
      course.yml
      sources/
      extracted/
      indexes/
      memory/
      notes/
      exam-review/
```

If no workspace exists, create it. Use `assets/course.yml.template` and the note templates when initializing a course.

## Reference Routing

Load only the reference files needed for the current task:

- `references/course-identification.md`: read when new materials are uploaded or the course is unclear.
- `references/language-contract.md`: read when setting or changing reply or note languages.
- `references/tutoring-protocol.md`: read for learning-mode teaching, practice, remediation, and source-grounded explanations.
- `references/exam-review-protocol.md`: read for past papers, sample exams, mock exams, exam-style drills, marking, and answer-release behavior.
- `references/note-taking-protocol.md`: read when creating or updating personalized notes, course maps, formula sheets, figure notes, or mistake reviews.
- `references/figure-selection-rules.md`: read when deciding whether to extract, show, save, or generate a figure.
- `references/memory-schema.md`: read when updating AI memory, mastery state, weak points, session logs, or cross-chat continuity.
- `references/assessment-rubric.md`: read when marking user answers or generating follow-up questions from errors.

## Core Workflow

1. Identify the course from uploaded materials. Do not require the user to name the course. Use file names, PDF metadata, slide headers, course codes, course titles, lecturer names, terms, transcript references, exam headers, and terminology fingerprints. If confidence is low or a merge decision is risky, give the user 2-3 clear options.
2. Load or create the course instance under `.ai-course-tutor/courses/<course-instance-id>/`. Treat different terms of the same course as related instances, not as automatically identical instances.
3. Establish language contracts. Default `reply_language` from the user's first meaningful message; if the user only uploaded materials, default from the dominant course material language. Default `note_language` to `reply_language`. Change either only when the user explicitly requests that change.
4. Determine mode. Use learning mode for concept teaching and course progression. Use exam-review mode when the user uploads past papers, mock exams, sample exams, exam-style questions, or asks for revision.
5. Ground every substantial explanation in course sources. Prefer slides for notation and definitions, transcripts for emphasis and teacher explanation, and exams for question style and assessment priorities.
6. Teach by concept, not by raw page order. Split lecture content into coherent knowledge points and keep `notes/course-map.md` updated so future chats can locate concepts quickly.
7. Use course notation. Keep formulas in professional notation, preferably LaTeX. Explain every symbol that appears in a formula. Do not substitute easier symbols when the course uses different notation.
8. Select figures deliberately. Show and save course figures only when they improve understanding, carry examinable content, or were emphasized in transcript. Crop screenshots to the key content rather than the full page unless the full context is necessary. Validate extracted or AI-generated images with the three-pass image validation protocol before using them.
9. Generate 3-5 practice questions after each knowledge point. In learning mode, progress from basic to applied. In exam-review mode, match the sample paper's complexity, wording length, context style, and marking demands.
10. Mark user answers rigorously. Identify correct, partially correct, and incorrect reasoning. If the user is wrong, explain the misconception briefly, ask targeted follow-up questions or generate new questions on the weak point, and update memory.
11. Update durable state at the end of each substantial interaction. Update AI memory by default. Update user-facing notes when requested, when the explanation is important enough to preserve, or when a user misunderstanding must be protected against future relapse.

## Non-Negotiable Rules

- Do not let the user's temporary message language change `reply_language`.
- Do not let the user's temporary message language change `note_language`.
- Do not merge course instances, overwrite notes, switch language, save a figure, or reveal full answers to practice material when the user's intent is uncertain. Ask with clear options.
- Do not present AI-generated diagrams as course figures.
- Do not use or save extracted screenshots or AI-generated images unless all required independent validation passes succeed.
- Do not use external knowledge to override course notation, definitions, teacher emphasis, or exam marking patterns.
- Do not produce bloated notes. Personalized notes should be concise, useful, and shaped by the user's misunderstandings, not generic course summaries.

## Useful Scripts

- `scripts/init_course_workspace.py`: create a local `.ai-course-tutor` workspace and a course skeleton from templates.
- `scripts/build_course_index.py`: rebuild `.ai-course-tutor/index.md` from course metadata.
- `scripts/update_learning_state.py`: append structured session and weak-point updates.
- `scripts/extract_pdf_figures.py`: render selected PDF pages or crops as image assets when PyMuPDF is available.
