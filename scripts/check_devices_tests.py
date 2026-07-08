#!/usr/bin/env python3
"""Regression tests for scripts/check_devices.py."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import check_devices
from product_model import load_devices


DEVICE = load_devices()[0]


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_devices.DeviceCheckError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def with_root():
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    original_root = check_devices.ROOT
    check_devices.ROOT = root
    return tmp, root, original_root


def test_stale_device_docs_fail() -> None:
    tmp, root, original_root = with_root()
    try:
        write(root / "docs" / "devices" / f"{check_devices.docs_slug(DEVICE)}.md")
        write(root / "docs" / "devices" / "old-device.md")
        run_fails(lambda: check_devices.check_unregistered_device_docs((DEVICE,)), "old-device.md")
    finally:
        check_devices.ROOT = original_root
        tmp.cleanup()


def test_stale_build_files_fail() -> None:
    tmp, root, original_root = with_root()
    try:
        write(root / "builds" / f"{DEVICE.config}.yaml")
        write(root / "builds" / f"{DEVICE.config}.factory.yaml")
        write(root / "builds" / "old-device.yaml")
        run_fails(lambda: check_devices.check_unregistered_build_files((DEVICE,)), "old-device.yaml")
    finally:
        check_devices.ROOT = original_root
        tmp.cleanup()


def test_missing_build_alias_fails() -> None:
    tmp, root, original_root = with_root()
    try:
        device = replace(DEVICE, build_aliases=["example-alias"])
        write(root / "builds" / f"{device.config}.yaml", f"../{device.package_path}\n")
        write(root / device.package_path, "\n".join(check_devices.REQUIRED_PACKAGE_INCLUDES))
        for include_path in check_devices.package_include_paths(root / device.package_path):
            write(include_path)
        run_fails(lambda: check_devices.check_build_package_variants((device,)), "example-alias.yaml")
    finally:
        check_devices.ROOT = original_root
        tmp.cleanup()


def test_standard_build_uses_catalog_package() -> None:
    tmp, root, original_root = with_root()
    try:
        write(root / "builds" / f"{DEVICE.config}.yaml", f"../devices/{DEVICE.config}/packages.yaml\n")
        run_fails(lambda: check_devices.check_build_package_variants((DEVICE,)), DEVICE.package_path)
    finally:
        check_devices.ROOT = original_root
        tmp.cleanup()


def test_documented_package_paths_reject_uncatalogued_devices() -> None:
    tmp, root, original_root = with_root()
    try:
        write(root / DEVICE.package_path)
        write(
            root / "docs" / "advanced" / "esphome-config.md",
            f"files: [{DEVICE.package_path}]\nfiles: [devices/old-device/packages.yaml]\n",
        )
        run_fails(lambda: check_devices.check_documented_package_paths((DEVICE,)), "not catalogued")
    finally:
        check_devices.ROOT = original_root
        tmp.cleanup()


def test_display_rotation_docs_require_catalogued_packages() -> None:
    tmp, root, original_root = with_root()
    try:
        write(root / "docs" / "advanced" / "display-rotation.md", "devices/other-device/packages.yaml\n")
        run_fails(lambda: check_devices.check_display_rotation_docs((DEVICE,)), DEVICE.package_path)
    finally:
        check_devices.ROOT = original_root
        tmp.cleanup()
