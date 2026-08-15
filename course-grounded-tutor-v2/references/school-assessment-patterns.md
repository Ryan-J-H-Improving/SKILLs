# School Assessment Patterns

## Purpose

Use school-provided questions to learn how the course tends to ask, frame, and mark questions. This mainly supports later midterm and final revision.

## Trigger

Use this protocol for analysis when the user uploads:

- Tutorial questions
- Workshop questions
- School-provided practice sets
- Sample quizzes
- Sample midterms or finals
- Assignment-style questions
- Marking rubrics or solutions

In ordinary learning mode, tutorial sheets, workshop questions, and small practice sets should usually be treated as low-confidence evidence. Analyze and record them, then continue normal learning-mode practice unless the user explicitly asks for school-style practice.

Use the school-style practice choice only when:

- The user is in midterm or final revision.
- The user uploads or references past papers, sample exams, mock exams, marking rubrics, or exam-style questions.
- The user explicitly asks for school-style, tutorial-style, or teacher-style practice.

## Analysis

For each source, identify:

- Tested knowledge points
- School's likely assessment intent
- Wording signals
- Scenario length and data style
- Required operations
- Expected answer structure
- Marking expectations
- Common traps
- Difficulty level
- Similarities to previous school questions
- Evidence confidence: low, medium, or high

Record the result in `exam-review/school-question-patterns.md`.

## Practice Generation

When generating review questions and school patterns are available in exam-review mode, midterm/final revision, or an explicit school-style request, ask the user which style they want:

1. Original AI questions
2. School-style imitation
3. Mixed set

Do not ask this style-choice question during ordinary concept learning merely because a tutorial sheet exists. In that situation, keep the standard learning-mode practice flow and store the pattern evidence for later.

If there is not enough evidence to imitate the school style reliably, say that the imitation will be provisional. A single tutorial sheet is usually low-confidence evidence unless it clearly matches an exam rubric or repeated course pattern.

## Boundary

Do not directly solve a current graded assessment unless the user clearly asks for a worked solution and the task is appropriate to answer. Default to topic mapping, hints, similar practice, and marking the user's attempt.
