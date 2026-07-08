#!/usr/bin/env python3
"""Validate media-player subscription lifecycle safeguards."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MEDIA_SELECT = ROOT / "common" / "device" / "media_player_select.yaml"
LIFECYCLE_DOC = ROOT / "docs" / "development" / "media-player-subscription-lifecycle.md"


class MediaSubscriptionCheckError(RuntimeError):
    pass


DOC_REQUIREMENTS = (
    "Empty entity values must not reboot the device.",
    "Invalid entity values must not reboot the device",
    "Re-saving the same entity during a reconnect must not register duplicate",
    "Callback generation checks must remain in place",
    "safe reboot",
)
LIFECYCLE_SCRIPTS = (
    "subscribe_media_player",
    "subscribe_linked_media_player",
    "subscribe_day_night_sensor",
)
MEDIA_SELECT_EXECUTE_SCRIPTS = (
    "subscribe_media_player",
    "subscribe_linked_media_player",
)
YAML_REQUIREMENTS = (
    "id: subscription_gen",
    "id: tv_subscription_gen",
    "id: subscribed_media_player_entity",
    "id: subscribed_linked_media_player_entity",
    "id: media_player_entity",
    "id: linked_media_player_entity",
    "id: tv_media_player_entity",
    "App.safe_reboot();",
    "entity.empty()",
    'entity.substr(0, 13) != "media_player."',
    "entity == id(subscribed_media_player_entity)",
    "entity == id(subscribed_linked_media_player_entity)",
    "int gen = id(subscription_gen);",
    "int *gen_ptr = &id(subscription_gen);",
    "int gen = id(tv_subscription_gen);",
    "int *gen_ptr = &id(tv_subscription_gen);",
    "if (gen != *gen_ptr) return;",
    'sub_text("group_members", id(group_members_sensor));',
)


def read(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise MediaSubscriptionCheckError(f"Missing file: {path.relative_to(ROOT)}") from exc


def require(text: str, expected: str, label: str) -> None:
    if expected not in text:
        raise MediaSubscriptionCheckError(f"{label} is missing {expected!r}")


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


def validate_media_subscription(yaml: str, docs: str, yaml_label: str = "media player YAML", docs_label: str = "lifecycle docs") -> None:
    for expected in DOC_REQUIREMENTS:
        require(docs, expected, docs_label)

    for script_id in LIFECYCLE_SCRIPTS:
        require(docs, f"`{script_id}`", docs_label)

    active_yaml = active_yaml_and_lambda_text(yaml)
    for script_id in MEDIA_SELECT_EXECUTE_SCRIPTS:
        require(active_yaml, f"script.execute: {script_id}", yaml_label)

    for expected in YAML_REQUIREMENTS:
        require(active_yaml, expected, yaml_label)


def main() -> int:
    yaml = read(MEDIA_SELECT)
    docs = read(LIFECYCLE_DOC)
    validate_media_subscription(
        yaml,
        docs,
        str(MEDIA_SELECT.relative_to(ROOT)),
        str(LIFECYCLE_DOC.relative_to(ROOT)),
    )

    print("Media subscription lifecycle checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
