#!/usr/bin/env python3
"""Regression tests for scripts/audit_device_text.py."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import audit_device_text


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def with_root():
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    original_root = audit_device_text.ROOT
    original_output = audit_device_text.OUTPUT
    original_search_dirs = audit_device_text.SEARCH_DIRS
    audit_device_text.ROOT = root
    audit_device_text.OUTPUT = root / "docs" / "development" / "device-text-audit.md"
    audit_device_text.SEARCH_DIRS = (
        root / "common" / "setup",
        root / "common" / "device",
        root / "common" / "addon",
        root / "devices",
    )
    return tmp, root, original_root, original_output, original_search_dirs


def restore(original_root, original_output, original_search_dirs) -> None:
    audit_device_text.ROOT = original_root
    audit_device_text.OUTPUT = original_output
    audit_device_text.SEARCH_DIRS = original_search_dirs


def test_collect_text_excludes_non_user_visible_values() -> None:
    tmp, root, original_root, original_output, original_search_dirs = with_root()
    try:
        write(
            root / "common" / "setup" / "screen.yaml",
            '\n'.join(
                (
                    'text: "WiFi Setup"',
                    "text: 'Home Assistant'",
                    "text: Starting up",
                    'text: ""',
                    'text: "0:00"',
                    'text: "${icon_wifi}"',
                    "text: $icon_wifi",
                    'text: "http://..."',
                    "text: !lambda 'return x;'",
                )
            ),
        )
        entries = audit_device_text.collect_text()
    finally:
        restore(original_root, original_output, original_search_dirs)
        tmp.cleanup()

    assert entries == {
        "Home Assistant": ["common/setup/screen.yaml:2"],
        "Starting up": ["common/setup/screen.yaml:3"],
        "WiFi Setup": ["common/setup/screen.yaml:1"],
    }


def test_collect_text_excludes_esphome_cache() -> None:
    tmp, root, original_root, original_output, original_search_dirs = with_root()
    try:
        write(root / "devices" / "panel" / "device" / "lvgl.yaml", 'text: "Volume"\n')
        write(root / "devices" / "panel" / ".esphome" / "external_components" / "cache" / "lvgl.yaml", 'text: "Cached"\n')
        entries = audit_device_text.collect_text()
    finally:
        restore(original_root, original_output, original_search_dirs)
        tmp.cleanup()

    assert entries == {"Volume": ["devices/panel/device/lvgl.yaml:1"]}


def test_collect_text_keeps_hash_inside_quoted_text() -> None:
    tmp, root, original_root, original_output, original_search_dirs = with_root()
    try:
        write(
            root / "common" / "setup" / "screen.yaml",
            'text: "Pair #1 speaker"\n'
            "text: 'Zone #2'\n"
            'text: "Ignored text" # setup note\n',
        )
        entries = audit_device_text.collect_text()
    finally:
        restore(original_root, original_output, original_search_dirs)
        tmp.cleanup()

    assert entries == {
        "Ignored text": ["common/setup/screen.yaml:3"],
        "Pair #1 speaker": ["common/setup/screen.yaml:1"],
        "Zone #2": ["common/setup/screen.yaml:2"],
    }


def test_render_markdown_escapes_multiline_headings() -> None:
    text = audit_device_text.render_markdown({"Line one\nLine two": ["common/setup/example.yaml:7"]})
    assert "## Line one\\nLine two" in text
    assert "- `common/setup/example.yaml:7`" in text


def main() -> int:
    test_collect_text_excludes_non_user_visible_values()
    test_collect_text_excludes_esphome_cache()
    test_collect_text_keeps_hash_inside_quoted_text()
    test_render_markdown_escapes_multiline_headings()
    print("Device text audit regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
