#!/usr/bin/env python3
"""Validate that npm check commands stay wired to their Python check scripts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "package.json"
REQUIRED_CHECK_ALL_COMMANDS = (
    "npm run docs:build",
)
REQUIRED_PYTHON_CHECK_PATTERNS = (
    "audit_*.py",
    "check_*.py",
    "*_tests.py",
)


class PackageScriptsCheckError(RuntimeError):
    pass


def load_scripts(package_json: Path = PACKAGE_JSON) -> dict[str, str]:
    data = json.loads(package_json.read_text())
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        raise PackageScriptsCheckError("package.json must contain a scripts object")
    for name, command in scripts.items():
        if not isinstance(command, str):
            raise PackageScriptsCheckError(f"package.json script {name} must be a string")
    return scripts


def python_script_refs(command: str) -> list[str]:
    return re.findall(r"scripts/[A-Za-z0-9_./-]+\.py", command)


def npm_check_refs(command: str) -> list[str]:
    return re.findall(r"npm run (check:[A-Za-z0-9:-]+)", command)


def required_python_check_scripts(root: Path) -> set[str]:
    scripts_dir = root / "scripts"
    return {
        path.name
        for pattern in REQUIRED_PYTHON_CHECK_PATTERNS
        for path in scripts_dir.glob(pattern)
    }


def check_package_scripts(root: Path = ROOT) -> None:
    scripts = load_scripts(root / "package.json")
    check_all = scripts.get("check:all")
    if check_all is None:
        raise PackageScriptsCheckError("package.json is missing check:all")

    errors: list[str] = []
    check_scripts = required_python_check_scripts(root)
    check_commands = {
        name: command
        for name, command in scripts.items()
        if name.startswith("check:")
    }

    for script_name in sorted(check_scripts):
        rel = f"scripts/{script_name}"
        if not any(rel in command for command in check_commands.values()):
            errors.append(f"{rel} is not referenced by any package.json check script")

    for name in sorted(check_commands):
        if name == "check:all":
            continue
        if f"npm run {name}" not in check_all:
            errors.append(f"{name} is not included in check:all")

    for command in REQUIRED_CHECK_ALL_COMMANDS:
        if command not in check_all:
            errors.append(f"check:all must include {command}")

    check_all_refs = npm_check_refs(check_all)
    duplicate_refs = sorted({name for name in check_all_refs if check_all_refs.count(name) > 1})
    for name in duplicate_refs:
        errors.append(f"check:all runs {name} more than once")

    for name in sorted(check_all_refs):
        if name not in scripts:
            errors.append(f"check:all references missing npm script {name}")

    for name, command in sorted(check_commands.items()):
        for rel in python_script_refs(command):
            if not (root / rel).exists():
                errors.append(f"{name} references missing {rel}")

    if errors:
        raise PackageScriptsCheckError("\n".join(errors))


def main() -> int:
    try:
        check_package_scripts()
    except PackageScriptsCheckError as exc:
        print(f"Package script check failed:\n{exc}", file=sys.stderr)
        return 1
    print("Package script checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
