#!/usr/bin/env python3
"""Regression tests for scripts/check_media_subscription.py."""

from __future__ import annotations

import check_media_subscription


BASE_DOCS = "\n".join(
    (
        *check_media_subscription.DOC_REQUIREMENTS,
        *(f"`{script_id}`" for script_id in check_media_subscription.LIFECYCLE_SCRIPTS),
    )
)
BASE_YAML = "\n".join(
    (
        *check_media_subscription.YAML_REQUIREMENTS,
        *(f"script.execute: {script_id}" for script_id in check_media_subscription.MEDIA_SELECT_EXECUTE_SCRIPTS),
    )
)


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_media_subscription.MediaSubscriptionCheckError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def without(text: str, item: str) -> str:
    return text.replace(item, "")


def test_validate_media_subscription_accepts_required_guards() -> None:
    check_media_subscription.validate_media_subscription(BASE_YAML, BASE_DOCS)


def test_validate_media_subscription_requires_empty_entity_guard() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            without(BASE_YAML, "entity.empty()"),
            BASE_DOCS,
        ),
        "entity.empty()",
    )


def test_validate_media_subscription_requires_invalid_entity_guard() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            without(BASE_YAML, 'entity.substr(0, 13) != "media_player."'),
            BASE_DOCS,
        ),
        'entity.substr(0, 13) != "media_player."',
    )


def test_validate_media_subscription_requires_duplicate_subscription_guards() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            without(BASE_YAML, "entity == id(subscribed_media_player_entity)"),
            BASE_DOCS,
        ),
        "entity == id(subscribed_media_player_entity)",
    )
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            without(BASE_YAML, "entity == id(subscribed_linked_media_player_entity)"),
            BASE_DOCS,
        ),
        "entity == id(subscribed_linked_media_player_entity)",
    )


def test_validate_media_subscription_requires_generation_checks() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            without(BASE_YAML, "if (gen != *gen_ptr) return;"),
            BASE_DOCS,
        ),
        "if (gen != *gen_ptr) return;",
    )


def test_validate_media_subscription_requires_lifecycle_scripts_in_yaml() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            without(BASE_YAML, "script.execute: subscribe_linked_media_player"),
            BASE_DOCS,
        ),
        "script.execute: subscribe_linked_media_player",
    )


def test_validate_media_subscription_requires_active_lifecycle_scripts_in_yaml() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            BASE_YAML.replace(
                "script.execute: subscribe_media_player",
                "# script.execute: subscribe_media_player",
            ),
            BASE_DOCS,
        ),
        "script.execute: subscribe_media_player",
    )


def test_validate_media_subscription_requires_active_lambda_guards() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            BASE_YAML.replace(
                "entity == id(subscribed_media_player_entity)",
                "// entity == id(subscribed_media_player_entity)",
            ),
            BASE_DOCS,
        ),
        "entity == id(subscribed_media_player_entity)",
    )


def test_validate_media_subscription_requires_lifecycle_scripts_in_docs() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            BASE_YAML,
            without(BASE_DOCS, "`subscribe_day_night_sensor`"),
        ),
        "`subscribe_day_night_sensor`",
    )


def test_validate_media_subscription_requires_safe_reboot_documentation() -> None:
    run_fails(
        lambda: check_media_subscription.validate_media_subscription(
            BASE_YAML,
            without(BASE_DOCS, "safe reboot"),
        ),
        "safe reboot",
    )


def main() -> int:
    test_validate_media_subscription_accepts_required_guards()
    test_validate_media_subscription_requires_empty_entity_guard()
    test_validate_media_subscription_requires_invalid_entity_guard()
    test_validate_media_subscription_requires_duplicate_subscription_guards()
    test_validate_media_subscription_requires_generation_checks()
    test_validate_media_subscription_requires_lifecycle_scripts_in_yaml()
    test_validate_media_subscription_requires_active_lifecycle_scripts_in_yaml()
    test_validate_media_subscription_requires_active_lambda_guards()
    test_validate_media_subscription_requires_lifecycle_scripts_in_docs()
    test_validate_media_subscription_requires_safe_reboot_documentation()
    print("Media subscription regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
