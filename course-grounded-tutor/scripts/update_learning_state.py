#!/usr/bin/env python3
"""Append compact learning-state updates for a course."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text.rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-dir", required=True)
    parser.add_argument("--mode", default="")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--sources", default="")
    parser.add_argument("--taught", default="")
    parser.add_argument("--user-performance", default="")
    parser.add_argument("--weak-point", default="")
    parser.add_argument("--follow-up", default="")
    args = parser.parse_args()

    course_dir = Path(args.course_dir)
    today = date.today().isoformat()

    session_entry = f"""
## {today}

- Mode: {args.mode}
- Topic: {args.topic}
- Sources: {args.sources}
- Taught: {args.taught}
- User performance: {args.user_performance}
- Updates: {args.follow_up}
"""
    append(course_dir / "memory" / "session-log.md", session_entry)

    if args.weak_point:
        weak_entry = f"""
## {args.weak_point}

- Status: fragile
- Evidence: {args.user_performance}
- Corrective explanation that worked:
- Course notation:
- Follow-up needed: {args.follow_up}
"""
        append(course_dir / "memory" / "weak-points.md", weak_entry)

    print(f"Updated memory files in {course_dir / 'memory'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

