#!/usr/bin/env python3
"""Initialize a project-local course tutor workspace."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from build_course_index import build_index
from workspace_common import WORKSPACE_ROLE_CANONICAL, yaml_scalar_paths


COURSE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


ROOT_TEMPLATE_FILES = {
    "teaching-blueprint.md.template": ("indexes", "teaching-blueprint.md"),
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


def known_canonical_courses(
    workspaces: list[Path], course_id: str, target_course_dir: Path
) -> list[Path]:
    matches: dict[str, Path] = {}
    target_resolved = target_course_dir.resolve()
    for workspace in workspaces:
        courses_root = workspace / "courses"
        if not courses_root.is_dir():
            continue
        for course_yml in courses_root.glob("*/course.yml"):
            fields = yaml_scalar_paths(course_yml)
            candidate_id = (
                fields.get("course.course_instance_id", "") or course_yml.parent.name
            )
            role = fields.get("workspace_role", WORKSPACE_ROLE_CANONICAL)
            candidate = course_yml.parent.resolve()
            if (
                candidate_id == course_id
                and role == WORKSPACE_ROLE_CANONICAL
                and candidate != target_resolved
            ):
                matches[str(candidate).casefold()] = candidate
    return sorted(matches.values(), key=lambda path: str(path).casefold())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".ai-course-tutor")
    parser.add_argument("--course-id", required=True)
    parser.add_argument(
        "--known-workspace",
        action="append",
        type=Path,
        default=[],
        help="repeat for every other .ai-course-tutor root already discovered",
    )
    parser.add_argument(
        "--confirm-no-known-canonical",
        action="store_true",
        help="explicitly confirm that no external canonical workspace is known",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not COURSE_ID_RE.fullmatch(args.course_id):
        parser.error("--course-id must contain lowercase letters, digits, and hyphens only")

    workspace = Path(args.workspace)
    course_dir = workspace / "courses" / args.course_id
    target_exists = (course_dir / "course.yml").is_file()
    target_workspace = workspace.resolve()
    external_workspaces: list[Path] = []
    for known in args.known_workspace:
        if not known.is_dir():
            parser.error(f"--known-workspace does not exist or is not a directory: {known}")
        if known.resolve() != target_workspace:
            external_workspaces.append(known)
    if (
        not target_exists
        and not external_workspaces
        and not args.confirm_no_known_canonical
    ):
        parser.error(
            "creating a canonical workspace requires at least one external "
            "--known-workspace search root or --confirm-no-known-canonical after "
            "checking existing course indexes"
        )

    known_roots = [workspace, *external_workspaces]
    conflicts = known_canonical_courses(known_roots, args.course_id, course_dir)
    if conflicts:
        rendered = "; ".join(str(path) for path in conflicts)
        parser.error(
            "canonical course already exists; use that workspace or explicitly "
            f"convert a duplicate to a reference mirror: {rendered}"
        )

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
        "memory/exercise-contracts",
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
