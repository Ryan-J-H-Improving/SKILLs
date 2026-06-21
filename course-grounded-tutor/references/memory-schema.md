# Memory Schema

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
- `practiced`
- `fragile`
- `mastered`
- `exam_ready`

`fragile` means the user can sometimes answer correctly but has a known misconception or unreliable trigger recognition.

## Learning State Contents

Track:

- Course contract summary
- Reply language and note language
- Current mode
- Covered concepts and mastery states
- Known weak points
- Corrections that worked
- Next recommended steps
- Cross-concept links

## Weak Point Entry

Use this shape:

```md
## Standard Error vs Standard Deviation

- Status: fragile
- Evidence: User used sample standard deviation where standard error was required.
- Corrective explanation that worked: Compare spread of observations vs spread of sample means.
- Course notation: `SE(\bar{X})`
- Follow-up needed: One applied scenario question.
```

## Session Log Entry

Append compact entries:

```md
## 2026-06-21

- Mode: learning
- Topic: Sampling distribution
- Sources: Week 3 slides pp. 10-15; transcript 00:12:40-00:24:10
- Taught: Definition, notation, standard error intuition
- User performance: Correct definition, confused SD and SE in calculation
- Updates: Marked standard error as fragile; added follow-up practice
```

## Compression Recovery

At the start of a new chat or after context loss:

1. Read `.ai-course-tutor/index.md`.
2. Identify the likely course from uploaded materials or user context.
3. Read `course.yml`.
4. Read `memory/learning-state.md`.
5. Read `notes/course-map.md`.
6. Continue from the next recommended step unless the user asks for something else.

