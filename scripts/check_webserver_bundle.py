#!/usr/bin/env python3
"""Smoke-test the generated ESPHome webserver bundle."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import json
import re

from generate_webserver import TOKENS as TEMPLATE_TOKENS
from product_model import firmware_manifest_slugs, load_devices, web_device_profiles


ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "docs" / "public" / "webserver" / "app.js"
FIRMWARE_PUBLIC_MANIFEST_BASE = "https://jtenniswood.github.io/esphome-media-player/firmware/"
PLACEHOLDERS = TEMPLATE_TOKENS


class WebserverBundleCheckError(RuntimeError):
    pass


def parse_json_assignment(text: str, name: str):
    matches = re.findall(rf"var {name} = (?P<value>.*?);", text, re.S)
    if len(matches) != 1:
        raise WebserverBundleCheckError(
            f"Expected exactly one {name} assignment in generated webserver bundle; found {len(matches)}"
        )
    return json.loads(matches[0])


def parse_string_map_assignment(text: str, name: str) -> dict[str, str]:
    value = parse_json_assignment(text, name)
    if not isinstance(value, dict):
        raise WebserverBundleCheckError(
            f"{name} must be an object with string keys and values; found {type(value).__name__}"
        )
    if any(not isinstance(key, str) or not isinstance(item, str) for key, item in value.items()):
        raise WebserverBundleCheckError(
            f"{name} must contain only string keys and values"
        )
    return value


def parse_string_list_assignment(text: str, name: str) -> list[str]:
    value = parse_json_assignment(text, name)
    if not isinstance(value, list):
        raise WebserverBundleCheckError(
            f"{name} must be a list of strings; found {type(value).__name__}"
        )
    if any(not isinstance(item, str) for item in value):
        raise WebserverBundleCheckError(
            f"{name} must contain only strings"
        )
    return value


def parse_string_assignment(text: str, name: str) -> str:
    matches = re.findall(rf'var {name} = "(?P<value>[^"]*)";', text)
    if len(matches) != 1:
        raise WebserverBundleCheckError(
            f"Expected exactly one {name} assignment in generated webserver bundle; found {len(matches)}"
        )
    return matches[0]


def check_generated_device_metadata(text: str) -> None:
    devices = load_devices()
    known_profiles = {device.profile for device in devices}

    actual_manifest_slugs = parse_string_map_assignment(text, "FIRMWARE_MANIFEST_SLUGS")
    expected_manifest_slugs = firmware_manifest_slugs()
    if actual_manifest_slugs != expected_manifest_slugs:
        raise WebserverBundleCheckError(
            f"FIRMWARE_MANIFEST_SLUGS {actual_manifest_slugs!r} does not match product/devices.json {expected_manifest_slugs!r}"
        )

    actual_profiles = parse_json_assignment(text, "WEB_DEVICE_PROFILES")
    expected_profiles = web_device_profiles()
    for group, values in actual_profiles.items():
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise WebserverBundleCheckError(f"WEB_DEVICE_PROFILES {group!r} must be a list of strings")
        unknown = sorted(set(values) - known_profiles)
        if unknown:
            raise WebserverBundleCheckError(
                f"WEB_DEVICE_PROFILES {group!r} contains unknown profile(s): {', '.join(unknown)}"
            )
    if actual_profiles != expected_profiles:
        raise WebserverBundleCheckError(
            f"WEB_DEVICE_PROFILES {actual_profiles!r} does not match product/devices.json {expected_profiles!r}"
        )

    base = parse_string_assignment(text, "FIRMWARE_PUBLIC_MANIFEST_BASE")
    if base != FIRMWARE_PUBLIC_MANIFEST_BASE:
        raise WebserverBundleCheckError(
            f"FIRMWARE_PUBLIC_MANIFEST_BASE {base!r} does not match {FIRMWARE_PUBLIC_MANIFEST_BASE!r}"
        )

    expected_urls = {
        config: f"{FIRMWARE_PUBLIC_MANIFEST_BASE}{slug}/manifest.json"
        for config, slug in expected_manifest_slugs.items()
    }
    actual_urls = {
        config: f"{base}{slug}/manifest.json"
        for config, slug in actual_manifest_slugs.items()
    }
    if actual_urls != expected_urls:
        raise WebserverBundleCheckError(
            f"public firmware manifest URLs {actual_urls!r} do not match expected {expected_urls!r}"
        )


def main() -> int:
    text = BUNDLE.read_text()
    leaked = [placeholder for placeholder in PLACEHOLDERS if placeholder in text]
    if leaked:
        print(f"Webserver bundle contains unreplaced template token(s): {', '.join(leaked)}", file=sys.stderr)
        return 1

    try:
        check_generated_device_metadata(text)
    except WebserverBundleCheckError as exc:
        print(f"Webserver bundle check failed: {exc}", file=sys.stderr)
        return 1

    try:
        result = subprocess.run(
            ["node", "--check", str(BUNDLE)],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        print("Webserver bundle check failed: node is not available", file=sys.stderr)
        return 1

    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode

    print("Webserver bundle smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
