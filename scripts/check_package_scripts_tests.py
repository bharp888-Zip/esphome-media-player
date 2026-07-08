#!/usr/bin/env python3
"""Regression tests for scripts/check_package_scripts.py."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import check_package_scripts


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def write_package(root: Path, scripts: dict[str, str]) -> None:
    write(root / "package.json", json.dumps({"scripts": scripts}, indent=2))


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_package_scripts.PackageScriptsCheckError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def test_package_scripts_pass_when_checks_are_wired() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write(root / "scripts" / "check_example_tests.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:example-tests": "python3 scripts/check_example_tests.py",
                "check:all": "npm run check:example && npm run check:example-tests && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        check_package_scripts.check_package_scripts(root)


def test_package_scripts_reject_unwired_check_file() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write(root / "scripts" / "check_orphan.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:all": "npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "scripts/check_orphan.py is not referenced",
        )


def test_package_scripts_reject_non_string_script_command() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write_package(
            root,
            {
                "check:example": ["python3", "scripts/check_example.py"],
                "check:all": "npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "package.json script check:example must be a string",
        )


def test_package_scripts_reject_unwired_regression_test_file() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write(root / "scripts" / "example_tests.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:all": "npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "scripts/example_tests.py is not referenced",
        )


def test_package_scripts_reject_unwired_audit_file() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write(root / "scripts" / "audit_example.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:all": "npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "scripts/audit_example.py is not referenced",
        )


def test_package_scripts_reject_check_command_missing_from_check_all() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write(root / "scripts" / "check_extra.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:extra": "python3 scripts/check_extra.py",
                "check:all": "npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "check:extra is not included in check:all",
        )


def test_package_scripts_reject_missing_python_file_reference() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_missing.py",
                "check:all": "npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "check:example references missing scripts/check_missing.py",
        )


def test_package_scripts_reject_duplicate_check_all_entries() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:all": "npm run check:example && npm run check:example && npm run docs:build",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "check:all runs check:example more than once",
        )


def test_package_scripts_require_docs_build_in_check_all() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "scripts" / "check_example.py", "")
        write_package(
            root,
            {
                "check:example": "python3 scripts/check_example.py",
                "check:all": "npm run check:example",
                "docs:build": "vitepress build docs",
            },
        )
        run_fails(
            lambda: check_package_scripts.check_package_scripts(root),
            "check:all must include npm run docs:build",
        )


def main() -> int:
    test_package_scripts_pass_when_checks_are_wired()
    test_package_scripts_reject_unwired_check_file()
    test_package_scripts_reject_non_string_script_command()
    test_package_scripts_reject_unwired_regression_test_file()
    test_package_scripts_reject_unwired_audit_file()
    test_package_scripts_reject_check_command_missing_from_check_all()
    test_package_scripts_reject_missing_python_file_reference()
    test_package_scripts_reject_duplicate_check_all_entries()
    test_package_scripts_require_docs_build_in_check_all()
    print("Package script regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
