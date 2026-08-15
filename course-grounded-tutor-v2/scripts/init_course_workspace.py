#!/usr/bin/env python3
"""Initialize a project-local course tutor workspace."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from build_course_index import build_index


COURSE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


ROOT_TEMPLATE_FILES = {
    "course-map.md.template": ("notes", "course-map.md"),
    "study-notes.md.template": ("notes", "study-notes.md"),
    "exam-review-notes.md.template": ("notes", "exam-review-notes.md"),
    "concept-map.md.template": ("notes", "concept-map.md"),
    "figure-notes.md.template": ("notes", "figure-notes.md"),
    "learning-state.md.template": ("memory", "learning-state.md"),
    "session-log.md.template": ("memory", "session-log.md"),
    "weak-points.md.template": ("memory", "weak-points.md"),
    "practice-history.md.template": ("memory", "practice-history.md"),
    "exam-topic-map.md.template": ("exam-review", "exam-topic-map.md"),
    "school-question-patterns.md.template": ("exam-review", "school-question-patterns.md"),
    "source-register.md.template": ("indexes", "source-register.md"),
}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_template(template_name: str, destination: Path, force: bool) -> None:
    source = skill_root() / "assets" / template_name
    if destination.exists() and not force:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".ai-course-tutor")
    parser.add_argument("--course-id", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not COURSE_ID_RE.fullmatch(args.course_id):
        parser.error("--course-id must contain lowercase letters, digits, and hyphens only")

    workspace = Path(args.workspace)
    course_dir = workspace / "courses" / args.course_id

    for subdir in [
        "sources/slides",
        "sources/transcripts",
        "sources/exams",
        "sources/tutorials",
        "sources/assignments",
        "sources/readings",
        "sources/data",
        "extracted/pages",
        "extracted/figures",
        "indexes",
        "memory",
        "notes",
        "exam-review",
    ]:
        (course_dir / subdir).mkdir(parents=True, exist_ok=True)

    copy_template("course.yml.template", course_dir / "course.yml", args.force)
    for template_name, relative_parts in ROOT_TEMPLATE_FILES.items():
        copy_template(template_name, course_dir / Path(*relative_parts), args.force)

    build_index(workspace)

    print(f"Initialized {course_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
