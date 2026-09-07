# Teaching Blueprint Protocol

## Purpose

Prevent teaching quality from depending on ad hoc reasoning in one chat or one model. The course map holds the cumulative cross-lesson roadmap. Each registered lesson blueprint is a user-readable, durable plan for exactly one lecture, tutorial, lab, or other coherent lesson and records source evidence, transitions, dependencies, formulas, visuals, question coverage, and learner risks.

Use `indexes/blueprints/manifest.json` as the machine registry, the `course.yml` active blueprint path as the current teaching authority, `notes/course-map.md` as the cumulative learner-facing roadmap, and `memory/learning-state.md` as current execution state. Point totals are lesson-local.

## Start-Of-Chat Preflight

At the start or resumption of every teaching chat:

1. Identify the course, run `scripts/resolve_course_workspace.py --course-dir <discovered-course> --require-ready`, and use only the returned canonical path.
2. Read `indexes/source-register.md`, `indexes/blueprints/manifest.json`, the active lesson blueprint declared in `course.yml`, `memory/learning-state.md`, `notes/course-map.md`, and active weak points.
3. Compare the blueprint source fingerprint and scope with registered materials.
4. Compare the active lesson's point total and order with the lesson-local progress denominator. Compare lesson presence and prerequisites with the cumulative course map.
5. If all records agree and the blueprint status is `ready`, load the next point. Do not recompute a valid plan merely because the chat or model changed.
6. If the manifest or active blueprint is absent, stale, cumulative, incomplete, or inconsistent, do not start formal teaching. Enter limited clarification, build or repair one lesson draft, and promote it with `scripts/validate_teaching_blueprint.py --promote --activate`.
7. Repeat canonical resolution immediately before every durable course write. A chat-start audit becomes stale if the workspace is migrated while the chat remains open.

The user does not need to request this analysis. Keep the user-facing preflight summary compact; the detailed record belongs in the blueprint.

## Whole-Scope Analysis

Analyze every currently available lecture or lesson before teaching the first point. Record the overall sequence, prerequisites, and supplied/missing scope in the course map. Then create one blueprint file per supplied lesson; never append a new lesson's points to the previous active file. When only part of a course has been supplied, mark future material as unavailable and never fabricate it.

For each source set:

1. Inspect all slide headings, definitions, formulas, examples, diagrams, and summary pages.
2. Segment matching transcripts into semantic passages. If timestamps or line numbers are coarse, use speaker, slide range, and a short unique anchor phrase as the locator.
3. Recover the lecturer's narrative: what question starts the section, what prior idea it uses, why the next concept appears, and what emphasis or warning the lecturer repeats.
4. Check relevant tutorials, school questions, and exams for scope and assessed operations without assuming ordinary tutorial style is exam style.
5. Separate course core, supporting prerequisites, AI-added bridges, and enrichment.
6. Identify notation collisions, overloaded symbols, hidden prerequisites, abrupt source transitions, formula transformations, and visually dependent reasoning.
7. Design coherent knowledge points around one relationship, method, decision, or concept family. Do not use slide count as the segmentation rule.

## Novice Teaching Simulation

Simulate the lesson from the perspective of a learner who has not read the uploaded materials. For every planned point, answer:

- What does the learner already know at this exact position?
- What new course terms appear, and have all of them been defined before use?
- What connects this point to the preceding one?
- Does the source itself supply that transition? If not, what minimal labeled bridge is required?
- Can the worked example be followed using only prior points and the current explanation?
- Can every planned exercise be answered using only content actually taught before it?
- Does a formula contain an unexplained object, operator, transformation, fixed/varying role, unit, or normalization step?
- Does the reasoning require a figure before text explanation?
- Is the point too large for one coherent explanation and one exercise set?
- Is the planned exercise meaningfully different from the worked example and difficult enough to reveal understanding?

If any answer exposes a gap, revise the plan before teaching.

## Three Independent Blueprint Audits

Complete all three from fresh checking perspectives and record `pass` only when each succeeds:

1. **Source-fidelity audit:** verify every point against slides and the matching transcript passage; check notation, source layer, lecturer emphasis, and source conflicts.
2. **Dependency-and-order audit:** ignore the source's page order temporarily and verify that every prerequisite, term, relationship, and formula operation appears before use. Confirm point totals and cross-file order.
3. **Novice-and-assessment audit:** simulate the learner encounter and planned exercises. Check cognitive load, visual timing, nontrivial difficulty, no copied worked examples, and no hidden untaught requirements.

These audits are separate from the three independent image-validation passes.

## Required Point Record

Each point in one registered lesson blueprint under `indexes/blueprints/` must record:

- Point number, stable title, and a stable `Point ID` such as `week-03-point-02`. Do not use the mutable progress fraction as the identifier.
- Previous dependency and the last stable concept it builds on.
- Why this point appears now and the course question it resolves.
- Slide or document evidence with precise locator.
- Transcript status, precise locator, teacher transition, and explanation sequence.
- Course core, supporting detail, AI-added bridge, and enrichment boundaries.
- New terms and when each is defined.
- Formula construction plan: objects, fixed/varying roles, relationships, each operation or transformation, final notation, units or normalization, and worked example.
- Visual decision and source figure or teaching-aid plan.
- One post-point exercise set plan, including tested relationships, cognitive actions, difficulty, and how it differs from the worked example.
- Stable eligible relationship mappings such as `R1 = canonical relationship meaning`, each limited to a relationship that is explicitly explained and demonstrated. Relationship IDs are local to the Point ID.
- An explanation mapping such as `R1 = notes/study-notes.md#exact-anchor` for every eligible relationship.
- A demonstration mapping such as `R1 = notes/study-notes.md#worked-example-step` for every eligible relationship.
- An explicit exercise-action mapping such as `A1 -> R1; A2 -> R1; A3 -> R2`. Use three to five actions; distinct cognitive actions may test the same relationship without inventing extra relationships.
- A question-rubric boundary stating the one explicit prompt and one criterion rule; do not plan hidden requirements.
- Automatic-advance evidence and likely blocking misconceptions.
- Load risk and any planned concise treatment for low-priority content.

A generic entry such as `transcript: main block`, `explain symbols`, or `ask questions` is insufficient.

Blueprint version `3` does not contain enforceable relationship and exercise-contract mappings. Repair it to version `3.1` before using it for new questions or advancement. Preserve valid source analysis and ordering; do not erase learning history.

## Draft And Promotion Workflow

Keep `Blueprint status: draft` while constructing or repairing a plan. Use `--report text` for grouped repair guidance or `--report json` for tool consumption. `--dry-run` checks whether promotion would succeed without modifying files.

```bash
python scripts/validate_teaching_blueprint.py \
  --blueprint <course-dir>/indexes/blueprints/<lesson-id>.md \
  --promote --dry-run --report text

python scripts/validate_teaching_blueprint.py \
  --blueprint <course-dir>/indexes/blueprints/<lesson-id>.md \
  --promote --activate --report text
```

Promotion changes draft to ready only after content validation passes, writes atomically through a same-directory temporary file, registers the file and hash, and synchronizes `course.yml` only when it is already active or `--activate` is supplied. Do not hand-edit `ready` or the manifest as a substitute for validation. Workspace auditing reopens every registered blueprint.

For a legacy V3 blueprint, use `scripts/migrate_blueprint_v3_to_v31.py create-draft` to create `teaching-blueprint.v31-draft.md`. Complete and promote the sidecar before `activate` replaces the official path and creates a timestamped backup.

For a V3.1 cumulative or unregistered blueprint, use `scripts/migrate_lesson_blueprints.py plan`, then `create-draft`, `activate --dry-run`, and `activate`. It preserves the source as a legacy hash anchor, splits by stable Point ID prefix, changes progress to the active lesson's local denominator, rewrites old cumulative Point references to stable Point IDs, and rebinds only active-lesson contracts.

A lesson blueprint is invalid if its prose still treats a course-wide Point number or denominator as teaching authority. Cross-lesson dependencies must use stable IDs such as `week-04-p11`; learner-facing numeric position must use the active lesson's own total.

When a legacy point has no Point ID, migration assigns a title-independent frozen ID such as `week-04-p07` from its original position. Treat that value as an opaque constant after first assignment. Renaming, renumbering, or moving a point must preserve its existing Point ID; no tool may recompute an ID already present in the blueprint.

## Transcript Evidence Gate

When a matching transcript exists, a point passes only if the blueprint preserves:

1. A usable passage locator.
2. The lecturer's transition from the previous idea.
3. The lecturer's explanation order or worked example.
4. Any explicit emphasis, limitation, or exam-relevant warning.

Registration and citation alone do not count as transcript use. If no transcript was supplied, record that explicitly and build the source bridge from slides plus the minimum labeled AI-added prerequisite.

## Change And Consistency Rules

The blueprint becomes stale when:

- A relevant source is added, replaced, or reclassified.
- Knowledge points are split, merged, reordered, or renamed.
- A tutor coverage failure reveals a missing dependency or operation.
- The course notation or teaching profile changes.
- The source register, manifest, course map, lesson-local progress denominator, or learning state disagrees with the active blueprint.

When stale:

1. Stop new teaching.
2. Repair the blueprint first.
3. Update course map and current state from the repaired plan.
4. Promote the repaired draft with the validator and rerun the workspace audit.
5. Resume from the last point with valid evidence, not from the furthest point previously displayed.

One tutor coverage failure requires a local plan audit. Two in the same lesson require a full audit of every remaining point and exercise before resuming.

## Model And Compression Continuity

After context compression, a new chat, or a model change, trust validated durable evidence rather than a prior model's confidence statement. Load the exact point record, source locators, unresolved relations, and planned exercise. Legacy statuses such as `guided` or `practiced` are not sufficient when their recorded evidence does not satisfy the V3.1 gates. Load the active immutable exercise contract before marking or resuming a pending question.
