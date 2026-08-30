# Exercise Contract Protocol

## Purpose

Prevent a question from requiring a term, operation, answer structure, inference, or marking criterion that was only mentioned, displayed, planned, or added after the learner answered.

```text
mentioned != explained != demonstrated != eligible for assessment
```

The validated teaching blueprint controls the lesson plan. A validated exercise contract controls the exact question shown to the learner and the exact rubric used to mark it.

## Hard Eligibility Rule

Every atomic answer action must reference one stable relationship ID from the current blueprint and must have both:

1. an explanation locator showing the relationship was explicitly taught; and
2. a worked-example locator showing the same cognitive operation was demonstrated in a different context.

The contract's `point_id` must equal the blueprint's stable Point ID, not a mutable value such as `2/10`. Its source fingerprint must match the validated blueprint, and a normal post-point contract must preserve the blueprint's explicit `A# -> R#` mapping. The contract's `tested_relationship`, explanation locator, and worked-example locator must also match that relationship's canonical blueprint mappings; renaming unrelated material to an existing R ID is invalid.

Prior points may be reused when they satisfy both conditions. Merely naming a framework, placing it in a table, displaying a figure, or recording `taught` at point level is insufficient.

For an integrated exercise, knowing the component frameworks is not enough. If the exercise requires a new synthesis structure, response format, multi-framework decision sequence, or accountable recommendation, demonstrate that complete structure before testing it.

## Contract Location And Lifecycle

Store contracts under:

```text
memory/exercise-contracts/<exercise-set-id>.json
```

Copy the shape from `assets/exercise-contract.json.template`. A contract is immutable after the question is displayed. A repair or replacement question receives a new exercise-set ID and a new contract.

Use these exercise kinds:

- `learning_post_point`: 3-5 atomic actions.
- `learning_targeted_repair`: 1-3 atomic actions covering only unresolved relationships.
- `exam_review`: 3-15 atomic actions; preserve the school paper's complexity while maintaining evidence and rubric symmetry.
- `cold_diagnostic`: 1-15 atomic actions, only when explicitly requested and clearly labeled unscored unless the user requests scoring.

## Atomic Action Rule

An atomic action has one operation, one target relationship, one expected response slot, and one rubric criterion.

Count separately:

- a selection and its justification;
- each requested classification;
- each calculation and each requested interpretation;
- each blank, correction, explanation, design choice, indicator, owner, timing decision, or outcome;
- every stakeholder or framework when the prompt requires separate outputs.

The scenario contains facts only. Do not hide requests in the scenario, sub-bullets, parentheses, or marking notes.

Bad:

```text
Choose a method, justify it, calculate the result, and explain the limitation.
```

Valid four-action form:

```text
A1 select the method
A2 state the decisive reason
A3 calculate the result
A4 explain one taught limitation
```

## Question-Rubric Symmetry

For every action:

- the prompt must explicitly request what the rubric will judge;
- the rubric has one criterion only;
- no criterion may depend on an untaught term, response convention, inference, or preferred wording;
- harmless wording that preserves course meaning must not become an extra criterion;
- the marker may not add completeness, ownership, evidence, indicator, format, or precision requirements after seeing the answer unless the prompt explicitly requested and teaching demonstrated them.

## Three Fresh Audits

Before validation, perform three independent checks from fresh perspectives. Do not reuse the question-generation rationale as audit evidence.

1. **Teaching-evidence audit:** inspect the actual learner-visible explanation and worked example for every relation ID. Durable notes may locate evidence but cannot replace missing teaching.
2. **Atomicity-and-load audit:** ignore intended difficulty and count every requested output. Split nested or compound actions and enforce the selected exercise-kind limit.
3. **Question-rubric-symmetry audit:** compare each rendered prompt with its sole marking criterion and reject hidden requirements.

Record a concise, specific evidence statement for each audit. `Looks good` or `covered above` is not evidence.

## Required Execution

Before displaying a question:

1. Complete the explanation and worked example.
2. Create the JSON contract with `status: draft`, complete all three fresh audits, and do not show it yet.
3. Ask the validator to promote the draft only when its content and blueprint binding pass:

   ```bash
   python scripts/validate_exercise_contract.py --contract <contract.json> --blueprint <teaching-blueprint.md> --progress <current/total> --promote --report text
   ```

4. Render with:

   ```bash
   python scripts/render_exercise_contract.py --contract <contract.json> --blueprint <teaching-blueprint.md> --progress <current/total>
   ```

5. Display the rendered output verbatim. Do not add another question, subpart, explanation request, or scoring condition around it.
6. Pass the same promoted contract path to `update_learning_state.py`. The updater blocks pending, scored, or advancing exercise states when the contract is missing, invalid, stale against the blueprint hash, or inconsistent with the point, source fingerprint, or exercise-set ID.

## Failure Handling

If an action lacks valid evidence or the learner identifies an untaught dependency:

1. Withdraw that action as `Not counted - tutor coverage gap`.
2. Do not reinterpret prior mention, a table, or the question itself as teaching evidence.
3. Mark the blueprint stale if its eligibility or demonstration mapping was wrong.
4. Teach and demonstrate the missing relationship.
5. Create a new targeted-repair contract and question.
6. Remove any learner weakness, score, or progress that depended on the invalid action.

Never edit the old contract to make the historical question appear valid.
