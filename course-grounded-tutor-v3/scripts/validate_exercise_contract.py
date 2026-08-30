#!/usr/bin/env python3
"""Validate or promote an exercise contract before learner display."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from exercise_contract import (
    contract_sha256,
    validate_blueprint_binding,
    validate_contract_file,
)
from workspace_common import (
    atomic_write_text,
    file_sha256,
    reference_mirror_write_error,
)


def report_payload(
    contract: Path,
    blueprint: Path,
    errors: list[str],
    promoted: bool = False,
    dry_run: bool = False,
    sha256: str = "",
) -> dict[str, object]:
    return {
        "contract": str(contract),
        "blueprint": str(blueprint),
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "promoted": promoted,
        "promotion_dry_run": dry_run,
        "sha256": sha256,
    }


def text_report(report: dict[str, object]) -> str:
    lines = [
        f"Contract: {report['contract']}",
        f"Blueprint: {report['blueprint']}",
        f"Valid: {'yes' if report['valid'] else 'no'}",
        f"Errors: {report['error_count']}",
    ]
    errors = report["errors"]
    if isinstance(errors, list):
        lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
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
            parser.error("exercise contract promotion is blocked: " + mirror_error)

    data, errors = validate_contract_file(
        args.contract, require_ready=not args.promote
    )
    if not errors:
        errors.extend(validate_blueprint_binding(data, args.blueprint, args.progress))

    promoted = False
    digest = ""
    if args.promote and not errors:
        candidate = dict(data)
        candidate["status"] = "ready"
        candidate["validated_at"] = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        candidate["blueprint_sha256"] = file_sha256(args.blueprint)
        candidate_text = json.dumps(candidate, ensure_ascii=False, indent=2)
        if not args.dry_run:
            atomic_write_text(args.contract, candidate_text)
            promoted = True
            data, errors = validate_contract_file(args.contract)
            if not errors:
                errors.extend(
                    validate_blueprint_binding(data, args.blueprint, args.progress)
                )
            if not errors:
                digest = contract_sha256(args.contract)
    elif not errors:
        digest = contract_sha256(args.contract)

    report = report_payload(
        args.contract,
        args.blueprint,
        errors,
        promoted=promoted,
        dry_run=bool(args.promote and args.dry_run),
        sha256=digest,
    )
    if args.report == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if not errors else 1
    elif args.report == "text":
        print(text_report(report), end="")
    elif errors:
        for error in errors:
            print(f"ERROR: {error}")

    if errors:
        return 1
    if args.promote and args.dry_run:
        print(f"Exercise contract promotion dry-run passed: {args.contract}")
    elif promoted:
        print(f"Exercise contract promoted: {args.contract}")
    else:
        print(f"Exercise contract valid: {args.contract}")
    if digest:
        print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
