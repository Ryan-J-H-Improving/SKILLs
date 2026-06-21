# Tutoring Protocol

## Learning Mode Structure

Teach one knowledge point at a time. Use this structure unless the user requests a different format:

1. Learning objective
2. Source-grounded explanation
3. Formula and notation
4. Course example or useful figure
5. Common misunderstandings
6. Practice questions
7. Marking and remediation after the user answers

## Explanation Rules

- Use slides for official definitions and notation.
- Use transcripts to identify what the teacher emphasized or explained informally.
- Cite sources in compact form: `Source: Week 3 slides p. 12; transcript 00:14:20-00:16:05`.
- Mark extra intuition as AI-added when it is not directly in the course source.
- Preserve course symbols and explain each symbol immediately after any formula.
- Include non-key content, but treat it more briefly than high-priority concepts.
- Expand explanations around the user's known misconceptions.

## Practice Questions

After each knowledge point, provide 3-5 questions:

- Start simple in learning mode.
- Increase difficulty gradually.
- Cover definitions, notation, interpretation, and application.
- Avoid repeating the same question style too often.
- Use course context, datasets, terminology, and examples where possible.

## Remediation Loop

When the user answers:

1. Mark the answer as correct, partially correct, or incorrect.
2. Identify the exact reasoning step that failed.
3. Restate the concept briefly using course notation.
4. Ask a targeted follow-up question or provide a new short practice item.
5. If the user is still wrong, ask the user to explain their current understanding before correcting again.
6. Update `memory/weak-points.md`, `memory/learning-state.md`, and any relevant note section.

## Output Stability

Keep format stable across turns. Do not switch to a new teaching layout unless:

- The user requests it.
- The mode changes from learning to exam review.
- The current content type requires a different structure, such as marking an exam answer.

