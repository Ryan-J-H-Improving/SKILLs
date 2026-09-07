#!/usr/bin/env python3
"""Lesson-blueprint registry helpers."""

from __future__ import annotations

import json
from pathlib import Path

from workspace_common import (
    BLUEPRINT_MANIFEST_VERSION,
    active_blueprint_path,
    atomic_write_text,
    file_sha256,
    relative_course_path,
    yaml_scalar_paths,
)


DEFAULT_MANIFEST_PATH = "indexes/blueprints/manifest.json"


def manifest_path(course_dir: Path) -> Path:
    metadata = yaml_scalar_paths(course_dir / "course.yml")
    raw = metadata.get("teaching.blueprint.manifest_path", DEFAULT_MANIFEST_PATH)
    path = Path(raw)
    if not path.is_absolute():
        path = course_dir / path
    return path.resolve()


def empty_manifest(course_dir: Path) -> dict[str, object]:
    metadata = yaml_scalar_paths(course_dir / "course.yml")
    return {
        "schema_version": BLUEPRINT_MANIFEST_VERSION,
        "course_instance_id": metadata.get("course.course_instance_id", "") or course_dir.name,
        "active_lesson_id": metadata.get("teaching.blueprint.active_lesson_id", ""),
        "lessons": [],
        "legacy_blueprints": [],
    }


def load_manifest(course_dir: Path) -> tuple[dict[str, object], list[str]]:
    path = manifest_path(course_dir)
    if not path.is_file():
        return empty_manifest(course_dir), [f"lesson blueprint manifest is missing: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"cannot read lesson blueprint manifest: {error}"]
    if not isinstance(data, dict):
        return {}, ["lesson blueprint manifest must contain one JSON object"]
    return data, []


def validate_manifest(course_dir: Path) -> list[str]:
    data, errors = load_manifest(course_dir)
    if errors:
        return errors
    if data.get("schema_version") != BLUEPRINT_MANIFEST_VERSION:
        errors.append(
            f"lesson blueprint manifest schema_version must be {BLUEPRINT_MANIFEST_VERSION}"
        )
    metadata = yaml_scalar_paths(course_dir / "course.yml")
    expected_course = metadata.get("course.course_instance_id", "") or course_dir.name
    if data.get("course_instance_id") != expected_course:
        errors.append("lesson blueprint manifest course_instance_id differs from course.yml")
    active_lesson = metadata.get("teaching.blueprint.active_lesson_id", "")
    if not active_lesson:
        errors.append("course.yml teaching.blueprint.active_lesson_id is required")
    if data.get("active_lesson_id") != active_lesson:
        errors.append("manifest active_lesson_id differs from course.yml")

    lessons = data.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        errors.append("lesson blueprint manifest must contain at least one lesson")
        return errors

    seen: set[str] = set()
    active_path = active_blueprint_path(course_dir)
    active_matches = 0
    for index, entry in enumerate(lessons, start=1):
        if not isinstance(entry, dict):
            errors.append(f"manifest lesson {index} must be an object")
            continue
        lesson_id = str(entry.get("lesson_id", "")).strip()
        if not lesson_id:
            errors.append(f"manifest lesson {index} needs lesson_id")
        elif lesson_id in seen:
            errors.append(f"manifest duplicates lesson_id {lesson_id!r}")
        else:
            seen.add(lesson_id)
        raw_path = str(entry.get("path", "")).strip()
        if not raw_path:
            errors.append(f"manifest lesson {lesson_id or index} needs path")
            continue
        path = Path(raw_path)
        if path.is_absolute():
            errors.append(f"manifest lesson {lesson_id or index} path must be relative")
            continue
        resolved = (course_dir / path).resolve()
        try:
            resolved.relative_to(course_dir.resolve())
        except ValueError:
            errors.append(f"manifest lesson {lesson_id or index} path escapes course workspace")
            continue
        if not resolved.is_file():
            errors.append(f"manifest lesson {lesson_id or index} blueprint is missing: {raw_path}")
            continue
        expected_hash = str(entry.get("sha256", "")).strip()
        if not expected_hash:
            errors.append(f"manifest lesson {lesson_id or index} needs sha256")
        elif file_sha256(resolved) != expected_hash:
            errors.append(f"manifest lesson {lesson_id or index} blueprint hash changed")
        if lesson_id == active_lesson:
            active_matches += 1
            if resolved != active_path:
                errors.append("active lesson manifest path differs from course.yml")
    if active_matches != 1:
        errors.append("manifest must contain exactly one entry for the active lesson")
    return errors


def register_lesson_blueprint(
    course_dir: Path,
    blueprint: Path,
    lesson_id: str,
    point_count: int,
    source_fingerprint: str,
    *,
    activate: bool,
) -> None:
    path = manifest_path(course_dir)
    data, errors = load_manifest(course_dir)
    if errors and path.is_file():
        raise ValueError("; ".join(errors))
    if errors:
        data = empty_manifest(course_dir)
    data["schema_version"] = BLUEPRINT_MANIFEST_VERSION
    data["course_instance_id"] = (
        yaml_scalar_paths(course_dir / "course.yml").get("course.course_instance_id", "")
        or course_dir.name
    )
    lessons = data.setdefault("lessons", [])
    if not isinstance(lessons, list):
        raise ValueError("lesson blueprint manifest lessons must be a list")
    record = {
        "lesson_id": lesson_id,
        "path": relative_course_path(course_dir, blueprint),
        "point_count": point_count,
        "status": "ready",
        "sha256": file_sha256(blueprint),
        "source_fingerprint": source_fingerprint,
    }
    replaced = False
    for index, entry in enumerate(lessons):
        if isinstance(entry, dict) and entry.get("lesson_id") == lesson_id:
            lessons[index] = record
            replaced = True
            break
    if not replaced:
        lessons.append(record)
    lessons.sort(key=lambda item: str(item.get("lesson_id", "")))
    if activate:
        data["active_lesson_id"] = lesson_id
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))
