# Learning Pacing Protocol

## Purpose

Keep first-exposure teaching coherent and sustainable. Segmentation protects understanding, but it must not multiply practice or turn every supporting term into a separate test.

## Teaching Units, Learning Clusters, And Checkpoints

Use three separate concepts:

- `Teaching unit`: one coherent rule, comparison, method, relationship, or decision boundary.
- `Learning cluster`: one or more tightly related teaching units that answer a shared course question.
- `Practice checkpoint`: the point at which evidence is collected for the whole cluster.

Splitting a dense source section into more teaching units does not create a new 3-5-question requirement for every unit. Keep the lesson total accurate, but place independent practice at coherent checkpoints.

## Restore The Course Narrative

Before each new teaching unit, inspect the adjacent slides and the matching transcript passage. Give a brief bridge that answers:

1. What previous idea this unit depends on.
2. Why the course introduces it now.
3. What question or limitation it resolves.
4. Which terms are genuinely new.

If the slide transition is abrupt but the transcript contains a verbal bridge, restore that bridge. If both sources jump, say so briefly and add only the minimum tutor-created bridge needed for understanding; label it `AI-added bridge`.

Do not begin with an unexplained table, term list, formula, diagnostic plot, or formal definition. Establish the problem it solves first.

## Source Layers

Classify content before teaching or testing it:

1. `Course core`: definitions, notation, methods, examples, or reasoning supported by current slides, transcript emphasis, or assessed material.
2. `Supporting detail`: a short prerequisite, bridge, vocabulary aid, or clarification needed to understand the core.
3. `Enrichment`: appendix derivations, broader theory, alternative terminology, or AI-added extensions that are useful but not required now.

Teach course core fully. Keep supporting detail concise. Defer enrichment unless it resolves a current misunderstanding, the user asks, or available evidence makes it exam-relevant.

Do not promote an AI-added named concept into a mastery target merely because it is pedagogically useful. A supporting or enrichment term is not independently testable unless course evidence supports it or the user explicitly opts in.

## Session Batch Size

Default to one dense unit or one to two moderate units before stopping at a checkpoint. Use up to three only when the units are short, tightly related, and the user is responding comfortably.

At the checkpoint, summarize the relationship among the units, collect the planned evidence, show the next course connection, and wait for a clear continue signal before opening another cluster.

## Practice Economy

In first-exposure learning mode:

- Use one or two lightweight guided answer actions for a cluster, not automatically for every teaching unit.
- After readiness, use three to five independent answer actions for the completed cluster.
- Count every requested decision, blank, calculation, explanation, or subpart as an answer action. A question with five subparts consumes five actions.
- Reuse valid evidence from the user's spontaneous explanations, guided answers, and earlier attempts. Do not ask the same understanding again under a new label.
- If existing evidence already covers part of the checkpoint, ask fewer than three new actions and record why.
- Move nonessential transfer practice to a later spaced mixed review.

The 3-5 range applies separately in exam review as defined by `exam-review-protocol.md`; exam-style questions may contain realistic subparts when they match the source assessment.

## Response Classification And Remediation

Classify a problem before creating another question:

- `Conceptual error`: the user's reasoning changes the statistical, mathematical, scientific, or course conclusion. Give one concise reteach and at most one immediate targeted remediation round.
- `Harmless expression issue`: spelling, grammar, wording, or notation that does not change meaning. Correct inline; do not gate, score fractionally, or record a weak point.
- `Essential omission`: ask only for the missing evidence, not a full replacement set.
- `Tutor coverage gap`: withdraw the item, teach the missing dependency, and use a guided check. Do not attribute the gap to the user.
- `Tutor record error`: repair durable state and every downstream false weakness before continuing.

After one immediate remediation round, defer nonblocking precision work to spaced review. If the user remains wrong on a core dependency, ask for their current mental model before reteaching.

## Load And Fatigue

Stop immediately when the user says they are tired, wants to pause, does not want more questions, or wants to end the session. Do not append a final quiz.

Treat repeated short answers, declining detail, multiple objections to question volume, or repeated requests to move on as possible load signals. Reduce the current checkpoint, summarize durable progress, and offer the next cluster only after a later clear continue signal.

## Surprise Recovery

If the user says content appeared suddenly, cannot see why it belongs, or is confused by many new terms:

1. Pause new teaching and questions.
2. Compare the source slide transition with the transcript transition.
3. Separate course core from supporting and AI-added content.
4. Rebuild the dependency chain from the last understood concept.
5. Give a short bridge and one worked connection.
6. Resume only after the user can state where the new unit fits.

Do not treat surprise as a learner weakness until the transition and source coverage have been audited.
