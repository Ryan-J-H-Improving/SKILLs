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

Resolve workspace role before comparing learning state:

- `canonical`: this is the only location allowed to receive teaching progress, notes, or exercise contracts for that course instance.
- `reference_mirror`: use it only for discovery or recovery. Follow its absolute `canonical_course_dir`, audit that target, and ignore the mirror's local progress even if its copied blueprint says `ready`.

`mirror_canonical_blueprint_sha256` and `mirror_canonical_learning_state_sha256` track only those two named recovery snapshots. A drift warning does not mean every mirror file should be copied from the canonical. To refresh a tracked hash, first copy the corresponding canonical blueprint or learning-state file into an isolated mirror copy, verify exact byte equality, audit the mirror, and then whitelist-activate that file and its metadata. Never silence drift by editing only the recorded hash.

If two directories both claim `canonical` for the same course instance, do not choose by recency or proximity. Treat the identity as ambiguous, present the conflicting paths, and require an explicit canonical decision before formal teaching.

## Initialization Guard

Before creating a course directory, inspect every discovered `.ai-course-tutor/index.md`, follow registered mirror paths, and collect the corresponding workspace roots. Run a multi-root workspace audit when more than one root is available.

Pass every external root to `scripts/init_course_workspace.py` with a repeated `--known-workspace`. The initializer must refuse the new directory when the same course instance already has a canonical workspace. `--force` is only for template replacement inside the selected location and never authorizes a second canonical.

Use `--confirm-no-known-canonical` only when no external workspace root is available after this search. This flag records an explicit initialization decision; it is not a substitute for ignoring an index or a path already discovered. If two canonicals already exist, ask the user which location should remain canonical, convert the other to a reference mirror, and rerun the multi-root audit.

The canonical workspace must be project-local to the course and must not live inside the distributable skill directory. If the audit reports `canonical_workspace_inside_skill_distribution`, keep teaching available but record a migration task. Move it only through an isolated-copy, whitelist-activation, and before/after fingerprint workflow; never repair this warning by linking course notes across unrelated project roots.

Use this confidence guide:

- High confidence: same course code/title plus matching institution or lecturer, or a strong combination of course code, term, and materials.
- Medium confidence: same course code or title but term, lecturer, or source version differs.
- Low confidence: only broad subject overlap, unclear title, or conflicting metadata.

High confidence: proceed and record the evidence.

Medium confidence: present the likely match and continue only if the choice is low-risk. If merging or reusing notes could confuse terms, ask the user.

Low confidence: create a new draft course instance and record unresolved fields. Ask the user only for decisions that materially affect organization or teaching.

## Source Registration

Register every uploaded or discovered teaching source in `indexes/source-register.md` before relying on it. Create the register from `assets/source-register.md.template` when an existing workspace does not have one. Assign a stable source ID and record:

- Material type, term/version, and local path
- Authority: current course source, related-term support, user note, or AI-added support
- Lecture, topic, or assessment coverage
- Processing status, such as indexed, OCR needed, figures extracted, or incomplete
- Any conflict with another source and how it was resolved

Use source IDs in notes and citations when file names or week labels are ambiguous. A source being uploaded does not mean the user has read it.

## Ambiguous Decisions

When uncertain, give 2-3 concrete options. Avoid open-ended questions unless the user must supply missing information.

Example:

```text
These materials look related to COURSE1234, but the term is unclear.
Choose one:
1. Add them to the existing COURSE1234 2026 S1 course.
2. Create a new COURSE1234 unknown-term course instance.
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
