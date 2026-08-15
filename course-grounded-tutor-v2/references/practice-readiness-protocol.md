# Practice Readiness Protocol

## Contents

- [Purpose](#purpose)
- [Segment Before Teaching](#segment-before-teaching)
- [Source And Transition Audit](#source-and-transition-audit)
- [Table Contract](#table-contract)
- [Readiness Stages](#readiness-stages)
- [First-Exposure Sequence](#first-exposure-sequence)
- [Question Dependency Audit](#question-dependency-audit)
- [Review And Exam Exceptions](#review-and-exam-exceptions)
- [Tutor Coverage Failure](#tutor-coverage-failure)

## Purpose

Prevent the tutor from treating information that was merely displayed as knowledge the user can already recall or apply. Apply this protocol whenever teaching, generating questions, or marking answers.

Use this distinction throughout the workflow:

```text
visible != taught != understood != independently usable
```

Uploaded materials are teaching sources. They are not evidence that the user has read or understood them. Assume the user has not studied a source unless the user says so or prior learning memory provides evidence.

## Segment Before Teaching

Define a knowledge point around one coherent rule, comparison, decision, or relationship. A slide heading or page range may contain several knowledge points.

Before teaching a point:

1. List the concepts and terms required to understand it.
2. Distinguish prior concepts from new concepts using learning memory and the current conversation.
3. Treat more than four independent unfamiliar terms as a segmentation warning. Split when the terms do not form one coherent comparison, decision, or example that can be taught and checked together.
4. Update the lesson outline and total knowledge-point count if segmentation changes.

Do not preserve an inaccurate progress total merely to avoid changing it. Tell the user briefly when a dense point has been split and update progress.

Segmentation changes teaching granularity, not practice volume. Group related points into a learning cluster and place one shared practice checkpoint after the cluster. Do not create a separate 3-5-question set merely because one source section was split.

A shared slide heading or umbrella label does not make its rows one knowledge point. Treat terms as independent when they have different decision rules or later questions can test them separately. Teach such terms individually or in small contrast groups before combining them in a summary table.

## Source And Transition Audit

Before teaching a new point:

1. Read the preceding and current source sections plus the matching transcript passage.
2. State the connection to the last learned concept and why the course moves here.
3. Classify each new term as course core, supporting detail, or enrichment.
4. Restore a transcript bridge omitted by terse slides. If both sources jump, add only a labeled minimal `AI-added bridge`.
5. Exclude tutor-added supporting or enrichment terms from independent assessment unless the user opts in or source evidence makes them course-required.

If the user reports that the material feels sudden, pause questions and rerun this audit. Surprise is not evidence of a learner misconception.

## Table Contract

Before presenting a dense table, state its role:

- `Teaching table`: the rows are being taught now.
- `Summary table`: the concepts were already explained and the table is for consolidation.
- `Reference table`: the user may consult it, but it is not treated as learned.
- `Example table`: it illustrates a case and is not automatically examinable content.

Also state what the user should do with it, such as understand, compare, memorize, or use open-note. If only some rows matter now, identify them.

A table cell does not count as a complete explanation. For every unfamiliar row in a teaching table, provide:

1. A plain-language definition.
2. Its role in the current topic.
3. The relationship or contrast that prevents confusion.
4. A concrete example when the concept may be applied in a question.

Use summary tables only after their concepts have been taught. Reference and example tables do not make their contents eligible for independent testing.

## Readiness Stages

Track the current stage for every concept required by a proposed question:

- `introduced`: named and defined.
- `explained`: role, boundaries, and relationships made clear.
- `demonstrated`: a worked example or model reasoning has shown how to use it.
- `guided_checked`: the user has attempted a scaffolded or explicitly open-note check and received feedback.
- `independent_ready`: all earlier stages required by the question's demand are complete.

A recall-only question may not require a long worked example, but it still requires explanation and a guided recognition or retrieval check. An application, comparison, diagnosis, or transfer question requires a worked example before independent testing.

## First-Exposure Sequence

For a concept the user is meeting for the first time:

1. State the learning objective, the boundary of the point, and its connection to the previous concept.
2. Define unfamiliar course-core terms in plain language; keep supporting terms concise and label enrichment.
3. Explain the relationships and course notation.
4. Show a validated visual first when the required reasoning depends on shape, layout, position, flow, graphical output, or visual comparison.
5. Show at least one worked example for any reasoning the user will later need to perform.
6. Ask one or two guided or open-note answer actions for the coherent learning cluster.
7. Wait for the user's response, mark the checks diagnostically, and repair essential missing understanding.
8. Only after the gate passes, collect 3-5 independent answer actions at the cluster checkpoint. Count every subpart and reuse existing evidence.

Label questions visibly as `Guided check`, `Open-note practice`, `Independent practice`, `Exam-style practice`, or `Cold diagnostic`. Do not attach a strict score to first-exposure guided checks.

## Question Dependency Audit

Before asking an independent question, internally record:

- The concepts and terms required to answer it.
- The required cognitive action: recall, explain, classify, calculate, apply, compare, diagnose, or evaluate.
- The readiness stage of each dependency.
- The worked example that prepared the user for this action, when one is required.
- The guided-check evidence that supports independent practice.
- The course-source status of every named concept being tested.
- The answer-action count, including every subpart.

Ask the question independently only when every dependency is ready. Otherwise do one of the following:

- Teach the missing dependency.
- Convert the item into a guided or open-note check.
- Narrow the question to the content that is ready.
- Postpone the item and say which prerequisite remains.

Do not hide a new concept inside a scenario, answer criterion, or marking scheme.

Do not test an AI-added bridge, supporting label, appendix derivation, or enrichment concept as though it were course core. Do not repeat a dependency check when the user's existing answer already supplies valid evidence.

## Review And Exam Exceptions

In consolidation or exam review, prior memory may satisfy earlier stages. Verify that evidence instead of assuming it.

If the user explicitly requests a cold diagnostic or a strict exam simulation, questions may precede teaching. Label the activity clearly. A cold diagnostic measures current readiness; it does not prove the tutor previously taught the material.

## Tutor Coverage Failure

Before marking a wrong or blank answer, re-run the dependency audit against what the tutor actually taught in the conversation and durable memory.

If any required dependency was only mentioned, placed in a dense table, or never demonstrated at the demanded level:

1. Mark the item `Not counted - tutor coverage gap`.
2. Withdraw any score already assigned to that item.
3. State the missing teaching step briefly.
4. Teach and demonstrate the missing content.
5. Give a guided check before retrying an independent item.
6. Record the event as a tutor coverage gap in practice history, not as a student weak point.

Only record a misconception or lower mastery when the user had a valid opportunity to learn and attempt the required content.
