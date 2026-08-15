# Memory Schema

## Contents

- [Purpose](#purpose)
- [Files](#files)
- [Mastery States](#mastery-states)
- [Learning State Contents](#learning-state-contents)
- [Weak Point Entry](#weak-point-entry)
- [Session Log Entry](#session-log-entry)
- [Practice History Entry](#practice-history-entry)
- [State Consistency](#state-consistency)
- [Compression Recovery](#compression-recovery)

## Purpose

Memory files are for continuity across context compression and separate chats. They should be understandable to the user, but their primary job is to help the AI teach consistently.

## Files

```text
memory/learning-state.md
memory/session-log.md
memory/weak-points.md
memory/practice-history.md
```

## Mastery States

Use these states for knowledge points:

- `not_started`
- `introduced`
- `guided`
- `practiced`
- `fragile`
- `mastered`
- `exam_ready`

`fragile` means the user can sometimes answer correctly but has a known misconception or unreliable trigger recognition.

`introduced` means the concept was named and defined but is not ready for independent scoring. `guided` means explanation or demonstration and a guided check have begun. `practiced` requires at least one valid independent attempt; merely displaying the concept does not qualify.

## Learning State Contents

Track:

- Course contract summary
- Reply language and note language
- Current mode
- Current lecture or lesson progress, including current knowledge-point number and total knowledge-point count
- Current learning cluster and practice-checkpoint status
- Current instruction stage and practice-readiness gate
- Required prerequisites, narrative bridge, new terms, source layer, worked-example status, guided-check evidence, and any blocking gap
- Current-session answer-action count, evidence reused, remediation rounds, and learner-load signal
- Covered concepts and mastery states
- Known weak points
- Corrections that worked
- Next recommended steps
- Cross-concept links

Use these readiness stages separately from mastery: `introduced`, `explained`, `demonstrated`, `guided_checked`, and `independent_ready`.

## Weak Point Entry

Use this shape:

```md
### Standard Error vs Standard Deviation

- Status: fragile
- Evidence: User used sample standard deviation where standard error was required.
- Corrective explanation that worked: Compare spread of observations vs spread of sample means.
- Course notation: `SE(\bar{X})`
- Follow-up needed: One applied scenario question.
```

## Session Log Entry

Append compact entries:

```md
### 2026-06-21T14:30:00+10:00

- Mode: learning
- Topic: Sampling distribution
- Lesson progress: 2/10
- Instruction stage: guided_checked
- Practice gate: independent practice allowed
- Sources: Week 3 slides pp. 10-15; transcript 00:12:40-00:24:10
- Taught: Definition, notation, standard error intuition
- User performance: Correct definition, confused SD and SE in calculation
- Updates: Marked standard error as fragile; added follow-up practice
```

## Practice History Entry

Record enough information to distinguish a student misconception from a tutor coverage failure:

```md
### 2026-06-21T14:35:00+10:00

- Topic: Standard error interpretation
- Learning phase: first exposure
- Question label: Guided check
- Required concepts: Standard deviation; standard error
- Source status: Course core
- Gate status before question: explained, not yet independent_ready
- Scored: no
- Answer actions: 1
- Evidence reused: none
- Tutor coverage gap: none
- Issue class: conceptual error
- User result: Confused the two quantities
- Misconception: Spread of observations vs spread of sample means
- Next recommended difficulty: One guided classification item
```

Store the user's exact relevant wording before paraphrasing it into an issue. This prevents a tutor summary from creating a false misconception.

## State Consistency

Treat the current-state block in `memory/learning-state.md` as canonical. After a substantial update:

1. Update progress, mastery tables, active weak points, and next steps together.
2. Remove or rewrite stale summary statements that contradict the canonical state.
3. Repair resolved weak points and any downstream conclusion created by a tutor record error.
4. Keep append-only session and practice logs as historical evidence, but do not let old values remain in current summaries.
5. Run a final consistency check for progress totals, current topic, mastery labels, and next recommended action.

Never leave states such as `16/16 learning_complete` beside a current summary that still says `14/16` or names a resolved weakness as active.

## Compression Recovery

At the start of a new chat or after context loss:

1. Read `.ai-course-tutor/index.md`.
2. Identify the likely course from uploaded materials, registered source fingerprints, or available context. Do not require the user to name the course.
3. Read `course.yml`.
4. Read `indexes/source-register.md`.
5. Read `memory/learning-state.md`.
6. Read `notes/course-map.md`.
7. Continue from the next recommended step unless the user asks for something else.

Before continuing, run the state-consistency check and load the active learning cluster, checkpoint evidence, load signal, and course delivery guardrails.
