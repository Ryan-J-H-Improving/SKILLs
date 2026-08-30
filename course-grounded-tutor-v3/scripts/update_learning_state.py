#!/usr/bin/env python3
"""Update V3.1 canonical learning state and durable milestone records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from exercise_contract import (
    contract_sha256,
    validate_blueprint_binding,
    validate_contract_file,
)
from validate_teaching_blueprint import get_point_binding, parse_fields, validate_blueprint
from workspace_common import (
    WORKSPACE_SCHEMA_VERSION,
    atomic_write_text,
    file_sha256,
    reference_mirror_write_error,
    yaml_scalar_paths,
)


STATE_START = "<!-- course-grounded-tutor:current-state:start -->"
STATE_END = "<!-- course-grounded-tutor:current-state:end -->"


def read_or_create(path: Path, heading: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"# {heading}\n"


def write(path: Path, text: str) -> None:
    atomic_write_text(path, text)


def remove_placeholder_section(text: str, placeholder: str) -> str:
    pattern = re.compile(
        rf"(?ms)^###\s+{re.escape(placeholder)}\s*\n.*?(?=^###\s+|\Z)"
    )
    return pattern.sub("", text).rstrip() + "\n"


def append_h3_entry(path: Path, heading: str, title: str, body: str) -> None:
    text = remove_placeholder_section(read_or_create(path, heading), "<Date>")
    entry = f"### {title}\n\n{body.strip()}\n"
    write(path, text.rstrip() + "\n\n" + entry)


def upsert_h3_section(
    path: Path, heading: str, title: str, body: str
) -> None:
    text = remove_placeholder_section(read_or_create(path, heading), "<Weak Point>")
    section = f"### {title}\n\n{body.strip()}\n"
    pattern = re.compile(
        rf"(?ms)^###\s+{re.escape(title)}\s*\n.*?(?=^###\s+|\Z)",
        re.IGNORECASE,
    )
    if pattern.search(text):
        text = pattern.sub(lambda _match: section.rstrip(), text, count=1)
    else:
        text = text.rstrip() + "\n\n" + section
    write(path, text)


def normalized(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


STATE_JSON_SCHEMA_VERSION = 1
STATE_JSON_FIELDS = {
    "course_dir",
    "mode",
    "topic",
    "current_lesson",
    "lesson_progress",
    "point_id",
    "current_point",
    "point_status",
    "blueprint_path",
    "blueprint_status",
    "source_fingerprint",
    "transcript_gate",
    "transcript_evidence",
    "narrative_bridge",
    "formula_gate",
    "unresolved_operations",
    "coverage_gate",
    "exercise_status",
    "exercise_coverage",
    "exercise_set_id",
    "exercise_contract",
    "mastery_evidence",
    "auto_advance",
    "tutor_coverage_failures",
    "remaining_lesson_audit",
    "last_stable_point",
    "learner_load_signal",
    "blocking_gaps",
    "tutor_coverage_gap",
    "sources",
    "taught",
    "user_performance",
    "weak_point",
    "course_notation",
    "follow_up",
    "difficulty",
    "scored",
    "issue_class",
    "misconception",
    "tested_relationships",
    "cognitive_actions",
    "answer_actions",
    "replacement_result",
}


def state_json_schema() -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Course Grounded Tutor State Update",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "course_dir", "topic"],
        "properties": {
            "schema_version": {"const": STATE_JSON_SCHEMA_VERSION},
            "course_dir": {"type": "string", "minLength": 1},
            "topic": {"type": "string", "minLength": 1},
            "tutor_coverage_gap": {"type": "boolean"},
            "tutor_coverage_failures": {"type": "integer", "minimum": 0},
            "auto_advance": {"enum": ["yes", "no"]},
            "remaining_lesson_audit": {
                "enum": ["not_required", "required", "passed"]
            },
            "scored": {"enum": ["", "yes", "no"]},
            **{
                field: {"type": "string"}
                for field in sorted(
                    STATE_JSON_FIELDS
                    - {
                        "course_dir",
                        "topic",
                        "tutor_coverage_gap",
                        "tutor_coverage_failures",
                        "auto_advance",
                        "remaining_lesson_audit",
                        "scored",
                    }
                )
            },
        },
    }


def apply_state_json(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> argparse.Namespace:
    if not args.state_json:
        return args
    allowed_tokens = {"--state-json", "--dry-run"}
    raw_args = sys.argv[1:]
    for index, token in enumerate(raw_args):
        if token == str(args.state_json) and index and raw_args[index - 1] == "--state-json":
            continue
        if token not in allowed_tokens:
            parser.error("--state-json cannot be combined with state field CLI flags")
    try:
        data = json.loads(args.state_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        parser.error(f"cannot read --state-json: {error}")
    if not isinstance(data, dict):
        parser.error("--state-json must contain one JSON object")
    unknown = sorted(set(data) - STATE_JSON_FIELDS - {"schema_version"})
    if unknown:
        parser.error("unknown --state-json fields: " + ", ".join(unknown))
    if data.get("schema_version") != STATE_JSON_SCHEMA_VERSION:
        parser.error(
            f"state JSON schema_version must be {STATE_JSON_SCHEMA_VERSION}"
        )
    for required in ["course_dir", "topic"]:
        if not isinstance(data.get(required), str) or not data[required].strip():
            parser.error(f"state JSON field {required!r} must be a non-empty string")
    for field, value in data.items():
        if field == "schema_version":
            continue
        if field == "course_dir":
            setattr(args, field, Path(value))
        elif field == "tutor_coverage_gap":
            if not isinstance(value, bool):
                parser.error("state JSON field 'tutor_coverage_gap' must be boolean")
            setattr(args, field, value)
        elif field == "tutor_coverage_failures":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                parser.error(
                    "state JSON field 'tutor_coverage_failures' must be a non-negative integer"
                )
            setattr(args, field, value)
        else:
            if not isinstance(value, str):
                parser.error(f"state JSON field {field!r} must be a string")
            setattr(args, field, value)
    for field, choices in {
        "auto_advance": {"yes", "no"},
        "remaining_lesson_audit": {"not_required", "required", "passed"},
        "scored": {"", "yes", "no"},
    }.items():
        if getattr(args, field) not in choices:
            parser.error(
                f"state JSON field {field!r} must be one of: {', '.join(sorted(choices))}"
            )
    return args


def limited_clarification_mode(args: argparse.Namespace) -> bool:
    return normalized(args.mode) in {
        "migration",
        "migration_required",
        "limited_clarification",
        "limited_clarification_only",
    }


def validate_limited_clarification(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    if not limited_clarification_mode(args):
        return
    point_status = normalized(args.point_status or args.instruction_stage)
    exercise_status = normalized(args.exercise_status or args.practice_gate)
    forbidden = []
    if point_status in {"teaching", "taught", "practiced", "mastered", "exam_ready"}:
        forbidden.append("formal point status")
    if exercise_status or args.exercise_set_id.strip() or args.exercise_contract.strip():
        forbidden.append("exercise activity")
    if normalized(args.auto_advance) == "yes":
        forbidden.append("automatic advance")
    if args.mastery_evidence.strip():
        forbidden.append("mastery evidence")
    if normalized(args.scored) == "yes":
        forbidden.append("scoring")
    if forbidden:
        parser.error(
            "migration-required workspaces allow limited clarification only; blocked: "
            + ", ".join(forbidden)
        )


def formal_teaching_requested(args: argparse.Namespace) -> bool:
    point_status = normalized(args.point_status or args.instruction_stage)
    exercise_status = normalized(args.exercise_status or args.practice_gate)
    return (
        point_status in {"teaching", "taught", "practiced", "mastered", "exam_ready"}
        or bool(args.taught.strip())
        or normalized(args.blueprint_status) == "ready"
        or exercise_status in {"pending", "in_progress", "passed"}
        or bool(args.exercise_set_id.strip())
        or bool(args.exercise_contract.strip())
        or normalized(args.auto_advance) == "yes"
    )


def verify_formal_blueprint(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    args.blueprint_resolved = ""
    args.blueprint_hash = ""
    if args.tutor_coverage_gap or limited_clarification_mode(args):
        return
    if not formal_teaching_requested(args):
        return

    course_yml = args.course_dir / "course.yml"
    if not course_yml.is_file():
        parser.error(
            "formal teaching is blocked: course.yml is missing; audit and migrate the workspace"
        )
    metadata = yaml_scalar_paths(course_yml)
    if metadata.get("workspace_schema_version") != str(WORKSPACE_SCHEMA_VERSION):
        parser.error(
            "formal teaching is blocked: workspace schema migration is required"
        )
    if metadata.get("workspace_migration_status") not in {"complete", "not_required"}:
        parser.error(
            "formal teaching is blocked: legacy workspace reconciliation is incomplete"
        )
    if metadata.get("teaching.blueprint.status") != "ready":
        parser.error(
            "formal teaching is blocked: course.yml does not record a promoted blueprint"
        )

    blueprint_path = Path(args.blueprint_path)
    if not blueprint_path.is_absolute():
        blueprint_path = args.course_dir / blueprint_path
    blueprint_path = blueprint_path.resolve()
    errors = validate_blueprint(blueprint_path, args.lesson_progress)
    if errors:
        parser.error("formal teaching requires a validated blueprint: " + "; ".join(errors))

    global_fields = parse_fields(
        blueprint_path.read_text(encoding="utf-8", errors="replace").split(
            "## Knowledge-Point Plan", 1
        )[0]
    )
    actual_fingerprint = global_fields.get("Source fingerprint", "")
    if args.source_fingerprint.strip() and args.source_fingerprint.strip() != actual_fingerprint:
        parser.error("source fingerprint does not match the validated blueprint")
    args.source_fingerprint = actual_fingerprint
    if not args.point_id.strip():
        parser.error("--point-id is required for formal teaching state updates")
    if not args.lesson_progress.strip():
        parser.error("--lesson-progress is required for formal teaching state updates")
    if get_point_binding(blueprint_path, args.point_id) is None:
        parser.error("point ID is not present in the validated blueprint")

    declared_version = metadata.get("teaching.blueprint.version", "")
    if declared_version and declared_version != "3.1":
        parser.error("course.yml teaching.blueprint.version does not match blueprint 3.1")
    declared_fingerprint = metadata.get("teaching.blueprint.source_fingerprint", "")
    if declared_fingerprint and declared_fingerprint != actual_fingerprint:
        parser.error("course.yml source fingerprint does not match the validated blueprint")
    args.blueprint_status = "ready"
    args.blueprint_resolved = str(blueprint_path)
    args.blueprint_hash = file_sha256(blueprint_path)


def load_exercise_contract(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    exercise_status = normalized(args.exercise_status or args.practice_gate)
    point_status = normalized(args.point_status or args.instruction_stage)
    advancing = normalized(args.auto_advance) == "yes" or point_status in {
        "practiced",
        "mastered",
        "exam_ready",
    }
    requires_contract = (
        exercise_status in {"pending", "in_progress", "passed"}
        or advancing
        or (bool(args.exercise_set_id.strip()) and normalized(args.coverage_gate) == "passed")
    )

    args.exercise_contract_valid = False
    args.exercise_contract_resolved = ""
    args.exercise_contract_hash = ""
    if not requires_contract:
        return

    if not args.exercise_contract.strip():
        parser.error(
            "a validated --exercise-contract is required before issuing, scoring, "
            "or advancing from an exercise"
        )
    for option, value in [
        ("--point-id", args.point_id),
        ("--exercise-set-id", args.exercise_set_id),
        ("--source-fingerprint", args.source_fingerprint),
    ]:
        if not value.strip():
            parser.error(f"{option} is required when an exercise contract is active")

    contract_path = Path(args.exercise_contract)
    if not contract_path.is_absolute():
        contract_path = args.course_dir / contract_path
    contract_path = contract_path.resolve()
    data, errors = validate_contract_file(contract_path)
    if errors:
        parser.error("invalid exercise contract: " + "; ".join(errors))

    blueprint_path = Path(args.blueprint_resolved or args.blueprint_path)
    if not blueprint_path.is_absolute():
        blueprint_path = (args.course_dir / blueprint_path).resolve()
    binding_errors = validate_blueprint_binding(
        data, blueprint_path, args.lesson_progress
    )
    if binding_errors:
        parser.error(
            "exercise contract is not authorized by the validated blueprint: "
            + "; ".join(binding_errors)
        )

    expected = {
        "exercise_set_id": args.exercise_set_id,
        "point_id": args.point_id,
        "source_fingerprint": args.source_fingerprint,
    }
    mismatches: list[str] = []
    for field, value in expected.items():
        if value.strip() and str(data.get(field, "")).strip() != value.strip():
            mismatches.append(
                f"{field} contract={data.get(field)!r} state={value!r}"
            )
    if mismatches:
        parser.error("exercise contract does not match state: " + "; ".join(mismatches))

    args.exercise_contract_valid = True
    args.exercise_contract_resolved = str(contract_path)
    args.exercise_contract_hash = contract_sha256(contract_path)
    args.blueprint_resolved = str(blueprint_path)


def validate_advance(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    effective_point_status = args.point_status or args.instruction_stage
    advancing = normalized(args.auto_advance) == "yes" or normalized(effective_point_status) in {
        "practiced",
        "mastered",
        "exam_ready",
    }
    if not advancing:
        return

    required = {
        "blueprint status": normalized(args.blueprint_status) == "ready",
        "source fingerprint": bool(args.source_fingerprint.strip()),
        "transcript gate": normalized(args.transcript_gate) in {"passed", "not_supplied"},
        "formula gate": normalized(args.formula_gate) in {"passed", "not_required"},
        "coverage gate": normalized(args.coverage_gate) == "passed",
        "validated exercise contract": args.exercise_contract_valid,
        "exercise status": normalized(args.exercise_status) == "passed",
        "mastery evidence": bool(args.mastery_evidence.strip()),
        "no tutor coverage gap": not args.tutor_coverage_gap,
        "remaining-lesson audit after repeated tutor gaps": (
            args.tutor_coverage_failures < 2
            or normalized(args.remaining_lesson_audit) == "passed"
        ),
    }
    failed = [name for name, passed in required.items() if not passed]
    if failed:
        parser.error("cannot advance point; failed V3.1 gates: " + ", ".join(failed))


def update_current_state(path: Path, args: argparse.Namespace) -> None:
    text = read_or_create(path, f"Learning State: {args.course_dir.name}")
    point_status = args.point_status or args.instruction_stage
    exercise_status = args.exercise_status or args.practice_gate
    exercise_coverage = args.exercise_coverage or args.practice_checkpoint
    mastery_evidence = args.mastery_evidence
    current_point = args.current_point or args.topic
    block = f"""{STATE_START}
## Current Session Snapshot

- Current mode: {args.mode}
- Current lesson: {args.current_lesson}
- Lesson progress: {args.lesson_progress}
- Point ID: {args.point_id}
- Current point: {current_point}
- Point status: {point_status}
- Workspace schema version: {args.workspace_schema_version}
- Blueprint path: {args.blueprint_path}
- Blueprint status: {args.blueprint_status}
- Blueprint SHA256: {args.blueprint_hash}
- Source fingerprint: {args.source_fingerprint}
- Transcript gate: {args.transcript_gate}
- Transcript evidence: {args.transcript_evidence}
- Narrative bridge: {args.narrative_bridge}
- Formula gate: {args.formula_gate}
- Unresolved formula operations: {args.unresolved_operations}
- Coverage gate: {args.coverage_gate}
- Exercise status: {exercise_status}
- Exercise coverage: {exercise_coverage}
- Exercise contract: {args.exercise_contract_resolved}
- Exercise contract SHA256: {args.exercise_contract_hash}
- Mastery evidence: {mastery_evidence}
- Automatic advance: {args.auto_advance}
- Tutor coverage failures this lesson: {args.tutor_coverage_failures}
- Remaining-lesson audit: {args.remaining_lesson_audit}
- Learner load signal: {args.learner_load_signal}
- Blocking gaps: {args.blocking_gaps}
- Last stable point: {args.last_stable_point}
- Next action: {args.follow_up}
{STATE_END}"""
    pattern = re.compile(rf"(?ms){re.escape(STATE_START)}.*?{re.escape(STATE_END)}")
    if pattern.search(text):
        text = pattern.sub(lambda _match: block, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    write(path, text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-json", type=Path)
    parser.add_argument("--print-schema", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--course-dir", type=Path)
    parser.add_argument("--mode", default="")
    parser.add_argument("--topic", default="")
    parser.add_argument("--current-lesson", default="")
    parser.add_argument("--lesson-progress", default="")
    parser.add_argument("--point-id", default="")
    parser.add_argument("--current-point", default="")
    parser.add_argument("--point-status", default="")
    parser.add_argument("--blueprint-path", default="indexes/teaching-blueprint.md")
    parser.add_argument("--blueprint-status", default="")
    parser.add_argument("--source-fingerprint", default="")
    parser.add_argument("--transcript-gate", default="")
    parser.add_argument("--transcript-evidence", default="")
    parser.add_argument("--narrative-bridge", default="")
    parser.add_argument("--formula-gate", default="")
    parser.add_argument("--unresolved-operations", default="")
    parser.add_argument("--coverage-gate", default="")
    parser.add_argument("--exercise-status", default="")
    parser.add_argument("--exercise-coverage", default="")
    parser.add_argument("--exercise-set-id", default="")
    parser.add_argument("--exercise-contract", default="")
    parser.add_argument("--mastery-evidence", default="")
    parser.add_argument("--auto-advance", choices=["yes", "no"], default="no")
    parser.add_argument("--tutor-coverage-failures", type=int, default=0)
    parser.add_argument(
        "--remaining-lesson-audit",
        choices=["not_required", "required", "passed"],
        default="not_required",
    )
    parser.add_argument("--last-stable-point", default="")
    parser.add_argument("--learner-load-signal", default="")
    parser.add_argument("--blocking-gaps", default="")
    parser.add_argument("--tutor-coverage-gap", action="store_true")
    parser.add_argument("--sources", default="")
    parser.add_argument("--taught", default="")
    parser.add_argument("--user-performance", default="")
    parser.add_argument("--weak-point", default="")
    parser.add_argument("--course-notation", default="")
    parser.add_argument("--follow-up", default="")
    parser.add_argument("--difficulty", default="")
    parser.add_argument("--scored", choices=["yes", "no"], default="")
    parser.add_argument("--issue-class", default="")
    parser.add_argument("--misconception", default="")
    parser.add_argument("--tested-relationships", default="")
    parser.add_argument("--cognitive-actions", default="")
    parser.add_argument("--answer-actions", default="")
    parser.add_argument("--replacement-result", default="")

    # V2 compatibility: accepted for existing automation, never used to infer mastery.
    parser.add_argument("--learning-cluster", default="", help=argparse.SUPPRESS)
    parser.add_argument("--instruction-stage", default="", help=argparse.SUPPRESS)
    parser.add_argument("--practice-gate", default="", help=argparse.SUPPRESS)
    parser.add_argument("--practice-checkpoint", default="", help=argparse.SUPPRESS)
    parser.add_argument("--required-concepts", default="", help=argparse.SUPPRESS)
    parser.add_argument("--new-terms", default="", help=argparse.SUPPRESS)
    parser.add_argument("--source-layers", default="", help=argparse.SUPPRESS)
    parser.add_argument("--worked-example-status", default="", help=argparse.SUPPRESS)
    parser.add_argument("--guided-check-evidence", default="", help=argparse.SUPPRESS)
    parser.add_argument("--evidence-reused", default="", help=argparse.SUPPRESS)
    parser.add_argument("--remediation-rounds", default="", help=argparse.SUPPRESS)
    parser.add_argument("--learning-phase", default="", help=argparse.SUPPRESS)
    parser.add_argument("--question-label", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.print_schema:
        if len(sys.argv) != 2:
            parser.error("--print-schema must be used alone")
        print(json.dumps(state_json_schema(), ensure_ascii=False, indent=2))
        return 0
    args = apply_state_json(args, parser)
    if args.course_dir is None:
        parser.error("--course-dir is required")
    if not args.topic.strip():
        parser.error("--topic is required")
    args.workspace_schema_version = "unknown"
    course_yml = args.course_dir / "course.yml"
    if course_yml.is_file():
        args.workspace_schema_version = yaml_scalar_paths(course_yml).get(
            "workspace_schema_version", "unknown"
        )

    if (
        args.weak_point
        and not args.tutor_coverage_gap
        and normalized(args.coverage_gate) != "passed"
    ):
        parser.error("cannot record a learner weak point before the coverage gate passes")
    validate_limited_clarification(args, parser)
    mirror_error = reference_mirror_write_error(args.course_dir)
    if mirror_error:
        if limited_clarification_mode(args):
            print(
                "Reference-mirror clarification validated; no progress, exercise, "
                "mastery, or durable state was changed."
            )
            return 0
        parser.error("state update is blocked: " + mirror_error)
    if limited_clarification_mode(args):
        print(
            "Limited clarification validated; no progress, exercise, mastery, or "
            "durable state was changed."
        )
        return 0
    args.blueprint_resolved = ""
    args.blueprint_hash = ""
    load_exercise_contract(args, parser)
    verify_formal_blueprint(args, parser)
    validate_advance(args, parser)

    if args.dry_run:
        print(f"State update dry-run passed for {args.course_dir}")
        if args.blueprint_hash:
            print(f"Blueprint SHA256: {args.blueprint_hash}")
        return 0

    timestamp = datetime.now().astimezone().isoformat(timespec="microseconds")
    memory_dir = args.course_dir / "memory"
    update_current_state(memory_dir / "learning-state.md", args)

    point_status = args.point_status or args.instruction_stage
    exercise_status = args.exercise_status or args.practice_gate
    session_body = f"""- Mode: {args.mode}
- Topic: {args.topic}
- Lesson progress: {args.lesson_progress}
- Point ID: {args.point_id}
- Point status: {point_status}
- Blueprint: {args.blueprint_status}; {args.source_fingerprint}
- Blueprint SHA256: {args.blueprint_hash}
- Transcript evidence: {args.transcript_evidence}
- Formula gate: {args.formula_gate}
- Exercise status: {exercise_status}
- Exercise contract: {args.exercise_contract_resolved}
- Exercise contract SHA256: {args.exercise_contract_hash}
- Mastery evidence: {args.mastery_evidence}
- Automatic advance: {args.auto_advance}
- Tutor coverage failures this lesson: {args.tutor_coverage_failures}
- Remaining-lesson audit: {args.remaining_lesson_audit}
- Learner load signal: {args.learner_load_signal}
- Sources: {args.sources}
- Taught: {args.taught}
- User performance: {args.user_performance}
- Next: {args.follow_up}"""
    append_h3_entry(memory_dir / "session-log.md", "Session Log", timestamp, session_body)

    if args.weak_point and not args.tutor_coverage_gap:
        weak_body = f"""- Status: fragile
- Exact evidence: {args.user_performance}
- Failed relationship: {args.misconception}
- Corrective explanation that worked:
- Course notation: {args.course_notation}
- Follow-up: {args.follow_up}"""
        upsert_h3_section(
            memory_dir / "weak-points.md",
            "Weak Points",
            args.weak_point,
            weak_body,
        )

    exercise_id = args.exercise_set_id or args.question_label
    if exercise_id:
        scored = args.scored or ("no" if args.tutor_coverage_gap else "")
        practice_body = f"""- Point: {args.lesson_progress} {args.topic}
- Point ID: {args.point_id}
- Exercise set: {exercise_id}
- Exercise contract: {args.exercise_contract_resolved}
- Exercise contract SHA256: {args.exercise_contract_hash}
- Tested relationships: {args.tested_relationships}
- Cognitive actions: {args.cognitive_actions}
- Difficulty: {args.difficulty}
- Answer actions: {args.answer_actions}
- Blueprint gate: {args.blueprint_status}
- Transcript gate: {args.transcript_gate}
- Formula gate: {args.formula_gate}
- Coverage gate: {args.coverage_gate}
- Scored: {scored}
- Tutor coverage gap: {"yes" if args.tutor_coverage_gap else "no"}
- Issue class: {args.issue_class}
- User result: {args.user_performance}
- Evidence gained: {args.mastery_evidence}
- Misconception: {args.misconception}
- Replacement result: {args.replacement_result}
- Automatic advance: {args.auto_advance}
- Next: {args.follow_up}"""
        append_h3_entry(
            memory_dir / "practice-history.md",
            "Practice History",
            timestamp,
            practice_body,
        )

    print(f"Updated memory files in {memory_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
