# SKILLs
A platform-aware AI tutoring skill for students who want teaching grounded in their actual course materials instead of generic explanations.

Personal Codex skills distilled from real study, work, and life experience.

This repository collects Codex skills I created from practical problems I have personally encountered. Each skill is meant to capture a reusable workflow, not just a one-time prompt.

## Skills

| Skill | Description |
| --- | --- |
| [course-grounded-tutor-v3](./course-grounded-tutor-v3) | **Recommended: V3.3.1.** Adds lesson-scoped teaching blueprints, bounded exercise contracts, pre-write canonical resolution, dirty-mirror blocking, note auditing, figure delivery checks, and lesson-local progress. |
| [course-grounded-tutor-v2](./course-grounded-tutor-v2) | Previous V2 workflow, retained for version history and comparison. |
| [course-grounded-tutor](./course-grounded-tutor) | Original V1 workflow, retained as the first stable release. |

## Current Release

`course-grounded-tutor-v3` is the maintained version. V3.3.1 prevents long-running chats from writing to a workspace that has since become a mirror, separates the cumulative course map from one blueprint per lesson, and rejects legacy cumulative progress references inside lesson-scoped plans.

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

Clone or download this repository, then copy the versioned skill folder you want to use into your agent's skill directory.

For example, to install the recommended V3 release in Codex:

```text
~/.codex/skills/course-grounded-tutor-v3
```

On Windows, this is usually:

```text
%USERPROFILE%\.codex\skills\course-grounded-tutor-v3
```

Then start a new Codex chat and invoke it with:

```text
Use $course-grounded-tutor-v3 to teach from these lecture slides and transcript.
```

Other agents can use the same `SKILL.md` and supporting files when they support Agent Skills-style instructions and local Python execution. `agents/openai.yaml` is an optional Codex adapter.

## License

This repository is licensed under the [MIT License](./LICENSE).
