#!/usr/bin/env python3
"""Validate speaker grouping slot widget IDs stay aligned."""

from __future__ import annotations

import re
from pathlib import Path

import firmware_release


ROOT = Path(__file__).resolve().parent.parent
SPEAKER_GROUP = ROOT / "common" / "addon" / "speaker_group.yaml"
SLOT_COUNT = 16
COMMON_ARRAY_PREFIXES = (
    "speaker_card",
    "speaker_name",
    "speaker_vol_label",
    "speaker_btns",
)
DEVICE_PREFIXES = (*COMMON_ARRAY_PREFIXES, "speaker_top")


class SpeakerGroupSlotError(RuntimeError):
    pass


def read(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise SpeakerGroupSlotError(f"Missing file: {path.relative_to(ROOT)}") from exc


def active_yaml_and_lambda_text(text: str) -> str:
    active_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        without_cpp_comment = stripped.split("//", 1)[0].rstrip()
        if without_cpp_comment:
            active_lines.append(without_cpp_comment)
    return "\n".join(active_lines)


def id_slots(text: str, prefix: str) -> set[int]:
    return {int(match) for match in re.findall(rf"\b{re.escape(prefix)}_(\d+)\b", text)}


def slot_counts(text: str, prefix: str) -> dict[int, int]:
    counts: dict[int, int] = {}
    for match in re.findall(rf"\b{re.escape(prefix)}_(\d+)\b", text):
        slot = int(match)
        counts[slot] = counts.get(slot, 0) + 1
    return counts


def expect_slots(path: Path, text: str, prefix: str, expected: set[int]) -> None:
    counts = slot_counts(text, prefix)
    actual = set(counts)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"extra {extra}")
        raise SpeakerGroupSlotError(f"{path.relative_to(ROOT)} {prefix} slots are wrong: {', '.join(details)}")
    duplicates = {slot: count for slot, count in counts.items() if count > 1}
    if duplicates:
        details = ", ".join(f"{prefix}_{slot} ({count})" for slot, count in sorted(duplicates.items()))
        raise SpeakerGroupSlotError(f"{path.relative_to(ROOT)} {prefix} slots are duplicated: {details}")


def check_common_arrays() -> None:
    text = active_yaml_and_lambda_text(read(SPEAKER_GROUP))
    expected = set(range(SLOT_COUNT))
    for prefix in COMMON_ARRAY_PREFIXES:
        expect_slots(SPEAKER_GROUP, text, prefix, expected)

    expect_slots(SPEAKER_GROUP, text, "speaker_top", set(range(1, SLOT_COUNT)))
    if "nullptr, id(speaker_top_1)" not in text:
        raise SpeakerGroupSlotError(f"{SPEAKER_GROUP.relative_to(ROOT)} tops array must keep slot 0 as nullptr")
    if f"for (int i = 0; i < {SLOT_COUNT}; i++)" not in text:
        raise SpeakerGroupSlotError(f"{SPEAKER_GROUP.relative_to(ROOT)} must iterate {SLOT_COUNT} speaker slots")


def check_device_layouts() -> None:
    full_slots = set(range(SLOT_COUNT))
    top_slots = set(range(1, SLOT_COUNT))
    for device in firmware_release.DEVICES:
        path = ROOT / "devices" / device.config / "device" / "lvgl.yaml"
        text = active_yaml_and_lambda_text(read(path))
        for prefix in DEVICE_PREFIXES:
            expected = top_slots if prefix == "speaker_top" else full_slots
            expect_slots(path, text, prefix, expected)


def main() -> int:
    check_common_arrays()
    check_device_layouts()
    print("Speaker group slot checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
