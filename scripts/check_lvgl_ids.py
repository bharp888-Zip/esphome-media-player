#!/usr/bin/env python3
"""Validate shared LVGL widget IDs across supported device layouts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from product_model import load_devices


ROOT = Path(__file__).resolve().parent.parent
ID_LINE_RE = re.compile(r"^\s+-?\s*id:\s+([A-Za-z0-9_]+)\s*$")
WIDGET_PARENT_RE = re.compile(
    r"^-\s+(arc|bar|button|buttonmatrix|calendar|canvas|chart|checkbox|dropdown|"
    r"image|keyboard|label|led|line|meter|obj|roller|slider|spinner|spinbox|"
    r"switch|tabview|textarea|tileview):\s*$"
)
OPTIONAL_DEVICE_IDS = {
    # Landscape devices name the track container differently from square/portrait layouts.
    "track_info_panel",
    "track_info_text",
    # JC1060 has icon labels inside the volume buttons.
    "volume_down_icon",
    "volume_up_icon",
}
REQUIRED_SHARED_IDS = (
    "main_page",
    "media_artist_label",
    "media_play_pause_button",
    "media_progress_bar",
    "media_time_label",
    "media_title_label",
    "settings_panel",
    "speakers_close_button",
    "speakers_container",
    "speakers_title_label",
    "group_vol_card",
    "group_vol_label",
    "volume_arc",
    "volume_down_button",
    "volume_pct_label",
    "volume_title_label",
    "volume_up_button",
)


class LvglIdCheckError(RuntimeError):
    pass


def lvgl_path(config: str) -> Path:
    return ROOT / "devices" / config / "device" / "lvgl.yaml"


def extract_id_list(path: Path) -> list[str]:
    try:
        text = path.read_text()
    except FileNotFoundError as exc:
        raise LvglIdCheckError(f"Missing LVGL file: {path.relative_to(ROOT)}") from exc
    ids: list[str] = []
    previous = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        active_line = line.split("#", 1)[0].rstrip()
        active_stripped = active_line.strip()
        match = ID_LINE_RE.match(active_line)
        if match and (previous in {"lvgl:", "pages:"} or WIDGET_PARENT_RE.match(previous)):
            ids.append(match.group(1))
        previous = active_stripped
    return ids


def extract_ids(path: Path) -> set[str]:
    return set(extract_id_list(path))


def duplicate_ids(ids: list[str]) -> list[str]:
    return sorted({widget_id for widget_id in ids if ids.count(widget_id) > 1})


def validate_no_duplicate_ids(device_id_lists: dict[str, list[str]]) -> None:
    failures = [
        f"{config} defines duplicate LVGL id(s): {', '.join(duplicates)}"
        for config, ids in sorted(device_id_lists.items())
        if (duplicates := duplicate_ids(ids))
    ]
    if failures:
        raise LvglIdCheckError("\n".join(failures))


def validate_device_ids(device_ids: dict[str, set[str]]) -> None:
    if not device_ids:
        raise LvglIdCheckError("No supported devices found")

    all_ids = set().union(*device_ids.values())
    required_ids = all_ids - OPTIONAL_DEVICE_IDS
    failures: list[str] = []
    for config, ids in sorted(device_ids.items()):
        missing_required = sorted(set(REQUIRED_SHARED_IDS) - ids)
        if missing_required:
            failures.append(f"{config} is missing required core LVGL id(s): {', '.join(missing_required)}")

        missing = sorted(required_ids - ids)
        if missing:
            failures.append(f"{config} is missing shared LVGL id(s): {', '.join(missing)}")

        if not ({"track_info_panel", "track_info_text"} & ids):
            failures.append(f"{config} must define either track_info_panel or track_info_text")

    if failures:
        raise LvglIdCheckError("\n".join(failures))


def main() -> int:
    try:
        device_id_lists = {device.config: extract_id_list(lvgl_path(device.config)) for device in load_devices()}
        validate_no_duplicate_ids(device_id_lists)
        device_ids = {config: set(ids) for config, ids in device_id_lists.items()}
        validate_device_ids(device_ids)
    except LvglIdCheckError as exc:
        print(f"LVGL id check failed: {exc}", file=sys.stderr)
        return 1

    print("LVGL id checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
