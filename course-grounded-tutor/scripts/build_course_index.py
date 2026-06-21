#!/usr/bin/env python3
"""Rebuild .ai-course-tutor/index.md from course.yml files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FIELD_RE = re.compile(r"^(\s*)([A-Za-z0-9_]+):\s*(.*)$")


def simple_yaml_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = FIELD_RE.match(line)
        if not match:
            continue
        key = match.group(2)
        value = match.group(3).strip().strip('"').strip("'")
        if value and key not in fields:
            fields[key] = value
    return fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".ai-course-tutor")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    courses_dir = workspace / "courses"
    lines = ["# Course Tutor Index", "", "## Courses", ""]

    if courses_dir.exists():
        for course_yml in sorted(courses_dir.glob("*/course.yml")):
            course_id = course_yml.parent.name
            fields = simple_yaml_fields(course_yml)
            title = fields.get("course_title") or fields.get("course_code") or course_id
            code = fields.get("course_code", "")
            term = fields.get("term", "")
            year = fields.get("year", "")
            institution = fields.get("institution", "")
            label_parts = [part for part in [code, title, year, term] if part]
            label = " ".join(label_parts) if label_parts else course_id
            lines.append(f"### {label}")
            lines.append("")
            lines.append(f"- Course instance id: `{course_id}`")
            if institution:
                lines.append(f"- Institution: {institution}")
            lines.append(f"- Path: `courses/{course_id}/course.yml`")
            lines.append("")

    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {workspace / 'index.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

