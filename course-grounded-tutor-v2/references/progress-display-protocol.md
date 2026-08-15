# Progress Display Protocol

## Purpose

Show the current course progress directly during tutoring so the user does not need to ask where they are.

## When To Display

Include a compact progress snapshot when course state is available:

- at the start or resumption of a tutoring or review session;
- when entering a new learning cluster or making a substantial topic transition;
- after substantial marking changes mastery or the next step;
- when the user asks for progress.

During a micro-correction, short clarification, or remediation answer, use at most one short status line or omit the snapshot. Do not repeat the full block on every exchange.

## Format

Use the locked reply language.

```text
Current progress
- Lesson progress: <current number>/<total knowledge points in this lecture>
- Now: <current topic>
- Cluster checkpoint: <current evidence status or remaining answer actions>
- Completed: <short list>
- Fragile: <short list>
- Next: <next recommended step>
- Exam readiness: <if relevant>
```

Keep it short. Do not repeat a long list of the whole course each turn.

## Numeric Lesson Progress

Always show the current knowledge-point number and the total number of knowledge points in the current lecture or lesson in a full progress snapshot. Do not turn that requirement into a repeated full block during every micro-turn.

Examples:

```text
Current progress
- Lesson progress: 2/10
- Now: Week 2 knowledge point 2 - ETL vs ELT
- Cluster checkpoint: 2/4 answer actions evidenced
- Completed: knowledge point 1 is practiced
- Fragile: bytes/bits conversion
- Next: complete the guided readiness check
```

If the current lecture has not been segmented yet, segment it first into a concise ordered knowledge-point list, record it in `notes/course-map.md`, then show progress as `1/<total>`, `2/<total>`, etc. Do not silently omit the numeric count.

If the total cannot be inferred from available materials, write:

```text
- Lesson progress: pending segmentation
```

Then make segmentation the immediate next action before continuing detailed teaching.

## State Source

Read from:

- `memory/learning-state.md`
- `memory/weak-points.md`
- `memory/practice-history.md`
- `notes/course-map.md`
- `exam-review/school-question-patterns.md` when exam review is active

Update `memory/learning-state.md` after substantial progress.
