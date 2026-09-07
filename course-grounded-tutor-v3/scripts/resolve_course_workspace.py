#!/usr/bin/env python3
"""Resolve a discovered course path to its only writable canonical workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_course_workspace import audit_course
from workspace_common import (
    WORKSPACE_ROLE_CANONICAL,
    WORKSPACE_ROLE_REFERENCE_MIRROR,
    yaml_scalar_paths,
)


def resolve_course(course_dir: Path) -> tuple[Path, str, list[str]]:
    warnings: list[str] = []
    current = course_dir.resolve()
    seen: set[Path] = set()
    for _ in range(3):
        if current in seen:
            raise ValueError("workspace role path contains a cycle")
        seen.add(current)
        course_yml = current / "course.yml"
        if not course_yml.is_file():
            raise ValueError(f"course.yml is missing at {current}")
        metadata = yaml_scalar_paths(course_yml)
        role = metadata.get("workspace_role", WORKSPACE_ROLE_CANONICAL)
        if role == WORKSPACE_ROLE_CANONICAL:
            return current, role, warnings
        if role != WORKSPACE_ROLE_REFERENCE_MIRROR:
            raise ValueError(f"unsupported workspace_role {role!r}")
        canonical = metadata.get("canonical_course_dir", "").strip()
        if not canonical:
            raise ValueError("reference mirror does not record canonical_course_dir")
        warnings.append(f"resolved reference mirror {current} to {canonical}")
        current = Path(canonical).resolve()
    raise ValueError("workspace role path exceeds the supported mirror depth")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-dir", required=True, type=Path)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        canonical, role, warnings = resolve_course(args.course_dir)
    except ValueError as error:
        parser.error(str(error))
    report = audit_course(canonical)
    if args.require_ready and report["status"] != "ready":
        parser.error(
            f"canonical workspace is not ready: {report['status']} at {canonical}"
        )
    result = {
        "requested_course_dir": str(args.course_dir.resolve()),
        "canonical_course_dir": str(canonical),
        "workspace_role": role,
        "status": report["status"],
        "allowed_mode": report["allowed_mode"],
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Canonical course directory: {canonical}")
        print(f"Status: {report['status']}")
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
