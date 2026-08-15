#!/usr/bin/env python3
"""Update the current state and durable learning-memory records for a course."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


STATE_START = "<!-- course-grounded-tutor:current-state:start -->"
STATE_END = "<!-- course-grounded-tutor:current-state:end -->"


def read_or_create(path: Path, heading: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"# {heading}\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def remove_placeholder_section(text: str, placeholder: str) -> str:
    pattern = re.compile(
        rf"(?ms)^###\s+{re.escape(placeholder)}\s*\n.*?(?=^###\s+|\Z)"
    )
    return pattern.sub("", text).rstrip() + "\n"


def append_h3_entry(path: Path, document_heading: str, title: str, body: str) -> None:
    text = read_or_create(path, document_heading)
    text = remove_placeholder_section(text, "<Date>")
    entry = f"### {title}\n\n{body.strip()}\n"
    write(path, text.rstrip() + "\n\n" + entry)


def upsert_h3_section(
    path: Path, document_heading: str, title: str, body: str
) -> None:
    text = read_or_create(path, document_heading)
    text = remove_placeholder_section(text, "<Weak Point>")
    section = f"### {title}\n\n{body.strip()}\n"
    pattern = re.compile(
        rf"(?ms)^###\s+{re.escape(title)}\s*\n.*?(?=^###\s+|\Z)",
        re.IGNORECASE,
    )
    if pattern.search(text):
        text = pattern.sub(section.rstrip(), text, count=1)
    else:
        text = text.rstrip() + "\n\n" + section
    write(path, text)


def update_current_state(path: Path, args: argparse.Namespace) -> None:
    text = read_or_create(path, f"Learning State: {args.course_dir.name}")
    normalized_gate = args.practice_gate.strip().lower().replace(" ", "_")
    allowed = "yes" if normalized_gate in {"independent_ready", "passed", "allowed"} else "no"
    block = f"""{STATE_START}
## Current Session Snapshot

- Current mode: {args.mode}
- Current lecture or lesson: {args.current_lesson}
- Lesson progress: {args.lesson_progress}
- Current topic: {args.topic}
- Current learning cluster: {args.learning_cluster}
- Narrative bridge: {args.narrative_bridge}
- Instruction stage: {args.instruction_stage}
- Practice gate: {args.practice_gate}
- Practice checkpoint: {args.practice_checkpoint}
- Independent practice allowed: {allowed}
- Required prerequisites: {args.required_concepts}
- New terms: {args.new_terms}
- Source layers: {args.source_layers}
- Worked example status: {args.worked_example_status}
- Guided check evidence: {args.guided_check_evidence}
- Existing evidence reused: {args.evidence_reused}
- Answer actions this session: {args.answer_actions}
- Immediate remediation rounds: {args.remediation_rounds}
- Learner load signal: {args.learner_load_signal}
- Blocking gaps: {args.blocking_gaps}
- Next recommended step: {args.follow_up}
{STATE_END}"""
    pattern = re.compile(
        rf"(?ms){re.escape(STATE_START)}.*?{re.escape(STATE_END)}"
    )
    if pattern.search(text):
        text = pattern.sub(block, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    write(path, text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-dir", required=True, type=Path)
    parser.add_argument("--mode", default="")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--current-lesson", default="")
    parser.add_argument("--lesson-progress", default="")
    parser.add_argument("--learning-cluster", default="")
    parser.add_argument("--narrative-bridge", default="")
    parser.add_argument("--instruction-stage", default="")
    parser.add_argument("--practice-gate", default="")
    parser.add_argument("--practice-checkpoint", default="")
    parser.add_argument("--required-concepts", default="")
    parser.add_argument("--new-terms", default="")
    parser.add_argument("--source-layers", default="")
    parser.add_argument("--worked-example-status", default="")
    parser.add_argument("--guided-check-evidence", default="")
    parser.add_argument("--evidence-reused", default="")
    parser.add_argument("--answer-actions", default="")
    parser.add_argument("--remediation-rounds", default="")
    parser.add_argument("--learner-load-signal", default="")
    parser.add_argument("--blocking-gaps", default="")
    parser.add_argument("--tutor-coverage-gap", action="store_true")
    parser.add_argument("--sources", default="")
    parser.add_argument("--taught", default="")
    parser.add_argument("--user-performance", default="")
    parser.add_argument("--weak-point", default="")
    parser.add_argument("--course-notation", default="")
    parser.add_argument("--follow-up", default="")
    parser.add_argument("--learning-phase", default="")
    parser.add_argument("--question-label", default="")
    parser.add_argument("--difficulty", default="")
    parser.add_argument("--scored", choices=["yes", "no"], default="")
    parser.add_argument("--issue-class", default="")
    parser.add_argument("--misconception", default="")
    args = parser.parse_args()

    timestamp = datetime.now().astimezone().isoformat(timespec="microseconds")
    memory_dir = args.course_dir / "memory"

    update_current_state(memory_dir / "learning-state.md", args)

    session_body = f"""- Mode: {args.mode}
- Topic: {args.topic}
- Lesson progress: {args.lesson_progress}
- Learning cluster: {args.learning_cluster}
- Practice checkpoint: {args.practice_checkpoint}
- Answer actions: {args.answer_actions}
- Evidence reused: {args.evidence_reused}
- Learner load signal: {args.learner_load_signal}
- Instruction stage: {args.instruction_stage}
- Practice gate: {args.practice_gate}
- Tutor coverage gap: {"yes" if args.tutor_coverage_gap else "no"}
- Sources: {args.sources}
- Taught: {args.taught}
- User performance: {args.user_performance}
- Updates: {args.follow_up}"""
    append_h3_entry(memory_dir / "session-log.md", "Session Log", timestamp, session_body)

    if args.weak_point and not args.tutor_coverage_gap:
        weak_body = f"""- Status: fragile
- Evidence: {args.user_performance}
- Corrective explanation that worked:
- Course notation: {args.course_notation}
- Follow-up needed: {args.follow_up}"""
        upsert_h3_section(
            memory_dir / "weak-points.md",
            "Weak Points",
            args.weak_point,
            weak_body,
        )

    if args.question_label:
        scored = args.scored or ("no" if args.tutor_coverage_gap else "")
        practice_body = f"""- Topic: {args.topic}
- Difficulty: {args.difficulty}
- Learning phase: {args.learning_phase}
- Question label: {args.question_label}
- Required concepts: {args.required_concepts}
- Source status: {args.source_layers}
- Gate status before question: {args.practice_gate}
- Scored: {scored}
- Answer actions: {args.answer_actions}
- Evidence reused: {args.evidence_reused}
- Tutor coverage gap: {"yes" if args.tutor_coverage_gap else "no"}
- Issue class: {args.issue_class}
- User result: {args.user_performance}
- Misconception: {args.misconception}
- Next recommended difficulty: {args.follow_up}"""
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
