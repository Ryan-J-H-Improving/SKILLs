# Assessment Rubric

Read `practice-readiness-protocol.md` before scoring any learning or review answer.

## Pre-Marking Coverage Audit

Before judging the user, identify the concepts, terms, notation, and cognitive action required by the question. Compare them with what was actually taught, demonstrated, and checked in the conversation and durable memory.

Classify the attempt as one of:

- `Valid scored attempt`: every dependency was ready, or the user explicitly requested a scored cold diagnostic or exam simulation.
- `Learning diagnostic`: a valid first-exposure or consolidation attempt; classify understanding without a numeric score by default.
- `Guided diagnostic`: the user is still in scaffolded or open-note practice; give feedback without strict scoring.
- `Not counted - tutor coverage gap`: at least one dependency was only mentioned, shown in a table, or not demonstrated at the required level.

For a tutor coverage gap, withdraw the item's score, teach the missing content, and ask a guided check. Do not add a weak point or lower mastery from that item.

## Marking Principles

Mark user answers according to the mode.

Learning mode:

- Prioritize diagnosing understanding.
- Mark correct, conceptually incorrect, incomplete, or correct with a harmless expression issue.
- Do not attach a numeric score by default, including to independent practice. Use one only when the user explicitly asks for scoring or a labeled scored diagnostic.
- Give concise correction. Ask a follow-up only for a genuine conceptual error or essential omission.
- Treat first-exposure guided checks as diagnostic rather than strict assessment.
- Correct harmless spelling, grammar, wording, or notation inline when the intended course meaning is unambiguous. Do not deduct fractions, block progress, or record a weak point.
- Reuse earlier valid evidence instead of requiring another answer to prove the same understanding.

Exam-review mode:

- Mark strictly.
- Award marks only for steps the answer actually contains.
- Penalize wrong formula selection, missing assumptions, unsupported interpretation, and notation errors that would confuse a marker.
- Give a score when possible.
- Permit pre-teaching scoring only for an explicitly labeled cold diagnostic or exam simulation.

## Feedback Format

Use this format for substantial answers:

```text
Result: Partially correct
Score: 3/5

What you got right:
- ...

Where marks were lost:
- ...

Correction:
- ...

Next targeted question:
- ...
```

For small checks, keep feedback shorter.

In ordinary learning mode, omit the `Score` line unless scoring was requested. State the conceptual status and the smallest next action instead.

## Misconception-Targeted Questions

When a user is wrong, generate the next question to isolate the misconception:

- If the formula choice is wrong, ask a recognition question.
- If substitution is wrong, ask a symbol-identification question.
- If interpretation is wrong, ask for a one-sentence conclusion in context.
- If the user repeats the same mistake, ask them to explain their current understanding before correcting again.

Use at most one immediate targeted remediation round for the same conceptual error. Ask only for missing essential evidence when the answer is incomplete. Do not generate remediation for harmless expression issues.

## Practice History

Record:

- Question topic
- Difficulty
- Question style
- Learning phase and question label
- Required concepts and readiness gate status
- Whether the attempt was scored
- Tutor coverage gap, if any
- Issue class: conceptual error, harmless expression issue, omission, tutor coverage gap, or tutor record error
- Evidence reused from earlier answers
- Answer-action count, including subparts
- User result
- Misconception if any
- Next recommended difficulty

Use this history to avoid repeated shallow questions.
