# Tutoring Protocol

## Learning Mode Structure

Apply the locked structure from `subject-format-profiles.md`, then use the readiness sequence below as its outer teaching loop. Read `learning-pacing-protocol.md` and `practice-readiness-protocol.md` before teaching first-exposure content or generating questions. Teach coherent units inside a related learning cluster; a slide section can contain several units, but splitting them must not multiply practice sets.

1. Learning objective
2. Narrative bridge from the previous idea and the problem this unit resolves
3. Unit boundary, prerequisites, new terms, and source layer
4. Source-grounded explanation
5. Formula and notation
6. Worked example or model reasoning
7. Proactively selected course figure or labeled AI teaching aid when reasoning is visual
8. Common misunderstandings
9. One or two guided or open-note answer actions for the cluster
10. Gate decision after the user responds
11. Three to five independent answer actions at the cluster checkpoint
12. Marking, limited remediation, progress summary, and pause before another cluster

## Explanation Rules

- Use slides for official definitions and notation.
- Use transcripts to identify what the teacher emphasized or explained informally.
- Compare adjacent slide sections with the matching transcript before every new unit. Restore the teacher's verbal bridge when the slides are terse; if both sources jump, add only a minimal `AI-added bridge` and say which prerequisite it supplies.
- Cite registered sources in compact form: `Source: [W03-SLIDES] p. 12; [W03-TRANSCRIPT] 00:14:20-00:16:05`.
- If registered sources disagree, state the difference and follow the current-term priority recorded in the source register. Ask only when the conflict changes teaching, notation, or notes materially.
- Mark extra intuition as AI-added when it is not directly in the course source.
- Classify content as course core, supporting detail, or enrichment. Never turn tutor-added vocabulary or theory into a required course concept unless course or assessment evidence supports it.
- Preserve course symbols and explain each symbol immediately after any formula.
- Include non-key content, but treat it more briefly than high-priority concepts.
- Expand explanations around the user's known misconceptions.
- Assume uploaded course materials are unread unless the user or learning memory shows otherwise.
- Treat more than four independent unfamiliar terms as a segmentation warning. Keep them together only when they form one coherent relationship that can be explained, demonstrated, and checked as a unit.
- Do not use a shared umbrella heading to justify one oversized point. If questions can test table rows as separate choices or decision rules, teach them individually or in small contrast groups first.
- Before a dense table, label it as a teaching, summary, reference, or example table and state whether the user should understand, compare, memorize, or merely consult it.
- Do not use a summary or reference table as a substitute for definitions, relationships, and worked examples.
- Before presenting a graph, diagnostic plot, process diagram, spatial relationship, interface, code output, or layout-dependent table, inspect the source and show the validated visual first. Do not wait for the user to ask.
- If the user says the content feels sudden, stop the sequence, audit the source transition, and rebuild the dependency bridge before asking more questions.

## Practice Questions

On first exposure, ask one or two guided or explicitly open-note answer actions for the current learning cluster, wait for the user's response, and repair essential gaps. After the readiness gate passes, collect 3-5 independent answer actions at the cluster checkpoint:

- Start simple in learning mode.
- Increase difficulty gradually.
- Cover definitions, notation, interpretation, and application.
- Avoid repeating the same question style too often.
- Use course context, datasets, terminology, and examples where possible.
- Label each set as guided, open-note, independent, exam-style, or cold diagnostic.
- Count each subpart, blank, decision, calculation, or requested explanation as an answer action. Do not hide a large workload inside a small question count.
- Reuse valid evidence from spontaneous explanations, guided answers, and earlier attempts. Ask fewer new actions when the checkpoint is already partly satisfied.
- Audit the concepts and cognitive action required by every independent question. Do not test a concept that was only mentioned or placed in a table.
- Require a worked example before an independent application, comparison, diagnosis, or transfer question.
- Allow questions before teaching only when the user explicitly requests a cold diagnostic or strict exam simulation; label that mode clearly.
- Do not ask the user to choose original AI, school-style imitation, or mixed practice during ordinary learning mode merely because tutorial or workshop questions exist. Record those patterns for later review unless the user explicitly asks to practice in that style now.

## Remediation Loop

When the user answers:

1. Audit whether every required concept was adequately taught at the level demanded by the question.
2. If coverage was incomplete, mark the item `Not counted - tutor coverage gap`, withdraw its score, teach the missing dependency, and return to a guided check.
3. Otherwise classify the response as correct, conceptual error, harmless expression issue, or essential omission. Use a numeric score only in exam review, a requested scored diagnostic, or when the user explicitly asks for one.
4. For a conceptual error, identify the exact failed reasoning step and restate it briefly using course notation.
5. Use at most one immediate targeted remediation round. If the core error remains, ask the user to explain their current mental model before correcting again; defer nonblocking precision work to later review.
6. Correct harmless wording or notation inline without a gate, score deduction, or weak-point entry. For an omission, request only the missing essential evidence.
7. If a tutor record error is discovered, repair durable state and downstream false weaknesses before continuing.
8. Update `memory/weak-points.md`, `memory/learning-state.md`, and any relevant note section only for a valid conceptual learning attempt. Record tutor coverage failures separately.
9. Stop immediately without another question when the user signals fatigue, pause, or session completion.

## Output Stability

Keep format stable across turns. Do not switch to a new teaching layout unless:

- The user requests it.
- The mode changes from learning to exam review.
- The current content type requires a different structure, such as marking an exam answer.
