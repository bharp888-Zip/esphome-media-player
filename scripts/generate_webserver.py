#!/usr/bin/env python3
"""Build the custom ESPHome web server JavaScript bundle."""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import sys

from product_model import (
    firmware_manifest_slugs,
    web_device_profiles,
    web_setting_default,
    web_setting_options,
    web_settings_entities,
    web_settings_number_limits,
    web_settings_state,
)


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "docs" / "webserver" / "src"
STYLE_PATH = SRC_DIR / "style.css"
TEMPLATE_PATH = SRC_DIR / "app.template.js"
SETTINGS_TEMPLATE_PATH = SRC_DIR / "settings.template.js"
DEVICE_PROFILES_TEMPLATE_PATH = SRC_DIR / "device_profiles.template.js"
API_TEMPLATE_PATH = SRC_DIR / "api.template.js"
UI_SECTIONS_TEMPLATE_PATH = SRC_DIR / "ui_sections.template.js"
FORMATTERS_TEMPLATE_PATH = SRC_DIR / "formatters.template.js"
CONTROLS_TEMPLATE_PATH = SRC_DIR / "controls.template.js"
FIRMWARE_TEMPLATE_PATH = SRC_DIR / "firmware.template.js"
RUNTIME_TEMPLATE_PATH = SRC_DIR / "runtime.template.js"
OUT_PATH = ROOT / "docs" / "public" / "webserver" / "app.js"
TOKENS = (
    "__MEDIA_PLAYER_CSS__",
    "__SETTINGS_SCHEMA__",
    "__DEVICE_PROFILE_HELPERS__",
    "__API_HELPERS__",
    "__APP_UI__",
    "__UI_FORMATTERS__",
    "__UI_CONTROLS__",
    "__FIRMWARE_HELPERS__",
    "__APP_RUNTIME_HELPERS__",
    "__FIRMWARE_MANIFEST_SLUGS__",
    "__WEB_DEVICE_PROFILES__",
    "__DEFAULT_SPEAKER_PANEL_TIMEOUT__",
    "__WEB_SETTING_OPTIONS__",
    "__WEB_SETTINGS_STATE__",
    "__WEB_SETTINGS_ENTITIES__",
    "__WEB_SETTINGS_NUMBER_LIMITS__",
)


class WebserverGenerationError(RuntimeError):
    pass


def partial_templates() -> tuple[tuple[str, Path], ...]:
    return (
        ("__SETTINGS_SCHEMA__", SETTINGS_TEMPLATE_PATH),
        ("__DEVICE_PROFILE_HELPERS__", DEVICE_PROFILES_TEMPLATE_PATH),
        ("__API_HELPERS__", API_TEMPLATE_PATH),
        ("__APP_UI__", UI_SECTIONS_TEMPLATE_PATH),
        ("__UI_FORMATTERS__", FORMATTERS_TEMPLATE_PATH),
        ("__UI_CONTROLS__", CONTROLS_TEMPLATE_PATH),
        ("__FIRMWARE_HELPERS__", FIRMWARE_TEMPLATE_PATH),
        ("__APP_RUNTIME_HELPERS__", RUNTIME_TEMPLATE_PATH),
    )


def validate_source_templates() -> None:
    partials = partial_templates()
    partial_tokens = [token for token, _path in partials]
    duplicate_tokens = sorted({token for token in partial_tokens if partial_tokens.count(token) > 1})
    if duplicate_tokens:
        raise WebserverGenerationError(
            f"Duplicate webserver partial token(s): {', '.join(duplicate_tokens)}"
        )

    partial_names = [path.name for _token, path in partials]
    duplicate_names = sorted({name for name in partial_names if partial_names.count(name) > 1})
    if duplicate_names:
        raise WebserverGenerationError(
            f"Duplicate webserver partial template file(s): {', '.join(duplicate_names)}"
        )

    expected_templates = {TEMPLATE_PATH.name, *partial_names}
    actual_templates = {path.name for path in SRC_DIR.glob("*.template.js")}
    missing = sorted(expected_templates - actual_templates)
    extra = sorted(actual_templates - expected_templates)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected: {', '.join(extra)}")
        raise WebserverGenerationError(f"Webserver template source mismatch ({'; '.join(details)})")


def validate_replacement_tokens(replacements: dict[str, str]) -> None:
    duplicate_required_tokens = sorted({token for token in TOKENS if TOKENS.count(token) > 1})
    if duplicate_required_tokens:
        raise WebserverGenerationError(
            f"Duplicate webserver template token(s): {', '.join(duplicate_required_tokens)}"
        )

    replacement_tokens = set(replacements)
    required_tokens = set(TOKENS)
    missing = sorted(required_tokens - replacement_tokens)
    extra = sorted(replacement_tokens - required_tokens)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing replacement(s): {', '.join(missing)}")
        if extra:
            details.append(f"unexpected replacement(s): {', '.join(extra)}")
        raise WebserverGenerationError(f"Webserver replacement tokens do not match template tokens ({'; '.join(details)})")


def js_literal(value: object) -> str:
    return json.dumps(value, separators=(",", ":"))


def build_bundle() -> str:
    validate_source_templates()
    css = STYLE_PATH.read_text().rstrip("\n")
    template = TEMPLATE_PATH.read_text()
    partial_replacements = {
        token: path.read_text().rstrip("\n")
        for token, path in partial_templates()
    }
    wrong_partial_counts = {
        token: template.count(token)
        for token in partial_replacements
        if template.count(token) != 1
    }
    if wrong_partial_counts:
        details = ", ".join(f"{token} ({count})" for token, count in wrong_partial_counts.items())
        raise WebserverGenerationError(f"Template partial token count must be exactly one: {details}")
    for token, value in partial_replacements.items():
        template = template.replace(token, value)

    replacements = {
        "__MEDIA_PLAYER_CSS__": js_literal(css),
        "__FIRMWARE_MANIFEST_SLUGS__": js_literal(firmware_manifest_slugs()),
        "__WEB_DEVICE_PROFILES__": js_literal(web_device_profiles()),
        "__DEFAULT_SPEAKER_PANEL_TIMEOUT__": js_literal(web_setting_default("speaker_panel_timeout")),
        "__WEB_SETTING_OPTIONS__": js_literal(web_setting_options()),
        "__WEB_SETTINGS_STATE__": js_literal(web_settings_state()),
        "__WEB_SETTINGS_ENTITIES__": js_literal(web_settings_entities()),
        "__WEB_SETTINGS_NUMBER_LIMITS__": js_literal(web_settings_number_limits()),
    }
    replacements.update(partial_replacements)
    validate_replacement_tokens(replacements)
    data_tokens = set(TOKENS) - set(partial_replacements)
    wrong_counts = {token: template.count(token) for token in data_tokens if template.count(token) != 1}
    if wrong_counts:
        details = ", ".join(f"{token} ({count})" for token, count in wrong_counts.items())
        raise WebserverGenerationError(f"Template token count must be exactly one: {details}")

    for token, value in replacements.items():
        template = template.replace(token, value)
    leaked = [token for token in TOKENS if token in template]
    if leaked:
        raise WebserverGenerationError(f"Generated bundle still contains token(s): {', '.join(leaked)}")
    return template


def write_or_check(path: Path, content: str, check: bool) -> bool:
    old = path.read_text() if path.exists() else ""
    if old == content:
        return False
    if check:
        rel = path.relative_to(ROOT)
        diff = "".join(
            difflib.unified_diff(
                old.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"{rel} (current)",
                tofile=f"{rel} (generated)",
            )
        )
        print(diff, file=sys.stderr)
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated bundle is stale")
    args = parser.parse_args()

    try:
        changed = write_or_check(OUT_PATH, build_bundle(), args.check)
        if args.check and changed:
            print("Generated web server bundle is stale. Run `npm run webserver:build`.", file=sys.stderr)
            return 1
        return 0
    except WebserverGenerationError as exc:
        print(f"Webserver generation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
