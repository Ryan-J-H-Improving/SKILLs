from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from importlib.util import find_spec
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from extract_pdf_figures import output_name, parse_pages, parse_rect  # noqa: E402
from exercise_contract import (  # noqa: E402
    render_contract,
    validate_blueprint_binding,
    validate_contract,
)
from validate_teaching_blueprint import validate_blueprint  # noqa: E402
from workspace_common import file_sha256, set_yaml_scalar, yaml_scalar_paths  # noqa: E402


def valid_blueprint(total: int = 1) -> str:
    points: list[str] = []
    for number in range(1, total + 1):
        points.append(
            f"""### Point {number}/{total}: Stable point {number}

- Point ID: week-02-point-{number:02d}
- Previous dependency: prior point or course entry
- Why now: resolves the next course question
- Course question: how this method works
- Slides/document evidence: W03-SLIDES pp. 2-3
- Transcript status: available
- Transcript evidence: SPEAKER 0, slides 2-3, anchor "next we compare"
- Teacher transition: the earlier limitation motivates this method
- Teacher sequence: problem, definition, demonstration, limitation
- Source layers: course core; no enrichment
- New terms: estimator defined before use
- Formula construction: objects, fixed roles, subtraction, scaling, final notation
- Visual decision: none required because no visual reasoning is tested
- Worked example: complete new numerical example
- Eligible relationships: R1 = relationship 1; R2 = relationship 2; R3 = relationship 3
- Explanation mapping: R1 = study-notes.md point {number} R1; R2 = study-notes.md point {number} R2; R3 = study-notes.md point {number} R3
- Demonstration mapping: R1 = study-notes.md point {number} example R1; R2 = study-notes.md point {number} example R2; R3 = study-notes.md point {number} example R3
- Exercise coverage: A1 -> R1; A2 -> R2; A3 -> R3
- Question-rubric boundary: R1, R2, and R3 each have one explicit prompt and one matching taught criterion
- Difficulty: new context requiring reasoning rather than copied substitution
- Automatic-advance evidence: all three relationships answered correctly
- Load risk: one new term and one operation only
"""
        )
    return f"""# Teaching Blueprint: Example

- Blueprint version: 3.1
- Blueprint status: ready
- Source fingerprint: abc123
- Available scope: Week 3 supplied materials
- Total knowledge points: {total}
- Last validated: 2026-08-26T10:00:00+10:00

## Whole-Scope Narrative

The lesson moves from the problem to the method.

## Order Audit

Dependencies and source transitions were checked.

## Knowledge-Point Plan

{''.join(points)}
## Three-Pass Validation

- Source fidelity: pass
- Dependency and order: pass
- Novice and assessment: pass

## Change Log
"""


def valid_contract(
    point_id: str = "week-02-point-02",
    exercise_set_id: str = "point-2-set-1",
    source_fingerprint: str = "abc123",
) -> dict[str, object]:
    actions: list[dict[str, object]] = []
    prompts = [
        ("classify", "Classify the source interface."),
        ("explain", "Explain the acquisition-to-transformation relationship."),
        ("select", "Select the appropriate storage order."),
    ]
    for index, (operation, prompt) in enumerate(prompts, start=1):
        actions.append(
            {
                "id": f"A{index}",
                "relation_id": f"R{index}",
                "operation": operation,
                "stimulus": "A new course-grounded scenario.",
                "prompt": prompt,
                "tested_relationship": f"relationship {index}",
                "expected_response_shape": "one response slot",
                "source_layer": "course_core",
                "teaching_evidence": {
                    "status": "demonstrated",
                    "explanation_locator": f"study-notes.md point 2 R{index}",
                    "explanation_summary": f"relationship {index} was explicitly explained",
                    "worked_example_locator": f"study-notes.md point 2 example R{index}",
                    "worked_example_summary": "the same operation was demonstrated in another context",
                },
                "rubric": {
                    "criterion": f"one explicit criterion for relationship {index}",
                    "explicit_in_prompt": True,
                    "requires_untaught_inference": False,
                },
            }
        )
    return {
        "contract_version": 1,
        "status": "ready",
        "exercise_kind": "learning_post_point",
        "course_id": "example-course-2026-s2",
        "lesson_id": "week-02",
        "point_id": point_id,
        "exercise_set_id": exercise_set_id,
        "source_fingerprint": source_fingerprint,
        "display": {
            "title": "Knowledge-point exercise",
            "answer_instruction": "Answer actions 1-3 in order.",
        },
        "scenario": "A learner must apply the completed point in a new context.",
        "actions": actions,
        "audits": {
            "teaching_evidence": {
                "result": "pass",
                "evidence": "Each relation was checked against the visible explanation and example.",
            },
            "atomicity_and_load": {
                "result": "pass",
                "evidence": "Three prompts each contain one response request.",
            },
            "question_rubric_symmetry": {
                "result": "pass",
                "evidence": "Each prompt has one explicit criterion and no hidden requirement.",
            },
        },
    }


def write_contract(
    course_dir: Path,
    point_id: str = "week-02-point-02",
    exercise_set_id: str = "point-2-set-1",
    source_fingerprint: str = "abc123",
) -> Path:
    path = course_dir / "memory" / "exercise-contracts" / f"{exercise_set_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            valid_contract(point_id, exercise_set_id, source_fingerprint),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def write_blueprint(course_dir: Path, total: int = 8) -> Path:
    course_dir.mkdir(parents=True, exist_ok=True)
    course_text = (SKILL_ROOT / "assets" / "course.yml.template").read_text(
        encoding="utf-8"
    )
    course_text = course_text.replace('status: "draft"', 'status: "ready"', 1)
    course_text = course_text.replace(
        'source_fingerprint: ""', 'source_fingerprint: "abc123"', 1
    )
    (course_dir / "course.yml").write_text(
        course_text,
        encoding="utf-8",
    )
    path = course_dir / "indexes" / "teaching-blueprint.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(valid_blueprint(total), encoding="utf-8")
    return path


def legacy_sources_text() -> str:
    return """# Source Index

## Week 01 - Lecture slides

- Type: Current-term lecture slides
- Term: Semester 2, 2026
- Original path: `S:/Course/Week01.pdf`
- Workspace copy: `../sources/slides/Week01.pdf`
- SHA-256: `ABC123`
- Identification confidence: High
- Coverage: Definitions and worked examples

## Week 01 - Transcript

- Type: Current-term lecture transcript
- Original path: `S:/Course/Week01-transcript.txt`
- Workspace copy: `../sources/transcripts/Week01-transcript.txt`
- SHA-256: `DEF456`
- Identification confidence: High
- Emphasis captured: Teacher transitions and warnings
"""


def legacy_learning_state(managed: bool = False) -> str:
    old_block = """<!-- course-grounded-tutor:current-state:start -->
## Old Current Snapshot

- Lesson progress: 3/9 taught
- Current topic: legacy cluster
- Mastered concepts: legacy claim without a V3.1 contract
<!-- course-grounded-tutor:current-state:end -->
"""
    block = old_block + "\n" if managed else ""
    return f"""# Learning State: Legacy Course

{block}## Course Contract

- Reply language: Chinese, locked

## Current Position

- Last topic: Legacy cluster A
- Next recommended topic: Legacy cluster B

## Covered Concepts

| Concept | Status | Notes |
| --- | --- | --- |
| Historical concept | mastered | Preserve this claim as history, but do not promote it. |

## User Custom Section

This sentence must survive migration exactly.
"""


def write_legacy_workspace(root: Path, managed_state: bool = False) -> Path:
    course_dir = root / "courses" / "legacy-format-course"
    (course_dir / "indexes").mkdir(parents=True)
    (course_dir / "memory").mkdir(parents=True)
    (course_dir / "course.yml").write_text(
        """course:
  course_instance_id: "legacy-format-course"
  course_code: "TEST2000"
  course_title: "Legacy Format Course"
  term: "S2"
  year: "2026"
contracts:
  reply_language:
    value: "zh-CN"
    locked: true
teaching:
  teaching_profile: "conceptual"
  locked: true
status:
  current_mode: "learning"
""",
        encoding="utf-8",
    )
    (course_dir / "indexes" / "sources.md").write_text(
        legacy_sources_text(), encoding="utf-8"
    )
    (course_dir / "memory" / "learning-state.md").write_text(
        legacy_learning_state(managed_state), encoding="utf-8"
    )
    blueprint = course_dir / "indexes" / "teaching-blueprint.md"
    blueprint.write_text(valid_blueprint(2), encoding="utf-8")
    return course_dir


class ExtractPdfFiguresTests(unittest.TestCase):
    def test_parse_pages_deduplicates_and_expands_ranges(self) -> None:
        self.assertEqual(parse_pages("1,3-5,3"), [1, 3, 4, 5])

    def test_parse_pages_rejects_invalid_ranges(self) -> None:
        with self.assertRaises(ValueError):
            parse_pages("5-3")
        with self.assertRaises(ValueError):
            parse_pages("0")

    def test_parse_rect_rejects_inverted_coordinates(self) -> None:
        with self.assertRaises(ValueError):
            parse_rect("100,200,50,300")

    def test_crop_names_include_coordinates(self) -> None:
        name = output_name(Path("week02.pdf"), 10, [72.0, 120.5, 540.0, 620.0], "")
        self.assertEqual(name, "week02-p010-crop-72-120p5-540-620.png")


class WorkspaceBlueprintAndMemoryTests(unittest.TestCase):
    def run_script(
        self, script: str, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def make_ready_course(self, workspace: Path, course_id: str) -> Path:
        self.run_script(
            "init_course_workspace.py",
            "--workspace",
            str(workspace),
            "--course-id",
            course_id,
            "--confirm-no-known-canonical",
        )
        course_dir = workspace / "courses" / course_id
        blueprint = course_dir / "indexes" / "teaching-blueprint.md"
        blueprint.write_text(
            valid_blueprint(1).replace(
                "Blueprint status: ready", "Blueprint status: draft"
            ),
            encoding="utf-8",
        )
        self.run_script(
            "validate_teaching_blueprint.py",
            "--blueprint",
            str(blueprint),
            "--promote",
        )
        state_json = course_dir / "migration" / "ready-state.json"
        state_json.parent.mkdir(parents=True, exist_ok=True)
        state_json.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "course_dir": str(course_dir),
                    "mode": "learning",
                    "topic": "Stable point 1",
                    "lesson_progress": "1/1",
                    "point_id": "week-02-point-01",
                    "point_status": "teaching",
                    "source_fingerprint": "abc123",
                }
            ),
            encoding="utf-8",
        )
        self.run_script("update_learning_state.py", "--state-json", str(state_json))
        state_json.unlink()
        return course_dir

    def test_init_creates_blueprint_source_layout_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                "example-course-2026-s1",
                "--confirm-no-known-canonical",
            )
            course_dir = workspace / "courses" / "example-course-2026-s1"
            for relative in [
                "sources/slides",
                "sources/transcripts",
                "sources/exams",
                "sources/tutorials",
                "sources/assignments",
                "sources/readings",
                "sources/data",
                "memory/exercise-contracts",
            ]:
                self.assertTrue((course_dir / relative).is_dir())
            self.assertTrue((course_dir / "indexes" / "source-register.md").is_file())
            self.assertTrue((course_dir / "indexes" / "teaching-blueprint.md").is_file())
            self.assertIn(
                "example-course-2026-s1", (workspace / "index.md").read_text("utf-8")
            )

    def test_init_requires_a_cross_workspace_scope_or_explicit_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            blocked = self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                "scope-required-course",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("--confirm-no-known-canonical", blocked.stderr)
            self.assertFalse(
                (workspace / "courses" / "scope-required-course").exists()
            )

            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                "scope-required-course",
                "--confirm-no-known-canonical",
            )
            self.assertTrue(
                (workspace / "courses" / "scope-required-course" / "course.yml").is_file()
            )

    def test_init_rejects_a_known_canonical_even_with_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first" / ".ai-course-tutor"
            second = Path(temp_dir) / "second" / ".ai-course-tutor"
            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(first),
                "--course-id",
                "duplicate-course",
                "--confirm-no-known-canonical",
            )
            blocked = self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(second),
                "--course-id",
                "duplicate-course",
                "--known-workspace",
                str(first),
                "--force",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("canonical course already exists", blocked.stderr)
            self.assertIn(str(first / "courses" / "duplicate-course"), blocked.stderr)
            self.assertFalse((second / "courses" / "duplicate-course").exists())

    def test_multi_workspace_audit_rejects_duplicate_canonicals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first" / ".ai-course-tutor"
            second = Path(temp_dir) / "second" / ".ai-course-tutor"
            self.make_ready_course(first, "duplicate-ready-course")
            self.make_ready_course(second, "duplicate-ready-course")
            audit = self.run_script(
                "audit_course_workspace.py",
                "--workspace",
                str(first),
                "--workspace",
                str(second),
                "--format",
                "json",
                check=False,
            )
            self.assertNotEqual(audit.returncode, 0)
            report = json.loads(audit.stdout)
            self.assertEqual(report["duplicate_canonical_count"], 1)
            self.assertEqual(report["invalid_count"], 2)
            for course in report["courses"]:
                codes = {item["code"] for item in course["issues"]}
                self.assertIn("duplicate_canonical_across_workspaces", codes)

    def test_note_audit_reports_drift_without_blocking_teaching(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            course_dir = self.make_ready_course(workspace, "note-drift-course")
            notes = course_dir / "notes"
            figures = notes / "figures"
            figures.mkdir(parents=True, exist_ok=True)
            (figures / "study-only.png").write_bytes(b"study")
            (figures / "registry-only.png").write_bytes(b"registry")
            (notes / "study-notes.md").write_text(
                """# Study Notes

## Contents

## Knowledge Points

![Study-only figure](figures/study-only.png)

\\[
x = 1
\\]

<u>Personal warning:</u> Do not confuse the two cases.

## Extra Weekly Section

## Mistake Review
""",
                encoding="utf-8",
            )
            (notes / "figure-notes.md").write_text(
                """# Figure Notes

## Course Figures

### Registry only

![Registry-only figure](figures/registry-only.png)

### Broken registry link

![Missing figure](figures/missing.png)
""",
                encoding="utf-8",
            )
            (notes / "week02-course-map.md").write_text(
                "# Week 02 Map\n",
                encoding="utf-8",
            )
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            report = json.loads(audit.stdout)
            course = report["courses"][0]
            codes = {item["code"] for item in course["issues"]}
            self.assertEqual(course["status"], "ready")
            self.assertIn("study_note_structure_drift", codes)
            self.assertIn("exam_review_notes_template_only", codes)
            self.assertIn("exam_formula_inventory_missing", codes)
            self.assertIn("study_figure_unregistered", codes)
            self.assertIn("registered_figure_delivery_unknown", codes)
            self.assertIn("figure_registry_link_broken", codes)
            self.assertIn("personal_warning_status_missing", codes)
            self.assertIn("course_map_authority_ambiguous", codes)
            self.assertGreater(report["note_warning_count"], 0)
            self.assertEqual(
                course["note_health"]["figures"]["study_embedded_count"], 1
            )

    def test_note_audit_accepts_consistent_note_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            course_dir = self.make_ready_course(workspace, "healthy-note-course")
            notes = course_dir / "notes"
            figures = notes / "figures"
            figures.mkdir(parents=True, exist_ok=True)
            (figures / "model.png").write_bytes(b"image")
            (notes / "study-notes.md").write_text(
                """# Study Notes

## Contents

## Knowledge Points

![Model](figures/model.png)

\\[
y = x
\\]

<u>Personal warning:</u> Check the direction.
**Warning status:** monitor

## Mistake Review
""",
                encoding="utf-8",
            )
            (notes / "figure-notes.md").write_text(
                """# Figure Notes

## Course Figures

### Model

![Model](figures/model.png)

- Delivery status: embedded
""",
                encoding="utf-8",
            )
            (notes / "exam-review-notes.md").write_text(
                """# Exam Review Notes

## Contents

## High-Frequency Topics

## Formula Sheet

### Course identity

\\[
y = x
\\]

- Evidence status: course formula; exam frequency unknown

## Question Patterns

## Mistake Review
""",
                encoding="utf-8",
            )
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            report = json.loads(audit.stdout)
            course = report["courses"][0]
            self.assertEqual(course["status"], "ready")
            self.assertEqual(course["note_health"]["warning_count"], 0)
            self.assertEqual(report["note_warning_count"], 0)

    def test_note_audit_follows_linked_learner_note_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            course_dir = self.make_ready_course(workspace, "linked-note-course")
            notes = course_dir / "notes"
            figures = notes / "figures"
            figures.mkdir(parents=True, exist_ok=True)
            (figures / "central.png").write_bytes(b"central")
            week_dir = Path(temp_dir) / "week3"
            week_dir.mkdir()
            (week_dir / "linked.png").write_bytes(b"linked")
            linked_note = week_dir / "Week 03 Study Notes.md"
            linked_note.write_text(
                "# Week 03 Study Notes\n\n![Linked](linked.png)\n",
                encoding="utf-8",
            )
            (notes / "study-notes.md").write_text(
                """# Study Notes

## Contents

- [Week 03 detailed notes](../../../../week3/Week%2003%20Study%20Notes.md)

## Knowledge Points

![Central](figures/central.png)

## Mistake Review
""",
                encoding="utf-8",
            )
            (notes / "figure-notes.md").write_text(
                """# Figure Notes

## Course Figures

### Central

![Central](figures/central.png)

- Delivery status: embedded

### Linked

![Linked](../../../../week3/linked.png)

- Delivery status: embedded
""",
                encoding="utf-8",
            )
            (notes / "exam-review-notes.md").write_text(
                "# Exam Review Notes\n\n## Formula Sheet\n\n### Course concepts\n\nNo formulas required.\n",
                encoding="utf-8",
            )
            os.utime(notes / "study-notes.md", (100, 100))
            os.utime(course_dir / "memory" / "session-log.md", (200, 200))
            os.utime(course_dir / "memory" / "practice-history.md", (200, 200))
            os.utime(linked_note, (300, 300))
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            course = json.loads(audit.stdout)["courses"][0]
            codes = {item["code"] for item in course["issues"]}
            note_health = course["note_health"]
            self.assertNotIn("registered_figure_delivery_unknown", codes)
            self.assertNotIn("registered_figure_delivery_mismatch", codes)
            self.assertNotIn("study_figure_link_broken", codes)
            self.assertNotIn("study_notes_lagging", codes)
            self.assertEqual(note_health["study_notes"]["surface_count"], 2)
            self.assertEqual(note_health["figures"]["study_embedded_count"], 2)

    def test_note_audit_reports_invalid_linked_note_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "project" / ".ai-course-tutor"
            course_dir = self.make_ready_course(workspace, "broken-linked-note-course")
            notes = course_dir / "notes"
            (notes / "study-notes.md").write_text(
                """# Study Notes

## Contents

- [Missing](../../../../week9/missing.md)
- [Outside](../../../../../outside.md)

## Knowledge Points

## Mistake Review
""",
                encoding="utf-8",
            )
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            course = json.loads(audit.stdout)["courses"][0]
            codes = {item["code"] for item in course["issues"]}
            self.assertIn("study_note_surface_link_broken", codes)
            self.assertIn("study_note_surface_outside_project", codes)

    def test_canonical_inside_skill_distribution_warns_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "skill-package"
            workspace = project / ".ai-course-tutor"
            course_dir = self.make_ready_course(workspace, "misplaced-course")
            (project / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            scripts = project / "scripts"
            scripts.mkdir()
            (scripts / "check_distributable.py").write_text("", encoding="utf-8")
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            course = json.loads(audit.stdout)["courses"][0]
            codes = {item["code"] for item in course["issues"]}
            self.assertEqual(course["status"], "ready")
            self.assertIn("canonical_workspace_inside_skill_distribution", codes)

    def test_templates_share_workspace_and_blueprint_versions(self) -> None:
        course_template = SKILL_ROOT / "assets" / "course.yml.template"
        fields = yaml_scalar_paths(course_template)
        self.assertEqual(fields["workspace_schema_version"], "1")
        self.assertEqual(fields["workspace_migration_status"], "not_required")
        self.assertEqual(fields["workspace_role"], "canonical")
        self.assertEqual(fields["teaching.blueprint.version"], "3.1")
        contract_text = (SKILL_ROOT / "assets" / "exercise-contract.json.template").read_text(
            encoding="utf-8"
        )
        self.assertNotIn('"point_id": "<current/total>"', contract_text)
        self.assertIn("stable semantic blueprint Point ID", contract_text)

    def test_course_index_reads_nested_yaml_without_key_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            course_dir = workspace / "courses" / "nested-course"
            course_dir.mkdir(parents=True)
            (course_dir / "course.yml").write_text(
                """workspace_schema_version: 1
status:
  current_mode: learning
course:
  course_code: TEST1000
  course_title: Nested YAML
  year: 2026
  term: S2
teaching:
  teaching_profile: quantitative
  blueprint:
    status: ready
""",
                encoding="utf-8",
            )
            self.run_script("build_course_index.py", "--workspace", str(workspace))
            index = (workspace / "index.md").read_text(encoding="utf-8")
            self.assertIn("TEST1000 Nested YAML 2026 S2", index)
            self.assertIn("Blueprint status: ready", index)

    def test_reference_mirror_routes_to_canonical_and_blocks_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            canonical = self.make_ready_course(
                workspace, "example-course-2026-s2"
            )
            canonical_state = canonical / "memory" / "learning-state.md"
            canonical_blueprint = canonical / "indexes" / "teaching-blueprint.md"

            mirror = workspace / "courses" / "example-course-mirror"
            (mirror / "indexes").mkdir(parents=True)
            mirror_yml = f'''workspace_schema_version: 1
workspace_migration_status: "not_required"
workspace_role: "reference_mirror"
canonical_course_dir: "{canonical}"
mirror_last_synced_at: "2026-08-29T02:00:00+10:00"
mirror_canonical_blueprint_sha256: "{file_sha256(canonical_blueprint)}"
mirror_canonical_learning_state_sha256: "{file_sha256(canonical_state)}"
course:
  course_instance_id: "example-course-2026-s2"
  course_code: "TEST3000"
  course_title: "Mirror Routing"
  term: "S2"
  year: "2026"
teaching:
  teaching_profile: "conceptual"
  blueprint:
    version: "3.1"
    status: "ready"
'''
            (mirror / "course.yml").write_text(mirror_yml, encoding="utf-8")
            (mirror / "indexes" / "teaching-blueprint.md").write_text(
                valid_blueprint(1), encoding="utf-8"
            )

            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(mirror),
                "--format",
                "json",
            )
            course = json.loads(audit.stdout)["courses"][0]
            self.assertEqual(course["status"], "reference_mirror")
            self.assertEqual(course["allowed_mode"], "limited_clarification_only")
            self.assertEqual(course["canonical_course_dir"], str(canonical))

            self.run_script("build_course_index.py", "--workspace", str(workspace))
            index = (workspace / "index.md").read_text(encoding="utf-8")
            self.assertIn("Formal teaching: disabled in this mirror", index)
            self.assertIn(f"Path: `{canonical / 'course.yml'}`", index)

            state_blocked = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(mirror),
                "--topic",
                "must not write",
                check=False,
            )
            self.assertNotEqual(state_blocked.returncode, 0)
            self.assertIn("reference mirrors are read-only", state_blocked.stderr)

            blueprint_blocked = self.run_script(
                "validate_teaching_blueprint.py",
                "--blueprint",
                str(mirror / "indexes" / "teaching-blueprint.md"),
                "--promote",
                "--dry-run",
                check=False,
            )
            self.assertNotEqual(blueprint_blocked.returncode, 0)
            self.assertIn("reference mirrors are read-only", blueprint_blocked.stderr)

            contract = write_contract(
                mirror,
                point_id="week-02-point-01",
                exercise_set_id="mirror-set",
            )
            contract_data = json.loads(contract.read_text(encoding="utf-8"))
            contract_data["status"] = "draft"
            contract.write_text(
                json.dumps(contract_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            contract_blocked = self.run_script(
                "validate_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(mirror / "indexes" / "teaching-blueprint.md"),
                "--promote",
                "--dry-run",
                check=False,
            )
            self.assertNotEqual(contract_blocked.returncode, 0)
            self.assertIn("reference mirrors are read-only", contract_blocked.stderr)

            before = canonical_state.read_text(encoding="utf-8")
            clarification = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(mirror),
                "--topic",
                "one local definition",
                "--mode",
                "limited_clarification_only",
            )
            self.assertIn("no progress", clarification.stdout)
            self.assertEqual(canonical_state.read_text(encoding="utf-8"), before)

    def test_reference_mirror_reports_canonical_drift_without_becoming_writable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            canonical = self.make_ready_course(workspace, "drift-course")
            mirror = workspace / "courses" / "drift-mirror"
            mirror.mkdir(parents=True)
            (mirror / "course.yml").write_text(
                f'''workspace_schema_version: 1
workspace_migration_status: "not_required"
workspace_role: "reference_mirror"
canonical_course_dir: "{canonical}"
mirror_last_synced_at: "2026-08-29T02:00:00+10:00"
mirror_canonical_blueprint_sha256: "outdated-blueprint"
mirror_canonical_learning_state_sha256: "outdated-state"
course:
  course_instance_id: "drift-course"
''',
                encoding="utf-8",
            )
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(mirror),
                "--format",
                "json",
            )
            course = json.loads(audit.stdout)["courses"][0]
            self.assertEqual(course["status"], "reference_mirror")
            codes = {item["code"] for item in course["issues"]}
            self.assertIn("mirror_blueprint_drift", codes)
            self.assertIn("mirror_learning_state_drift", codes)

    def test_reference_mirror_rejects_a_canonical_workspace_that_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            canonical = workspace / "courses" / "incomplete-course"
            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                canonical.name,
                "--confirm-no-known-canonical",
            )
            mirror = workspace / "courses" / "incomplete-course-mirror"
            mirror.mkdir(parents=True)
            (mirror / "course.yml").write_text(
                f'''workspace_schema_version: 1
workspace_migration_status: "not_required"
workspace_role: "reference_mirror"
canonical_course_dir: "{canonical}"
course:
  course_instance_id: "incomplete-course"
''',
                encoding="utf-8",
            )
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(mirror),
                "--format",
                "json",
                check=False,
            )
            self.assertNotEqual(audit.returncode, 0)
            course = json.loads(audit.stdout)["courses"][0]
            self.assertEqual(course["status"], "invalid")
            codes = {item["code"] for item in course["issues"]}
            self.assertIn("mirror_canonical_not_ready", codes)

    def test_yaml_scalar_insertion_preserves_nested_paths(self) -> None:
        text = """course:
  course_code: TEST1000
teaching:
  teaching_profile: conceptual
status:
  current_mode: learning
"""
        text = set_yaml_scalar(text, "teaching.blueprint.version", '"3.1"')
        text = set_yaml_scalar(text, "teaching.blueprint.status", '"ready"')
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "course.yml"
            path.write_text(text, encoding="utf-8")
            fields = yaml_scalar_paths(path)
        self.assertEqual(fields["teaching.blueprint.version"], "3.1")
        self.assertEqual(fields["teaching.blueprint.status"], "ready")
        self.assertEqual(fields["status.current_mode"], "learning")

    def test_legacy_workspace_plan_and_draft_are_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = write_legacy_workspace(Path(temp_dir))
            originals = {
                relative: file_sha256(course_dir / relative)
                for relative in [
                    "course.yml",
                    "indexes/sources.md",
                    "memory/learning-state.md",
                ]
            }
            plan = self.run_script(
                "migrate_legacy_workspace.py",
                "plan",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            plan_data = json.loads(plan.stdout)
            self.assertEqual(
                plan_data["source_action"], "convert_sources_md_and_preserve_verbatim"
            )
            self.assertEqual(plan_data["learning_state"], "legacy_unmanaged")

            created = self.run_script(
                "migrate_legacy_workspace.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            self.assertFalse(json.loads(created.stdout)["valid"])
            for relative, digest in originals.items():
                self.assertEqual(file_sha256(course_dir / relative), digest)
            self.assertFalse((course_dir / "indexes" / "source-register.md").exists())
            draft_root = course_dir / "migration" / "v3.1.1-legacy"
            source_draft = (draft_root / "source-register.md.draft").read_text("utf-8")
            state_draft = (draft_root / "learning-state.md.draft").read_text("utf-8")
            self.assertIn("LEGACY-SRC-001", source_draft)
            self.assertIn(legacy_sources_text().strip(), source_draft)
            self.assertIn("This sentence must survive migration exactly.", state_draft)
            self.assertIn("<MIGRATION REQUIRED", state_draft)

    def test_legacy_workspace_dry_run_and_drift_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = write_legacy_workspace(Path(temp_dir))
            dry_run = self.run_script(
                "migrate_legacy_workspace.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--safe-point-id",
                "week-02-point-02",
                "--current-lesson",
                "Week 02",
                "--dry-run",
                "--format",
                "json",
                check=False,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
            self.assertTrue(json.loads(dry_run.stdout)["valid"])
            self.assertFalse((course_dir / "migration").exists())

            self.run_script(
                "migrate_legacy_workspace.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--safe-point-id",
                "week-02-point-02",
            )
            state = course_dir / "memory" / "learning-state.md"
            state.write_text(state.read_text("utf-8") + "\nExternal change.\n", encoding="utf-8")
            blocked = self.run_script(
                "migrate_legacy_workspace.py",
                "activate",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertTrue(
                any(
                    "original file changed" in error
                    for error in json.loads(blocked.stdout)["errors"]
                )
            )
            self.assertFalse((course_dir / "indexes" / "source-register.md").exists())

    def test_legacy_workspace_blocks_new_source_register_after_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = write_legacy_workspace(Path(temp_dir))
            self.run_script(
                "migrate_legacy_workspace.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--safe-point-id",
                "week-02-point-01",
            )
            target = course_dir / "indexes" / "source-register.md"
            target.write_text("# Independently created register\n", encoding="utf-8")
            blocked = self.run_script(
                "migrate_legacy_workspace.py",
                "activate",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertTrue(
                any(
                    "original existence changed" in error
                    for error in json.loads(blocked.stdout)["errors"]
                )
            )
            self.assertEqual(target.read_text("utf-8"), "# Independently created register\n")

    def test_pending_workspace_migration_blocks_formal_teaching(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "pending-course"
            write_blueprint(course_dir, total=1)
            course_yml = course_dir / "course.yml"
            course_yml.write_text(
                course_yml.read_text("utf-8").replace(
                    'workspace_migration_status: "not_required"',
                    'workspace_migration_status: "pending_reconciliation"',
                ),
                encoding="utf-8",
            )
            blocked = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "Stable point 1",
                "--lesson-progress",
                "1/1",
                "--point-id",
                "week-02-point-01",
                "--point-status",
                "teaching",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("reconciliation is incomplete", blocked.stderr)
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
                check=False,
            )
            self.assertEqual(
                json.loads(audit.stdout)["courses"][0]["status"],
                "migration_required",
            )

    def test_legacy_workspace_activation_preserves_history_without_promoting_mastery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = write_legacy_workspace(Path(temp_dir), managed_state=True)
            original_sources = file_sha256(course_dir / "indexes" / "sources.md")
            self.run_script(
                "migrate_legacy_workspace.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--safe-point-id",
                "week-02-point-02",
                "--current-lesson",
                "Week 02",
            )
            validated = self.run_script(
                "migrate_legacy_workspace.py",
                "validate-draft",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
                check=False,
            )
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertTrue(json.loads(validated.stdout)["valid"])
            self.run_script(
                "migrate_legacy_workspace.py",
                "activate",
                "--course-dir",
                str(course_dir),
            )
            self.assertEqual(file_sha256(course_dir / "indexes" / "sources.md"), original_sources)
            backup_roots = list(
                (course_dir / "migration" / "v3.1.1-legacy" / "backups").iterdir()
            )
            self.assertEqual(len(backup_roots), 1)
            self.assertTrue((backup_roots[0] / "indexes" / "sources.md").is_file())
            self.assertTrue((course_dir / "indexes" / "source-register.md").is_file())
            self.assertTrue((course_dir / "memory" / "exercise-contracts").is_dir())
            metadata = yaml_scalar_paths(course_dir / "course.yml")
            self.assertEqual(metadata["workspace_schema_version"], "1")
            self.assertEqual(metadata["workspace_migration_status"], "complete")
            self.assertEqual(metadata["workspace_role"], "canonical")
            self.assertEqual(metadata["canonical_course_dir"], "")
            state_text = (course_dir / "memory" / "learning-state.md").read_text("utf-8")
            managed_match = re.search(
                r"(?s)<!-- course-grounded-tutor:current-state:start -->.*?"
                r"<!-- course-grounded-tutor:current-state:end -->",
                state_text,
            )
            self.assertIsNotNone(managed_match)
            self.assertIn("Point status: not_started", managed_match.group(0))
            self.assertIn("Mastery evidence:", managed_match.group(0))
            self.assertNotIn("mastered", managed_match.group(0).casefold())
            self.assertIn("Historical concept | mastered", state_text)
            self.assertIn("legacy-course-grounded-tutor:current-state:start", state_text)
            self.assertIn("This sentence must survive migration exactly.", state_text)
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            self.assertEqual(json.loads(audit.stdout)["courses"][0]["status"], "ready")

    def test_blueprint_promote_is_dry_run_safe_and_updates_course_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "promotion-course"
            course_dir.mkdir(parents=True)
            (course_dir / "course.yml").write_text(
                (SKILL_ROOT / "assets" / "course.yml.template").read_text("utf-8"),
                encoding="utf-8",
            )
            blueprint = course_dir / "indexes" / "teaching-blueprint.md"
            blueprint.parent.mkdir(parents=True)
            draft = valid_blueprint(1).replace("Blueprint status: ready", "Blueprint status: draft")
            blueprint.write_text(draft, encoding="utf-8")

            dry_run = self.run_script(
                "validate_teaching_blueprint.py",
                "--blueprint",
                str(blueprint),
                "--promote",
                "--dry-run",
                "--report",
                "json",
            )
            dry_payload = json.loads(dry_run.stdout)
            self.assertTrue(dry_payload["valid"])
            self.assertEqual(dry_payload["sha256"], "")
            self.assertIn("Blueprint status: draft", blueprint.read_text("utf-8"))

            promoted = self.run_script(
                "validate_teaching_blueprint.py",
                "--blueprint",
                str(blueprint),
                "--promote",
                "--report",
                "json",
            )
            payload = json.loads(promoted.stdout)
            self.assertTrue(payload["promoted"])
            self.assertEqual(payload["sha256"], file_sha256(blueprint))
            self.assertIn("Blueprint status: ready", blueprint.read_text("utf-8"))
            metadata = yaml_scalar_paths(course_dir / "course.yml")
            self.assertEqual(metadata["teaching.blueprint.status"], "ready")
            self.assertEqual(metadata["teaching.blueprint.source_fingerprint"], "abc123")

    def test_invalid_blueprint_draft_is_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "teaching-blueprint.md"
            draft = valid_blueprint(1).replace("Blueprint status: ready", "Blueprint status: draft")
            draft = draft.replace("relationship 1", "<MIGRATION REQUIRED>", 1)
            blueprint.write_text(draft, encoding="utf-8")
            result = self.run_script(
                "validate_teaching_blueprint.py",
                "--blueprint",
                str(blueprint),
                "--promote",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Blueprint status: draft", blueprint.read_text("utf-8"))

    def test_blueprint_validator_accepts_complete_plan_and_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "teaching-blueprint.md"
            blueprint.write_text(valid_blueprint(2), encoding="utf-8")
            self.assertEqual(validate_blueprint(blueprint, "1/2"), [])

    def test_blueprint_validator_rejects_coarse_transcript_and_wrong_total(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "teaching-blueprint.md"
            text = valid_blueprint(1).replace(
                'SPEAKER 0, slides 2-3, anchor "next we compare"', "main block"
            )
            blueprint.write_text(text, encoding="utf-8")
            errors = validate_blueprint(blueprint, "1/2")
            self.assertTrue(any("semantic transcript locator" in error for error in errors))
            self.assertTrue(any("Progress denominator" in error for error in errors))

    def test_blueprint_validator_rejects_generic_formula_and_question_plans(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "teaching-blueprint.md"
            text = valid_blueprint(1)
            text = text.replace(
                "objects, fixed roles, subtraction, scaling, final notation",
                "explain symbols",
            ).replace(
                "A1 -> R1; A2 -> R2; A3 -> R3",
                "ask questions",
            )
            blueprint.write_text(text, encoding="utf-8")
            errors = validate_blueprint(blueprint)
            self.assertTrue(any("Formula construction" in error for error in errors))
            self.assertTrue(any("Exercise coverage" in error for error in errors))

    def test_blueprint_validator_rejects_legacy_v3_without_relation_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "teaching-blueprint.md"
            text = valid_blueprint(1).replace("Blueprint version: 3.1", "Blueprint version: 3")
            blueprint.write_text(text, encoding="utf-8")
            errors = validate_blueprint(blueprint)
            self.assertTrue(any("version must be 3.1" in error for error in errors))

    def test_exercise_contract_accepts_atomic_demonstrated_actions(self) -> None:
        contract = valid_contract()
        self.assertEqual(validate_contract(contract), [])
        rendered = render_contract(contract)
        self.assertIn("Atomic answer actions: 3", rendered)
        self.assertIn("1. A new course-grounded scenario.", rendered)
        self.assertNotIn("criterion", rendered)

    def test_exercise_contract_is_bound_to_blueprint_point_and_relationships(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "teaching-blueprint.md"
            blueprint.write_text(valid_blueprint(2), encoding="utf-8")
            contract = valid_contract(point_id="week-02-point-02")
            self.assertEqual(
                validate_blueprint_binding(contract, blueprint, "2/2"), []
            )

            first = contract["actions"][0]  # type: ignore[index]
            first["relation_id"] = "R9"  # type: ignore[index]
            errors = validate_blueprint_binding(contract, blueprint, "2/2")
            self.assertTrue(any("not eligible" in error for error in errors))
            self.assertTrue(any("does not match blueprint plan" in error for error in errors))

    def test_contract_cli_validates_and_renders_through_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "example-course-2026-s2"
            blueprint = write_blueprint(course_dir)
            contract = write_contract(course_dir)
            validated = self.run_script(
                "validate_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "2/8",
            )
            self.assertIn("Exercise contract valid", validated.stdout)
            self.assertIn("SHA256:", validated.stdout)

            rendered = self.run_script(
                "render_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "2/8",
            )
            self.assertIn("Atomic answer actions: 3", rendered.stdout)
            self.assertNotIn("criterion", rendered.stdout)

    def test_contract_promotion_binds_the_current_blueprint_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "contract-promotion"
            blueprint = write_blueprint(course_dir)
            contract = write_contract(course_dir)
            data = json.loads(contract.read_text("utf-8"))
            data["status"] = "draft"
            contract.write_text(json.dumps(data, indent=2), encoding="utf-8")
            dry_run = self.run_script(
                "validate_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "2/8",
                "--promote",
                "--dry-run",
                "--report",
                "json",
            )
            self.assertEqual(json.loads(dry_run.stdout)["sha256"], "")
            self.assertEqual(json.loads(contract.read_text("utf-8"))["status"], "draft")
            promoted = self.run_script(
                "validate_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "2/8",
                "--promote",
                "--report",
                "json",
            )
            payload = json.loads(promoted.stdout)
            self.assertTrue(payload["promoted"])
            promoted_data = json.loads(contract.read_text("utf-8"))
            self.assertEqual(promoted_data["blueprint_sha256"], file_sha256(blueprint))
            self.assertTrue(promoted_data["validated_at"])

            blueprint.write_text(blueprint.read_text("utf-8").rstrip() + "\n\n", encoding="utf-8")
            errors = validate_blueprint_binding(promoted_data, blueprint, "2/8")
            self.assertTrue(any("SHA256" in error for error in errors))

    def test_exercise_contract_rejects_mentioned_but_not_demonstrated_content(self) -> None:
        contract = valid_contract()
        first = contract["actions"][0]  # type: ignore[index]
        first["teaching_evidence"]["status"] = "mentioned"  # type: ignore[index]
        first["teaching_evidence"]["worked_example_locator"] = ""  # type: ignore[index]
        errors = validate_contract(contract)
        self.assertTrue(any("status must be demonstrated" in error for error in errors))
        self.assertTrue(any("worked_example_locator" in error for error in errors))

    def test_exercise_contract_rejects_compound_prompt_and_hidden_load(self) -> None:
        contract = valid_contract()
        first = contract["actions"][0]  # type: ignore[index]
        first["prompt"] = "Select the method and then explain why it applies."  # type: ignore[index]
        extra = dict(contract["actions"][0])  # type: ignore[index]
        contract["actions"] = [*contract["actions"], extra, extra, extra]  # type: ignore[index]
        errors = validate_contract(contract)
        self.assertTrue(any("combine multiple requests" in error for error in errors))
        self.assertTrue(any("requires 3-5 atomic actions" in error for error in errors))

    def test_exercise_contract_rejects_hidden_rubric_requirement(self) -> None:
        contract = valid_contract()
        first = contract["actions"][0]  # type: ignore[index]
        first["rubric"]["explicit_in_prompt"] = False  # type: ignore[index]
        first["rubric"]["requires_untaught_inference"] = True  # type: ignore[index]
        errors = validate_contract(contract)
        self.assertTrue(any("explicit in the prompt" in error for error in errors))
        self.assertTrue(any("requires_untaught_inference" in error for error in errors))

    def test_state_update_blocks_self_declared_coverage_without_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "example-course-2026-s2"
            result = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "Unverified point",
                "--lesson-progress",
                "2/8",
                "--exercise-set-id",
                "point-2-set-1",
                "--source-fingerprint",
                "abc123",
                "--coverage-gate",
                "passed",
                "--exercise-status",
                "pending",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("validated --exercise-contract", result.stderr)

    def test_non_advancing_teaching_cannot_use_a_self_declared_ready_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "missing-blueprint"
            course_dir.mkdir(parents=True)
            course_text = (SKILL_ROOT / "assets" / "course.yml.template").read_text("utf-8")
            course_text = course_text.replace('status: "draft"', 'status: "ready"', 1)
            (course_dir / "course.yml").write_text(course_text, encoding="utf-8")
            result = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "Most common teaching path",
                "--lesson-progress",
                "1/1",
                "--point-id",
                "week-02-point-01",
                "--point-status",
                "teaching",
                "--blueprint-status",
                "ready",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("validated blueprint", result.stderr)

    def test_state_json_supports_dry_run_and_rejects_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "json-course"
            blueprint = write_blueprint(course_dir, total=1)
            payload = {
                "schema_version": 1,
                "course_dir": str(course_dir),
                "mode": "learning",
                "topic": "Stable point 1",
                "lesson_progress": "1/1",
                "point_id": "week-02-point-01",
                "point_status": "teaching",
                "blueprint_status": "ready",
                "source_fingerprint": "abc123",
                "auto_advance": "no",
            }
            state_json = Path(temp_dir) / "state.json"
            state_json.write_text(json.dumps(payload), encoding="utf-8")
            self.run_script(
                "update_learning_state.py",
                "--state-json",
                str(state_json),
                "--dry-run",
            )
            self.assertFalse((course_dir / "memory" / "learning-state.md").exists())

            self.run_script("update_learning_state.py", "--state-json", str(state_json))
            state = (course_dir / "memory" / "learning-state.md").read_text("utf-8")
            self.assertIn(f"Blueprint SHA256: {file_sha256(blueprint)}", state)

            payload["unexpected"] = "blocked"
            state_json.write_text(json.dumps(payload), encoding="utf-8")
            rejected = self.run_script(
                "update_learning_state.py", "--state-json", str(state_json), check=False
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("unknown --state-json fields", rejected.stderr)

    def test_migration_mode_allows_clarification_but_blocks_teaching(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "legacy-course"
            self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--mode",
                "limited_clarification",
                "--topic",
                "User-requested definition",
                "--user-performance",
                "Asked for one local clarification",
            )
            self.assertFalse((course_dir / "memory" / "learning-state.md").exists())
            blocked = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--mode",
                "limited_clarification",
                "--topic",
                "Unauthorized teaching",
                "--point-status",
                "teaching",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("limited clarification only", blocked.stderr)

    def test_fresh_workspace_e2e_reaches_ready_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                "fresh-course",
                "--confirm-no-known-canonical",
            )
            course_dir = workspace / "courses" / "fresh-course"
            blueprint = course_dir / "indexes" / "teaching-blueprint.md"
            blueprint.write_text(
                valid_blueprint(1).replace(
                    "Blueprint status: ready", "Blueprint status: draft"
                ),
                encoding="utf-8",
            )
            self.run_script(
                "validate_teaching_blueprint.py",
                "--blueprint",
                str(blueprint),
                "--promote",
            )
            payload = {
                "schema_version": 1,
                "course_dir": str(course_dir),
                "mode": "learning",
                "topic": "Stable point 1",
                "lesson_progress": "1/1",
                "point_id": "week-02-point-01",
                "point_status": "teaching",
                "source_fingerprint": "abc123",
            }
            state_json = Path(temp_dir) / "fresh-state.json"
            state_json.write_text(json.dumps(payload), encoding="utf-8")
            self.run_script("update_learning_state.py", "--state-json", str(state_json))
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            self.assertEqual(json.loads(audit.stdout)["courses"][0]["status"], "ready")

    def test_full_point_cycle_promotes_renders_and_advances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            course_dir = self.make_ready_course(
                workspace, "example-course-2026-s2"
            )
            blueprint = course_dir / "indexes" / "teaching-blueprint.md"
            contract = write_contract(
                course_dir,
                point_id="week-02-point-01",
                exercise_set_id="point-1-cycle",
            )
            contract_data = json.loads(contract.read_text("utf-8"))
            contract_data["status"] = "draft"
            for action in contract_data["actions"]:
                evidence = action["teaching_evidence"]
                evidence["explanation_locator"] = evidence[
                    "explanation_locator"
                ].replace("point 2", "point 1")
                evidence["worked_example_locator"] = evidence[
                    "worked_example_locator"
                ].replace("point 2", "point 1")
            contract.write_text(
                json.dumps(contract_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            ordinary = self.run_script(
                "validate_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "1/1",
                check=False,
            )
            self.assertNotEqual(ordinary.returncode, 0)
            self.assertIn("status must be ready", ordinary.stdout + ordinary.stderr)

            promoted = self.run_script(
                "validate_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "1/1",
                "--promote",
                check=False,
            )
            self.assertEqual(
                promoted.returncode, 0, promoted.stdout + promoted.stderr
            )
            rendered = self.run_script(
                "render_exercise_contract.py",
                "--contract",
                str(contract),
                "--blueprint",
                str(blueprint),
                "--progress",
                "1/1",
            )
            self.assertIn("Atomic answer actions: 3", rendered.stdout)

            advanced = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "Stable point 1",
                "--lesson-progress",
                "1/1",
                "--point-id",
                "week-02-point-01",
                "--point-status",
                "practiced",
                "--auto-advance",
                "yes",
                "--blueprint-status",
                "ready",
                "--source-fingerprint",
                "abc123",
                "--transcript-gate",
                "passed",
                "--transcript-evidence",
                "SPEAKER 0, stable point construction passage",
                "--formula-gate",
                "passed",
                "--coverage-gate",
                "passed",
                "--exercise-status",
                "passed",
                "--exercise-set-id",
                "point-1-cycle",
                "--exercise-contract",
                str(contract),
                "--mastery-evidence",
                "All three planned relationships were correctly applied",
                check=False,
            )
            self.assertEqual(
                advanced.returncode, 0, advanced.stdout + advanced.stderr
            )
            state = (course_dir / "memory" / "learning-state.md").read_text("utf-8")
            self.assertIn("Point status: practiced", state)
            self.assertIn("Automatic advance: yes", state)
            self.assertIn(f"Blueprint SHA256: {file_sha256(blueprint)}", state)
            self.assertIn(f"Exercise contract SHA256: {file_sha256(contract)}", state)

    def test_legacy_blueprint_migrates_through_sidecar_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / ".ai-course-tutor"
            self.run_script(
                "init_course_workspace.py",
                "--workspace",
                str(workspace),
                "--course-id",
                "legacy-course",
                "--confirm-no-known-canonical",
            )
            course_dir = workspace / "courses" / "legacy-course"
            course_yml = course_dir / "course.yml"
            course_yml.write_text(
                course_yml.read_text("utf-8").replace(
                    "workspace_schema_version: 1", "workspace_schema_version: 0"
                ),
                encoding="utf-8",
            )
            official = course_dir / "indexes" / "teaching-blueprint.md"
            legacy_text = valid_blueprint(1).replace(
                "Blueprint version: 3.1", "Blueprint version: 3"
            )
            official.write_text(legacy_text, encoding="utf-8")
            self.run_script(
                "migrate_blueprint_v3_to_v31.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--lesson-id",
                "week-02",
            )
            self.assertEqual(official.read_text("utf-8"), legacy_text)
            draft = course_dir / "indexes" / "teaching-blueprint.v31-draft.md"
            repaired = draft.read_text("utf-8").replace(
                "- Source fidelity: pending", "- Source fidelity: pass"
            ).replace(
                "- Dependency and order: pending", "- Dependency and order: pass"
            ).replace(
                "- Novice and assessment: pending", "- Novice and assessment: pass"
            )
            draft.write_text(repaired, encoding="utf-8")
            self.run_script(
                "validate_teaching_blueprint.py",
                "--blueprint",
                str(draft),
                "--promote",
            )
            self.run_script(
                "migrate_blueprint_v3_to_v31.py",
                "activate",
                "--course-dir",
                str(course_dir),
            )
            self.assertTrue(
                any((course_dir / "indexes").glob("teaching-blueprint.v3-backup-*.md"))
            )
            metadata = yaml_scalar_paths(course_yml)
            self.assertEqual(metadata["workspace_schema_version"], "1")
            self.assertEqual(metadata["teaching.blueprint.status"], "ready")
            self.assertEqual(
                metadata["workspace_migration_status"], "pending_reconciliation"
            )

            source_register = course_dir / "indexes" / "source-register.md"
            source_register.write_text(
                source_register.read_text("utf-8").replace(
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| `W02-SLIDES` | slides | 2026 S2 | `sources/slides/week02.pdf` | current course source | stable point | indexed | synthetic test source |",
                ),
                encoding="utf-8",
            )
            self.run_script(
                "migrate_legacy_workspace.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--safe-point-id",
                "week-02-point-01",
                "--current-lesson",
                "Week 02",
            )
            workspace_activation = self.run_script(
                "migrate_legacy_workspace.py",
                "activate",
                "--course-dir",
                str(course_dir),
                check=False,
            )
            self.assertEqual(
                workspace_activation.returncode,
                0,
                workspace_activation.stdout + workspace_activation.stderr,
            )

            payload = {
                "schema_version": 1,
                "course_dir": str(course_dir),
                "mode": "learning",
                "topic": "Stable point 1",
                "lesson_progress": "1/1",
                "point_id": "week-02-point-01",
                "point_status": "teaching",
                "source_fingerprint": "abc123",
            }
            state_json = Path(temp_dir) / "migrated-state.json"
            state_json.write_text(json.dumps(payload), encoding="utf-8")
            self.run_script("update_learning_state.py", "--state-json", str(state_json))
            audit = self.run_script(
                "audit_course_workspace.py",
                "--course-dir",
                str(course_dir),
                "--format",
                "json",
            )
            self.assertEqual(json.loads(audit.stdout)["courses"][0]["status"], "ready")

    def test_migration_point_ids_ignore_title_changes_and_preserve_existing_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "point-id-course"
            indexes = course_dir / "indexes"
            indexes.mkdir(parents=True)
            official = indexes / "teaching-blueprint.md"
            legacy = valid_blueprint(2).replace(
                "Blueprint version: 3.1", "Blueprint version: 3"
            )
            legacy_without_ids = re.sub(r"(?m)^- Point ID:.*\n", "", legacy)
            official.write_text(legacy_without_ids, encoding="utf-8")

            self.run_script(
                "migrate_blueprint_v3_to_v31.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--lesson-id",
                "Week 04",
            )
            draft = indexes / "teaching-blueprint.v31-draft.md"
            first_ids = re.findall(r"(?m)^- Point ID:\s*(\S+)", draft.read_text("utf-8"))
            self.assertEqual(first_ids, ["week-04-p01", "week-04-p02"])

            official.write_text(
                legacy_without_ids.replace("Stable point 1", "重命名后的第一知识点"),
                encoding="utf-8",
            )
            self.run_script(
                "migrate_blueprint_v3_to_v31.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--lesson-id",
                "Week 04",
                "--force",
            )
            second_ids = re.findall(r"(?m)^- Point ID:\s*(\S+)", draft.read_text("utf-8"))
            self.assertEqual(second_ids, first_ids)

            official.write_text(legacy, encoding="utf-8")
            self.run_script(
                "migrate_blueprint_v3_to_v31.py",
                "create-draft",
                "--course-dir",
                str(course_dir),
                "--lesson-id",
                "Week 04",
                "--force",
            )
            preserved_ids = re.findall(r"(?m)^- Point ID:\s*(\S+)", draft.read_text("utf-8"))
            self.assertEqual(
                preserved_ids, ["week-02-point-01", "week-02-point-02"]
            )

    def test_distributable_checker_rejects_private_workspace_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Safe skill\n", encoding="utf-8")
            passed = self.run_script(
                "check_distributable.py", "--skill-dir", str(skill_dir), check=False
            )
            self.assertEqual(passed.returncode, 0, passed.stdout)
            private = skill_dir / ".ai-course-tutor" / "courses"
            private.mkdir(parents=True)
            (private / "notes.md").write_text("private", encoding="utf-8")
            failed = self.run_script(
                "check_distributable.py", "--skill-dir", str(skill_dir), check=False
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("forbidden directory artifact", failed.stdout)

    def test_state_update_records_v3_gates_and_avoids_false_weakness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "data-systems-2026-s2"
            self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--mode",
                "learning",
                "--topic",
                "Acquisition undercurrents",
                "--current-lesson",
                "Week 2",
                "--lesson-progress",
                "2/8",
                "--point-status",
                "teaching",
                "--blueprint-status",
                "stale",
                "--source-fingerprint",
                "abc123",
                "--transcript-gate",
                "blocked",
                "--formula-gate",
                "not_required",
                "--coverage-gate",
                "failed",
                "--exercise-status",
                "withdrawn",
                "--exercise-set-id",
                "point-2-set-1",
                "--answer-actions",
                "1",
                "--issue-class",
                "tutor coverage gap",
                "--user-performance",
                "Could not answer",
                "--weak-point",
                "Security and privacy",
                "--tutor-coverage-gap",
                "--tutor-coverage-failures",
                "1",
            )
            memory = course_dir / "memory"
            state = (memory / "learning-state.md").read_text("utf-8")
            self.assertEqual(state.count("course-grounded-tutor:current-state:start"), 1)
            self.assertIn("Automatic advance: no", state)
            self.assertIn("Transcript gate: blocked", state)
            self.assertIn("Tutor coverage failures this lesson: 1", state)
            self.assertFalse((memory / "weak-points.md").exists())
            history = (memory / "practice-history.md").read_text("utf-8")
            self.assertIn("Tutor coverage gap: yes", history)
            self.assertIn("Issue class: tutor coverage gap", history)

    def test_state_update_blocks_false_automatic_advance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "quant-methods-2026-s2"
            write_blueprint(course_dir)
            contract = write_contract(course_dir)
            result = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "KDE formula",
                "--lesson-progress",
                "2/8",
                "--point-id",
                "week-02-point-02",
                "--point-status",
                "practiced",
                "--auto-advance",
                "yes",
                "--blueprint-status",
                "ready",
                "--source-fingerprint",
                "abc123",
                "--transcript-gate",
                "passed",
                "--formula-gate",
                "blocked",
                "--coverage-gate",
                "passed",
                "--exercise-status",
                "passed",
                "--exercise-set-id",
                "point-2-set-1",
                "--exercise-contract",
                str(contract),
                "--mastery-evidence",
                "Only outside normalization was tested",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("formula gate", result.stderr)

    def test_state_update_allows_valid_automatic_advance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "quant-methods-2026-s2"
            write_blueprint(course_dir)
            contract = write_contract(course_dir)
            self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "KDE construction",
                "--lesson-progress",
                "2/8",
                "--point-id",
                "week-02-point-02",
                "--point-status",
                "practiced",
                "--auto-advance",
                "yes",
                "--blueprint-status",
                "ready",
                "--source-fingerprint",
                "abc123",
                "--transcript-gate",
                "passed",
                "--transcript-evidence",
                "SPEAKER 0, KDE construction passage",
                "--formula-gate",
                "passed",
                "--coverage-gate",
                "passed",
                "--exercise-status",
                "passed",
                "--exercise-set-id",
                "point-2-set-1",
                "--exercise-contract",
                str(contract),
                "--mastery-evidence",
                "Explained displacement, bandwidth scaling, and normalization",
            )
            state = (course_dir / "memory" / "learning-state.md").read_text("utf-8")
            self.assertIn("Automatic advance: yes", state)
            self.assertIn("Point status: practiced", state)
            self.assertIn("Point ID: week-02-point-02", state)

    def test_legacy_practiced_status_cannot_bypass_v3_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "legacy-course"
            result = self.run_script(
                "update_learning_state.py",
                "--course-dir",
                str(course_dir),
                "--topic",
                "Legacy point",
                "--instruction-stage",
                "practiced",
                "--guided-check-evidence",
                "A recognition choice was correct",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("validated --exercise-contract", result.stderr)

    def test_repeated_tutor_gaps_require_remaining_lesson_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "quant-methods-2026-s2"
            write_blueprint(course_dir)
            contract = write_contract(course_dir)
            base = [
                "--course-dir",
                str(course_dir),
                "--topic",
                "Next point",
                "--lesson-progress",
                "2/8",
                "--point-id",
                "week-02-point-02",
                "--point-status",
                "practiced",
                "--auto-advance",
                "yes",
                "--blueprint-status",
                "ready",
                "--source-fingerprint",
                "abc123",
                "--transcript-gate",
                "passed",
                "--formula-gate",
                "not_required",
                "--coverage-gate",
                "passed",
                "--exercise-status",
                "passed",
                "--exercise-set-id",
                "point-2-set-1",
                "--exercise-contract",
                str(contract),
                "--mastery-evidence",
                "All planned relationships were explained",
                "--tutor-coverage-failures",
                "2",
            ]
            blocked = self.run_script(
                "update_learning_state.py", *base, check=False
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("remaining-lesson audit", blocked.stderr)

            passed = self.run_script(
                "update_learning_state.py",
                *base,
                "--remaining-lesson-audit",
                "passed",
                check=False,
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)

    def test_weak_point_is_upserted_instead_of_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            course_dir = Path(temp_dir) / "courses" / "example-course-2026-s1"
            common = [
                "--course-dir",
                str(course_dir),
                "--topic",
                "Standard error",
                "--weak-point",
                "SD vs SE",
                "--coverage-gate",
                "passed",
            ]
            self.run_script(
                "update_learning_state.py",
                *common,
                "--user-performance",
                "First error",
            )
            self.run_script(
                "update_learning_state.py",
                *common,
                "--user-performance",
                "Later evidence",
            )
            weak_points = (course_dir / "memory" / "weak-points.md").read_text("utf-8")
            self.assertEqual(weak_points.count("### SD vs SE"), 1)
            self.assertIn("Later evidence", weak_points)
            self.assertNotIn("First error", weak_points)

    @unittest.skipUnless(find_spec("pymupdf"), "PyMuPDF is not installed")
    def test_pdf_crops_are_unique_and_protected_from_overwrite(self) -> None:
        import pymupdf

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            pdf = temp / "sample.pdf"
            output = temp / "figures"
            document = pymupdf.open()
            page = document.new_page(width=300, height=300)
            page.insert_text((20, 40), "left content")
            page.insert_text((170, 40), "right content")
            document.save(pdf)
            document.close()

            for rect in ["0,0,150,150", "150,0,300,150"]:
                self.run_script(
                    "extract_pdf_figures.py",
                    "--pdf",
                    str(pdf),
                    "--out",
                    str(output),
                    "--pages",
                    "1",
                    "--rect",
                    rect,
                )
            self.assertEqual(len(list(output.glob("*.png"))), 2)

            duplicate = self.run_script(
                "extract_pdf_figures.py",
                "--pdf",
                str(pdf),
                "--out",
                str(output),
                "--pages",
                "1",
                "--rect",
                "0,0,150,150",
                check=False,
            )
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("output already exists", duplicate.stderr)


if __name__ == "__main__":
    unittest.main()
