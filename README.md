# SKILLs

Personal Codex skills distilled from real study, work, and life experience.

This repository collects Codex skills I created from practical problems I have personally encountered. Each skill is meant to capture a reusable workflow, not just a one-time prompt.

## Skills

| Skill | Description |
| --- | --- |
| [course-grounded-tutor](./course-grounded-tutor) | A course-grounded AI tutoring workflow that teaches from lecture slides, transcripts, exams, notes, and personalized learning memory while preserving course notation, language contracts, weak-point tracking, and exam-review behavior. |

## Purpose

The goal of this repository is to turn real experiences into reusable AI workflows.

These skills are built around problems such as:

- studying real courses with large amounts of material
- keeping AI explanations grounded in official course sources
- preserving teacher-specific notation, terminology, and emphasis
- maintaining stable reply and note languages across chats
- tracking weak points, mistakes, and mastery over time
- turning learning sessions into concise study and exam-review notes

## Repository Structure

Each skill lives in its own folder:

```text
skill-name/
  SKILL.md        # Main Codex skill instructions
  README.md      # Human-readable overview
  agents/         # Optional agent configuration
  assets/         # Optional templates or reusable files
  references/     # Detailed protocols and supporting rules
  scripts/        # Optional helper scripts
```

## Usage

Clone or download this repository, then copy the skill folder you want to use into your Codex skills directory.

For example, to install `course-grounded-tutor`:

```text
~/.codex/skills/course-grounded-tutor
```

On Windows, this is usually:

```text
%USERPROFILE%\.codex\skills\course-grounded-tutor
```

Then start a new Codex chat and invoke it with:

```text
Use $course-grounded-tutor to teach from these lecture slides and transcript.
```

## License

This repository is licensed under the [MIT License](./LICENSE).
