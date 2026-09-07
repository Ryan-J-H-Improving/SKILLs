# Progress Display Protocol

## Purpose

Show where the learner is without requiring a question and without turning every micro-turn into a status report.

## When To Display

Show a compact snapshot:

- at the start or resumption of teaching or review;
- when entering a new lesson or substantial topic;
- after marking changes the current point or next step materially;
- when the user asks.

Omit the full block during a short clarification or remediation turn.

## Format

Use the locked reply language:

```text
Current progress
- Current lesson: <lesson title>
- Teaching position: <current point>/<total points in this lesson>
- Now: <point title>
- Point status: <teaching | exercise pending | repair needed | practiced>
- Evidence: <practiced points>/<lesson total> practiced; <mastered points>/<lesson total> mastered
- Course coverage: <supplied lessons outlined>/<supplied lessons> <only when useful>
- Previously covered: <short summary without claiming mastery>
- Fragile: <only active learner weak points>
- Next: <next concrete action>
- Notes: <current | approximately N days behind | X unresolved figure-delivery warnings>
- Exam readiness: <only when relevant>
```

Do not display a separate guided or independent checkpoint because V3.1 uses one exercise set per point.

Show the `Notes` line only when the read-only workspace audit reports a meaningful lag or unresolved delivery warning. It is a maintenance signal, not a reason to interrupt the current explanation or claim that learning evidence is invalid.

The position counter answers "where should this lesson resume?" It does not answer course completion or mastery. Never combine points from several weeks into one denominator such as `40/54`. Show `Week 5 - 2/16` and keep course coverage separate. Derive practiced/mastered counts only from valid current evidence.

## Numeric Consistency

The denominator must come from the active registered lesson blueprint. Before display, compare it with the manifest, course map, and learning state.

If the lesson has not been planned, show:

```text
- Teaching position: pending validated blueprint
```

Then complete the blueprint before detailed teaching. If segmentation changes, update blueprint, course map, current state, and progress together before showing a new total.

## State Source

Read from:

- `course.yml` active blueprint path
- `indexes/blueprints/manifest.json`
- `memory/learning-state.md`
- `memory/weak-points.md`
- `memory/practice-history.md`
- `notes/course-map.md`
- exam-review records when active

Do not use an append-only historical value when it contradicts canonical current state.
