# Migration And Lightweight Mode

## Workspace States

Run `scripts/audit_course_workspace.py` before formal teaching.

- `ready`: the workspace schema, promoted blueprint, current-state hash, and required directories agree. Formal teaching may proceed.
- `reference_mirror`: the directory is a read-only discovery/recovery copy. Follow `canonical_course_dir` and audit it; only the canonical workspace can teach or record evidence.
- `migration_required`: legacy or incomplete records need repair. Permit only limited clarification while migration is underway.
- `invalid`: current-schema records contradict each other or fail validation. Permit only limited clarification until repaired.

## Limited Clarification

This is a narrow response to a local question the user explicitly asked, such as defining one term, restating one already supplied sentence, or clarifying what a symbol denotes. It must not:

- begin or resume the planned lesson;
- introduce the next knowledge point;
- issue, score, or repair an exercise;
- record `teaching`, `taught`, `practiced`, `mastered`, or `exam_ready`;
- add mastery evidence or advance numeric progress.

When uncertain whether a request is local clarification or formal teaching, preserve the user's question, repair the workspace first, and do not advance.

Reference mirrors may validate a limited clarification, but state updates, blueprint promotion, and exercise-contract promotion are mechanically blocked. Do not repair or migrate a mirror in place; work in its canonical directory or explicitly change the canonical assignment first.

## Legacy Blueprint Migration

Create a sidecar draft without changing the active file:

```bash
python scripts/migrate_blueprint_v3_to_v31.py create-draft \
  --course-dir <course-dir> \
  --lesson-id <lesson-id>
```

Repair every migration placeholder from registered sources. Then obtain a grouped report and promote only when all checks pass:

```bash
python scripts/validate_teaching_blueprint.py \
  --blueprint <course-dir>/indexes/teaching-blueprint.v31-draft.md \
  --promote --report text

python scripts/migrate_blueprint_v3_to_v31.py activate \
  --course-dir <course-dir>
```

Activation preserves the old blueprint as a timestamped backup. It does not promote learner progress. Blueprint activation marks `workspace_migration_status: pending_reconciliation`, so do not run the formal state updater yet. Complete the legacy source and state migration below, then rerun the workspace audit.

## Legacy Source And State Migration

Use `scripts/migrate_legacy_workspace.py` after the V3.1 blueprint is promoted and activated. The selected safe recovery point must be an existing stable Point ID. Migration never infers mastery from old prose, tables, scores, `introduced`, `practiced`, or `mastered` labels.

1. Run `plan` to identify the source-index and learning-state formats without writing.
2. Run `create-draft` with an explicit `--safe-point-id`. Use `--dry-run` first when checking a new legacy shape.
3. Inspect the sidecars under `migration/v3.1.1-legacy/`. The generated source table is an index aid; the complete old `sources.md` remains preserved in the draft.
4. Run `validate-draft`. It requires a ready V3.1 blueprint, matching point and progress, current blueprint hash and source fingerprint, a structured source row, and `Point status: not_started`.
5. Run `activate --dry-run`, then `activate`. Activation rechecks every original fingerprint, writes timestamped backups, creates the exercise-contract directory, and atomically replaces each managed text file.
6. Rerun `audit_course_workspace.py`. A course is ready only when `workspace_migration_status` is `complete` or `not_required` and every other gate passes.

Do not delete legacy `sources.md`, preserved state sections, or migration backups. Do not edit a draft after its source files changed; regenerate it so the manifest records the new baseline.

## Lightweight Questions In Ready Workspaces

A ready workspace may answer a small clarification without creating an exercise contract or updating memory when the answer neither changes progress nor supplies assessment evidence. Keep the locked reply language and course notation, ground the answer in the current source, and return to the recorded point afterward. Any planned explanation, new point, exercise, scoring, remediation, or mastery decision uses the full workflow.
