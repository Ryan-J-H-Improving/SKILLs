#!/usr/bin/env python3
"""Create and activate a sidecar V3-to-V3.1 blueprint migration draft."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from validate_teaching_blueprint import (
    ACTION_RELATION_RE,
    FIELD_RE,
    POINT_RE,
    parse_fields,
    validate_blueprint,
)
from workspace_common import (
    BLUEPRINT_VERSION,
    SKILL_VERSION,
    WORKSPACE_SCHEMA_VERSION,
    atomic_write_text,
    set_yaml_scalar,
)


MIGRATION_FIELDS = [
    (
        "Eligible relationships",
        "<MIGRATION REQUIRED: define R1 = one canonical taught relationship; continue as needed>",
    ),
    (
        "Explanation mapping",
        "<MIGRATION REQUIRED: map every R# to an exact learner-visible explanation locator>",
    ),
    (
        "Demonstration mapping",
        "<MIGRATION REQUIRED: map every R# to an exact worked-example locator>",
    ),
    (
        "Question-rubric boundary",
        "<MIGRATION REQUIRED: one explicit prompt and one matching taught criterion per action>",
    ),
]


def frozen_point_id(lesson_id: str, position: int) -> str:
    """Allocate a title-independent ID once; existing IDs are never recomputed."""
    normalized_lesson = re.sub(
        r"[^a-z0-9._-]+", "-", lesson_id.strip().lower()
    ).strip("-")
    if not normalized_lesson:
        raise ValueError("lesson ID cannot produce a stable Point ID")
    return f"{normalized_lesson}-p{position:02d}"


def _replace_global_field(text: str, field: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^- {re.escape(field)}:\s*.*$")
    if not pattern.search(text):
        raise ValueError(f"Blueprint field not found: {field}")
    replacement = f"- {field}: {value}"
    return pattern.sub(lambda _match: replacement, text, count=1)


def migrate_point_block(block: str, lesson_id: str, position: int) -> str:
    fields = {name.strip(): value.strip() for name, value in FIELD_RE.findall(block)}
    lines = block.splitlines()
    insert_at = 1
    additions: list[str] = []
    if "Point ID" not in fields:
        additions.append(f"- Point ID: {frozen_point_id(lesson_id, position)}")
    for field, placeholder in MIGRATION_FIELDS:
        if field not in fields:
            additions.append(f"- {field}: {placeholder}")

    coverage = fields.get("Exercise coverage", "")
    if coverage and not ACTION_RELATION_RE.search(coverage):
        pattern = re.compile(r"(?m)^- Exercise coverage:\s*(.*?)\s*$")
        block = pattern.sub(
            lambda match: (
                f"- Legacy exercise coverage: {match.group(1)}\n"
                "- Exercise coverage: <MIGRATION REQUIRED: map 3-5 actions as "
                "A1 -> R1; A2 -> R2; A3 -> R3>"
            ),
            block,
            count=1,
        )
        lines = block.splitlines()
    elif "Exercise coverage" not in fields:
        additions.append(
            "- Exercise coverage: <MIGRATION REQUIRED: map 3-5 actions as "
            "A1 -> R1; A2 -> R2; A3 -> R3>"
        )

    if additions:
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
        lines[insert_at:insert_at] = additions + [""]
    return "\n".join(lines).rstrip() + "\n"


def create_migration_draft(source: Path, lesson_id: str) -> str:
    text = source.read_text(encoding="utf-8", errors="replace")
    text = _replace_global_field(text, "Blueprint version", BLUEPRINT_VERSION)
    text = _replace_global_field(text, "Blueprint status", "draft")
    text = _replace_global_field(text, "Last validated", "migration pending")

    matches = list(POINT_RE.finditer(text))
    rebuilt: list[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else text.find(
            "## Three-Pass Validation", match.end()
        )
        if end < 0:
            end = len(text)
        rebuilt.append(text[cursor:match.start()])
        rebuilt.append(
            migrate_point_block(text[match.start():end], lesson_id, index + 1)
        )
        cursor = end
    rebuilt.append(text[cursor:])
    draft = "".join(rebuilt)
    for field in ["Source fidelity", "Dependency and order", "Novice and assessment"]:
        draft = re.sub(
            rf"(?m)^- {re.escape(field)}:\s*.*$",
            f"- {field}: pending",
            draft,
            count=1,
        )
    change = (
        f"\n- {datetime.now().astimezone().isoformat(timespec='seconds')}: "
        "Created V3.1 migration draft; source order retained, new relationship evidence remains unresolved.\n"
    )
    if "## Change Log" in draft:
        draft = draft.rstrip() + change
    else:
        draft = draft.rstrip() + "\n\n## Change Log\n" + change
    return draft


def create_command(args: argparse.Namespace) -> int:
    source = args.course_dir / "indexes" / "teaching-blueprint.md"
    output = args.output or args.course_dir / "indexes" / "teaching-blueprint.v31-draft.md"
    if not source.is_file():
        raise ValueError(f"legacy blueprint not found: {source}")
    if output.exists() and not args.force:
        raise ValueError(f"migration draft already exists: {output}")
    draft = create_migration_draft(source, args.lesson_id)
    atomic_write_text(output, draft)
    errors = validate_blueprint(output, require_ready=False)
    print(f"Created migration draft: {output}")
    print(f"Unresolved validation checks: {len(errors)}")
    print(
        "Next: repair the draft from registered sources, then run "
        "validate_teaching_blueprint.py --promote."
    )
    return 0


def activate_command(args: argparse.Namespace) -> int:
    official = args.course_dir / "indexes" / "teaching-blueprint.md"
    draft = args.draft or args.course_dir / "indexes" / "teaching-blueprint.v31-draft.md"
    errors = validate_blueprint(draft)
    if errors:
        raise ValueError(
            "cannot activate an invalid or unpromoted draft: " + "; ".join(errors)
        )
    timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")
    backup = official.with_name(f"teaching-blueprint.v3-backup-{timestamp}.md")
    had_official = official.exists()
    if had_official:
        atomic_write_text(backup, official.read_text(encoding="utf-8"))
    activated_text = draft.read_text(encoding="utf-8")
    atomic_write_text(official, activated_text)

    course_yml = args.course_dir / "course.yml"
    if not course_yml.is_file():
        raise ValueError(f"course.yml not found: {course_yml}")
    course_text = course_yml.read_text(encoding="utf-8")
    course_text = set_yaml_scalar(
        course_text, "workspace_schema_version", str(WORKSPACE_SCHEMA_VERSION)
    )
    course_text = set_yaml_scalar(
        course_text, "workspace_migration_status", '"pending_reconciliation"'
    )
    course_text = set_yaml_scalar(
        course_text, "last_migrated_with_skill_version", f'"{SKILL_VERSION}"'
    )
    course_text = set_yaml_scalar(
        course_text, "teaching.blueprint.version", f'"{BLUEPRINT_VERSION}"'
    )
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.status", '"ready"')
    global_fields = parse_fields(activated_text.split("## Knowledge-Point Plan", 1)[0])
    course_text = set_yaml_scalar(
        course_text,
        "teaching.blueprint.source_fingerprint",
        f'"{global_fields.get("Source fingerprint", "")}"',
    )
    atomic_write_text(course_yml, course_text)
    print(f"Activated blueprint: {official}")
    if had_official:
        print(f"Legacy backup: {backup}")
    print(
        "Workspace reconciliation is pending; run migrate_legacy_workspace.py "
        "before formal state updates."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create-draft")
    create.add_argument("--course-dir", required=True, type=Path)
    create.add_argument("--lesson-id", required=True)
    create.add_argument("--output", type=Path)
    create.add_argument("--force", action="store_true")
    create.set_defaults(handler=create_command)

    activate = subparsers.add_parser("activate")
    activate.add_argument("--course-dir", required=True, type=Path)
    activate.add_argument("--draft", type=Path)
    activate.set_defaults(handler=activate_command)
    args = parser.parse_args()
    try:
        return args.handler(args)
    except ValueError as error:
        parser.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
