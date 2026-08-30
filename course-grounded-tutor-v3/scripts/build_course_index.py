#!/usr/bin/env python3
"""Rebuild .ai-course-tutor/index.md from course.yml files."""

from __future__ import annotations

import argparse
from pathlib import Path

from workspace_common import (
    WORKSPACE_ROLE_CANONICAL,
    WORKSPACE_ROLE_REFERENCE_MIRROR,
    atomic_write_text,
    yaml_scalar_paths,
)


def build_index(workspace: Path) -> Path:
    courses_dir = workspace / "courses"
    lines = ["# Course Tutor Index", "", "## Courses", ""]

    if courses_dir.exists():
        for course_yml in sorted(courses_dir.glob("*/course.yml")):
            course_id = course_yml.parent.name
            fields = yaml_scalar_paths(course_yml)
            title = (
                fields.get("course.course_title")
                or fields.get("course.course_code")
                or course_id
            )
            code = fields.get("course.course_code", "")
            term = fields.get("course.term", "")
            year = fields.get("course.year", "")
            institution = fields.get("course.institution", "")
            teaching_profile = fields.get("teaching.teaching_profile", "")
            blueprint_status = fields.get("teaching.blueprint.status", "")
            workspace_role = fields.get("workspace_role", WORKSPACE_ROLE_CANONICAL)
            canonical_course_dir = fields.get("canonical_course_dir", "")
            label_parts: list[str] = []
            for part in [code, title, year, term]:
                if part and part not in label_parts:
                    label_parts.append(part)
            label = " ".join(label_parts) if label_parts else course_id
            lines.append(f"### {label}")
            lines.append("")
            lines.append(f"- Course instance id: `{course_id}`")
            lines.append(f"- Workspace role: `{workspace_role}`")
            if institution:
                lines.append(f"- Institution: {institution}")
            if teaching_profile:
                lines.append(f"- Teaching profile: {teaching_profile}")
            if blueprint_status:
                lines.append(f"- Blueprint status: {blueprint_status}")
            if (
                workspace_role == WORKSPACE_ROLE_REFERENCE_MIRROR
                and canonical_course_dir
            ):
                canonical_yml = Path(canonical_course_dir) / "course.yml"
                lines.append("- Formal teaching: disabled in this mirror")
                lines.append(f"- Canonical course: `{canonical_course_dir}`")
                lines.append(f"- Path: `{canonical_yml}`")
                lines.append(f"- Mirror metadata: `courses/{course_id}/course.yml`")
            else:
                lines.append(f"- Path: `courses/{course_id}/course.yml`")
            lines.append("")

    workspace.mkdir(parents=True, exist_ok=True)
    index_path = workspace / "index.md"
    atomic_write_text(index_path, "\n".join(lines))
    return index_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".ai-course-tutor")
    args = parser.parse_args()

    index_path = build_index(Path(args.workspace))
    print(f"Wrote {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
