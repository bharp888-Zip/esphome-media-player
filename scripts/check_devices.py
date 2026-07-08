#!/usr/bin/env python3
"""Validate supported device wiring across release, docs, builds, and web metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable

import generate_webserver
from product_model import Device, ROOT, display_dimensions, display_layout_label, load_devices, release_matrix, web_device_profiles


DOC_PACKAGE_PATH_RE = re.compile(r"devices/[a-z0-9-]+/packages(?:-[a-z0-9]+)?\.yaml")
PACKAGE_DOCS_DIRS = (("docs", "advanced"), ("docs", "devices"))
COMMON_SETUP_INCLUDES = (
    "actions_prompt.yaml",
    "ha_setup_prompt.yaml",
    "loading_screen.yaml",
    "setup_prompt.yaml",
    "wifi_setup_prompt.yaml",
)
REQUIRED_DEVICE_HOOKS = (
    "on_client_connected:",
    'client_info.find("Home Assistant")',
    "id(ha_base_url)",
    "script.execute: apply_timezone",
    "script.execute: subscribe_media_player",
    "script.execute: subscribe_linked_media_player",
    "script.execute: subscribe_day_night_sensor",
    "on_client_disconnected:",
    "lvgl.pause",
    "light.turn_off:",
    "lvgl.resume",
)
REQUIRED_PACKAGE_INCLUDES = (
    "base: !include ../../common/device/base.yaml",
    "web_settings: !include ../../common/addon/web_settings.yaml",
    "device: !include device/device.yaml",
    "lvgl: !include device/lvgl.yaml",
)


class DeviceCheckError(RuntimeError):
    pass


def read(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise DeviceCheckError(f"Missing file: {path.relative_to(ROOT)}") from exc


def path_label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def active_yaml_lines(path: Path) -> list[str]:
    lines: list[str] = []
    for line in read(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped.split("#", 1)[0].rstrip())
    return lines


def assert_active_yaml_contains(path: Path, expected: str) -> None:
    text = "\n".join(active_yaml_lines(path))
    if expected not in text:
        raise DeviceCheckError(f"{path.relative_to(ROOT)} does not contain active YAML line {expected!r}")


def package_include_paths(package_yaml: Path) -> list[Path]:
    paths: list[Path] = []
    for stripped in active_yaml_lines(package_yaml):
        if "!include" not in stripped:
            continue
        match = re.search(r"!include\s+([^\s#]+)", stripped)
        if match:
            paths.append(package_yaml.parent / match.group(1))
    return paths


def package_include_lines(package_yaml: Path) -> set[str]:
    return {line for line in active_yaml_lines(package_yaml) if "!include" in line}


def docs_slug(device: Device) -> str:
    return device.docs_path.strip("/").removeprefix("devices/")


def primary_package_name(device: Device) -> str:
    return Path(device.package_path).name


def package_paths(device: Device) -> list[str]:
    paths = [device.package_path]
    paths.extend(device.alternate_package_paths or [])
    return paths


def supported_build_names(device: Device) -> set[str]:
    names = {f"{device.config}.yaml", f"{device.config}.factory.yaml"}
    names.update(f"{alias}.yaml" for alias in device.build_aliases or [])
    return names


def duplicate_values(values: Iterable[str]) -> list[str]:
    items = list(values)
    return sorted({value for value in items if items.count(value) > 1})


def parse_release_matrix() -> dict[str, tuple[str, str]]:
    matrix = release_matrix()
    return {
        item["asset_slug"]: (item["config"], item["chip"])
        for item in matrix["include"]
    }


def generated_web_manifest_slugs() -> dict[str, str]:
    text = generate_webserver.build_bundle()
    match = re.search(r"var FIRMWARE_MANIFEST_SLUGS = (?P<value>.*?);", text, re.S)
    if not match:
        raise DeviceCheckError("Generated webserver bundle does not expose FIRMWARE_MANIFEST_SLUGS")
    return json.loads(match.group("value"))


def check_package_include_targets(package_yaml: Path) -> None:
    missing = [path_label(path) for path in package_include_paths(package_yaml) if not path.is_file()]
    if missing:
        raise DeviceCheckError(
            f"{path_label(package_yaml)} references missing package include target(s): {', '.join(missing)}"
        )


def check_setup_includes(device: Device) -> None:
    lvgl_yaml = ROOT / "devices" / device.config / "device" / "lvgl.yaml"
    active_lines = active_yaml_lines(lvgl_yaml)
    for file_name in COMMON_SETUP_INCLUDES:
        common = ROOT / "common" / "setup" / file_name
        if not common.is_file():
            raise DeviceCheckError(f"Missing {common.relative_to(ROOT)}")
        expected = f"!include ../../../common/setup/{file_name}"
        if not any(expected in line for line in active_lines):
            raise DeviceCheckError(f"{lvgl_yaml.relative_to(ROOT)} must include {expected!r}")

    legacy_setup_dir = ROOT / "devices" / device.config / "setup"
    legacy_wrappers = sorted(path.name for path in legacy_setup_dir.glob("*.yaml")) if legacy_setup_dir.is_dir() else []
    if legacy_wrappers:
        raise DeviceCheckError(
            f"{legacy_setup_dir.relative_to(ROOT)} still contains setup wrapper file(s): {', '.join(legacy_wrappers)}"
        )


def check_device_behavior_hooks(device: Device) -> None:
    behavior_paths = (
        ROOT / "common" / "addon" / "home_assistant_api.yaml",
        ROOT / "common" / "addon" / "esphome_ota.yaml",
        ROOT / "common" / "device" / "media_player_select.yaml",
    )
    text = "\n".join(line for path in behavior_paths for line in active_yaml_lines(path))
    missing = [hook for hook in REQUIRED_DEVICE_HOOKS if hook not in text]
    if missing:
        raise DeviceCheckError(f"Shared device behavior is missing hook(s): {', '.join(missing)}")


def check_device_package_includes(package_yaml: Path, require_core_includes: bool = True) -> None:
    include_lines = package_include_lines(package_yaml)
    if require_core_includes:
        missing = [include for include in REQUIRED_PACKAGE_INCLUDES if include not in include_lines]
        if missing:
            raise DeviceCheckError(f"{package_yaml.relative_to(ROOT)} is missing required package include(s): {', '.join(missing)}")

    active_lines = set(active_yaml_lines(package_yaml))
    uses_warm_tones = 'post_artwork_script: "apply_warm_tones"' in active_lines
    has_warm_tones_package = "warm_tones: !include ../../common/addon/warm_tones.yaml" in include_lines
    if uses_warm_tones and not has_warm_tones_package:
        raise DeviceCheckError(f"{package_yaml.relative_to(ROOT)} uses apply_warm_tones but does not include warm_tones")
    check_package_include_targets(package_yaml)


def check_unregistered_device_dirs(devices: tuple[Device, ...]) -> None:
    supported_configs = {device.config for device in devices}
    stray_dirs = [
        path.name
        for path in (ROOT / "devices").iterdir()
        if path.is_dir() and path.name not in supported_configs and any(child.is_file() for child in path.rglob("*"))
    ]
    if stray_dirs:
        raise DeviceCheckError(
            "Unregistered device directorie(s) contain files: "
            f"{', '.join(sorted(stray_dirs))}. Add them to product/devices.json or remove the dead files."
        )


def check_unregistered_device_docs(devices: tuple[Device, ...]) -> None:
    supported_docs = {f"{docs_slug(device)}.md" for device in devices}
    stray_docs = sorted(path.name for path in (ROOT / "docs" / "devices").glob("*.md") if path.name not in supported_docs)
    if stray_docs:
        raise DeviceCheckError(f"Unregistered device docs page(s): {', '.join(stray_docs)}")


def check_unregistered_build_files(devices: tuple[Device, ...]) -> None:
    supported_builds = set().union(*(supported_build_names(device) for device in devices))
    stray_builds = sorted(path.name for path in (ROOT / "builds").glob("*.yaml") if path.name not in supported_builds)
    if stray_builds:
        raise DeviceCheckError(f"Unregistered build YAML file(s): {', '.join(stray_builds)}")


def check_build_package_variants(devices: tuple[Device, ...]) -> None:
    for device in devices:
        build_yaml = ROOT / "builds" / f"{device.config}.yaml"
        assert_active_yaml_contains(build_yaml, f"../{device.package_path}")

        for package_path in package_paths(device):
            path = ROOT / package_path
            if not path.is_file():
                raise DeviceCheckError(f"{device.asset_slug} package path is missing: {package_path}")
            check_device_package_includes(path, require_core_includes=Path(package_path).name == "packages.yaml")

        for alias in device.build_aliases or []:
            alias_yaml = ROOT / "builds" / f"{alias}.yaml"
            if not alias_yaml.is_file():
                raise DeviceCheckError(f"Missing {alias_yaml.relative_to(ROOT)}")


def check_documented_package_paths(devices: tuple[Device, ...]) -> None:
    valid_paths = {path for device in devices for path in package_paths(device)}
    for docs_dir_parts in PACKAGE_DOCS_DIRS:
        docs_dir = ROOT.joinpath(*docs_dir_parts)
        for docs_path in sorted(docs_dir.glob("*.md")):
            for package_path in sorted(set(DOC_PACKAGE_PATH_RE.findall(read(docs_path)))):
                if package_path not in valid_paths:
                    raise DeviceCheckError(
                        f"{path_label(docs_path)} documents package path {package_path!r}, but that package is not catalogued"
                    )


def check_display_rotation_docs(devices: tuple[Device, ...]) -> None:
    text = read(ROOT / "docs" / "advanced" / "display-rotation.md")
    for device in devices:
        if device.package_path not in text:
            raise DeviceCheckError(f"docs/advanced/display-rotation.md does not document {device.package_path!r}")


def check_web_profiles(devices: tuple[Device, ...]) -> None:
    profiles = web_device_profiles()
    known_profiles = {device.profile for device in devices}
    for group, values in profiles.items():
        unknown = sorted(set(values) - known_profiles)
        if unknown:
            raise DeviceCheckError(f"Web profile group {group!r} contains unknown device profile(s): {', '.join(unknown)}")
        if duplicate_values(values):
            raise DeviceCheckError(f"Web profile group {group!r} contains duplicate profile(s): {', '.join(duplicate_values(values))}")


def check_device(device: Device, release_matrix: dict[str, tuple[str, str]], web_slugs: dict[str, str]) -> None:
    expected_release = (device.config, device.chip)
    if release_matrix.get(device.asset_slug) != expected_release:
        raise DeviceCheckError(
            f"release matrix for {device.asset_slug} is {release_matrix.get(device.asset_slug)!r}, expected {expected_release!r}"
        )

    build_yaml = ROOT / "builds" / f"{device.config}.yaml"
    factory_yaml = ROOT / "builds" / f"{device.config}.factory.yaml"
    base_package_yaml = ROOT / "devices" / device.config / "packages.yaml"
    package_yaml = ROOT / device.package_path
    esphome_yaml = ROOT / "devices" / device.config / "esphome.yaml"
    docs_path = ROOT / "docs" / f"{device.docs_path.strip('/')}.md"

    for path in (build_yaml, factory_yaml, base_package_yaml, package_yaml, esphome_yaml, docs_path):
        if not path.is_file():
            raise DeviceCheckError(f"Missing {path.relative_to(ROOT)}")

    assert_active_yaml_contains(base_package_yaml, f'device_slug: "{device.profile}"')
    assert_active_yaml_contains(base_package_yaml, f'firmware_manifest_slug: "{device.web_slug}"')
    assert_active_yaml_contains(package_yaml, f'display_rotation: "{device.display["default_rotation"]}"')
    assert_active_yaml_contains(esphome_yaml, f"files: [{device.package_path}]")
    assert_active_yaml_contains(factory_yaml, f"core: !include {device.config}.yaml")
    assert_active_yaml_contains(factory_yaml, 'firmware_version: "0.0.0"')
    assert_active_yaml_contains(factory_yaml, "name: jtenniswood.media-player")
    assert_active_yaml_contains(factory_yaml, 'version: "${firmware_version}"')
    assert_active_yaml_contains(factory_yaml, f"devices/{device.config}/esphome.yaml@main")

    docs_text = read(docs_path)
    if f'<InstallButton device="{device.web_slug}" />' not in docs_text:
        raise DeviceCheckError(f"{docs_path.relative_to(ROOT)} must contain the installer for {device.web_slug}")
    if f'<PurchaseLinks device="{device.web_slug}" />' not in docs_text:
        raise DeviceCheckError(f"{docs_path.relative_to(ROOT)} must render purchase links from product/devices.json")

    if web_slugs.get(device.profile) != device.web_slug:
        raise DeviceCheckError(
            f"web settings manifest slug for {device.profile} is {web_slugs.get(device.profile)!r}, expected {device.web_slug!r}"
        )

    if display_layout_label(device) not in {"landscape", "portrait", "square"}:
        raise DeviceCheckError(f"{device.asset_slug} has unsupported display layout")

    check_setup_includes(device)
    check_device_behavior_hooks(device)


def main() -> int:
    try:
        devices = load_devices()
        expected_assets = {device.asset_slug for device in devices}

        release_matrix = parse_release_matrix()
        if set(release_matrix) != expected_assets:
            raise DeviceCheckError(f"release device assets {sorted(release_matrix)} do not match product/devices.json")

        web_slugs = generated_web_manifest_slugs()
        expected_profiles = {device.profile for device in devices}
        if set(web_slugs) != expected_profiles:
            raise DeviceCheckError(f"web settings profiles {sorted(web_slugs)} do not match product/devices.json")

        check_web_profiles(devices)
        for device in devices:
            check_device(device, release_matrix, web_slugs)
        check_unregistered_device_dirs(devices)
        check_unregistered_device_docs(devices)
        check_unregistered_build_files(devices)
        check_build_package_variants(devices)
        check_documented_package_paths(devices)
        check_display_rotation_docs(devices)
    except DeviceCheckError as exc:
        print(f"Device metadata check failed: {exc}", file=sys.stderr)
        return 1

    print("Device metadata checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
