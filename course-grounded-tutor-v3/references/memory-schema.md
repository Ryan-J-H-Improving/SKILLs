# Memory Schema

## Purpose

Preserve teaching quality across context compression, separate chats, lower reasoning settings, and model changes. Memory must remain concise, user-readable, and evidence-based.

## Files

```text
indexes/teaching-blueprint.md
memory/learning-state.md
memory/session-log.md
memory/weak-points.md
memory/practice-history.md
memory/exercise-contracts/<exercise-set-id>.json
notes/course-map.md
```

The blueprint is canonical for source scope, point order, dependencies, and total. The current-state block is canonical for execution progress. Append-only logs are evidence, not current truth.

`course.yml` stores the unique top-level `workspace_schema_version`, `workspace_migration_status`, and `workspace_role`. Do not infer these values from indented generic keys such as `version` or `status`. Current schema version is `1`; blueprint format version is independently `3.1`. Formal teaching requires migration status `complete` or `not_required` and workspace role `canonical`.

Use `reference_mirror` only for a duplicate retained for discovery or recovery. It must record an absolute `canonical_course_dir`, last-sync time, and the canonical blueprint and learning-state hashes observed at that sync. Drift warnings describe mirror freshness; they never authorize teaching from the mirror. There must be only one writable canonical state and one exercise-contract history for each course instance.

## Point States

- `not_started`
- `teaching`
- `exercise_pending`
- `taught`
- `practiced`
- `fragile`
- `mastered`
- `exam_ready`

`taught` means explanation and demonstration were completed but no valid full point exercise evidence exists, including when the learner explicitly skipped practice. `practiced` requires valid evidence for every relationship claimed by the point. `fragile` requires a genuine learner misconception after valid tutor coverage.

Legacy `introduced` or `guided` states are incomplete. Legacy `practiced` states remain provisional when their evidence does not satisfy the V3.1 gates.

## Current State Contents

Track:

- Course contract and locked languages.
- Current mode, lesson, stable Point ID, point number, and blueprint total.
- Workspace schema version plus blueprint path, source fingerprint, validation status, SHA-256, and point record.
- Transcript evidence and narrative bridge for the current point.
- Formula construction status and unresolved operations.
- Exercise-set status, answer-action count, tested relationships, and evidence gained.
- Validated exercise-contract path and SHA-256 fingerprint for every issued or scored set.
- Automatic-advance eligibility.
- Tutor coverage failure count for the lesson.
- Remaining-lesson audit status after repeated tutor failures.
- Valid learner weak points and corrections that worked.
- Learner load or stop signal.
- Last stable point and exact next recovery step.

## Session Log Entry

Append only at meaningful milestones:

```md
### 2026-08-26T14:30:00+10:00

- Mode: learning
- Lesson progress: 2/10
- Point: Sampling distribution
- Blueprint: ready; source fingerprint abc123
- Transcript evidence: W03 transcript 00:12:40-00:16:05
- Exercise status: passed, 3/3 actions
- Evidence: distinguished SD from SE and applied the course formula
- Tutor coverage failures this lesson: 0
- Next: automatically teach point 3
```

Do not append a full session entry after every short clarification.

## Practice History Entry

Record enough to audit mastery:

```md
### 2026-08-26T14:35:00+10:00

- Point: 2/10 Sampling distribution
- Exercise set: post-point set 1
- Exercise contract: memory/exercise-contracts/post-point-set-1.json
- Exercise contract SHA256: <hash>
- Tested relationships: population SD vs standard error; formula selection
- Cognitive actions: explain; apply
- Answer actions: 3
- Coverage gate: passed
- Formula construction gate: passed
- Result: 3/3 conceptually correct
- Evidence gained: both planned relationships
- Automatic advance: yes
```

Store the user's exact relevant wording before paraphrasing a misconception. Do not use `continue`, `okay`, or similar pacing messages as evidence.

## Weak Point Entry

Create a weak point only after valid tutor coverage:

```md
### Standard Error vs Standard Deviation

- Status: fragile
- Exact evidence: User used sample standard deviation where standard error was required.
- Failed relationship: spread of observations vs spread of sample means
- Corrective explanation that worked: compare the two sampling objects
- Course notation: `SE(\bar{X})`
- Follow-up: one spaced applied item
```

Tutor coverage failures belong in practice history and blueprint repair records, never learner weak points.

## State Consistency

After a point completion, blueprint change, tutor record repair, or session stop:

1. Compare the source fingerprint, point order, and total across blueprint, course map, and state.
2. Update the canonical current-state block.
3. Remove stale current summaries that contradict it.
4. Repair every downstream weakness or progress statement created by a tutor error.
5. Keep historical logs append-only but clearly mark withdrawn evidence.

Never leave a completed count that depends on a withdrawn exercise.

Prefer the exclusive JSON interface for state changes:

```bash
python scripts/update_learning_state.py --print-schema
python scripts/update_learning_state.py --state-json <state-update.json> --dry-run
python scripts/update_learning_state.py --state-json <state-update.json>
```

Start from `assets/state-update.json.template`. JSON mode rejects unknown fields and cannot be mixed with state-field CLI flags. The legacy flag interface remains supported. Both modes validate the complete update before writing and replace managed files atomically.

The updater owns only the managed current-state block and entries it appends or upserts through documented headings. Preserve user-authored text outside those regions. Session and practice history are append-only; correct prior mistakes with explicit withdrawal records rather than silent deletion.

## Compression Recovery

At a new chat or after context loss:

1. Read `.ai-course-tutor/index.md` and identify the course from materials and fingerprints.
2. Read `course.yml` and `indexes/source-register.md`.
3. Read and validate `indexes/teaching-blueprint.md`.
4. Read `memory/learning-state.md`, active weak points, and the relevant practice evidence.
5. Read the current point in `notes/course-map.md`.
6. Check all four gates and cross-file consistency.
7. Resume the recorded action directly. Do not ask the user to restate the course or whether to continue.
