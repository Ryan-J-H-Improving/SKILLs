#!/usr/bin/env python3
"""Migrate one active or cumulative blueprint into registered lesson blueprints."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from exercise_contract import validate_blueprint_binding, validate_contract_file
from lesson_blueprints import DEFAULT_MANIFEST_PATH
from validate_teaching_blueprint import (
    POINT_RE,
    parse_fields,
    point_field_records,
    promoted_blueprint_text,
    validate_blueprint,
)
from workspace_common import (
    BLUEPRINT_MANIFEST_VERSION,
    BLUEPRINT_VERSION,
    SKILL_VERSION,
    WORKSPACE_SCHEMA_VERSION,
    atomic_write_text,
    file_sha256,
    lesson_id_from_point_id,
    reference_mirror_write_error,
    relative_course_path,
    set_yaml_scalar,
    yaml_scalar_paths,
)


STATE_START = "<!-- course-grounded-tutor:current-state:start -->"
STATE_END = "<!-- course-grounded-tutor:current-state:end -->"
MIGRATION_DIR = Path("migration") / "lesson-blueprints-v330"


def _replace_header_field(text: str, field: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^- {re.escape(field)}:\s*.*$")
    replacement = f"- {field}: {value}"
    if pattern.search(text):
        return pattern.sub(lambda _match: replacement, text, count=1)
    status = re.compile(r"(?m)^- Blueprint status:\s*.*$")
    if not status.search(text):
        raise ValueError("blueprint has no Blueprint status field")
    return status.sub(lambda match: match.group(0) + "\n" + replacement, text, count=1)


def _replace_state_field(text: str, field: str, value: str) -> str:
    block_pattern = re.compile(
        rf"(?ms){re.escape(STATE_START)}.*?{re.escape(STATE_END)}"
    )
    match = block_pattern.search(text)
    if not match:
        raise ValueError("learning-state.md has no managed current-state block")
    block = match.group(0)
    field_pattern = re.compile(rf"(?m)^- {re.escape(field)}:\s*.*$")
    if not field_pattern.search(block):
        raise ValueError(f"managed learning state has no field {field!r}")
    block = field_pattern.sub(lambda _match: f"- {field}: {value}", block, count=1)
    return text[: match.start()] + block + text[match.end() :]


def _state_field(text: str, field: str) -> str:
    block = re.search(
        rf"(?ms){re.escape(STATE_START)}(.*?){re.escape(STATE_END)}", text
    )
    scope = block.group(1) if block else text
    match = re.search(rf"(?m)^- {re.escape(field)}:\s*(.*?)\s*$", scope)
    return match.group(1).strip() if match else ""


def _point_blocks(text: str) -> list[tuple[int, str, str, str]]:
    points = list(POINT_RE.finditer(text))
    validation = text.find("## Three-Pass Validation")
    result: list[tuple[int, str, str, str]] = []
    for index, match in enumerate(points):
        end = points[index + 1].start() if index + 1 < len(points) else validation
        if end < 0:
            end = len(text)
        body = text[match.end() : end].strip()
        fields = parse_fields(body)
        point_id = fields.get("Point ID", "")
        lesson_id = lesson_id_from_point_id(point_id)
        if not lesson_id:
            raise ValueError(f"cannot derive lesson ID from point {point_id!r}")
        result.append((int(match.group(1)), lesson_id, match.group(3).strip(), body))
    return result


def _stable_point_references(text: str, point_ids: dict[int, str]) -> str:
    """Replace legacy cumulative Point numbers with stable point IDs."""

    text = re.sub(
        r"(?mi)^- .*?(?:global blueprint positions|global denominator).*?(?:\n|$)",
        "",
        text,
    )

    def progress(match: re.Match[str]) -> str:
        number = int(match.group(1))
        return point_ids.get(number, match.group(0))

    def point_range(match: re.Match[str]) -> str:
        first = int(match.group(1))
        last = int(match.group(2))
        if first not in point_ids or last not in point_ids:
            return match.group(0)
        return f"{point_ids[first]} through {point_ids[last]}"

    def point_list(match: re.Match[str]) -> str:
        numbers = [int(value) for value in re.findall(r"\d+", match.group(1))]
        if not numbers or any(number not in point_ids for number in numbers):
            return match.group(0)
        values = [point_ids[number] for number in numbers]
        if len(values) == 1:
            return values[0]
        return ", ".join(values[:-1]) + ", and " + values[-1]

    def single(match: re.Match[str]) -> str:
        number = int(match.group(1))
        return point_ids.get(number, match.group(0))

    text = re.sub(r"(?<!### )\bPoint\s+(\d+)\s*/\s*\d+\b", progress, text)
    text = re.sub(
        r"\bPoints?\s+(\d+)\s*(?:-|–|to)\s*(\d+)\b",
        point_range,
        text,
    )
    text = re.sub(
        r"\bPoints\s+(\d+(?:\s*,\s*\d+)+(?:\s*,?\s*and\s*\d+)?)",
        point_list,
        text,
    )
    text = re.sub(r"(?<!### )\bPoint\s+(\d+)\b", single, text)
    return text


def split_blueprint(text: str) -> dict[str, str]:
    records = _point_blocks(text)
    point_ids = {
        number: parse_fields(body).get("Point ID", "")
        for number, _lesson_id, _title, body in records
    }
    groups: dict[str, list[tuple[str, str]]] = {}
    for _number, lesson_id, title, body in records:
        groups.setdefault(lesson_id, []).append((title, body))
    if len(groups) == 1:
        lesson_id = next(iter(groups))
        rewritten = _stable_point_references(text, point_ids)
        return {lesson_id: rewritten.rstrip() + "\n"}

    plan_marker = "## Knowledge-Point Plan"
    validation_marker = "## Three-Pass Validation"
    if plan_marker not in text or validation_marker not in text:
        raise ValueError("blueprint needs Knowledge-Point Plan and Three-Pass Validation")
    prefix = _stable_point_references(
        text.split(plan_marker, 1)[0].rstrip(), point_ids
    )
    suffix = _stable_point_references(
        validation_marker + text.split(validation_marker, 1)[1], point_ids
    )
    outputs: dict[str, str] = {}
    for lesson_id, point_blocks in groups.items():
        total = len(point_blocks)
        header = _replace_header_field(prefix, "Blueprint status", "draft")
        header = _replace_header_field(header, "Blueprint scope", "lesson")
        header = _replace_header_field(header, "Lesson ID", lesson_id)
        header = _replace_header_field(header, "Available scope", lesson_id)
        header = _replace_header_field(header, "Total knowledge points", str(total))
        header = _replace_header_field(header, "Last validated", "pending")
        rendered = []
        for number, (title, body) in enumerate(point_blocks, start=1):
            rendered.append(
                f"### Point {number}/{total}: {title}\n\n"
                + _stable_point_references(body, point_ids)
            )
        outputs[lesson_id] = (
            header
            + "\n\n"
            + plan_marker
            + "\n\n"
            + "\n\n".join(rendered)
            + "\n\n"
            + suffix.strip()
            + "\n"
        )
    return outputs


def _current_state(course_dir: Path) -> tuple[Path, str, str]:
    path = course_dir / "memory" / "learning-state.md"
    text = path.read_text(encoding="utf-8")
    point_id = _state_field(text, "Point ID")
    lesson_id = lesson_id_from_point_id(point_id)
    if not lesson_id:
        raise ValueError(f"cannot derive active lesson from current Point ID {point_id!r}")
    return path, text, point_id


def create_drafts(
    course_dir: Path,
    *,
    dry_run: bool,
    source_blueprint: Path | None = None,
) -> dict[str, object]:
    metadata = yaml_scalar_paths(course_dir / "course.yml")
    source_raw: str | Path = source_blueprint or metadata.get(
        "teaching.blueprint.path", "indexes/teaching-blueprint.md"
    )
    source = Path(source_raw)
    if not source.is_absolute():
        source = course_dir / source
    source = source.resolve()
    source_text = source.read_text(encoding="utf-8")
    source_errors = validate_blueprint(source, require_lesson_scope=False)
    if source_errors:
        raise ValueError("source blueprint is invalid: " + "; ".join(source_errors))
    outputs = split_blueprint(source_text)
    _, state_text, point_id = _current_state(course_dir)
    active_lesson = lesson_id_from_point_id(point_id)
    if active_lesson not in outputs:
        raise ValueError(f"current point lesson {active_lesson!r} is absent from blueprint")
    root = course_dir / MIGRATION_DIR
    drafts = root / "drafts"
    plan = {
        "schema_version": 1,
        "source_path": relative_course_path(course_dir, source),
        "source_sha256": file_sha256(source),
        "active_lesson_id": active_lesson,
        "current_point_id": point_id,
        "original_progress": _state_field(state_text, "Lesson progress"),
        "lessons": [
            {
                "lesson_id": lesson_id,
                "draft_path": (drafts / f"{lesson_id}.md").relative_to(course_dir).as_posix(),
                "point_count": len(point_field_records(text)),
                "source_fingerprint": parse_fields(
                    text.split("## Knowledge-Point Plan", 1)[0]
                ).get("Source fingerprint", ""),
                "preserves_source_bytes": len(outputs) == 1,
            }
            for lesson_id, text in outputs.items()
        ],
    }
    if not dry_run:
        for lesson_id, text in outputs.items():
            atomic_write_text(drafts / f"{lesson_id}.md", text)
        atomic_write_text(root / "plan.json", json.dumps(plan, ensure_ascii=False, indent=2))
    return plan


def _ready_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text.split("## Knowledge-Point Plan", 1)[0])
    if fields.get("Blueprint status", "").lower() == "ready":
        errors = validate_blueprint(path)
        if errors:
            raise ValueError("ready lesson blueprint is invalid: " + "; ".join(errors))
        return text.rstrip() + "\n"
    candidate, errors = promoted_blueprint_text(path)
    if errors:
        raise ValueError("lesson blueprint cannot be promoted: " + "; ".join(errors))
    return candidate


def _rebind_contracts(course_dir: Path, active_blueprint: Path, active_lesson: str) -> None:
    contract_dir = course_dir / "memory" / "exercise-contracts"
    for contract in sorted(contract_dir.glob("*.json")):
        data, errors = validate_contract_file(contract)
        if errors:
            raise ValueError(f"cannot migrate invalid contract {contract.name}: {'; '.join(errors)}")
        point_id = str(data.get("point_id", ""))
        if lesson_id_from_point_id(point_id) != active_lesson:
            raise ValueError(
                f"active contract directory contains another lesson: {contract.name} ({point_id})"
            )
        data["blueprint_sha256"] = file_sha256(active_blueprint)
        data["validated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        candidate = json.dumps(data, ensure_ascii=False, indent=2)
        atomic_write_text(contract, candidate)
        rebound, errors = validate_contract_file(contract)
        if not errors:
            errors.extend(validate_blueprint_binding(rebound, active_blueprint))
        if errors:
            raise ValueError(f"rebound contract failed {contract.name}: {'; '.join(errors)}")


def activate(course_dir: Path, *, dry_run: bool) -> dict[str, object]:
    root = course_dir / MIGRATION_DIR
    plan_path = root / "plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    source = (course_dir / str(plan["source_path"])).resolve()
    if file_sha256(source) != plan.get("source_sha256"):
        raise ValueError("source blueprint changed after draft creation")
    active_lesson = str(plan["active_lesson_id"])
    ready_by_lesson: dict[str, str] = {}
    for entry in plan["lessons"]:
        draft = (course_dir / str(entry["draft_path"])).resolve()
        ready_by_lesson[str(entry["lesson_id"])] = _ready_text(draft)
    if dry_run:
        return {"valid": True, "active_lesson_id": active_lesson, "lessons": len(ready_by_lesson)}

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = root / "backups" / timestamp
    backup.mkdir(parents=True, exist_ok=False)
    protected = [
        course_dir / "course.yml",
        source,
        course_dir / "memory" / "learning-state.md",
    ] + sorted((course_dir / "memory" / "exercise-contracts").glob("*.json"))
    for original in protected:
        destination = backup / original.relative_to(course_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)

    legacy_dir = course_dir / "indexes" / "blueprints" / "legacy"
    legacy = legacy_dir / f"{source.stem}.pre-v330-{timestamp}{source.suffix}"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, legacy)

    lesson_records = []
    final_by_lesson: dict[str, Path] = {}
    for entry in plan["lessons"]:
        lesson_id = str(entry["lesson_id"])
        final = course_dir / "indexes" / "blueprints" / f"{lesson_id}.md"
        atomic_write_text(final, ready_by_lesson[lesson_id])
        errors = validate_blueprint(final)
        if errors:
            raise ValueError(f"activated lesson {lesson_id} is invalid: {'; '.join(errors)}")
        final_by_lesson[lesson_id] = final
        fields = parse_fields(
            ready_by_lesson[lesson_id].split("## Knowledge-Point Plan", 1)[0]
        )
        lesson_records.append(
            {
                "lesson_id": lesson_id,
                "path": relative_course_path(course_dir, final),
                "point_count": len(point_field_records(ready_by_lesson[lesson_id])),
                "status": "ready",
                "sha256": file_sha256(final),
                "source_fingerprint": fields.get("Source fingerprint", ""),
            }
        )

    active = final_by_lesson[active_lesson]
    _rebind_contracts(course_dir, active, active_lesson)
    manifest = {
        "schema_version": BLUEPRINT_MANIFEST_VERSION,
        "course_instance_id": (
            yaml_scalar_paths(course_dir / "course.yml").get(
                "course.course_instance_id", ""
            )
            or course_dir.name
        ),
        "active_lesson_id": active_lesson,
        "lessons": lesson_records,
        "legacy_blueprints": [
            {
                "path": relative_course_path(course_dir, legacy),
                "sha256": file_sha256(legacy),
                "reason": "pre-V3.3 active or cumulative blueprint retained for historical contracts",
            }
        ],
    }
    atomic_write_text(
        course_dir / DEFAULT_MANIFEST_PATH,
        json.dumps(manifest, ensure_ascii=False, indent=2),
    )

    course_yml = course_dir / "course.yml"
    course_text = course_yml.read_text(encoding="utf-8")
    course_text = set_yaml_scalar(course_text, "workspace_schema_version", str(WORKSPACE_SCHEMA_VERSION))
    course_text = set_yaml_scalar(course_text, "last_migrated_with_skill_version", f'"{SKILL_VERSION}"')
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.path", f'"{relative_course_path(course_dir, active)}"')
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.active_lesson_id", f'"{active_lesson}"')
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.manifest_path", f'"{DEFAULT_MANIFEST_PATH}"')
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.version", f'"{BLUEPRINT_VERSION}"')
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.status", '"ready"')
    active_fields = parse_fields(active.read_text(encoding="utf-8").split("## Knowledge-Point Plan", 1)[0])
    course_text = set_yaml_scalar(course_text, "teaching.blueprint.source_fingerprint", f'"{active_fields.get("Source fingerprint", "")}"')
    atomic_write_text(course_yml, course_text)

    state_path, state_text, current_point = _current_state(course_dir)
    active_records = point_field_records(active.read_text(encoding="utf-8"))
    positions = {
        fields.get("Point ID", ""): index
        for index, (_, _, _, fields) in enumerate(active_records, start=1)
    }
    if current_point not in positions:
        raise ValueError("current point is absent from activated lesson blueprint")
    state_text = _replace_state_field(state_text, "Workspace schema version", str(WORKSPACE_SCHEMA_VERSION))
    state_text = _replace_state_field(state_text, "Lesson progress", f"{positions[current_point]}/{len(active_records)}")
    state_text = _replace_state_field(state_text, "Blueprint path", relative_course_path(course_dir, active))
    state_text = _replace_state_field(state_text, "Blueprint status", "ready")
    state_text = _replace_state_field(state_text, "Blueprint SHA256", file_sha256(active))
    contract_raw = _state_field(state_text, "Exercise contract")
    if contract_raw:
        canonical_contract = course_dir / "memory" / "exercise-contracts" / Path(contract_raw).name
        if canonical_contract.is_file():
            state_text = _replace_state_field(
                state_text,
                "Exercise contract",
                relative_course_path(course_dir, canonical_contract),
            )
            state_text = _replace_state_field(
                state_text, "Exercise contract SHA256", file_sha256(canonical_contract)
            )
    atomic_write_text(state_path, state_text)

    result = {
        "valid": True,
        "active_lesson_id": active_lesson,
        "active_blueprint": relative_course_path(course_dir, active),
        "active_blueprint_sha256": file_sha256(active),
        "lesson_count": len(lesson_records),
        "backup": relative_course_path(course_dir, backup),
    }
    atomic_write_text(root / "activation.json", json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "create-draft", "activate"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--course-dir", required=True, type=Path)
        sub.add_argument("--dry-run", action="store_true")
        if command != "activate":
            sub.add_argument(
                "--source-blueprint",
                type=Path,
                help="course-relative legacy or cumulative blueprint to split",
            )
    args = parser.parse_args()
    if args.command in {"create-draft", "activate"}:
        mirror_error = reference_mirror_write_error(args.course_dir)
        if mirror_error:
            parser.error("lesson blueprint migration is blocked: " + mirror_error)
    try:
        if args.command == "plan":
            result = create_drafts(
                args.course_dir,
                dry_run=True,
                source_blueprint=args.source_blueprint,
            )
        elif args.command == "create-draft":
            result = create_drafts(
                args.course_dir,
                dry_run=args.dry_run,
                source_blueprint=args.source_blueprint,
            )
        else:
            result = activate(args.course_dir, dry_run=args.dry_run)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
