#!/usr/bin/env python3
"""Render only validated exercise-contract content for learner display."""

from __future__ import annotations

import argparse
from pathlib import Path

from exercise_contract import (
    render_contract,
    validate_blueprint_binding,
    validate_contract_file,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--blueprint", required=True, type=Path)
    parser.add_argument("--progress", default="")
    args = parser.parse_args()

    data, errors = validate_contract_file(args.contract)
    if not errors:
        errors.extend(validate_blueprint_binding(data, args.blueprint, args.progress))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(render_contract(data), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
