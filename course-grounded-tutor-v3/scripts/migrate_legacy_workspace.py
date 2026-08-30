#!/usr/bin/env python3
"""Plan, draft, validate, and activate conservative legacy workspace migration."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from validate_teaching_blueprint import (
    get_point_binding,
    parse_fields,
    point_field_records,
    validate_blueprint,
)
from workspace_common import (
    BLUEPRINT_VERSION,
    SKILL_VERSION,
    WORKSPACE_ROLE_CANONICAL,
    WORKSPACE_SCHEMA_VERSION,
    atomic_write_text,
    file_sha256,
    set_yaml_scalar,
    yaml_scalar_paths,
)


STATE_START = "<!-- course-grounded-tutor:current-state:start -->"
STATE_END = "<!-- course-grounded-tutor:current-state:end -->"
DRAFT_RELATIVE = Path("migration") / "v3.1.1-legacy"
MANIFEST_VERSION = 1
REQUIRED_STATE_FIELDS = {
    "Workspace schema version",
    "Current lesson",
    "Lesson progress",
    "Point ID",
    "Current point",
    "Point status",
    "Blueprint path",
    "Blueprint status",
    "Blueprint SHA256",
    "Source fingerprint",
    "Automatic advance",
    "Blocking gaps",
    "Next action",
}
STATE_FIELD_RE = re.compile(r"(?m)^- ([^:\n]+):[ \t]*(.*?)[ \t]*$")
LEGACY_SECTION_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
LEGACY_BULLET_RE = re.compile(r"(?m)^- ([^:\n]+):\s*(.*?)\s*$")


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def draft_paths(course_dir: Path) -> dict[str, Path]:
    root = course_dir / DRAFT_RELATIVE
    return {
        "root": root,
        "course": root / "course.yml.draft",
        "source": root / "source-register.md.draft",
        "state": root / "learning-state.md.draft",
        "manifest": root / "manifest.json",
    }


def original_record(path: Path, course_dir: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(course_dir)).replace("\\", "/"),
        "exists": path.is_file(),
        "sha256": file_sha256(path) if path.is_file() else "",
    }


def selected_source_path(course_dir: Path) -> Path | None:
    current = course_dir / "indexes" / "source-register.md"
    legacy = course_dir / "indexes" / "sources.md"
    if current.is_file():
        return current
    if legacy.is_file():
        return legacy
    return None


def course_plan(course_dir: Path) -> dict[str, object]:
    course_yml = course_dir / "course.yml"
    source_register = course_dir / "indexes" / "source-register.md"
    legacy_sources = course_dir / "indexes" / "sources.md"
    state = course_dir / "memory" / "learning-state.md"
    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    blueprint_errors = validate_blueprint(blueprint)
    state_text = state.read_text(encoding="utf-8", errors="replace") if state.is_file() else ""
    if source_register.is_file():
        source_action = "preserve_existing_source_register"
    elif legacy_sources.is_file():
        source_action = "convert_sources_md_and_preserve_verbatim"
    else:
        source_action = "source_inventory_required"
    return {
        "course_dir": str(course_dir),
        "course_yml": "present" if course_yml.is_file() else "missing",
        "source_action": source_action,
        "learning_state": (
            "managed_current_block"
            if STATE_START in state_text and STATE_END in state_text
            else "legacy_unmanaged"
            if state.is_file()
            else "missing"
        ),
        "blueprint": "ready" if not blueprint_errors else "migration_required",
        "blueprint_error_count": len(blueprint_errors),
        "exercise_contract_directory": (
            "present"
            if (course_dir / "memory" / "exercise-contracts").is_dir()
            else "create_on_activation"
        ),
        "activation_rule": (
            "requires a ready V3.1 blueprint and an explicit safe recovery Point ID; "
            "legacy practiced/mastered claims are preserved but never promoted"
        ),
    }


def _clean_cell(value: str) -> str:
    value = value.strip().strip("`")
    return " ".join(value.split()).replace("|", "\\|")


def _legacy_sections(text: str) -> list[tuple[str, dict[str, str]]]:
    matches = list(LEGACY_SECTION_RE.finditer(text))
    sections: list[tuple[str, dict[str, str]]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fields = {
            name.strip(): value.strip()
            for name, value in LEGACY_BULLET_RE.findall(text[match.end():end])
        }
        sections.append((match.group(1).strip(), fields))
    return sections


def _authority(source_type: str) -> str:
    lowered = source_type.casefold()
    if "related-term" in lowered or "related term" in lowered:
        return "related-term evidence"
    if "current-term" in lowered or "current term" in lowered:
        return "current course source"
    if "assigned" in lowered:
        return "current course assigned source"
    return "legacy source; authority requires review"


def source_register_draft(course_dir: Path) -> tuple[str, str]:
    current = course_dir / "indexes" / "source-register.md"
    if current.is_file():
        return current.read_text(encoding="utf-8", errors="replace"), str(
            current.relative_to(course_dir)
        ).replace("\\", "/")

    legacy = course_dir / "indexes" / "sources.md"
    if not legacy.is_file():
        return (
            "# Source Register\n\n## Sources\n\n"
            "<MIGRATION REQUIRED: register at least one course source>\n",
            "",
        )
    legacy_text = legacy.read_text(encoding="utf-8", errors="replace")
    rows: list[str] = []
    used = {
        "Type",
        "Term",
        "Workspace copy",
        "Original path",
        "Coverage",
        "Content note",
        "Emphasis captured",
        "Assessment-pattern value",
        "Title",
        "Identification confidence",
        "SHA-256",
    }
    for index, (title, fields) in enumerate(_legacy_sections(legacy_text), start=1):
        source_type = fields.get("Type", "legacy source; verify type")
        term = fields.get("Term", "legacy term; verify")
        path = fields.get("Workspace copy") or fields.get("Original path", "")
        coverage = (
            fields.get("Coverage")
            or fields.get("Content note")
            or fields.get("Emphasis captured")
            or fields.get("Assessment-pattern value")
            or fields.get("Title")
            or title
        )
        confidence = fields.get("Identification confidence", "unrecorded")
        fingerprint = fields.get("SHA-256", "unrecorded")
        extra = [f"{name}: {value}" for name, value in fields.items() if name not in used]
        notes = (
            f"Migrated from sources.md; heading: {title}; identification: {confidence}; "
            f"SHA-256: {fingerprint}"
        )
        if extra:
            notes += "; " + "; ".join(extra)
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`LEGACY-SRC-{index:03d}`",
                    _clean_cell(source_type),
                    _clean_cell(term),
                    f"`{_clean_cell(path)}`" if path else "unresolved",
                    _clean_cell(_authority(source_type)),
                    _clean_cell(coverage),
                    "migrated; verify before source-fidelity audit",
                    _clean_cell(notes),
                ]
            )
            + " |"
        )
    legacy_hash = file_sha256(legacy)
    preserved = legacy_text.replace("```", "` ` `")
    text = f"""# Source Register

## Migration Record

- Original file: `indexes/sources.md`
- Original SHA256: `{legacy_hash}`
- Generated: {now()}
- Rule: Generated rows are an index aid. The preserved legacy text remains authoritative until each row is reviewed against the source.

## Sources

| Source ID | Type | Term/version | Local path | Authority | Coverage | Processing status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows) if rows else '| `LEGACY-SRC-001` | <MIGRATION REQUIRED> | | | | | | |'}

## Preserved Legacy Source Index

<!-- course-grounded-tutor:legacy-source:start sha256={legacy_hash} -->
```markdown
{preserved.rstrip()}
```
<!-- course-grounded-tutor:legacy-source:end -->
"""
    return text, str(legacy.relative_to(course_dir)).replace("\\", "/")


def _point_record(blueprint: Path, point_id: str) -> tuple[int, int, str] | None:
    if validate_blueprint(blueprint):
        return None
    for number, total, title, fields in point_field_records(
        blueprint.read_text(encoding="utf-8", errors="replace")
    ):
        if fields.get("Point ID") == point_id:
            return number, total, title
    return None


def managed_state_block(
    course_dir: Path, safe_point_id: str, current_lesson: str
) -> str:
    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    record = _point_record(blueprint, safe_point_id) if safe_point_id else None
    if record:
        number, total, title = record
        global_fields = parse_fields(
            blueprint.read_text(encoding="utf-8", errors="replace").split(
                "## Knowledge-Point Plan", 1
            )[0]
        )
        progress = f"{number}/{total}"
        blueprint_status = "ready"
        blueprint_hash = file_sha256(blueprint)
        source_fingerprint = global_fields.get("Source fingerprint", "")
        point_status = "not_started"
        blocking = (
            "Legacy progress and mastery claims are preserved below but not promoted; "
            "resume from this explicitly selected safe point."
        )
        next_action = f"Review registered sources, then teach {safe_point_id} from the promoted blueprint."
    else:
        title = "<MIGRATION REQUIRED: select a safe recovery Point ID>"
        progress = "<MIGRATION REQUIRED: current/total>"
        safe_point_id = "<MIGRATION REQUIRED: stable Point ID>"
        blueprint_status = "migration_required"
        blueprint_hash = ""
        source_fingerprint = ""
        point_status = "legacy_provisional"
        blocking = "A ready V3.1 blueprint and explicit safe recovery point are required."
        next_action = "Repair and promote the blueprint, then regenerate this draft with --safe-point-id."
    return f"""{STATE_START}
## Current Session Snapshot

- Workspace schema version: {WORKSPACE_SCHEMA_VERSION}
- Current mode: migration_reconciliation
- Current lesson: {current_lesson or 'Legacy workspace reconciliation'}
- Lesson progress: {progress}
- Point ID: {safe_point_id}
- Current point: {title}
- Point status: {point_status}
- Blueprint path: indexes/teaching-blueprint.md
- Blueprint status: {blueprint_status}
- Blueprint SHA256: {blueprint_hash}
- Source fingerprint: {source_fingerprint}
- Transcript gate: not_started
- Transcript evidence:
- Narrative bridge:
- Formula gate: not_started
- Unresolved formula operations:
- Coverage gate: not_started
- Exercise status: not_started
- Exercise coverage:
- Exercise contract:
- Exercise contract SHA256:
- Mastery evidence:
- Automatic advance: no
- Tutor coverage failures this lesson: 0
- Remaining-lesson audit: not_required
- Learner load signal:
- Blocking gaps: {blocking}
- Last stable point: legacy history preserved below; no legacy status promoted
- Next action: {next_action}
{STATE_END}"""


def learning_state_draft(
    course_dir: Path, safe_point_id: str, current_lesson: str
) -> str:
    path = course_dir / "memory" / "learning-state.md"
    original = (
        path.read_text(encoding="utf-8", errors="replace")
        if path.is_file()
        else f"# Learning State: {course_dir.name}\n"
    )
    has_start = STATE_START in original
    has_end = STATE_END in original
    if has_start != has_end:
        raise ValueError("legacy learning state has only one managed-state sentinel")
    block = managed_state_block(course_dir, safe_point_id, current_lesson)
    if has_start:
        pattern = re.compile(
            rf"(?ms){re.escape(STATE_START)}.*?{re.escape(STATE_END)}"
        )
        match = pattern.search(original)
        if not match:
            raise ValueError("legacy managed-state sentinels are malformed")
        old_block = match.group(0).replace(
            "course-grounded-tutor:current-state",
            "legacy-course-grounded-tutor:current-state",
        )
        migrated = pattern.sub(lambda _match: block, original, count=1).rstrip()
        legacy_hash = file_sha256(path) if path.is_file() else ""
        migrated += f"""

## Preserved Legacy Managed Snapshot

- Original learning-state SHA256: `{legacy_hash}`
- Status: historical context only; no mastery or progress was promoted.

```text
{old_block.rstrip()}
```
"""
        return migrated + "\n"

    lines = original.splitlines()
    insert_at = 1 if lines and lines[0].startswith("# ") else 0
    lines[insert_at:insert_at] = ["", block, ""]
    return "\n".join(lines).rstrip() + "\n"


def course_yml_draft(course_dir: Path) -> str:
    path = course_dir / "course.yml"
    if not path.is_file():
        raise ValueError(f"course.yml not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    text = set_yaml_scalar(text, "workspace_schema_version", str(WORKSPACE_SCHEMA_VERSION))
    text = set_yaml_scalar(text, "workspace_migration_status", '"complete"')
    text = set_yaml_scalar(text, "last_migrated_with_skill_version", f'"{SKILL_VERSION}"')
    metadata = yaml_scalar_paths(path)
    if "created_with_skill_version" not in metadata:
        text = set_yaml_scalar(text, "created_with_skill_version", '"legacy"')
    if "workspace_role" not in metadata:
        text = set_yaml_scalar(text, "workspace_role", f'"{WORKSPACE_ROLE_CANONICAL}"')
        text = set_yaml_scalar(text, "canonical_course_dir", '""')
        text = set_yaml_scalar(text, "mirror_last_synced_at", '""')
        text = set_yaml_scalar(text, "mirror_canonical_blueprint_sha256", '""')
        text = set_yaml_scalar(text, "mirror_canonical_learning_state_sha256", '""')

    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    if not validate_blueprint(blueprint):
        global_fields = parse_fields(
            blueprint.read_text(encoding="utf-8", errors="replace").split(
                "## Knowledge-Point Plan", 1
            )[0]
        )
        text = set_yaml_scalar(
            text, "teaching.blueprint.path", '"indexes/teaching-blueprint.md"'
        )
        text = set_yaml_scalar(
            text, "teaching.blueprint.version", f'"{BLUEPRINT_VERSION}"'
        )
        text = set_yaml_scalar(text, "teaching.blueprint.status", '"ready"')
        text = set_yaml_scalar(
            text,
            "teaching.blueprint.source_fingerprint",
            f'"{global_fields.get("Source fingerprint", "")}"',
        )
    return text


def create_manifest(course_dir: Path, source_path: Path | None) -> dict[str, object]:
    originals = [
        original_record(course_dir / "course.yml", course_dir),
        original_record(course_dir / "memory" / "learning-state.md", course_dir),
    ]
    if source_path:
        originals.append(original_record(source_path, course_dir))
        source_register = course_dir / "indexes" / "source-register.md"
        if source_path.resolve() != source_register.resolve():
            originals.append(original_record(source_register, course_dir))
    else:
        originals.append(
            original_record(course_dir / "indexes" / "source-register.md", course_dir)
        )
    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    return {
        "manifest_version": MANIFEST_VERSION,
        "status": "draft",
        "generated_at": now(),
        "course_id": course_dir.name,
        "originals": originals,
        "blueprint_sha256": file_sha256(blueprint) if blueprint.is_file() else "",
        "policy": {
            "legacy_evidence": "preserve_without_promotion",
            "activation": "all draft checks and original fingerprint checks must pass",
        },
    }


def _write_candidates(
    root: Path, course_text: str, source_text: str, state_text: str, manifest: dict[str, object]
) -> dict[str, Path]:
    paths = {
        "root": root,
        "course": root / "course.yml.draft",
        "source": root / "source-register.md.draft",
        "state": root / "learning-state.md.draft",
        "manifest": root / "manifest.json",
    }
    atomic_write_text(paths["course"], course_text)
    atomic_write_text(paths["source"], source_text)
    atomic_write_text(paths["state"], state_text)
    atomic_write_text(paths["manifest"], json.dumps(manifest, ensure_ascii=False, indent=2))
    return paths


def _managed_fields(state_text: str) -> dict[str, str]:
    pattern = re.compile(rf"(?ms){re.escape(STATE_START)}.*?{re.escape(STATE_END)}")
    match = pattern.search(state_text)
    return {
        name.strip(): value.strip()
        for name, value in STATE_FIELD_RE.findall(match.group(0) if match else "")
    }


def validate_draft(course_dir: Path, paths: dict[str, Path]) -> list[str]:
    errors: list[str] = []
    for name in ["course", "source", "state", "manifest"]:
        if not paths[name].is_file():
            errors.append(f"draft file missing: {paths[name]}")
    if errors:
        return errors

    course_fields = yaml_scalar_paths(paths["course"])
    if course_fields.get("workspace_schema_version") != str(WORKSPACE_SCHEMA_VERSION):
        errors.append("course draft workspace_schema_version is not current")
    if course_fields.get("workspace_migration_status") != "complete":
        errors.append("course draft workspace_migration_status must be complete")

    source_text = paths["source"].read_text(encoding="utf-8", errors="replace")
    if not source_text.startswith("# Source Register"):
        errors.append("source-register draft must start with '# Source Register'")
    if "<MIGRATION REQUIRED" in source_text:
        errors.append("source-register draft contains unresolved migration placeholders")
    source_rows = [
        line
        for line in source_text.splitlines()
        if line.startswith("|")
        and "Source ID" not in line
        and not re.fullmatch(r"[|\s:-]+", line)
    ]
    if not source_rows:
        errors.append("source-register draft contains no source rows")

    state_text = paths["state"].read_text(encoding="utf-8", errors="replace")
    if "<MIGRATION REQUIRED" in state_text:
        errors.append("learning-state draft contains unresolved migration placeholders")
    fields = _managed_fields(state_text)
    missing = sorted(REQUIRED_STATE_FIELDS - fields.keys())
    if missing:
        errors.append("learning-state draft missing fields: " + ", ".join(missing))

    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    blueprint_errors = validate_blueprint(blueprint)
    if blueprint_errors:
        errors.append(
            f"active teaching blueprint is not ready ({len(blueprint_errors)} errors)"
        )
        return errors
    blueprint_hash = file_sha256(blueprint)
    global_fields = parse_fields(
        blueprint.read_text(encoding="utf-8", errors="replace").split(
            "## Knowledge-Point Plan", 1
        )[0]
    )
    if course_fields.get("teaching.blueprint.version") != BLUEPRINT_VERSION:
        errors.append("course draft blueprint version does not match the active blueprint")
    if course_fields.get("teaching.blueprint.status") != "ready":
        errors.append("course draft blueprint status must be ready")
    if course_fields.get("teaching.blueprint.source_fingerprint") != global_fields.get(
        "Source fingerprint", ""
    ):
        errors.append("course draft source fingerprint does not match the blueprint")

    if missing:
        return errors
    if fields.get("Workspace schema version") != str(WORKSPACE_SCHEMA_VERSION):
        errors.append("learning-state workspace schema does not match")
    if fields.get("Blueprint status") != "ready":
        errors.append("learning-state blueprint status must be ready")
    if fields.get("Blueprint SHA256") != blueprint_hash:
        errors.append("learning-state blueprint SHA256 is stale")
    if fields.get("Source fingerprint") != global_fields.get("Source fingerprint", ""):
        errors.append("learning-state source fingerprint differs from blueprint")
    if fields.get("Point status") != "not_started":
        errors.append(
            "legacy migration may activate only at not_started; old mastery is preserved, not promoted"
        )
    point_id = fields.get("Point ID", "")
    binding = get_point_binding(blueprint, point_id)
    if binding is None:
        errors.append("learning-state Point ID is not present in the blueprint")
    record = _point_record(blueprint, point_id)
    if record and fields.get("Lesson progress") != f"{record[0]}/{record[1]}":
        errors.append("learning-state progress does not match the selected blueprint point")

    try:
        manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"manifest JSON is invalid: {error}")
        return errors
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        errors.append(f"manifest_version must be {MANIFEST_VERSION}")
    if manifest.get("blueprint_sha256") != blueprint_hash:
        errors.append("blueprint changed after migration draft creation; regenerate the draft")
    return errors


def _original_drift_errors(course_dir: Path, manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for record in manifest.get("originals", []):
        if not isinstance(record, dict):
            errors.append("manifest original record is invalid")
            continue
        path = course_dir / str(record.get("path", ""))
        expected_exists = record.get("exists") is True
        if path.is_file() != expected_exists:
            errors.append(f"original existence changed: {path}")
        elif expected_exists and file_sha256(path) != record.get("sha256"):
            errors.append(f"original file changed after draft creation: {path}")
    return errors


def report_payload(course_dir: Path, errors: list[str], action: str) -> dict[str, object]:
    return {
        "course_dir": str(course_dir),
        "action": action,
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "allowed_next": "activate" if not errors else "repair_or_regenerate_draft",
    }


def print_report(payload: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"Course: {payload['course_dir']}")
    print(f"Action: {payload['action']}")
    print(f"Valid: {'yes' if payload['valid'] else 'no'}")
    print(f"Errors: {payload['error_count']}")
    for error in payload["errors"]:
        print(f"- {error}")
    print(f"Next: {payload['allowed_next']}")


def create_draft_command(args: argparse.Namespace) -> int:
    paths = draft_paths(args.course_dir)
    if paths["manifest"].is_file():
        try:
            existing_manifest = json.loads(
                paths["manifest"].read_text(encoding="utf-8")
            )
        except json.JSONDecodeError:
            existing_manifest = {}
        if existing_manifest.get("status") == "activated":
            raise ValueError(
                "the recorded migration is already activated; do not overwrite its manifest"
            )
    if paths["root"].exists() and not args.force and not args.dry_run:
        raise ValueError(f"migration draft already exists: {paths['root']}")
    source_text, source_relative = source_register_draft(args.course_dir)
    state_text = learning_state_draft(
        args.course_dir, args.safe_point_id, args.current_lesson
    )
    course_text = course_yml_draft(args.course_dir)
    source_path = args.course_dir / source_relative if source_relative else None
    manifest = create_manifest(args.course_dir, source_path)
    manifest["safe_point_id"] = args.safe_point_id
    if args.dry_run:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_paths = _write_candidates(
                Path(temporary), course_text, source_text, state_text, manifest
            )
            errors = validate_draft(args.course_dir, temporary_paths)
        print_report(report_payload(args.course_dir, errors, "create-draft-dry-run"), args.format)
        return 0 if not errors else 1
    paths["root"].mkdir(parents=True, exist_ok=True)
    _write_candidates(paths["root"], course_text, source_text, state_text, manifest)
    errors = validate_draft(args.course_dir, paths)
    print_report(report_payload(args.course_dir, errors, "create-draft"), args.format)
    return 0


def validate_command(args: argparse.Namespace) -> int:
    paths = draft_paths(args.course_dir)
    errors = validate_draft(args.course_dir, paths)
    if not errors:
        manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        errors.extend(_original_drift_errors(args.course_dir, manifest))
    print_report(report_payload(args.course_dir, errors, "validate-draft"), args.format)
    return 0 if not errors else 1


def activate_command(args: argparse.Namespace) -> int:
    paths = draft_paths(args.course_dir)
    errors = validate_draft(args.course_dir, paths)
    manifest: dict[str, object] = {}
    if not errors:
        manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        errors.extend(_original_drift_errors(args.course_dir, manifest))
    if errors or args.dry_run:
        print_report(
            report_payload(
                args.course_dir,
                errors,
                "activate-dry-run" if args.dry_run else "activate",
            ),
            args.format,
        )
        return 0 if not errors else 1

    timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%f")
    backup_root = paths["root"] / "backups" / timestamp
    destinations = {
        "course": args.course_dir / "course.yml",
        "source": args.course_dir / "indexes" / "source-register.md",
        "state": args.course_dir / "memory" / "learning-state.md",
    }
    before: dict[str, str | None] = {}
    backup_root.mkdir(parents=True, exist_ok=False)
    for record in manifest.get("originals", []):
        if not isinstance(record, dict) or record.get("exists") is not True:
            continue
        original = args.course_dir / str(record.get("path", ""))
        backup = backup_root / str(original.relative_to(args.course_dir))
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, backup)
    for name, destination in destinations.items():
        before[name] = (
            destination.read_text(encoding="utf-8", errors="replace")
            if destination.is_file()
            else None
        )
    try:
        for name, destination in destinations.items():
            atomic_write_text(
                destination, paths[name].read_text(encoding="utf-8", errors="replace")
            )
        (args.course_dir / "memory" / "exercise-contracts").mkdir(
            parents=True, exist_ok=True
        )
    except Exception:
        for name, destination in destinations.items():
            previous = before[name]
            if previous is None:
                if destination.exists():
                    destination.unlink()
            else:
                atomic_write_text(destination, previous)
        raise

    manifest["status"] = "activated"
    manifest["activated_at"] = now()
    manifest["backup_root"] = str(backup_root.relative_to(args.course_dir)).replace(
        "\\", "/"
    )
    atomic_write_text(paths["manifest"], json.dumps(manifest, ensure_ascii=False, indent=2))
    print_report(report_payload(args.course_dir, [], "activate"), args.format)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan")
    plan.add_argument("--course-dir", required=True, type=Path)
    plan.add_argument("--format", choices=["text", "json"], default="text")
    plan.set_defaults(handler=None)

    create = subparsers.add_parser("create-draft")
    create.add_argument("--course-dir", required=True, type=Path)
    create.add_argument("--safe-point-id", default="")
    create.add_argument("--current-lesson", default="")
    create.add_argument("--force", action="store_true")
    create.add_argument("--dry-run", action="store_true")
    create.add_argument("--format", choices=["text", "json"], default="text")
    create.set_defaults(handler=create_draft_command)

    validate = subparsers.add_parser("validate-draft")
    validate.add_argument("--course-dir", required=True, type=Path)
    validate.add_argument("--format", choices=["text", "json"], default="text")
    validate.set_defaults(handler=validate_command)

    activate = subparsers.add_parser("activate")
    activate.add_argument("--course-dir", required=True, type=Path)
    activate.add_argument("--dry-run", action="store_true")
    activate.add_argument("--format", choices=["text", "json"], default="text")
    activate.set_defaults(handler=activate_command)

    args = parser.parse_args()
    try:
        if args.command == "plan":
            payload = course_plan(args.course_dir)
            if args.format == "json":
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                for key, value in payload.items():
                    print(f"{key}: {value}")
            return 0
        return args.handler(args)
    except ValueError as error:
        parser.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
