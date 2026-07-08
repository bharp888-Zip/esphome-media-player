#!/usr/bin/env python3
"""Regression tests for scripts/check_speaker_group_slots.py."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import check_speaker_group_slots
import firmware_release


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def common_arrays() -> str:
    full = ", ".join(f"id(speaker_card_{i})" for i in range(16))
    names = ", ".join(f"id(speaker_name_{i})" for i in range(16))
    labels = ", ".join(f"id(speaker_vol_label_{i})" for i in range(16))
    buttons = ", ".join(f"id(speaker_btns_{i})" for i in range(16))
    tops = "nullptr, " + ", ".join(f"id(speaker_top_{i})" for i in range(1, 16))
    return (
        f"lv_obj_t *cards[] = {{{full}}};\n"
        f"lv_obj_t *name_labels[] = {{{names}}};\n"
        f"lv_obj_t *vol_labels[] = {{{labels}}};\n"
        f"lv_obj_t *btns[] = {{{buttons}}};\n"
        f"lv_obj_t *tops[] = {{{tops}}};\n"
        "for (int i = 0; i < 16; i++) {}\n"
    )


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_speaker_group_slots.SpeakerGroupSlotError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def with_root():
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    original_root = check_speaker_group_slots.ROOT
    original_speaker_group = check_speaker_group_slots.SPEAKER_GROUP
    check_speaker_group_slots.ROOT = root
    check_speaker_group_slots.SPEAKER_GROUP = root / "common" / "addon" / "speaker_group.yaml"
    return tmp, root, original_root, original_speaker_group


def restore_root(original_root: Path, original_speaker_group: Path) -> None:
    check_speaker_group_slots.ROOT = original_root
    check_speaker_group_slots.SPEAKER_GROUP = original_speaker_group


def test_common_missing_slot_fails() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        write(
            root / "common" / "addon" / "speaker_group.yaml",
            common_arrays().replace("id(speaker_btns_15)", ""),
        )
        run_fails(check_speaker_group_slots.check_common_arrays, "speaker_btns slots are wrong")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def test_common_duplicate_slot_fails() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        write(
            root / "common" / "addon" / "speaker_group.yaml",
            common_arrays().replace("id(speaker_card_15)", "id(speaker_card_15), id(speaker_card_15)"),
        )
        run_fails(check_speaker_group_slots.check_common_arrays, "speaker_card slots are duplicated")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def test_common_commented_slot_does_not_count() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        write(
            root / "common" / "addon" / "speaker_group.yaml",
            common_arrays().replace("id(speaker_btns_15)", "/* removed */") + "\n// id(speaker_btns_15)\n",
        )
        run_fails(check_speaker_group_slots.check_common_arrays, "speaker_btns slots are wrong")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def test_common_duplicate_top_slot_fails() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        write(
            root / "common" / "addon" / "speaker_group.yaml",
            common_arrays().replace("id(speaker_top_15)", "id(speaker_top_15), id(speaker_top_15)"),
        )
        run_fails(check_speaker_group_slots.check_common_arrays, "speaker_top slots are duplicated")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def test_device_missing_slot_fails() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        device = firmware_release.DEVICES[0]
        layout = "\n".join(
            f"id: speaker_card_{i}\nid: speaker_name_{i}\nid: speaker_vol_label_{i}\nid: speaker_btns_{i}"
            for i in range(16)
        )
        layout += "\n" + "\n".join(f"id: speaker_top_{i}" for i in range(1, 15))
        write(root / "devices" / device.config / "device" / "lvgl.yaml", layout)
        run_fails(check_speaker_group_slots.check_device_layouts, "speaker_top slots are wrong")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def test_device_commented_slot_does_not_count() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        device = firmware_release.DEVICES[0]
        layout = "\n".join(
            f"id: speaker_card_{i}\nid: speaker_name_{i}\nid: speaker_vol_label_{i}\nid: speaker_btns_{i}"
            for i in range(15)
        )
        layout += "\nid: speaker_card_15\nid: speaker_name_15\nid: speaker_vol_label_15\n# id: speaker_btns_15\n"
        layout += "\n" + "\n".join(f"id: speaker_top_{i}" for i in range(1, 16))
        write(root / "devices" / device.config / "device" / "lvgl.yaml", layout)
        run_fails(check_speaker_group_slots.check_device_layouts, "speaker_btns slots are wrong")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def test_device_duplicate_slot_fails() -> None:
    tmp, root, original_root, original_speaker_group = with_root()
    try:
        device = firmware_release.DEVICES[0]
        layout = "\n".join(
            f"id: speaker_card_{i}\nid: speaker_name_{i}\nid: speaker_vol_label_{i}\nid: speaker_btns_{i}"
            for i in range(16)
        )
        layout += "\nid: speaker_card_15\n"
        layout += "\n" + "\n".join(f"id: speaker_top_{i}" for i in range(1, 16))
        write(root / "devices" / device.config / "device" / "lvgl.yaml", layout)
        run_fails(check_speaker_group_slots.check_device_layouts, "speaker_card slots are duplicated")
    finally:
        restore_root(original_root, original_speaker_group)
        tmp.cleanup()


def main() -> int:
    test_common_missing_slot_fails()
    test_common_duplicate_slot_fails()
    test_common_commented_slot_does_not_count()
    test_common_duplicate_top_slot_fails()
    test_device_missing_slot_fails()
    test_device_commented_slot_does_not_count()
    test_device_duplicate_slot_fails()
    print("Speaker group slot regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
