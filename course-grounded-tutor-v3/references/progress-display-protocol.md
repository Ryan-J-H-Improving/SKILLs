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
- Teaching position: <current point>/<total points>
- Now: <point title>
- Point status: <teaching | exercise pending | repair needed | practiced>
- Evidence: <practiced points>/<total points> practiced; <mastered points>/<total points> mastered
- Previously covered: <short summary without claiming mastery>
- Fragile: <only active learner weak points>
- Next: <next concrete action>
- Notes: <current | approximately N days behind | X unresolved figure-delivery warnings>
- Exam readiness: <only when relevant>
```

Do not display a separate guided or independent checkpoint because V3.1 uses one exercise set per point.

Show the `Notes` line only when the read-only workspace audit reports a meaningful lag or unresolved delivery warning. It is a maintenance signal, not a reason to interrupt the current explanation or claim that learning evidence is invalid.

The position counter answers "where should teaching resume?" It does not answer "how much has the learner mastered?" Never label it as completion. In particular, a migrated course may resume at `38/38` while the current point is `not_started` and no historical claim has been promoted into V3.1 evidence. State that distinction explicitly at session start and derive practiced/mastered counts only from valid current evidence.

## Numeric Consistency

The denominator must come from the validated teaching blueprint. Before display, compare it with the course map and learning state.

If the lesson has not been planned, show:

```text
- Teaching position: pending validated blueprint
```

Then complete the blueprint before detailed teaching. If segmentation changes, update blueprint, course map, current state, and progress together before showing a new total.

## State Source

Read from:

- `indexes/teaching-blueprint.md`
- `memory/learning-state.md`
- `memory/weak-points.md`
- `memory/practice-history.md`
- `notes/course-map.md`
- exam-review records when active

Do not use an append-only historical value when it contradicts canonical current state.
