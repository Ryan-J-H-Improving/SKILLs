#!/usr/bin/env python3
"""Shared workspace schema, hashing, and atomic-write helpers."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path


WORKSPACE_SCHEMA_VERSION = 1
SKILL_VERSION = "3.2.3"
BLUEPRINT_VERSION = "3.1"
WORKSPACE_ROLE_CANONICAL = "canonical"
WORKSPACE_ROLE_REFERENCE_MIRROR = "reference_mirror"
WORKSPACE_ROLES = {
    WORKSPACE_ROLE_CANONICAL,
    WORKSPACE_ROLE_REFERENCE_MIRROR,
}
COURSE_FIELD_RE = re.compile(r"^(\s*)([A-Za-z0-9_]+):\s*(.*)$")


def workspace_role(course_dir: Path) -> str:
    course_yml = course_dir / "course.yml"
    if not course_yml.is_file():
        return WORKSPACE_ROLE_CANONICAL
    return yaml_scalar_paths(course_yml).get(
        "workspace_role", WORKSPACE_ROLE_CANONICAL
    )


def reference_mirror_write_error(course_dir: Path) -> str:
    course_yml = course_dir / "course.yml"
    if not course_yml.is_file():
        return ""
    metadata = yaml_scalar_paths(course_yml)
    if metadata.get("workspace_role", WORKSPACE_ROLE_CANONICAL) != WORKSPACE_ROLE_REFERENCE_MIRROR:
        return ""
    canonical = metadata.get("canonical_course_dir", "").strip()
    destination = canonical or "the canonical course directory recorded in course.yml"
    return (
        "reference mirrors are read-only and cannot create teaching evidence; "
        f"use the canonical workspace at {destination}"
    )


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = text.rstrip() + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def yaml_scalar_paths(path: Path) -> dict[str, str]:
    """Read scalar YAML paths needed by the workspace without a YAML dependency."""
    fields: dict[str, str] = {}
    stack: list[tuple[int, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = COURSE_FIELD_RE.match(line)
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "    "))
        key = match.group(2)
        raw_value = match.group(3).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        dotted = ".".join([item[1] for item in stack] + [key])
        if raw_value:
            fields[dotted] = raw_value.strip('"').strip("'")
        else:
            stack.append((indent, key))
    return fields


def set_yaml_scalar(text: str, dotted_path: str, rendered_value: str) -> str:
    """Replace a scalar or insert its missing mapping path without flattening YAML."""
    target = dotted_path.split(".")
    lines = text.splitlines()
    stack: list[tuple[int, str]] = []
    containers: dict[tuple[str, ...], tuple[int, int]] = {}
    for index, line in enumerate(lines):
        match = COURSE_FIELD_RE.match(line)
        if not match:
            continue
        indent_text, key, raw_value = match.groups()
        indent = len(indent_text.replace("\t", "    "))
        while stack and stack[-1][0] >= indent:
            stack.pop()
        current = [item[1] for item in stack] + [key]
        if current == target:
            lines[index] = f"{indent_text}{key}: {rendered_value}"
            return "\n".join(lines).rstrip() + "\n"
        if not raw_value.strip():
            stack.append((indent, key))
            containers[tuple(current)] = (index, indent)

    if len(target) == 1:
        return f"{target[0]}: {rendered_value}\n" + "\n".join(lines).rstrip() + "\n"

    prefix_length = 0
    parent_index = -1
    parent_indent = -2
    for length in range(len(target) - 1, 0, -1):
        container = containers.get(tuple(target[:length]))
        if container:
            prefix_length = length
            parent_index, parent_indent = container
            break
    if parent_index < 0:
        raise ValueError(f"YAML parent path not found: {'.'.join(target[:-1])}")

    insert_at = len(lines)
    for index in range(parent_index + 1, len(lines)):
        match = COURSE_FIELD_RE.match(lines[index])
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "    "))
        if indent <= parent_indent:
            insert_at = index
            break

    indent = parent_indent + 2
    additions: list[str] = []
    for key in target[prefix_length:-1]:
        additions.append(" " * indent + f"{key}:")
        indent += 2
    additions.append(" " * indent + f"{target[-1]}: {rendered_value}")
    lines[insert_at:insert_at] = additions
    return "\n".join(lines).rstrip() + "\n"
