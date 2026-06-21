# Course Identification

## Goal

Identify the course and course instance from materials without requiring the user to name it.

## Evidence To Extract

Use all available evidence:

- File names and folder names
- PDF metadata
- Cover pages, headers, footers, watermarks, and page titles
- Course code, course title, school, department, institution, term, year, and lecturer names
- Lecture week, topic names, module names, and assessment labels
- Transcript timestamps, lecture titles, and repeated teacher phrases
- Exam paper headers, sample paper labels, and marking rubrics
- Distinctive terminology, notation, datasets, software outputs, or recurring examples

## Matching Existing Courses

Read `.ai-course-tutor/index.md` first. Then inspect likely `course.yml` files.

Use this confidence guide:

- High confidence: same course code/title plus matching institution or lecturer, or a strong combination of course code, term, and materials.
- Medium confidence: same course code or title but term, lecturer, or source version differs.
- Low confidence: only broad subject overlap, unclear title, or conflicting metadata.

High confidence: proceed and record the evidence.

Medium confidence: present the likely match and continue only if the choice is low-risk. If merging or reusing notes could confuse terms, ask the user.

Low confidence: create a new draft course instance and record unresolved fields. Ask the user only for decisions that materially affect organization or teaching.

## Ambiguous Decisions

When uncertain, give 2-3 concrete options. Avoid open-ended questions unless the user must supply missing information.

Example:

```text
These materials look related to STAT5002, but the term is unclear.
Choose one:
1. Add them to the existing STAT5002 2026 S1 course.
2. Create a new STAT5002 unknown-term course instance.
3. Treat them as reference material only and do not merge them into notes yet.
```

## Course Instance Rules

Do not treat course code alone as identity. Track at least:

- Course code
- Course title
- Institution
- Term or teaching period
- Year
- Lecturer or teaching team when available
- Source version or upload batch

Different terms of the same course may be linked. Use prior terms as supporting context when helpful, especially for students repeating or reviewing the course, but do not silently mix sources in notes or explanations.

## Source Priority

Use this default priority:

1. Current term slides for definitions, notation, and official structure
2. Current term transcripts for emphasis, explanations, and teacher hints
3. Current term exams, sample papers, and rubrics for assessment style
4. Related-term materials from the same course as supplementary support
5. General knowledge only as extra intuition, clearly marked

When materials conflict, cite the conflict and ask if it affects a teaching or note decision.

