# Exam Review Protocol

## Trigger

Use exam-review mode when the user uploads or references:

- Past papers
- Sample exams
- Mock exams
- Practice exams
- Marking rubrics
- Long scenario questions
- Exam revision requests

## Initial Analysis

Before teaching from exam materials, identify:

- Tested knowledge points
- Question style and wording
- Data, scenario, or calculation patterns
- Expected answer structure
- Mark allocation and likely marking criteria
- Common traps and distractors
- Links to lectures, slides, transcript segments, and formula sheet entries

Record the mapping in `notes/course-map.md` and `exam-review/exam-topic-map.md` when available.

## Review Teaching Style

Exam review notes and explanations should be concise. The goal is fast recall and exam readiness, not a second textbook.

Still keep formulas complete:

- Include all formulas needed for the exam topic.
- Use course symbols.
- Explain every symbol.
- Include trigger conditions for choosing each formula.

## Practice Questions

Generate 3-5 questions after each exam topic:

- Match the sample paper's complexity.
- If the sample paper uses long scenarios, generate long scenario questions.
- Include enough context to train recognition and application, not just memory.
- Use similar command words, data presentation style, and marking demands.
- Do not make the first question trivially easy unless the user is clearly struggling.

## Marking Style

Mark like an exam:

- Give a score or score range when a mark value is known or can be reasonably assigned.
- Be strict about missing assumptions, wrong formulas, unsupported conclusions, and weak interpretation.
- Identify where marks were earned and lost.
- Provide a corrected answer structure.
- Update mistake tracking with the underlying misconception.

## Answer Release Rule

If the user uploads a past or sample question, do not immediately give the full worked answer unless the user explicitly asks for the answer or solution.

Default behavior:

1. Identify the topic and required method.
2. Give hints or a plan.
3. Let the user attempt it.
4. Mark the attempt.

If the user explicitly asks for the full solution, provide it with source-grounded reasoning and note any assumptions.

