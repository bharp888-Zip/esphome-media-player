#!/usr/bin/env python3
"""Regression tests for scripts/check_lvgl_ids.py."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import check_lvgl_ids


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_lvgl_ids.LvglIdCheckError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def test_validate_device_ids_accepts_shared_ids_and_optional_track_variants() -> None:
    check_lvgl_ids.validate_device_ids(
        {
            "landscape": {*check_lvgl_ids.REQUIRED_SHARED_IDS, "play_btn", "volume_slider", "track_info_panel"},
            "square": {*check_lvgl_ids.REQUIRED_SHARED_IDS, "play_btn", "volume_slider", "track_info_text"},
        }
    )


def test_validate_device_ids_rejects_missing_shared_id() -> None:
    run_fails(
        lambda: check_lvgl_ids.validate_device_ids(
            {
                "complete": {*check_lvgl_ids.REQUIRED_SHARED_IDS, "play_btn", "volume_slider", "track_info_panel"},
                "missing": {*check_lvgl_ids.REQUIRED_SHARED_IDS, "play_btn", "track_info_text"},
            }
        ),
        "volume_slider",
    )


def test_validate_device_ids_rejects_missing_required_core_id() -> None:
    ids = set(check_lvgl_ids.REQUIRED_SHARED_IDS)
    ids.add("track_info_panel")
    ids.remove("media_play_pause_button")
    run_fails(
        lambda: check_lvgl_ids.validate_device_ids({"missing-core-control": ids}),
        "media_play_pause_button",
    )


def test_validate_device_ids_rejects_missing_track_info_widget() -> None:
    ids = set(check_lvgl_ids.REQUIRED_SHARED_IDS)
    run_fails(
        lambda: check_lvgl_ids.validate_device_ids({"no-track": ids}),
        "must define either track_info_panel or track_info_text",
    )


def test_validate_device_ids_rejects_empty_input() -> None:
    run_fails(lambda: check_lvgl_ids.validate_device_ids({}), "No supported devices found")


def test_validate_no_duplicate_ids_rejects_copied_widget_ids() -> None:
    run_fails(
        lambda: check_lvgl_ids.validate_no_duplicate_ids(
            {
                "copied-layout": ["play_btn", "volume_slider", "play_btn"],
                "clean-layout": ["play_btn", "volume_slider", "track_info_panel"],
            }
        ),
        "copied-layout defines duplicate LVGL id(s): play_btn",
    )


def test_extract_id_list_ignores_action_target_ids() -> None:
    tmp = TemporaryDirectory()
    try:
        path = Path(tmp.name) / "lvgl.yaml"
        path.write_text(
            "lvgl:\n"
            "  id: main_lvgl\n"
            "  pages:\n"
            "    - id: main_page\n"
            "      widgets:\n"
            "        - arc:\n"
            "            id: volume_arc\n"
            "            on_value:\n"
            "              - lvgl.label.update:\n"
            "                  id: volume_pct_label\n"
            "        - label:\n"
            "            id: volume_pct_label\n"
            "        - button:\n"
            "            on_click:\n"
            "              - script.execute:\n"
            "                  id: speaker_toggle\n"
        )
        assert check_lvgl_ids.extract_id_list(path) == [
            "main_lvgl",
            "main_page",
            "volume_arc",
            "volume_pct_label",
        ]
    finally:
        tmp.cleanup()


def test_extract_id_list_ignores_commented_widget_ids() -> None:
    tmp = TemporaryDirectory()
    try:
        path = Path(tmp.name) / "lvgl.yaml"
        path.write_text(
            "lvgl:\n"
            "  pages:\n"
            "    - id: main_page # active page id\n"
            "      widgets:\n"
            "        - label:\n"
            "            # id: stale_label\n"
            "            id: active_label # active widget id\n"
        )
        assert check_lvgl_ids.extract_id_list(path) == ["main_page", "active_label"]
    finally:
        tmp.cleanup()


def main() -> int:
    test_validate_device_ids_accepts_shared_ids_and_optional_track_variants()
    test_validate_device_ids_rejects_missing_shared_id()
    test_validate_device_ids_rejects_missing_required_core_id()
    test_validate_device_ids_rejects_missing_track_info_widget()
    test_validate_device_ids_rejects_empty_input()
    test_validate_no_duplicate_ids_rejects_copied_widget_ids()
    test_extract_id_list_ignores_action_target_ids()
    test_extract_id_list_ignores_commented_widget_ids()
    print("LVGL id regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
