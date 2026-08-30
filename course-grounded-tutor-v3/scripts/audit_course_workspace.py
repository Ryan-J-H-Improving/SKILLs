#!/usr/bin/env python3
"""Audit course workspaces without modifying course or learner data."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

from exercise_contract import validate_blueprint_binding, validate_contract_file
from validate_teaching_blueprint import validate_blueprint
from workspace_common import (
    BLUEPRINT_VERSION,
    SKILL_VERSION,
    WORKSPACE_SCHEMA_VERSION,
    WORKSPACE_ROLE_CANONICAL,
    WORKSPACE_ROLE_REFERENCE_MIRROR,
    WORKSPACE_ROLES,
    file_sha256,
    yaml_scalar_paths,
)


STATE_START = "<!-- course-grounded-tutor:current-state:start -->"
MANAGED_STATE_FIELDS = [
    "Workspace schema version",
    "Point ID",
    "Blueprint status",
    "Blueprint SHA256",
]
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\n]+)\)")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
SAVED_FILE_RE = re.compile(r"(?im)^-?\s*(?:\*\*)?Saved (?:file|source crop)(?:\*\*)?:\s*`?([^`\n]+?)`?\s*$")
DELIVERY_RE = re.compile(r"(?im)^-?\s*(?:\*\*)?Delivery status(?:\*\*)?:\s*`?([a-z_]+)`?\s*$")
H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
H3_RE = re.compile(r"(?m)^###\s+(.+?)\s*$")
FIGURE_HEADING_RE = re.compile(r"(?m)^(#{2,3})\s+(.+?)\s*$")
EXPECTED_STUDY_SECTIONS = {
    "contents": {"contents", "目录"},
    "knowledge_points": {"knowledge points", "知识点", "知识点内容"},
    "mistake_review": {"mistake review", "错题整理", "错题回顾"},
}
OPTIONAL_STUDY_SECTIONS = {"restart status", "migration status", "迁移状态"}
FIGURE_DELIVERY_STATUSES = {"embedded", "pending_insertion", "reference_only", "archived"}


def issue(code: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _short_list(values: list[str], limit: int = 5) -> str:
    shown = values[:limit]
    suffix = f"; +{len(values) - limit} more" if len(values) > limit else ""
    return "; ".join(shown) + suffix


def _markdown_target(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1:value.index(">")]
    elif " " in value:
        value = value.split(None, 1)[0]
    return unquote(value.strip().strip('"\''))


def _figure_key(raw: str, markdown: bool = True) -> str:
    value = (
        _markdown_target(raw)
        if markdown
        else unquote(raw.strip().strip('`"\''))
    )
    value = value.replace("\\", "/").rstrip("/")
    return value.rsplit("/", 1)[-1].casefold()


def _broken_markdown_images(note_path: Path, links: list[str]) -> list[str]:
    broken: list[str] = []
    for raw in links:
        target = _markdown_target(raw)
        if not target or re.match(r"^[a-z][a-z0-9+.-]*://", target, re.I):
            continue
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = note_path.parent / candidate
        if not candidate.is_file():
            broken.append(target)
    return sorted(set(broken), key=str.casefold)


def _linked_study_surfaces(
    course_dir: Path,
    study_path: Path,
    study_text: str,
) -> tuple[list[Path], list[str], list[str]]:
    """Resolve explicitly linked learner-note Markdown files inside the project."""
    project_root = course_dir.parents[2].resolve()
    linked: list[Path] = []
    missing: list[str] = []
    outside_project: list[str] = []
    seen: set[Path] = set()
    for raw in MARKDOWN_LINK_RE.findall(study_text):
        target = _markdown_target(raw)
        if not target or re.match(r"^[a-z][a-z0-9+.-]*://", target, re.I):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target or Path(target).suffix.casefold() != ".md":
            continue
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = study_path.parent / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(project_root)
        except ValueError:
            outside_project.append(target)
            continue
        if not resolved.is_file():
            missing.append(target)
            continue
        if resolved != study_path.resolve() and resolved not in seen:
            seen.add(resolved)
            linked.append(resolved)
    return linked, sorted(set(missing), key=str.casefold), sorted(set(outside_project), key=str.casefold)


def _formula_count(text: str) -> int:
    bracketed = [
        block for block in re.findall(r"(?s)\\\[(.*?)\\\]", text) if block.strip()
    ]
    dollars = [
        block for block in re.findall(r"(?s)\$\$(.*?)\$\$", text) if block.strip()
    ]
    return len(bracketed) + len(dollars)


def _figure_registry(text: str) -> list[dict[str, str]]:
    headings = list(FIGURE_HEADING_RE.finditer(text))
    records: list[dict[str, str]] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        block = text[heading.end():end]
        image_match = IMAGE_RE.search(block)
        saved_match = SAVED_FILE_RE.search(block)
        raw_path = image_match.group(1) if image_match else saved_match.group(1) if saved_match else ""
        if not raw_path:
            continue
        delivery_match = DELIVERY_RE.search(block)
        records.append(
            {
                "title": heading.group(2).strip(),
                "path": raw_path.strip(),
                "key": _figure_key(raw_path, markdown=bool(image_match)),
                "delivery_status": delivery_match.group(1).casefold() if delivery_match else "",
                "link_kind": "markdown" if image_match else "saved_file",
            }
        )
    return records


def audit_notes(course_dir: Path, issues: list[dict[str, str]]) -> dict[str, object]:
    issue_start = len(issues)
    notes_dir = course_dir / "notes"
    study_path = notes_dir / "study-notes.md"
    figure_path = notes_dir / "figure-notes.md"
    exam_path = notes_dir / "exam-review-notes.md"
    course_map_path = notes_dir / "course-map.md"

    study_text = study_path.read_text(encoding="utf-8", errors="replace") if study_path.is_file() else ""
    figure_text = figure_path.read_text(encoding="utf-8", errors="replace") if figure_path.is_file() else ""
    exam_text = exam_path.read_text(encoding="utf-8", errors="replace") if exam_path.is_file() else ""

    for name, path in [
        ("study-notes.md", study_path),
        ("figure-notes.md", figure_path),
        ("exam-review-notes.md", exam_path),
        ("course-map.md", course_map_path),
    ]:
        if not path.is_file():
            issues.append(issue("note_file_missing", f"notes/{name} is missing", severity="warning"))

    linked_surfaces, missing_surfaces, outside_surfaces = _linked_study_surfaces(
        course_dir,
        study_path,
        study_text,
    ) if study_path.is_file() else ([], [], [])
    if missing_surfaces:
        issues.append(
            issue(
                "study_note_surface_link_broken",
                "linked learner-note files do not resolve: " + _short_list(missing_surfaces),
                severity="warning",
            )
        )
    if outside_surfaces:
        issues.append(
            issue(
                "study_note_surface_outside_project",
                "linked learner-note files are outside the course project and were not audited: "
                + _short_list(outside_surfaces),
                severity="warning",
            )
        )
    study_surfaces = [(study_path, study_text)]
    study_surfaces.extend(
        (path, path.read_text(encoding="utf-8", errors="replace"))
        for path in linked_surfaces
    )
    combined_study_text = "\n".join(text for _, text in study_surfaces)

    h2_headings = [heading.strip() for heading in H2_RE.findall(study_text)]
    normalized_h2 = [heading.casefold() for heading in h2_headings]
    missing_sections = [
        name
        for name, aliases in EXPECTED_STUDY_SECTIONS.items()
        if not any(heading in aliases for heading in normalized_h2)
    ]
    expected_aliases = set().union(*EXPECTED_STUDY_SECTIONS.values())
    unexpected_sections = [
        heading
        for heading in h2_headings
        if heading.casefold() not in expected_aliases
        and heading.casefold() not in OPTIONAL_STUDY_SECTIONS
    ]
    if missing_sections:
        issues.append(
            issue(
                "study_note_required_sections_missing",
                "study notes are missing required top-level sections: " + ", ".join(missing_sections),
                severity="warning",
            )
        )
    if unexpected_sections:
        issues.append(
            issue(
                "study_note_structure_drift",
                "unexpected study-note top-level sections: " + _short_list(unexpected_sections),
                severity="warning",
            )
        )

    study_formula_count = _formula_count(combined_study_text)
    exam_formula_count = _formula_count(exam_text)
    substantive_exam_h3 = [heading for heading in H3_RE.findall(exam_text) if "<" not in heading and ">" not in heading]
    exam_template_only = exam_path.is_file() and not substantive_exam_h3 and exam_formula_count == 0
    if exam_template_only:
        issues.append(
            issue(
                "exam_review_notes_template_only",
                "exam-review-notes.md still contains no substantive topic, formula, pattern, or mistake entry",
                severity="warning",
            )
        )
    if study_formula_count > 0 and exam_formula_count == 0:
        issues.append(
            issue(
                "exam_formula_inventory_missing",
                f"study notes contain {study_formula_count} display-math blocks but exam review notes contain no formula inventory",
                severity="warning",
            )
        )

    surface_links = [
        (path, IMAGE_RE.findall(text))
        for path, text in study_surfaces
    ]
    study_links = [raw for _, links in surface_links for raw in links]
    registry_records = _figure_registry(figure_text)
    study_by_key = {_figure_key(raw): raw for raw in study_links if _figure_key(raw)}
    registry_by_key = {record["key"]: record for record in registry_records if record["key"]}
    unregistered = sorted(set(study_by_key) - set(registry_by_key))
    registered_not_embedded = sorted(set(registry_by_key) - set(study_by_key))
    delivery_unknown = [
        key for key in registered_not_embedded if not registry_by_key[key]["delivery_status"]
    ]
    declared_embedded_missing = [
        key
        for key in registered_not_embedded
        if registry_by_key[key]["delivery_status"] == "embedded"
    ]
    pending_insertion = [
        key
        for key in registered_not_embedded
        if registry_by_key[key]["delivery_status"] == "pending_insertion"
    ]
    invalid_delivery = sorted(
        {
            record["delivery_status"]
            for record in registry_records
            if record["delivery_status"]
            and record["delivery_status"] not in FIGURE_DELIVERY_STATUSES
        }
    )
    preview_missing = sorted(
        record["key"] for record in registry_records if record["link_kind"] == "saved_file"
    )
    if unregistered:
        issues.append(
            issue(
                "study_figure_unregistered",
                f"{len(unregistered)} study-note figures are absent from figure-notes: {_short_list(unregistered)}",
                severity="warning",
            )
        )
    if delivery_unknown:
        issues.append(
            issue(
                "registered_figure_delivery_unknown",
                f"{len(delivery_unknown)} registered figures are not embedded and have no delivery status: {_short_list(delivery_unknown)}",
                severity="warning",
            )
        )
    if declared_embedded_missing:
        issues.append(
            issue(
                "registered_figure_delivery_mismatch",
                f"{len(declared_embedded_missing)} figures declare embedded but are absent from study notes: {_short_list(declared_embedded_missing)}",
                severity="warning",
            )
        )
    if pending_insertion:
        issues.append(
            issue(
                "registered_figure_pending_insertion",
                f"{len(pending_insertion)} validated figures are still pending insertion: {_short_list(pending_insertion)}",
                severity="warning",
            )
        )
    if invalid_delivery:
        issues.append(
            issue(
                "figure_delivery_status_invalid",
                "unknown figure delivery statuses: " + ", ".join(invalid_delivery),
                severity="warning",
            )
        )
    if preview_missing:
        issues.append(
            issue(
                "figure_registry_preview_missing",
                f"{len(preview_missing)} figure-register entries name a saved file but do not embed a preview: {_short_list(preview_missing)}",
                severity="warning",
            )
        )

    project_root = course_dir.parents[2].resolve()
    broken_study_links: list[str] = []
    for surface_path, links in surface_links:
        try:
            surface_label = surface_path.resolve().relative_to(project_root).as_posix()
        except ValueError:
            surface_label = surface_path.name
        broken_study_links.extend(
            f"{surface_label} -> {target}"
            for target in _broken_markdown_images(surface_path, links)
        )
    broken_study_links = sorted(set(broken_study_links), key=str.casefold)
    figure_markdown_links = [
        record["path"] for record in registry_records if record["link_kind"] == "markdown"
    ]
    broken_registry_links = _broken_markdown_images(figure_path, figure_markdown_links) if figure_path.is_file() else []
    if broken_study_links:
        issues.append(
            issue(
                "study_figure_link_broken",
                f"{len(broken_study_links)} embedded study-note image links do not resolve: {_short_list(broken_study_links)}",
                severity="warning",
            )
        )
    if broken_registry_links:
        issues.append(
            issue(
                "figure_registry_link_broken",
                f"{len(broken_registry_links)} figure-register image links do not resolve: {_short_list(broken_registry_links)}",
                severity="warning",
            )
        )

    warning_count = len(re.findall(r"(?i)<u>\s*personal warning:\s*</u>", combined_study_text))
    warning_status_count = len(
        re.findall(
            r"(?im)^(?:-\s*)?(?:\*\*)?(?:warning status|personal warning status|警告状态)(?:\*\*)?\s*:",
            combined_study_text,
        )
    )
    if warning_count > warning_status_count:
        issues.append(
            issue(
                "personal_warning_status_missing",
                f"{warning_count} personal warnings exist but only {warning_status_count} warning lifecycle statuses are recorded",
                severity="warning",
            )
        )

    map_files = sorted(
        [path for path in notes_dir.glob("*.md") if "course-map" in path.name.casefold()],
        key=lambda path: path.name.casefold(),
    ) if notes_dir.is_dir() else []
    companion_maps = [path for path in map_files if path.name.casefold() != "course-map.md"]
    undeclared_companions: list[str] = []
    for path in companion_maps:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"(?im)^(?:-\s*)?(?:derived from|canonical course map|canonical):.*course-map\.md", text):
            undeclared_companions.append(path.name)
    if undeclared_companions:
        issues.append(
            issue(
                "course_map_authority_ambiguous",
                "course-map companion files do not declare derivation from notes/course-map.md: " + _short_list(undeclared_companions),
                severity="warning",
            )
        )

    evidence_paths = [
        course_dir / "memory" / "session-log.md",
        course_dir / "memory" / "practice-history.md",
    ]
    activity_paths = [path for path in evidence_paths if path.is_file()]
    if not activity_paths:
        activity_paths = [course_dir / "memory" / "learning-state.md"]
    latest_activity = max(
        (path.stat().st_mtime for path in activity_paths if path.is_file()),
        default=study_path.stat().st_mtime if study_path.is_file() else 0,
    )
    latest_note_update = max(
        (path.stat().st_mtime for path, _ in study_surfaces if path.is_file()),
        default=0,
    )
    lag_hours = max(0.0, (latest_activity - latest_note_update) / 3600) if latest_note_update else 0.0
    if lag_hours >= 48:
        issues.append(
            issue(
                "study_notes_lagging",
                f"study notes are approximately {lag_hours / 24:.1f} days behind the newest session or practice activity",
                severity="warning",
            )
        )

    return {
        "audited": True,
        "warning_count": len(issues) - issue_start,
        "study_notes": {
            "surface_count": len(study_surfaces),
            "linked_surfaces": [
                path.relative_to(project_root).as_posix() for path in linked_surfaces
            ],
            "missing_linked_surfaces": missing_surfaces,
            "outside_project_surfaces": outside_surfaces,
            "top_level_sections": h2_headings,
            "missing_required_sections": missing_sections,
            "unexpected_top_level_sections": unexpected_sections,
            "formula_count": study_formula_count,
            "personal_warning_count": warning_count,
            "warning_status_count": warning_status_count,
            "lag_hours": round(lag_hours, 1),
        },
        "exam_review_notes": {
            "template_only": exam_template_only,
            "formula_count": exam_formula_count,
        },
        "figures": {
            "study_embedded_count": len(study_by_key),
            "registry_count": len(registry_by_key),
            "study_unregistered": unregistered,
            "registered_not_embedded": registered_not_embedded,
            "delivery_unknown": delivery_unknown,
            "declared_embedded_missing": declared_embedded_missing,
            "pending_insertion": pending_insertion,
            "broken_study_links": broken_study_links,
            "broken_registry_links": broken_registry_links,
            "registry_preview_missing": preview_missing,
        },
        "course_map": {
            "files": [path.name for path in map_files],
            "companion_count": len(companion_maps),
            "undeclared_companions": undeclared_companions,
        },
    }


def audit_course(course_dir: Path) -> dict[str, object]:
    issues: list[dict[str, str]] = []
    course_yml = course_dir / "course.yml"
    metadata: dict[str, str] = {}
    schema_version = 0
    workspace_role = WORKSPACE_ROLE_CANONICAL
    if not course_yml.is_file():
        issues.append(issue("course_yml_missing", "course.yml is missing"))
    else:
        metadata = yaml_scalar_paths(course_yml)
        workspace_role = metadata.get("workspace_role", WORKSPACE_ROLE_CANONICAL)
        if workspace_role not in WORKSPACE_ROLES:
            issues.append(
                issue(
                    "workspace_role_invalid",
                    f"workspace_role must be one of {sorted(WORKSPACE_ROLES)}; found {workspace_role!r}",
                )
            )
        raw_schema = metadata.get("workspace_schema_version", "0")
        try:
            schema_version = int(raw_schema)
        except ValueError:
            issues.append(
                issue(
                    "workspace_schema_invalid",
                    f"workspace_schema_version must be an integer; found {raw_schema!r}",
                )
            )
        if schema_version != WORKSPACE_SCHEMA_VERSION:
            issues.append(
                issue(
                    "workspace_migration_required",
                    f"workspace schema {schema_version} must migrate to {WORKSPACE_SCHEMA_VERSION}",
                )
            )
        migration_status = metadata.get("workspace_migration_status", "")
        if schema_version == WORKSPACE_SCHEMA_VERSION:
            if migration_status in {"pending_reconciliation", "draft"}:
                issues.append(
                    issue(
                        "workspace_reconciliation_required",
                        f"workspace migration status is {migration_status}",
                    )
                )
            elif migration_status not in {"complete", "not_required"}:
                issues.append(
                    issue(
                        "workspace_migration_status_invalid",
                        "workspace_migration_status must be complete or not_required",
                    )
                )

    course_id = metadata.get("course.course_instance_id", "") or course_dir.name
    project_root = course_dir.parents[2].resolve()
    skill_markers = [
        project_root / "SKILL.md",
        project_root / "scripts" / "check_distributable.py",
        project_root / "agents" / "openai.yaml",
    ]
    if (
        workspace_role == WORKSPACE_ROLE_CANONICAL
        and skill_markers[0].is_file()
        and any(path.is_file() for path in skill_markers[1:])
    ):
        issues.append(
            issue(
                "canonical_workspace_inside_skill_distribution",
                f"canonical course workspace is inside distributable skill directory {project_root}; plan a separately reviewed move into the course project",
                severity="warning",
            )
        )
    if workspace_role == WORKSPACE_ROLE_REFERENCE_MIRROR:
        issues.append(
            issue(
                "reference_mirror_read_only",
                "this directory is a discovery/recovery mirror; formal teaching and durable state writes must use its canonical course directory",
                severity="warning",
            )
        )
        canonical_raw = metadata.get("canonical_course_dir", "").strip()
        canonical_blueprint_hash = ""
        canonical_blueprint_errors: list[str] = []
        if not canonical_raw:
            issues.append(
                issue(
                    "mirror_canonical_path_missing",
                    "reference_mirror requires canonical_course_dir",
                )
            )
        else:
            canonical_dir = Path(canonical_raw)
            if not canonical_dir.is_absolute():
                issues.append(
                    issue(
                        "mirror_canonical_path_relative",
                        "canonical_course_dir must be an absolute path",
                    )
                )
            elif canonical_dir.resolve() == course_dir.resolve():
                issues.append(
                    issue(
                        "mirror_canonical_path_self",
                        "reference_mirror cannot point to itself",
                    )
                )
            else:
                canonical_yml = canonical_dir / "course.yml"
                if not canonical_yml.is_file():
                    issues.append(
                        issue(
                            "mirror_canonical_missing",
                            f"canonical course.yml is unavailable at {canonical_yml}",
                        )
                    )
                else:
                    canonical_metadata = yaml_scalar_paths(canonical_yml)
                    canonical_role = canonical_metadata.get(
                        "workspace_role", WORKSPACE_ROLE_CANONICAL
                    )
                    if canonical_role != WORKSPACE_ROLE_CANONICAL:
                        issues.append(
                            issue(
                                "mirror_canonical_role_invalid",
                                "canonical_course_dir must point directly to a canonical workspace, not another mirror",
                            )
                        )
                    canonical_id = canonical_metadata.get(
                        "course.course_instance_id", ""
                    )
                    if canonical_id and canonical_id != course_id:
                        issues.append(
                            issue(
                                "mirror_course_id_mismatch",
                                f"mirror course ID {course_id!r} differs from canonical ID {canonical_id!r}",
                            )
                        )
                    canonical_audit = audit_course(canonical_dir)
                    if canonical_audit["status"] != "ready":
                        issues.append(
                            issue(
                                "mirror_canonical_not_ready",
                                "canonical_course_dir must point to a workspace that passes a full ready audit",
                            )
                        )
                    canonical_blueprint = (
                        canonical_dir / "indexes" / "teaching-blueprint.md"
                    )
                    if not canonical_blueprint.is_file():
                        issues.append(
                            issue(
                                "mirror_canonical_blueprint_missing",
                                "canonical teaching blueprint is missing",
                            )
                        )
                    else:
                        canonical_blueprint_errors = validate_blueprint(
                            canonical_blueprint
                        )
                        if canonical_blueprint_errors:
                            issues.append(
                                issue(
                                    "mirror_canonical_blueprint_invalid",
                                    f"canonical blueprint failed {len(canonical_blueprint_errors)} validation checks",
                                )
                            )
                        else:
                            canonical_blueprint_hash = file_sha256(
                                canonical_blueprint
                            )
                            recorded_blueprint_hash = metadata.get(
                                "mirror_canonical_blueprint_sha256", ""
                            )
                            if not recorded_blueprint_hash:
                                issues.append(
                                    issue(
                                        "mirror_sync_metadata_missing",
                                        "mirror_canonical_blueprint_sha256 is not recorded",
                                        severity="warning",
                                    )
                                )
                            elif recorded_blueprint_hash != canonical_blueprint_hash:
                                issues.append(
                                    issue(
                                        "mirror_blueprint_drift",
                                        "canonical blueprint changed after the mirror's recorded sync point",
                                        severity="warning",
                                    )
                                )
                    canonical_state = canonical_dir / "memory" / "learning-state.md"
                    if not canonical_state.is_file():
                        issues.append(
                            issue(
                                "mirror_canonical_state_missing",
                                "canonical learning state is missing",
                            )
                        )
                    else:
                        recorded_state_hash = metadata.get(
                            "mirror_canonical_learning_state_sha256", ""
                        )
                        actual_state_hash = file_sha256(canonical_state)
                        if not recorded_state_hash:
                            issues.append(
                                issue(
                                    "mirror_sync_metadata_missing",
                                    "mirror_canonical_learning_state_sha256 is not recorded",
                                    severity="warning",
                                )
                            )
                        elif recorded_state_hash != actual_state_hash:
                            issues.append(
                                issue(
                                    "mirror_learning_state_drift",
                                    "canonical learning state changed after the mirror's recorded sync point",
                                    severity="warning",
                                )
                            )
        has_error = any(item["severity"] == "error" for item in issues)
        return {
            "course_dir": str(course_dir),
            "course_id": course_id,
            "skill_version": SKILL_VERSION,
            "workspace_schema_version": schema_version,
            "workspace_role": workspace_role,
            "canonical_course_dir": canonical_raw,
            "status": "invalid" if has_error else "reference_mirror",
            "allowed_mode": "limited_clarification_only",
            "blueprint_sha256": canonical_blueprint_hash,
            "blueprint_errors": canonical_blueprint_errors,
            "contracts": [],
            "note_health": {
                "audited": False,
                "warning_count": 0,
                "reason": "reference mirrors do not own learner notes",
            },
            "issues": issues,
        }

    source_register = course_dir / "indexes" / "source-register.md"
    legacy_sources = course_dir / "indexes" / "sources.md"
    if not source_register.is_file():
        if legacy_sources.is_file():
            issues.append(
                issue(
                    "legacy_source_register",
                    "indexes/sources.md must be migrated to indexes/source-register.md",
                )
            )
        else:
            issues.append(issue("source_register_missing", "source register is missing"))

    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    blueprint_errors: list[str] = []
    blueprint_hash = ""
    if not blueprint.is_file():
        issues.append(
            issue(
                "blueprint_missing",
                "validated teaching blueprint is missing; build one before formal teaching",
            )
        )
    else:
        blueprint_errors = validate_blueprint(blueprint)
        if blueprint_errors:
            issues.append(
                issue(
                    "blueprint_invalid",
                    f"blueprint failed {len(blueprint_errors)} validation checks",
                )
            )
        else:
            blueprint_hash = file_sha256(blueprint)

    declared_version = metadata.get("teaching.blueprint.version", "")
    if declared_version and declared_version != BLUEPRINT_VERSION:
        issues.append(
            issue(
                "blueprint_version_mismatch",
                f"course.yml declares blueprint {declared_version}; expected {BLUEPRINT_VERSION}",
            )
        )
    declared_status = metadata.get("teaching.blueprint.status", "")
    if blueprint_hash and declared_status != "ready":
        issues.append(
            issue(
                "blueprint_status_mismatch",
                "course.yml must record teaching.blueprint.status as ready",
            )
        )
    if blueprint_hash:
        blueprint_text = blueprint.read_text(encoding="utf-8", errors="replace")
        blueprint_fields = {
            name.strip(): value.strip()
            for name, value in re.findall(
                r"(?m)^- ([^:\n]+):\s*(.*?)\s*$",
                blueprint_text.split("## Knowledge-Point Plan", 1)[0],
            )
        }
        declared_fingerprint = metadata.get(
            "teaching.blueprint.source_fingerprint", ""
        )
        actual_fingerprint = blueprint_fields.get("Source fingerprint", "")
        if declared_fingerprint != actual_fingerprint:
            issues.append(
                issue(
                    "blueprint_fingerprint_mismatch",
                    "course.yml source fingerprint differs from the promoted blueprint",
                )
            )

    state_path = course_dir / "memory" / "learning-state.md"
    if not state_path.is_file():
        issues.append(issue("learning_state_missing", "memory/learning-state.md is missing"))
    else:
        state_text = state_path.read_text(encoding="utf-8", errors="replace")
        if STATE_START not in state_text:
            issues.append(
                issue(
                    "legacy_learning_state",
                    "learning-state.md has no managed current-state block",
                )
            )
        else:
            for field in MANAGED_STATE_FIELDS:
                if not re.search(rf"(?m)^- {re.escape(field)}:", state_text):
                    issues.append(
                        issue(
                            "managed_state_field_missing",
                            f"managed learning state is missing field: {field}",
                        )
                    )
            state_schema_match = re.search(
                r"(?m)^- Workspace schema version:\s*(.*?)\s*$", state_text
            )
            if (
                state_schema_match
                and state_schema_match.group(1).strip() != str(schema_version)
            ):
                issues.append(
                    issue(
                        "state_schema_mismatch",
                        "learning state workspace schema differs from course.yml",
                    )
                )
            if blueprint_hash and f"- Blueprint SHA256: {blueprint_hash}" not in state_text:
                issues.append(
                    issue(
                        "state_blueprint_hash_stale",
                        "learning state does not record the current validated blueprint hash",
                    )
                )

    contract_dir = course_dir / "memory" / "exercise-contracts"
    contract_results: list[dict[str, object]] = []
    if not contract_dir.is_dir():
        issues.append(
            issue(
                "contract_directory_missing",
                "memory/exercise-contracts is missing",
            )
        )
    else:
        for contract in sorted(contract_dir.glob("*.json")):
            data, errors = validate_contract_file(contract)
            if not errors and blueprint.is_file():
                errors.extend(validate_blueprint_binding(data, blueprint))
            contract_results.append(
                {"path": str(contract), "valid": not errors, "errors": errors}
            )
            if errors:
                issues.append(
                    issue(
                        "contract_invalid",
                        f"{contract.name} failed {len(errors)} checks",
                    )
                )

    note_health = audit_notes(course_dir, issues)

    migration_codes = {
        "workspace_migration_required",
        "workspace_reconciliation_required",
        "workspace_migration_status_invalid",
        "legacy_source_register",
        "blueprint_missing",
        "blueprint_invalid",
        "blueprint_version_mismatch",
        "blueprint_status_mismatch",
        "blueprint_fingerprint_mismatch",
        "legacy_learning_state",
        "learning_state_missing",
        "managed_state_field_missing",
        "state_schema_mismatch",
        "state_blueprint_hash_stale",
        "contract_directory_missing",
    }
    has_migration_issue = any(item["code"] in migration_codes for item in issues)
    status = "migration_required" if has_migration_issue else "ready"
    if not has_migration_issue and any(item["severity"] == "error" for item in issues):
        status = "invalid"
    return {
        "course_dir": str(course_dir),
        "course_id": course_id,
        "skill_version": SKILL_VERSION,
        "workspace_schema_version": schema_version,
        "workspace_role": workspace_role,
        "canonical_course_dir": "",
        "status": status,
        "allowed_mode": (
            "formal_teaching" if status == "ready" else "limited_clarification_only"
        ),
        "blueprint_sha256": blueprint_hash,
        "blueprint_errors": blueprint_errors,
        "contracts": contract_results,
        "note_health": note_health,
        "issues": issues,
    }


def text_report(report: dict[str, object]) -> str:
    courses = report["courses"]
    lines = [
        f"Workspace audit: {report['workspace']}",
        f"Courses: {len(courses)}",
        f"Ready: {report['ready_count']}",
        f"Reference mirrors: {report['reference_mirror_count']}",
        f"Migration required: {report['migration_required_count']}",
        f"Duplicate canonical course IDs: {report['duplicate_canonical_count']}",
        f"Note warnings: {report['note_warning_count']}",
    ]
    for course in courses:
        lines.append(f"\n{course['course_id']}: {course['status']}")
        lines.append(f"- Allowed mode: {course['allowed_mode']}")
        note_health = course.get("note_health", {})
        if note_health.get("audited"):
            figures = note_health.get("figures", {})
            lines.append(
                f"- Note health: {note_health.get('warning_count', 0)} warnings; "
                f"{note_health.get('study_notes', {}).get('surface_count', 0)} study-note surfaces; "
                f"{figures.get('study_embedded_count', 0)} embedded figures; "
                f"{figures.get('registry_count', 0)} registered figures"
            )
        for item in course["issues"]:
            lines.append(f"- {item['severity'].upper()} {item['code']}: {item['message']}")
        for error in course["blueprint_errors"]:
            lines.append(f"  Blueprint: {error}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--workspace", type=Path, action="append")
    target.add_argument("--course-dir", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.course_dir:
        course_dirs = [args.course_dir]
        workspace_label = str(args.course_dir.parent.parent)
    else:
        unique_dirs: dict[str, Path] = {}
        for workspace in args.workspace:
            courses_root = workspace / "courses"
            for path in courses_root.glob("*"):
                if path.is_dir():
                    unique_dirs[str(path.resolve()).casefold()] = path
        course_dirs = sorted(unique_dirs.values(), key=lambda path: str(path).casefold())
        workspace_label = "; ".join(str(path) for path in args.workspace)
    courses = [audit_course(path) for path in course_dirs]
    canonical_by_id: dict[str, list[dict[str, object]]] = {}
    for course in courses:
        if course["workspace_role"] == WORKSPACE_ROLE_CANONICAL:
            canonical_by_id.setdefault(str(course["course_id"]), []).append(course)
    duplicate_groups = {
        course_id: group
        for course_id, group in canonical_by_id.items()
        if len(group) > 1
    }
    for course_id, group in duplicate_groups.items():
        locations = "; ".join(str(course["course_dir"]) for course in group)
        for course in group:
            course["issues"].append(
                issue(
                    "duplicate_canonical_across_workspaces",
                    f"course {course_id!r} has multiple canonical workspaces: {locations}",
                )
            )
            course["status"] = "invalid"
            course["allowed_mode"] = "limited_clarification_only"
    report = {
        "workspace": workspace_label,
        "skill_version": SKILL_VERSION,
        "workspace_schema_version": WORKSPACE_SCHEMA_VERSION,
        "courses": courses,
        "ready_count": sum(course["status"] == "ready" for course in courses),
        "reference_mirror_count": sum(
            course["status"] == "reference_mirror" for course in courses
        ),
        "migration_required_count": sum(
            course["status"] == "migration_required" for course in courses
        ),
        "invalid_count": sum(course["status"] == "invalid" for course in courses),
        "duplicate_canonical_count": len(duplicate_groups),
        "note_warning_count": sum(
            int(course.get("note_health", {}).get("warning_count", 0))
            for course in courses
        ),
    }
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(text_report(report), end="")
    accepted_statuses = {"ready", "reference_mirror"}
    return 0 if all(course["status"] in accepted_statuses for course in courses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
