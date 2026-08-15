# Subject Format Profiles

## Purpose

Select one stable teaching structure that fits the course instead of forcing every subject into the same explanation format. Store the selected profile in `course.yml` and reuse it across chats.

## Selection

Infer the profile from the course materials, assessed work, notation, and dominant reasoning task. Use one primary profile and add a modifier only when the course is genuinely mixed.

| Profile | Use when the course mainly requires |
| --- | --- |
| `quantitative-formal` | Formulas, derivations, calculations, statistical or mathematical interpretation |
| `computational-systems` | Code, algorithms, pipelines, architectures, data flows, or debugging |
| `conceptual-case-based` | Frameworks, classifications, business decisions, policy, or applied cases |
| `evidence-argument` | Claims, evidence, readings, critique, essays, or competing interpretations |
| `language-terminology` | Vocabulary, grammar, translation, definitions, or dense term hierarchies |
| `mixed` | Two profiles are both essential to the same assessed task |

If confidence is low and the choice would noticeably change teaching, show 2-3 likely profiles with a one-line example and let the user choose. Do not ask when the material makes the choice clear.

## Stable Structures

### Quantitative-Formal

1. Objective and prerequisites
2. Course definition and notation
3. Intuition or derivation
4. Fully worked example with units and interpretation
5. Assumptions, method-selection triggers, and common errors
6. Readiness check, then independent practice

### Computational-Systems

1. Objective, inputs, outputs, and constraints
2. Component, algorithm, or pipeline model
3. Step-by-step trace using course terminology
4. Code, pseudocode, diagram, or data example when useful
5. Failure modes, tradeoffs, and operational checks
6. Readiness check, then independent practice

### Conceptual-Case-Based

1. Objective and decision boundary
2. Plain-language definitions
3. Relationships, contrasts, and framework
4. Worked case showing how the framework changes a decision
5. Exceptions, limitations, and common confusions
6. Readiness check, then independent practice

### Evidence-Argument

1. Question or claim
2. Key concepts and source position
3. Evidence and reasoning chain
4. Counterargument, limitation, or competing view
5. Model paragraph, outline, or case analysis
6. Readiness check, then independent practice

### Language-Terminology

1. Communicative goal or concept family
2. Term, form, pronunciation, or course definition
3. Hierarchy and contrast with nearby terms
4. Positive examples and non-examples
5. Usage constraints, memory cue, and common confusion
6. Readiness check, then independent practice

### Mixed

Name the primary profile and one modifier, for example `computational-systems + quantitative-formal`. Keep one stable outer structure and insert the modifier only where the assessed task needs it.

## Lock And Change Rules

Store:

```yaml
teaching:
  teaching_profile: "computational-systems"
  profile_source: "inferred_from_slides_and_assessments"
  locked: true
```

Do not change the profile because one lesson has a different content type. Change it only when the user explicitly asks for a different structure or sustained course evidence shows the current profile is a poor fit. Record the reason in `memory/session-log.md`.

The profile controls explanation order, not content coverage. Continue to follow the practice-readiness gate, source rules, language contracts, and mode-specific assessment rules.
