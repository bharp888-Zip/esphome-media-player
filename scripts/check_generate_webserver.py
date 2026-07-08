#!/usr/bin/env python3
"""Regression tests for scripts/generate_webserver.py."""

from __future__ import annotations

from pathlib import Path
import re
from tempfile import TemporaryDirectory

import generate_webserver


FUNCTION_RE = re.compile(r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
REMOVED_STALE_CSS_SELECTORS = (
    ".number-row",
    ".suffix",
    ".grid-2",
    ".status-list",
    ".status-row",
    ".status-value",
    ".dot",
    ".section-title",
    ".setting-divider",
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def with_root():
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    originals = {
        "ROOT": generate_webserver.ROOT,
        "SRC_DIR": generate_webserver.SRC_DIR,
        "STYLE_PATH": generate_webserver.STYLE_PATH,
        "TEMPLATE_PATH": generate_webserver.TEMPLATE_PATH,
        "SETTINGS_TEMPLATE_PATH": generate_webserver.SETTINGS_TEMPLATE_PATH,
        "DEVICE_PROFILES_TEMPLATE_PATH": generate_webserver.DEVICE_PROFILES_TEMPLATE_PATH,
        "API_TEMPLATE_PATH": generate_webserver.API_TEMPLATE_PATH,
        "UI_SECTIONS_TEMPLATE_PATH": generate_webserver.UI_SECTIONS_TEMPLATE_PATH,
        "FORMATTERS_TEMPLATE_PATH": generate_webserver.FORMATTERS_TEMPLATE_PATH,
        "CONTROLS_TEMPLATE_PATH": generate_webserver.CONTROLS_TEMPLATE_PATH,
        "FIRMWARE_TEMPLATE_PATH": generate_webserver.FIRMWARE_TEMPLATE_PATH,
        "RUNTIME_TEMPLATE_PATH": generate_webserver.RUNTIME_TEMPLATE_PATH,
        "OUT_PATH": generate_webserver.OUT_PATH,
    }
    src = root / "docs" / "webserver" / "src"
    generate_webserver.ROOT = root
    generate_webserver.SRC_DIR = src
    generate_webserver.STYLE_PATH = src / "style.css"
    generate_webserver.TEMPLATE_PATH = src / "app.template.js"
    generate_webserver.SETTINGS_TEMPLATE_PATH = src / "settings.template.js"
    generate_webserver.DEVICE_PROFILES_TEMPLATE_PATH = src / "device_profiles.template.js"
    generate_webserver.API_TEMPLATE_PATH = src / "api.template.js"
    generate_webserver.UI_SECTIONS_TEMPLATE_PATH = src / "ui_sections.template.js"
    generate_webserver.FORMATTERS_TEMPLATE_PATH = src / "formatters.template.js"
    generate_webserver.CONTROLS_TEMPLATE_PATH = src / "controls.template.js"
    generate_webserver.FIRMWARE_TEMPLATE_PATH = src / "firmware.template.js"
    generate_webserver.RUNTIME_TEMPLATE_PATH = src / "runtime.template.js"
    generate_webserver.OUT_PATH = root / "docs" / "public" / "webserver" / "app.js"
    return tmp, root, originals


def restore(originals: dict[str, Path]) -> None:
    for name, value in originals.items():
        setattr(generate_webserver, name, value)


def write_fixture(root: Path, missing_token: str | None = None, duplicate_token: str | None = None) -> None:
    write(root / "docs" / "webserver" / "src" / "style.css", ".app { color: red; }\n")
    tokens = [token for token in generate_webserver.TOKENS if token != missing_token]
    if duplicate_token is not None:
        tokens.append(duplicate_token)
    write(root / "docs" / "webserver" / "src" / "app.template.js", "\n".join(tokens) + "\n")
    write(root / "docs" / "webserver" / "src" / "settings.template.js", "var settingsFixture = true;\n")
    write(root / "docs" / "webserver" / "src" / "device_profiles.template.js", "function profileFixture() {}\n")
    write(root / "docs" / "webserver" / "src" / "api.template.js", "function apiFixture() {}\n")
    write(root / "docs" / "webserver" / "src" / "ui_sections.template.js", "function uiFixture() {}\n")
    write(root / "docs" / "webserver" / "src" / "formatters.template.js", "function formattersFixture() {}\n")
    write(root / "docs" / "webserver" / "src" / "controls.template.js", "function controlsFixture() {}\n")
    write(root / "docs" / "webserver" / "src" / "firmware.template.js", "function firmwareFixture() {}\n")
    write(root / "docs" / "webserver" / "src" / "runtime.template.js", "function runtimeFixture() {}\n")


def run_fails(func, expected: str) -> None:
    try:
        func()
    except generate_webserver.WebserverGenerationError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def unused_template_functions(src_dir: Path) -> list[str]:
    sources = {
        path: path.read_text()
        for path in sorted(src_dir.glob("*.template.js"))
    }
    combined = "\n".join(sources.values())
    unused: list[str] = []
    for path, text in sources.items():
        for match in FUNCTION_RE.finditer(text):
            name = match.group(1)
            references = re.findall(rf"\b{re.escape(name)}\b", combined)
            if len(references) <= 1:
                unused.append(f"{path.name}:{name}")
    return unused


def stale_css_selectors(css_text: str) -> list[str]:
    return [
        selector
        for selector in REMOVED_STALE_CSS_SELECTORS
        if re.search(rf"{re.escape(selector)}(?:[^A-Za-z0-9_-]|$)", css_text)
    ]


def test_build_bundle_replaces_all_template_tokens() -> None:
    tmp, root, originals = with_root()
    try:
        write_fixture(root)
        text = generate_webserver.build_bundle()
    finally:
        restore(originals)
        tmp.cleanup()

    assert "var settingsFixture = true;" in text
    assert "function profileFixture() {}" in text
    assert "function apiFixture() {}" in text
    assert "function uiFixture() {}" in text
    assert "function formattersFixture() {}" in text
    assert "function controlsFixture() {}" in text
    assert "function firmwareFixture() {}" in text
    assert "function runtimeFixture() {}" in text
    assert not any(token in text for token in generate_webserver.TOKENS)


def test_build_bundle_fails_when_template_token_is_missing() -> None:
    tmp, root, originals = with_root()
    try:
        write_fixture(root, missing_token="__API_HELPERS__")
        run_fails(generate_webserver.build_bundle, "__API_HELPERS__")
    finally:
        restore(originals)
        tmp.cleanup()


def test_build_bundle_fails_when_template_token_is_duplicated() -> None:
    tmp, root, originals = with_root()
    try:
        write_fixture(root, duplicate_token="__API_HELPERS__")
        run_fails(generate_webserver.build_bundle, "__API_HELPERS__ (2)")
    finally:
        restore(originals)
        tmp.cleanup()


def test_build_bundle_fails_when_partial_template_is_unreferenced() -> None:
    tmp, root, originals = with_root()
    try:
        write_fixture(root)
        write(root / "docs" / "webserver" / "src" / "unused.template.js", "function unusedFixture() {}\n")
        run_fails(generate_webserver.build_bundle, "unexpected: unused.template.js")
    finally:
        restore(originals)
        tmp.cleanup()


def test_build_bundle_fails_when_partial_token_is_duplicated() -> None:
    tmp, root, originals = with_root()
    original_partials = generate_webserver.partial_templates
    try:
        write_fixture(root)
        generate_webserver.partial_templates = lambda: (
            ("__SETTINGS_SCHEMA__", generate_webserver.SETTINGS_TEMPLATE_PATH),
            ("__SETTINGS_SCHEMA__", generate_webserver.DEVICE_PROFILES_TEMPLATE_PATH),
            ("__API_HELPERS__", generate_webserver.API_TEMPLATE_PATH),
            ("__APP_UI__", generate_webserver.UI_SECTIONS_TEMPLATE_PATH),
            ("__UI_FORMATTERS__", generate_webserver.FORMATTERS_TEMPLATE_PATH),
            ("__UI_CONTROLS__", generate_webserver.CONTROLS_TEMPLATE_PATH),
            ("__FIRMWARE_HELPERS__", generate_webserver.FIRMWARE_TEMPLATE_PATH),
            ("__APP_RUNTIME_HELPERS__", generate_webserver.RUNTIME_TEMPLATE_PATH),
        )
        run_fails(generate_webserver.build_bundle, "Duplicate webserver partial token")
    finally:
        generate_webserver.partial_templates = original_partials
        restore(originals)
        tmp.cleanup()


def test_build_bundle_fails_when_partial_file_is_duplicated() -> None:
    tmp, root, originals = with_root()
    original_partials = generate_webserver.partial_templates
    try:
        write_fixture(root)
        generate_webserver.partial_templates = lambda: (
            ("__SETTINGS_SCHEMA__", generate_webserver.SETTINGS_TEMPLATE_PATH),
            ("__DEVICE_PROFILE_HELPERS__", generate_webserver.SETTINGS_TEMPLATE_PATH),
            ("__API_HELPERS__", generate_webserver.API_TEMPLATE_PATH),
            ("__APP_UI__", generate_webserver.UI_SECTIONS_TEMPLATE_PATH),
            ("__UI_FORMATTERS__", generate_webserver.FORMATTERS_TEMPLATE_PATH),
            ("__UI_CONTROLS__", generate_webserver.CONTROLS_TEMPLATE_PATH),
            ("__FIRMWARE_HELPERS__", generate_webserver.FIRMWARE_TEMPLATE_PATH),
            ("__APP_RUNTIME_HELPERS__", generate_webserver.RUNTIME_TEMPLATE_PATH),
        )
        run_fails(generate_webserver.build_bundle, "Duplicate webserver partial template file")
    finally:
        generate_webserver.partial_templates = original_partials
        restore(originals)
        tmp.cleanup()


def test_partial_template_tokens_are_required_tokens() -> None:
    partial_tokens = {token for token, _ in generate_webserver.partial_templates()}
    missing = partial_tokens - set(generate_webserver.TOKENS)
    assert not missing, missing


def test_replacement_tokens_must_cover_required_tokens() -> None:
    replacements = {token: "" for token in generate_webserver.TOKENS if token != "__API_HELPERS__"}
    run_fails(
        lambda: generate_webserver.validate_replacement_tokens(replacements),
        "missing replacement(s): __API_HELPERS__",
    )


def test_replacement_tokens_reject_duplicate_required_tokens() -> None:
    original_tokens = generate_webserver.TOKENS
    try:
        generate_webserver.TOKENS = (*original_tokens, "__API_HELPERS__")
        replacements = {token: "" for token in original_tokens}
        run_fails(
            lambda: generate_webserver.validate_replacement_tokens(replacements),
            "Duplicate webserver template token(s): __API_HELPERS__",
        )
    finally:
        generate_webserver.TOKENS = original_tokens


def test_replacement_tokens_reject_unexpected_tokens() -> None:
    replacements = {token: "" for token in generate_webserver.TOKENS}
    replacements["__UNUSED_PARTIAL__"] = ""
    run_fails(
        lambda: generate_webserver.validate_replacement_tokens(replacements),
        "unexpected replacement(s): __UNUSED_PARTIAL__",
    )


def test_unused_template_function_detection() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "app.template.js", "function usedFixture() {}\nusedFixture();\nfunction deadFixture() {}\n")
        assert unused_template_functions(root) == ["app.template.js:deadFixture"]
    finally:
        tmp.cleanup()


def test_webserver_template_functions_are_referenced() -> None:
    unused = unused_template_functions(generate_webserver.SRC_DIR)
    assert not unused, f"Unused webserver template function(s): {', '.join(unused)}"


def test_stale_css_selector_detection() -> None:
    css = ".active{display:block}.number-row{display:grid}.status-row span{color:red}"
    assert stale_css_selectors(css) == [".number-row", ".status-row"]


def test_removed_stale_css_selectors_stay_removed() -> None:
    stale = stale_css_selectors(generate_webserver.STYLE_PATH.read_text())
    assert not stale, f"Removed stale webserver CSS selector(s) returned: {', '.join(stale)}"


def main() -> int:
    test_build_bundle_replaces_all_template_tokens()
    test_build_bundle_fails_when_template_token_is_missing()
    test_build_bundle_fails_when_template_token_is_duplicated()
    test_build_bundle_fails_when_partial_template_is_unreferenced()
    test_build_bundle_fails_when_partial_token_is_duplicated()
    test_build_bundle_fails_when_partial_file_is_duplicated()
    test_partial_template_tokens_are_required_tokens()
    test_replacement_tokens_must_cover_required_tokens()
    test_replacement_tokens_reject_duplicate_required_tokens()
    test_replacement_tokens_reject_unexpected_tokens()
    test_unused_template_function_detection()
    test_webserver_template_functions_are_referenced()
    test_stale_css_selector_detection()
    test_removed_stale_css_selectors_stay_removed()
    print("Webserver generator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
