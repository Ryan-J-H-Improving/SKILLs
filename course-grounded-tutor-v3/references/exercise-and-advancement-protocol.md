# Exercise And Advancement Protocol

## Purpose

Prevent the tutor from confusing displayed information, a correct recognition choice, or a pacing signal with usable understanding.

```text
visible != explained != demonstrated != exercised != evidenced
```

Uploaded materials are sources, not proof that the user has read them. A correction is teaching, not evidence that the correction has been learned.

## Point Boundary

Define one knowledge point around one coherent relationship, method, comparison, decision rule, or concept family that can be explained and exercised together.

Before teaching it:

1. Load its validated blueprint record.
2. Separate prior knowledge from new terms and supporting prerequisites.
3. Split a point when more than four independent unfamiliar terms do not form one coherent relationship.
4. If segmentation changes, update the blueprint, course map, state denominator, and point order before continuing.
5. Do not create an exercise target from an AI-added label, supporting detail, or enrichment unless the course or user makes it required.

## Four Gate Check

### 1. Transcript Evidence

Confirm the point record contains either:

- a precise matching transcript locator plus the teacher's transition and explanation order; or
- an explicit statement that no matching transcript was supplied, with any minimal tutor bridge labeled `AI-added bridge`.

`Transcript consulted`, `main block`, or a source ID without teaching content does not pass.

### 2. Formula Construction

For every formula needed by the explanation or exercise, establish in this order:

1. The real objects or quantities being described.
2. What is fixed, what varies, and what the formula outputs.
3. Each symbol using the course's notation.
4. Each relationship and operation in dependency order, including subtraction, ratios, summation, transformation, scaling, normalization, limits, conditioning, or optimization.
5. Units, domain, boundary conditions, and geometric or probabilistic meaning when relevant.
6. The final compact formula.
7. A worked example that demonstrates the same reasoning demanded later.

A symbol glossary alone is not a construction. For a transformed expression such as `K((x-X_i)/h)`, understanding one outside factor does not prove the inner displacement and scaling are understood.

### 3. Exercise Coverage And Evidence

Create one post-point exercise set only after explanation and demonstration. Follow `references/exercise-contract-protocol.md` and map each atomic answer action to:

- the exact taught relationship it tests;
- the required cognitive action;
- the source layer;
- the worked example that prepared the action;
- the way the item differs from that example;
- the evidence required to mark that relationship complete.

Do not ask an item if any dependency was merely named, placed in a table, shown in a figure without explanation, or omitted. Do not infer whole-point mastery from an item that samples only one consequence.

Before displaying any exercise, create and validate its immutable JSON contract, render it with `scripts/render_exercise_contract.py`, and display that output verbatim. A handwritten `coverage-gate passed` statement is not evidence.

### 4. Index Consistency

Before displaying progress or advancing, confirm that the validated blueprint, source register, course map, learning state, and progress denominator agree. A source or point-count mismatch blocks teaching until repaired.

## One Exercise Set Per Point

Do not split first-exposure practice into guided and independent stages. After the explanation, provide one labeled `Knowledge-point exercise` set:

- Default to three answer actions.
- Use four or five only when the point contains several separately examinable operations.
- Start at a meaningful course-appropriate level, not a trivial restatement.
- Include interpretation, comparison, calculation, application, or explanation as appropriate to the subject.
- Do not reproduce the worked example by changing only names, values, or surface wording.
- Do not repeat the same relationship in multiple near-identical items.
- Count every subpart, decision, blank, calculation, and requested explanation as an answer action.
- Use only material taught by the end of this point.
- Split compound prompts so each rendered numbered action has one operation, one response slot, and one rubric criterion.
- Do not place requests in the scenario, parenthetical text, sub-bullets, or marking rubric.
- Do not add a scoring criterion that the rendered prompt did not explicitly request and the worked example did not demonstrate.
- Integrated application requires a complete worked demonstration of the integration structure, not only prior teaching of its component frameworks.

Cold diagnostics and strict exam simulations may precede teaching only when explicitly requested and clearly labeled.

## Advancement Evidence

After marking the one exercise set:

- If all required actions are correct and the user expresses no unresolved conceptual uncertainty, mark the point `practiced` and immediately begin the next point. Do not ask whether to continue.
- If the user explicitly asks to skip exercises, continue if appropriate but record the point as `taught`, not `practiced`.
- `Continue`, `okay`, `I see`, `no problem`, copying the explanation, or choosing an answer whose wording reveals the answer are not sufficient mastery evidence.
- Record evidence at relation or operation level. Do not promote the whole point when only part was tested.
- Pass the validated contract path to `scripts/update_learning_state.py`; advancement without a matching contract is invalid.

## Tutor Coverage Failure

Before attributing a wrong, blank, or confused answer to the learner, compare every required dependency with the actual teaching turn and durable blueprint.

If coverage was incomplete:

1. Mark the item `Not counted - tutor coverage gap` and withdraw any score or progress.
2. Record the missing object, term, relationship, operation, example, visual, or transition.
3. Repair the blueprint and all downstream state before resuming.
4. Teach the missing dependency concisely.
5. Ask one new targeted item at the required level; do not repeat the invalid original.
6. Do not record a learner weakness from this event.

One coverage failure triggers a local remaining-point audit. Two in the same lesson trigger a full audit of every remaining point and exercise.

## Genuine Learner Error

When coverage was valid:

1. Identify the exact failed reasoning step.
2. Give one concise correction using course notation.
3. Ask one new targeted item for only that relationship.
4. If the error remains, ask the user to describe their mental model before correcting again.
5. Advance automatically only after the blocking relationship receives valid evidence.

Harmless wording, spelling, or notation that preserves the course meaning receives an inline correction and does not block progress.
