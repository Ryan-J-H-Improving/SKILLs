#!/usr/bin/env python3
"""Fail when a distributable skill contains private workspace or cache artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FORBIDDEN_DIRS = {
    ".ai-course-tutor",
    "tmp",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
FORBIDDEN_SUFFIXES = {
    ".pdf",
    ".ppt",
    ".pptx",
    ".csv",
    ".tsv",
    ".mp3",
    ".wav",
    ".m4a",
    ".mp4",
    ".mov",
    ".pyc",
    ".pyo",
}
PERSONAL_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/](?:Users|Sydney)[\\/]|/Users/[^/]+/|/home/[^/]+/)",
    re.IGNORECASE,
)
ROUTED_PATH_RE = re.compile(
    r"`((?:references|assets|scripts|agents)/[^`<>\s]+)`"
)
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".txt", ".template"}


def scan(skill_dir: Path) -> list[str]:
    issues: list[str] = []
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if any(part in FORBIDDEN_DIRS for part in relative.parts):
            issues.append(f"forbidden directory artifact: {relative}")
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            issues.append(f"course material or cache file is not distributable: {relative}")
        if path.name == Path(__file__).name:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and ".template" not in path.name:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if PERSONAL_PATH_RE.search(text):
            issues.append(f"personal absolute path found: {relative}")
        for routed in ROUTED_PATH_RE.findall(text):
            routed_path = skill_dir / routed.rstrip(".,:;")
            if not routed_path.exists():
                issues.append(f"broken routed path in {relative}: {routed}")
    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    issues = scan(args.skill_dir.resolve())
    if issues:
        for item in issues:
            print(f"ERROR: {item}")
        return 1
    print(f"Distributable check passed: {args.skill_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
