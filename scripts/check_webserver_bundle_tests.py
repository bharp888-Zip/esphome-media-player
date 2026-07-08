#!/usr/bin/env python3
"""Regression tests for scripts/check_webserver_bundle.py."""

from __future__ import annotations

import json

import check_webserver_bundle
import generate_webserver
from product_model import firmware_manifest_slugs, web_device_profiles


MISSING = object()


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_webserver_bundle.WebserverBundleCheckError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def bundle_text(
    manifest_slugs: object = MISSING,
    profile_groups: object = MISSING,
    base_url: str | None = None,
) -> str:
    slugs = firmware_manifest_slugs() if manifest_slugs is MISSING else manifest_slugs
    profiles = web_device_profiles() if profile_groups is MISSING else profile_groups
    base = base_url if base_url is not None else check_webserver_bundle.FIRMWARE_PUBLIC_MANIFEST_BASE
    return (
        f"var FIRMWARE_MANIFEST_SLUGS = {json.dumps(slugs)};\n"
        f"var WEB_DEVICE_PROFILES = {json.dumps(profiles)};\n"
        f'var FIRMWARE_PUBLIC_MANIFEST_BASE = "{base}";\n'
    )


def test_generated_device_metadata_passes_for_product_model_values() -> None:
    check_webserver_bundle.check_generated_device_metadata(bundle_text())


def test_generated_device_metadata_rejects_wrong_manifest_slug() -> None:
    wrong_slugs = dict(firmware_manifest_slugs())
    first_config = sorted(wrong_slugs)[0]
    wrong_slugs[first_config] = "wrong-slug"
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(bundle_text(manifest_slugs=wrong_slugs)),
        "FIRMWARE_MANIFEST_SLUGS",
    )


def test_generated_device_metadata_rejects_manifest_slug_list() -> None:
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(bundle_text(manifest_slugs=["slug"])),
        "FIRMWARE_MANIFEST_SLUGS must be an object",
    )


def test_generated_device_metadata_rejects_manifest_slug_non_string_value() -> None:
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(
            bundle_text(manifest_slugs={"device-a": 123})
        ),
        "FIRMWARE_MANIFEST_SLUGS must contain only string keys and values",
    )


def test_generated_device_metadata_rejects_wrong_public_base_url() -> None:
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(bundle_text(base_url="https://example.invalid/")),
        "FIRMWARE_PUBLIC_MANIFEST_BASE",
    )


def test_generated_device_metadata_rejects_wrong_profile_groups() -> None:
    wrong_profiles = dict(web_device_profiles())
    wrong_profiles["screen_rotation"] = []
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(bundle_text(profile_groups=wrong_profiles)),
        "WEB_DEVICE_PROFILES",
    )


def test_generated_device_metadata_rejects_unknown_profile() -> None:
    wrong_profiles = dict(web_device_profiles())
    wrong_profiles["screen_rotation"] = [*wrong_profiles["screen_rotation"], "old-device"]
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(bundle_text(profile_groups=wrong_profiles)),
        "unknown profile",
    )


def test_generated_device_metadata_rejects_profile_group_non_list() -> None:
    wrong_profiles = dict(web_device_profiles())
    wrong_profiles["screen_rotation"] = {"device": True}
    run_fails(
        lambda: check_webserver_bundle.check_generated_device_metadata(bundle_text(profile_groups=wrong_profiles)),
        "must be a list of strings",
    )


def test_json_assignment_requires_assignment() -> None:
    run_fails(
        lambda: check_webserver_bundle.parse_json_assignment("var OTHER = {};", "FIRMWARE_MANIFEST_SLUGS"),
        "Expected exactly one FIRMWARE_MANIFEST_SLUGS assignment",
    )


def test_json_assignment_rejects_duplicate_assignment() -> None:
    run_fails(
        lambda: check_webserver_bundle.parse_json_assignment(
            'var FIRMWARE_MANIFEST_SLUGS = {"first": "slug"};\n'
            'var FIRMWARE_MANIFEST_SLUGS = {"second": "slug"};\n',
            "FIRMWARE_MANIFEST_SLUGS",
        ),
        "found 2",
    )


def test_string_assignment_rejects_duplicate_assignment() -> None:
    run_fails(
        lambda: check_webserver_bundle.parse_string_assignment(
            'var FIRMWARE_PUBLIC_MANIFEST_BASE = "https://example.invalid/one/";\n'
            'var FIRMWARE_PUBLIC_MANIFEST_BASE = "https://example.invalid/two/";\n',
            "FIRMWARE_PUBLIC_MANIFEST_BASE",
        ),
        "found 2",
    )


def test_placeholder_list_comes_from_generator_tokens() -> None:
    assert check_webserver_bundle.PLACEHOLDERS is generate_webserver.TOKENS


def main() -> int:
    test_generated_device_metadata_passes_for_product_model_values()
    test_generated_device_metadata_rejects_wrong_manifest_slug()
    test_generated_device_metadata_rejects_manifest_slug_list()
    test_generated_device_metadata_rejects_manifest_slug_non_string_value()
    test_generated_device_metadata_rejects_wrong_public_base_url()
    test_generated_device_metadata_rejects_wrong_profile_groups()
    test_generated_device_metadata_rejects_unknown_profile()
    test_generated_device_metadata_rejects_profile_group_non_list()
    test_json_assignment_requires_assignment()
    test_json_assignment_rejects_duplicate_assignment()
    test_string_assignment_rejects_duplicate_assignment()
    test_placeholder_list_comes_from_generator_tokens()
    print("Webserver bundle regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
