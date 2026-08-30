#!/usr/bin/env python3
"""Validate and render deterministic tutoring exercise contracts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


CONTRACT_VERSION = 1
READY_STATUS = "ready"
ACTION_ID_RE = re.compile(r"^A([1-9][0-9]*)$")
RELATION_ID_RE = re.compile(r"^R([1-9][0-9]*)$")
STABLE_POINT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MULTILINE_REQUEST_RE = re.compile(r"(?m)^\s*(?:[-*]|\d+[.)])\s+")
EXPLICIT_MULTI_REQUEST_RE = re.compile(
    r"(?:\b(?:and then|as well as)\b|并且|并分别|以及分别|；|;)",
    re.IGNORECASE,
)
SECOND_REQUEST_RE = re.compile(
    r"(?:\bwhy\b|\bgive (?:a|one|the) reason\b|\bjustify\b|"
    r"为什么|说明理由|解释理由|并说明|并解释|并给出)",
    re.IGNORECASE,
)

ACTION_LIMITS = {
    "learning_post_point": (3, 5),
    "learning_targeted_repair": (1, 3),
    "exam_review": (3, 15),
    "cold_diagnostic": (1, 15),
}

REQUIRED_AUDITS = {
    "teaching_evidence",
    "atomicity_and_load",
    "question_rubric_symmetry",
}

ALLOWED_OPERATIONS = {
    "apply",
    "calculate",
    "classify",
    "compare",
    "construct",
    "correct",
    "design",
    "explain",
    "identify",
    "interpret",
    "justify",
    "select",
    "trace",
}


def load_contract(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"exercise contract not found: {path}") from None
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid exercise contract JSON at line {error.lineno}: {error.msg}"
        ) from None
    if not isinstance(data, dict):
        raise ValueError("exercise contract root must be an object")
    return data


def contract_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical(value: Any) -> str:
    return " ".join(str(value).split()).casefold()


def _audit_result(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("result", "")).strip().lower()
    return str(value).strip().lower()


def validate_contract(
    data: dict[str, Any], require_ready: bool = True
) -> list[str]:
    errors: list[str] = []

    if data.get("contract_version") != CONTRACT_VERSION:
        errors.append(f"contract_version must be {CONTRACT_VERSION}")
    status = str(data.get("status", "")).lower()
    if require_ready and status != READY_STATUS:
        errors.append("status must be ready")
    if not require_ready and status not in {"draft", READY_STATUS}:
        errors.append("status must be draft or ready before promotion")

    kind = str(data.get("exercise_kind", ""))
    if kind not in ACTION_LIMITS:
        errors.append(
            "exercise_kind must be one of: " + ", ".join(sorted(ACTION_LIMITS))
        )

    for field in [
        "course_id",
        "lesson_id",
        "point_id",
        "exercise_set_id",
        "source_fingerprint",
    ]:
        if not _nonempty(data.get(field)):
            errors.append(f"{field} is required")

    point_id = str(data.get("point_id", "")).strip()
    if point_id and not STABLE_POINT_ID_RE.fullmatch(point_id):
        errors.append(
            "point_id must be a stable blueprint identifier, not a progress fraction like 2/10"
        )

    display = data.get("display")
    if not isinstance(display, dict):
        errors.append("display must be an object")
    else:
        if not _nonempty(display.get("title")):
            errors.append("display.title is required")
        if not _nonempty(display.get("answer_instruction")):
            errors.append("display.answer_instruction is required")

    scenario = data.get("scenario", "")
    if scenario is not None and not isinstance(scenario, str):
        errors.append("scenario must be a string")
    elif isinstance(scenario, str):
        if "?" in scenario or "？" in scenario:
            errors.append("scenario may contain facts only, not answer requests")
        if MULTILINE_REQUEST_RE.search(scenario):
            errors.append("scenario may not hide numbered or bulleted answer requests")

    actions = data.get("actions")
    if not isinstance(actions, list):
        errors.append("actions must be an array")
        actions = []

    if kind in ACTION_LIMITS:
        minimum, maximum = ACTION_LIMITS[kind]
        if not minimum <= len(actions) <= maximum:
            errors.append(
                f"{kind} requires {minimum}-{maximum} atomic actions; found {len(actions)}"
            )

    seen_ids: set[str] = set()
    for index, action in enumerate(actions, start=1):
        prefix = f"action {index}"
        if not isinstance(action, dict):
            errors.append(f"{prefix} must be an object")
            continue

        action_id = str(action.get("id", ""))
        expected_id = f"A{index}"
        if not ACTION_ID_RE.fullmatch(action_id):
            errors.append(f"{prefix} id must use A1, A2, ...")
        elif action_id != expected_id:
            errors.append(f"{prefix} id must be {expected_id}")
        if action_id in seen_ids:
            errors.append(f"duplicate action id: {action_id}")
        seen_ids.add(action_id)

        relation_id = str(action.get("relation_id", ""))
        if not RELATION_ID_RE.fullmatch(relation_id):
            errors.append(f"{prefix} relation_id must use R1, R2, ...")

        operation = str(action.get("operation", "")).strip().lower()
        if operation not in ALLOWED_OPERATIONS:
            errors.append(
                f"{prefix} operation must be one of: "
                + ", ".join(sorted(ALLOWED_OPERATIONS))
            )

        prompt = action.get("prompt")
        if not _nonempty(prompt):
            errors.append(f"{prefix} prompt is required")
        else:
            prompt_text = str(prompt).strip()
            if "\n" in prompt_text or "\r" in prompt_text:
                errors.append(f"{prefix} prompt must be one line and one answer request")
            if sum(prompt_text.count(mark) for mark in ["?", "？"]) > 1:
                errors.append(f"{prefix} prompt contains multiple questions")
            if EXPLICIT_MULTI_REQUEST_RE.search(prompt_text):
                errors.append(f"{prefix} prompt appears to combine multiple requests")
            if operation not in {"explain", "justify"} and SECOND_REQUEST_RE.search(
                prompt_text
            ):
                errors.append(
                    f"{prefix} prompt adds a reason/explanation to another action; split it"
                )

        stimulus = action.get("stimulus", "")
        if stimulus is not None and not isinstance(stimulus, str):
            errors.append(f"{prefix} stimulus must be a string")
        elif isinstance(stimulus, str) and ("?" in stimulus or "？" in stimulus):
            errors.append(f"{prefix} stimulus may contain facts only")

        if not _nonempty(action.get("tested_relationship")):
            errors.append(f"{prefix} tested_relationship is required")
        if not _nonempty(action.get("expected_response_shape")):
            errors.append(f"{prefix} expected_response_shape is required")
        if not _nonempty(action.get("source_layer")):
            errors.append(f"{prefix} source_layer is required")

        evidence = action.get("teaching_evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{prefix} teaching_evidence must be an object")
        else:
            if str(evidence.get("status", "")).lower() != "demonstrated":
                errors.append(f"{prefix} teaching evidence status must be demonstrated")
            for field in [
                "explanation_locator",
                "explanation_summary",
                "worked_example_locator",
                "worked_example_summary",
            ]:
                if not _nonempty(evidence.get(field)):
                    errors.append(f"{prefix} teaching_evidence.{field} is required")

        rubric = action.get("rubric")
        if not isinstance(rubric, dict):
            errors.append(f"{prefix} rubric must be an object")
        else:
            if not _nonempty(rubric.get("criterion")):
                errors.append(f"{prefix} rubric.criterion is required")
            if rubric.get("explicit_in_prompt") is not True:
                errors.append(f"{prefix} rubric must be explicit in the prompt")
            if rubric.get("requires_untaught_inference") is not False:
                errors.append(
                    f"{prefix} rubric requires_untaught_inference must be false"
                )

    audits = data.get("audits")
    if not isinstance(audits, dict):
        errors.append("audits must be an object")
    else:
        missing_audits = REQUIRED_AUDITS - audits.keys()
        if missing_audits:
            errors.append("missing audits: " + ", ".join(sorted(missing_audits)))
        for name in REQUIRED_AUDITS & audits.keys():
            value = audits[name]
            if _audit_result(value) != "pass":
                errors.append(f"audit {name} must be pass")
            if isinstance(value, dict) and not _nonempty(value.get("evidence")):
                errors.append(f"audit {name} requires independent evidence")

    return errors


def validate_contract_file(
    path: Path, require_ready: bool = True
) -> tuple[dict[str, Any], list[str]]:
    try:
        data = load_contract(path)
    except ValueError as error:
        return {}, [str(error)]
    return data, validate_contract(data, require_ready=require_ready)


def validate_blueprint_binding(
    data: dict[str, Any], blueprint_path: Path, progress: str = ""
) -> list[str]:
    """Verify that an internally valid contract is authorized by the blueprint."""
    from validate_teaching_blueprint import get_point_binding, validate_blueprint

    blueprint_errors = validate_blueprint(blueprint_path, progress)
    if blueprint_errors:
        return [f"blueprint: {error}" for error in blueprint_errors]

    point_id = str(data.get("point_id", "")).strip()
    binding = get_point_binding(blueprint_path, point_id)
    if binding is None:
        return [f"blueprint has no point with Point ID {point_id!r}"]

    errors: list[str] = []
    declared_blueprint_hash = str(data.get("blueprint_sha256", "")).strip()
    if declared_blueprint_hash:
        actual_blueprint_hash = hashlib.sha256(blueprint_path.read_bytes()).hexdigest()
        if declared_blueprint_hash != actual_blueprint_hash:
            errors.append(
                "blueprint SHA256 differs from the contract's promoted blueprint"
            )
    blueprint_fingerprint = str(binding["source_fingerprint"]).strip()
    contract_fingerprint = str(data.get("source_fingerprint", "")).strip()
    if blueprint_fingerprint != contract_fingerprint:
        errors.append(
            "source fingerprint differs between blueprint and contract: "
            f"{blueprint_fingerprint!r} != {contract_fingerprint!r}"
        )

    eligible = dict(binding["eligible_relationships"])
    explanation_mapping = dict(binding["explanation_mapping"])
    demonstration_mapping = dict(binding["demonstration_mapping"])
    planned = dict(binding["action_mapping"])
    for action in data.get("actions", []):
        if not isinstance(action, dict):
            continue
        action_id = str(action.get("id", ""))
        relation_id = str(action.get("relation_id", ""))
        if relation_id not in eligible:
            errors.append(
                f"{action_id} uses {relation_id}, which is not eligible in blueprint point {point_id}"
            )
        if relation_id not in demonstration_mapping:
            errors.append(
                f"{action_id} uses {relation_id}, which lacks blueprint demonstration evidence"
            )
        canonical_relationship = eligible.get(relation_id, "")
        if canonical_relationship and _canonical(action.get("tested_relationship", "")) != _canonical(
            canonical_relationship
        ):
            errors.append(
                f"{action_id} tested_relationship does not match blueprint {relation_id} meaning"
            )
        evidence = action.get("teaching_evidence")
        if isinstance(evidence, dict):
            explanation_locator = explanation_mapping.get(relation_id, "")
            if explanation_locator and _canonical(
                evidence.get("explanation_locator", "")
            ) != _canonical(explanation_locator):
                errors.append(
                    f"{action_id} explanation locator does not match blueprint {relation_id} mapping"
                )
            demonstration_locator = demonstration_mapping.get(relation_id, "")
            if demonstration_locator and _canonical(
                evidence.get("worked_example_locator", "")
            ) != _canonical(demonstration_locator):
                errors.append(
                    f"{action_id} worked-example locator does not match blueprint {relation_id} mapping"
                )
        if data.get("exercise_kind") == "learning_post_point":
            planned_relation = planned.get(action_id)
            if planned_relation != relation_id:
                errors.append(
                    f"{action_id} -> {relation_id} does not match blueprint plan "
                    f"{action_id} -> {planned_relation or '<missing>'}"
                )
    return errors


def render_contract(data: dict[str, Any]) -> str:
    errors = validate_contract(data)
    if errors:
        raise ValueError("cannot render invalid exercise contract: " + "; ".join(errors))

    display = data["display"]
    actions = data["actions"]
    lines = [str(display["title"]).strip(), ""]
    scenario = str(data.get("scenario", "")).strip()
    if scenario:
        lines.extend([scenario, ""])
    lines.append(f"Atomic answer actions: {len(actions)}")
    lines.append("")
    for index, action in enumerate(actions, start=1):
        stimulus = str(action.get("stimulus", "")).strip()
        if stimulus:
            lines.extend([f"{index}. {stimulus}", ""])
            lines.append(f"   {str(action['prompt']).strip()}")
        else:
            lines.append(f"{index}. {str(action['prompt']).strip()}")
        lines.append("")
    lines.append(str(display["answer_instruction"]).strip())
    return "\n".join(lines).rstrip() + "\n"
