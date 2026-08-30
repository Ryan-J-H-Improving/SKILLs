#!/usr/bin/env python3
"""Validate a V3.1 teaching blueprint before detailed tutoring begins."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from workspace_common import (
    BLUEPRINT_VERSION,
    atomic_write_text,
    file_sha256,
    reference_mirror_write_error,
    set_yaml_scalar,
)


POINT_RE = re.compile(r"^### Point\s+(\d+)/(\d+):\s+(.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^- ([^:\n]+):\s*(.*?)\s*$", re.MULTILINE)
RELATION_MAPPING_RE = re.compile(
    r"\b(R[1-9][0-9]*)\s*(?:=|:)\s*([^;；\n]+)"
)
ACTION_RELATION_RE = re.compile(
    r"\bA([1-9][0-9]*)\s*(?:->|→|:)\s*R([1-9][0-9]*)\b"
)
POINT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REQUIRED_POINT_FIELDS = {
    "Point ID",
    "Previous dependency",
    "Why now",
    "Course question",
    "Slides/document evidence",
    "Transcript status",
    "Transcript evidence",
    "Teacher transition",
    "Teacher sequence",
    "Source layers",
    "New terms",
    "Formula construction",
    "Visual decision",
    "Worked example",
    "Eligible relationships",
    "Explanation mapping",
    "Demonstration mapping",
    "Exercise coverage",
    "Question-rubric boundary",
    "Difficulty",
    "Automatic-advance evidence",
    "Load risk",
}
PLACEHOLDER_RE = re.compile(r"<[^>]+>|\b(?:TODO|TBD)\b", re.IGNORECASE)
GENERIC_VALUES = {
    "explain symbols",
    "explain formula",
    "ask questions",
    "teacher explains topic",
    "use transcript",
    "see slides",
}


def parse_fields(text: str) -> dict[str, str]:
    return {name.strip(): value.strip() for name, value in FIELD_RE.findall(text)}


def parse_relation_mapping(value: str) -> dict[str, str]:
    return {
        relation: description.strip()
        for relation, description in RELATION_MAPPING_RE.findall(value)
    }


def point_field_records(text: str) -> list[tuple[int, int, str, dict[str, str]]]:
    points = list(POINT_RE.finditer(text))
    records: list[tuple[int, int, str, dict[str, str]]] = []
    for index, match in enumerate(points):
        end = (
            points[index + 1].start()
            if index + 1 < len(points)
            else text.find("## Three-Pass Validation", match.end())
        )
        if end < 0:
            end = len(text)
        records.append(
            (
                int(match.group(1)),
                int(match.group(2)),
                match.group(3).strip(),
                parse_fields(text[match.end():end]),
            )
        )
    return records


def get_point_binding(path: Path, point_id: str) -> dict[str, object] | None:
    """Return the validated identifiers that bind a contract to one blueprint point."""
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    global_fields = parse_fields(text.split("## Knowledge-Point Plan", 1)[0])
    for _, _, _, fields in point_field_records(text):
        if fields.get("Point ID") != point_id:
            continue
        eligible_mapping = parse_relation_mapping(
            fields.get("Eligible relationships", "")
        )
        explanation_mapping = parse_relation_mapping(
            fields.get("Explanation mapping", "")
        )
        demonstration_mapping = parse_relation_mapping(
            fields.get("Demonstration mapping", "")
        )
        action_mapping = {
            f"A{action}": f"R{relation}"
            for action, relation in ACTION_RELATION_RE.findall(
                fields.get("Exercise coverage", "")
            )
        }
        return {
            "source_fingerprint": global_fields.get("Source fingerprint", ""),
            "eligible_relationships": eligible_mapping,
            "explanation_mapping": explanation_mapping,
            "demonstration_mapping": demonstration_mapping,
            "action_mapping": action_mapping,
        }
    return None


def validate_blueprint(
    path: Path, progress: str = "", require_ready: bool = True
) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"blueprint not found: {path}"]

    text = path.read_text(encoding="utf-8", errors="replace")
    global_text = text.split("## Knowledge-Point Plan", 1)[0]
    global_fields = parse_fields(global_text)

    if global_fields.get("Blueprint version") != BLUEPRINT_VERSION:
        errors.append(f"Blueprint version must be {BLUEPRINT_VERSION}")
    status = global_fields.get("Blueprint status", "").lower()
    if require_ready and status != "ready":
        errors.append("Blueprint status must be ready")
    if not require_ready and status not in {"draft", "ready"}:
        errors.append("Blueprint status must be draft or ready before promotion")
    if not global_fields.get("Source fingerprint"):
        errors.append("Source fingerprint is required")
    if not global_fields.get("Available scope"):
        errors.append("Available scope is required")

    total_text = global_fields.get("Total knowledge points", "")
    try:
        total = int(total_text)
        if total < 1:
            raise ValueError
    except ValueError:
        total = 0
        errors.append("Total knowledge points must be a positive integer")

    records = point_field_records(text)
    if total and len(records) != total:
        errors.append(f"Expected {total} point sections, found {len(records)}")

    seen_point_ids: set[str] = set()
    for index, (number, denominator, title, fields) in enumerate(records, start=1):

        if number != index:
            errors.append(f"Point section {index} is numbered {number}")
        if total and denominator != total:
            errors.append(
                f"Point {number} denominator {denominator} does not match total {total}"
            )
        if not title or PLACEHOLDER_RE.search(title):
            errors.append(f"Point {number} needs a stable title")

        missing = sorted(REQUIRED_POINT_FIELDS - fields.keys())
        if missing:
            errors.append(f"Point {number} missing fields: {', '.join(missing)}")
        for field in REQUIRED_POINT_FIELDS & fields.keys():
            value = fields[field]
            if not value or PLACEHOLDER_RE.search(value) or value.lower() == "pending":
                errors.append(f"Point {number} field '{field}' is incomplete")

        point_id = fields.get("Point ID", "")
        if point_id and not POINT_ID_RE.fullmatch(point_id):
            errors.append(
                f"Point {number} Point ID must contain only letters, numbers, '.', '_', or '-'"
            )
        if point_id in seen_point_ids:
            errors.append(f"Point {number} duplicates Point ID: {point_id}")
        if point_id:
            seen_point_ids.add(point_id)

        transcript_status = fields.get("Transcript status", "").lower()
        transcript_evidence = fields.get("Transcript evidence", "").lower()
        if transcript_status not in {"available", "not supplied"}:
            errors.append(
                f"Point {number} Transcript status must be 'available' or 'not supplied'"
            )
        if transcript_status == "available" and transcript_evidence in {
            "main block",
            "transcript consulted",
            "available",
        }:
            errors.append(f"Point {number} needs a precise semantic transcript locator")
        if transcript_status == "available" and len(transcript_evidence) < 20:
            errors.append(f"Point {number} transcript evidence is too coarse")

        for field in [
            "Teacher transition",
            "Teacher sequence",
            "Formula construction",
            "Exercise coverage",
            "Automatic-advance evidence",
        ]:
            value = fields.get(field, "").strip().lower()
            if value in GENERIC_VALUES:
                errors.append(f"Point {number} field '{field}' is too generic")

        exercise_coverage = fields.get("Exercise coverage", "")

        eligible_mapping = parse_relation_mapping(
            fields.get("Eligible relationships", "")
        )
        explanation_mapping = parse_relation_mapping(
            fields.get("Explanation mapping", "")
        )
        demonstration_mapping = parse_relation_mapping(
            fields.get("Demonstration mapping", "")
        )
        eligible_ids = set(eligible_mapping)
        explanation_ids = set(explanation_mapping)
        demonstration_ids = set(demonstration_mapping)
        exercise_mappings = [
            (f"A{action}", f"R{relation}")
            for action, relation in ACTION_RELATION_RE.findall(exercise_coverage)
        ]
        action_ids = [action for action, _ in exercise_mappings]
        exercise_ids = {relation for _, relation in exercise_mappings}
        if not eligible_ids:
            errors.append(
                f"Point {number} needs 'R# = canonical relationship' mappings"
            )
        if not 3 <= len(exercise_mappings) <= 5:
            errors.append(
                f"Point {number} Exercise coverage must contain 3-5 A# -> R# mappings"
            )
        expected_action_ids = [f"A{item}" for item in range(1, len(action_ids) + 1)]
        if action_ids and action_ids != expected_action_ids:
            errors.append(
                f"Point {number} Exercise coverage action IDs must be sequential from A1"
            )
        unexplained_eligible = eligible_ids - explanation_ids
        if unexplained_eligible:
            errors.append(
                f"Point {number} eligible relationships lack explanation mapping: "
                + ", ".join(sorted(unexplained_eligible))
            )
        undemonstrated_eligible = eligible_ids - demonstration_ids
        if undemonstrated_eligible:
            errors.append(
                f"Point {number} eligible relationships lack demonstration mapping: "
                + ", ".join(sorted(undemonstrated_eligible))
            )
        unknown_ids = exercise_ids - eligible_ids
        if unknown_ids:
            errors.append(
                f"Point {number} exercise uses ineligible relationships: "
                + ", ".join(sorted(unknown_ids))
            )
        undemonstrated_ids = exercise_ids - demonstration_ids
        if undemonstrated_ids:
            errors.append(
                f"Point {number} exercise relationships lack demonstration mapping: "
                + ", ".join(sorted(undemonstrated_ids))
            )

    validation_parts = text.split("## Three-Pass Validation", 1)
    if len(validation_parts) != 2:
        errors.append("Three-Pass Validation section is required")
    else:
        validation_text = validation_parts[1].split("## Change Log", 1)[0]
        validation_fields = parse_fields(validation_text)
        for field in ["Source fidelity", "Dependency and order", "Novice and assessment"]:
            if validation_fields.get(field, "").lower() != "pass":
                errors.append(f"Validation '{field}' must be pass")

    if progress:
        progress_match = re.fullmatch(r"(\d+)/(\d+)", progress.strip())
        if not progress_match:
            errors.append("Progress must use current/total format")
        elif total and int(progress_match.group(2)) != total:
            errors.append(
                f"Progress denominator {progress_match.group(2)} does not match blueprint total {total}"
            )

    return errors


def _suggestion(error: str) -> str:
    if "Blueprint version" in error:
        return f"Set Blueprint version to {BLUEPRINT_VERSION}."
    if "Blueprint status" in error:
        return "Keep the file draft while editing, then run this validator with --promote."
    if "missing fields" in error:
        return "Add the listed fields using assets/teaching-blueprint.md.template."
    if "Point ID" in error:
        return "Use one stable semantic identifier such as week-03-sampling-distribution."
    if "relationship" in error or "Exercise coverage" in error:
        return "Define canonical R# mappings, explanation and demonstration locators, then map A# -> R#."
    if "Transcript" in error or "transcript" in error:
        return "Record a precise transcript passage or explicitly state that no transcript was supplied."
    if "Progress denominator" in error or "denominator" in error:
        return "Reconcile the blueprint total and numeric current/total progress before promotion."
    if "Validation" in error:
        return "Run the named audit independently and record pass only with specific evidence."
    return "Repair this field from registered course sources, then validate again."


def build_report(path: Path, errors: list[str]) -> dict[str, object]:
    global_errors: list[dict[str, str]] = []
    point_errors: dict[str, list[dict[str, str]]] = {}
    for error in errors:
        item = {"error": error, "suggestion": _suggestion(error)}
        match = re.match(r"Point (\d+)\b", error)
        if match:
            point_errors.setdefault(match.group(1), []).append(item)
        else:
            global_errors.append(item)
    return {
        "blueprint": str(path),
        "valid": not errors,
        "error_count": len(errors),
        "global": global_errors,
        "points": point_errors,
    }


def format_text_report(report: dict[str, object]) -> str:
    lines = [
        f"Blueprint: {report['blueprint']}",
        f"Valid: {'yes' if report['valid'] else 'no'}",
        f"Errors: {report['error_count']}",
    ]
    global_errors = report["global"]
    if isinstance(global_errors, list) and global_errors:
        lines.append("\nGlobal")
        for item in global_errors:
            lines.append(f"- {item['error']}")
            lines.append(f"  Fix: {item['suggestion']}")
    points = report["points"]
    if isinstance(points, dict):
        for number, items in sorted(points.items(), key=lambda item: int(item[0])):
            lines.append(f"\nPoint {number}")
            for item in items:
                lines.append(f"- {item['error']}")
                lines.append(f"  Fix: {item['suggestion']}")
    return "\n".join(lines) + "\n"


def _replace_blueprint_field(text: str, field: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^- {re.escape(field)}:\s*.*$")
    replacement = f"- {field}: {value}"
    if not pattern.search(text):
        raise ValueError(f"Blueprint field not found: {field}")
    return pattern.sub(lambda _match: replacement, text, count=1)


def promoted_blueprint_text(path: Path, progress: str = "") -> tuple[str, list[str]]:
    errors = validate_blueprint(path, progress, require_ready=False)
    if errors:
        return "", errors
    text = path.read_text(encoding="utf-8")
    text = _replace_blueprint_field(text, "Blueprint status", "ready")
    text = _replace_blueprint_field(
        text,
        "Last validated",
        datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    return text, []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", required=True, type=Path)
    parser.add_argument("--progress", default="")
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--report", nargs="?", const="text", choices=["text", "json"], default=""
    )
    args = parser.parse_args()
    if args.dry_run and not args.promote:
        parser.error("--dry-run is only valid with --promote")
    if args.promote:
        mirror_error = reference_mirror_write_error(args.blueprint.parent.parent)
        if mirror_error:
            parser.error("blueprint promotion is blocked: " + mirror_error)

    promoted = False
    candidate_hash = ""
    if args.promote:
        candidate, errors = promoted_blueprint_text(args.blueprint, args.progress)
        if not errors:
            if not args.dry_run:
                atomic_write_text(args.blueprint, candidate)
                promoted = True
                errors = validate_blueprint(args.blueprint, args.progress)
                if not errors:
                    candidate_hash = file_sha256(args.blueprint)
                    course_yml = args.blueprint.parent.parent / "course.yml"
                    if course_yml.is_file():
                        global_fields = parse_fields(
                            candidate.split("## Knowledge-Point Plan", 1)[0]
                        )
                        course_text = course_yml.read_text(encoding="utf-8")
                        course_text = set_yaml_scalar(
                            course_text,
                            "teaching.blueprint.version",
                            f'"{BLUEPRINT_VERSION}"',
                        )
                        course_text = set_yaml_scalar(
                            course_text, "teaching.blueprint.status", '"ready"'
                        )
                        course_text = set_yaml_scalar(
                            course_text,
                            "teaching.blueprint.source_fingerprint",
                            f'"{global_fields.get("Source fingerprint", "")}"',
                        )
                        atomic_write_text(course_yml, course_text)
    else:
        errors = validate_blueprint(args.blueprint, args.progress)
        if not errors:
            candidate_hash = file_sha256(args.blueprint)

    report = build_report(args.blueprint, errors)
    report["promoted"] = promoted
    report["promotion_dry_run"] = bool(args.promote and args.dry_run)
    report["sha256"] = candidate_hash
    if args.report == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if not errors else 1
    elif args.report == "text":
        print(format_text_report(report), end="")
    elif errors:
        for error in errors:
            print(f"ERROR: {error}")

    if errors:
        return 1
    if args.promote and args.dry_run:
        print(f"Blueprint promotion dry-run passed: {args.blueprint}")
    elif promoted:
        print(f"Blueprint promoted: {args.blueprint}")
    else:
        print(f"Blueprint valid: {args.blueprint}")
    if candidate_hash:
        print(f"SHA256: {candidate_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
