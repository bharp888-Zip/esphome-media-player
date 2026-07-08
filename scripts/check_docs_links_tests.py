#!/usr/bin/env python3
"""Regression tests for scripts/check_docs_links.py."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import check_docs_links


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def run_fails(func, expected: str) -> None:
    try:
        func()
    except check_docs_links.DocsLinkError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError(f"{expected!r} unexpectedly passed")


def test_valid_local_links_pass() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Install](/installation)\n![Hero](./images/hero.png)\n")
        write(root / "installation.md", "[Back](/)\n")
        write(root / "images" / "hero.png", "")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_page_link_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Missing](/missing-page)\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken link")
    finally:
        tmp.cleanup()


def test_markdown_links_inside_fenced_code_are_ignored() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(
            root / "index.md",
            "```md\n[Missing](/missing-page)\n![Missing](./images/missing.png)\n[missing]: /missing-page\n```\n",
        )
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_links_and_html_inside_inline_code_are_ignored() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "`[Missing](/missing-page)` and `<img src>`\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_valid_reference_style_link_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Install][install-page]\n\n[install-page]: /installation\n")
        write(root / "installation.md", "# Installation\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_reference_style_link_target_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Missing][missing-page]\n\n[missing-page]: /missing-page\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken link")
    finally:
        tmp.cleanup()


def test_missing_reference_style_definition_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Missing][missing-page]\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "missing reference link definition")
    finally:
        tmp.cleanup()


def test_duplicate_reference_style_definition_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(
            root / "index.md",
            "[Install][install-page]\n\n"
            "[install-page]: /installation\n"
            "[INSTALL-PAGE]: /other-installation\n",
        )
        write(root / "installation.md", "# Installation\n")
        write(root / "other-installation.md", "# Other\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "duplicate reference link definition")
    finally:
        tmp.cleanup()


def test_missing_relative_image_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "features" / "settings.md", "![Missing](../images/missing.png)\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken image")
    finally:
        tmp.cleanup()


def test_markdown_image_without_alt_text_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "![](./images/hero.png)\n")
        write(root / "images" / "hero.png", "")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "without alt text")
    finally:
        tmp.cleanup()


def test_reference_style_image_without_alt_text_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "![ ][hero]\n\n[hero]: ./images/hero.png\n")
        write(root / "images" / "hero.png", "")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "without alt text")
    finally:
        tmp.cleanup()


def test_local_link_outside_docs_fails() -> None:
    tmp = TemporaryDirectory()
    project = Path(tmp.name)
    root = project / "docs"
    try:
        write(root / "index.md", "[Repository Readme](../README.md)\n")
        write(project / "README.md", "# Outside Docs\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "points outside docs")
    finally:
        tmp.cleanup()


def test_local_image_outside_docs_fails() -> None:
    tmp = TemporaryDirectory()
    project = Path(tmp.name)
    root = project / "docs"
    try:
        write(root / "index.md", "![Outside](../outside.png)\n")
        write(project / "outside.png", "")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "points outside docs")
    finally:
        tmp.cleanup()


def test_html_local_link_and_image_pass() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", '<a href="/installation">Install</a>\n<img src="./images/hero.png" alt="Hero" />\n')
        write(root / "installation.md", "# Installation\n")
        write(root / "images" / "hero.png", "")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_html_local_link_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", '<a href="/missing-page">Missing</a>\n')
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken link")
    finally:
        tmp.cleanup()


def test_missing_html_local_image_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", '<img src="./images/missing.png" alt="Missing" />\n')
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken image")
    finally:
        tmp.cleanup()


def test_html_image_without_alt_text_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", '<img src="./images/hero.png" />\n')
        write(root / "images" / "hero.png", "")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "without alt text")
    finally:
        tmp.cleanup()


def test_html_image_with_blank_alt_text_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", '<img src="./images/hero.png" alt=" " />\n')
        write(root / "images" / "hero.png", "")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "without alt text")
    finally:
        tmp.cleanup()


def test_reference_style_image_counts_as_referenced() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "![Hero][hero]\n\n[hero]: ./images/hero.png\n")
        write(root / "images" / "hero.png", "")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_unused_docs_image_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "# Home\n")
        write(root / "images" / "unused.png", "")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "not referenced")
    finally:
        tmp.cleanup()


def test_external_and_anchor_links_are_ignored() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[External](https://example.com)\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_valid_same_page_anchor_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "# Home\n\n[Jump](#local-heading)\n\n## Local Heading\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_same_page_anchor_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "# Home\n\n[Jump](#missing-heading)\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken anchor")
    finally:
        tmp.cleanup()


def test_headings_inside_fenced_code_do_not_create_anchors() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Jump](#not-a-real-heading)\n\n```md\n## Not A Real Heading\n```\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken anchor")
    finally:
        tmp.cleanup()


def test_valid_page_anchor_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Details](/features/settings#screen-tone)\n")
        write(root / "features" / "settings.md", "# Settings\n\n## Screen Tone\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_vitepress_style_slash_anchor_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Details](/screen-saver#day-night-awareness)\n")
        write(root / "screen-saver.md", "# Screen Saver\n\n## Day/Night awareness\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_duplicate_heading_anchor_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Second](/settings#night-schedule-1)\n")
        write(root / "settings.md", "# Settings\n\n## Night Schedule\n\n## Night Schedule\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_page_anchor_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / "index.md", "[Details](/features/settings#missing-heading)\n")
        write(root / "features" / "settings.md", "# Settings\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken anchor")
    finally:
        tmp.cleanup()


def test_valid_sidebar_links_pass() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / ".vitepress" / "config.js", "{ text: 'Install', link: '/installation' }\n")
        write(root / "installation.md", "# Installation\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_sidebar_link_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / ".vitepress" / "config.js", "{ text: 'Missing', link: '/missing-page' }\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "broken sidebar link")
    finally:
        tmp.cleanup()


def test_raw_docs_asset_reference_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(
            root / ".vitepress" / "config.js",
            "const socialImage = 'https://raw.githubusercontent.com/jtenniswood/esphome-media-player/main/docs/images/social.jpg'\n",
        )
        write(root / "images" / "social.jpg", "")
        write(root / "index.md", "![Social](./images/social.jpg)\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_raw_docs_asset_reference_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(
            root / ".vitepress" / "config.js",
            "const socialImage = 'https://raw.githubusercontent.com/jtenniswood/esphome-media-player/main/docs/images/missing.jpg'\n",
        )
        run_fails(lambda: check_docs_links.validate_docs_links(root), "missing raw docs asset")
    finally:
        tmp.cleanup()


def test_base_public_asset_reference_passes() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / ".vitepress" / "config.js", "['link', { href: `${base}favicon.svg` }]\n")
        write(root / "public" / "favicon.svg", "<svg></svg>\n")
        check_docs_links.validate_docs_links(root)
    finally:
        tmp.cleanup()


def test_missing_base_public_asset_reference_fails() -> None:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    try:
        write(root / ".vitepress" / "config.js", "['link', { href: `${base}missing.svg` }]\n")
        run_fails(lambda: check_docs_links.validate_docs_links(root), "missing public asset")
    finally:
        tmp.cleanup()


def main() -> int:
    test_valid_local_links_pass()
    test_missing_page_link_fails()
    test_markdown_links_inside_fenced_code_are_ignored()
    test_links_and_html_inside_inline_code_are_ignored()
    test_valid_reference_style_link_passes()
    test_missing_reference_style_link_target_fails()
    test_missing_reference_style_definition_fails()
    test_duplicate_reference_style_definition_fails()
    test_missing_relative_image_fails()
    test_markdown_image_without_alt_text_fails()
    test_reference_style_image_without_alt_text_fails()
    test_local_link_outside_docs_fails()
    test_local_image_outside_docs_fails()
    test_html_local_link_and_image_pass()
    test_missing_html_local_link_fails()
    test_missing_html_local_image_fails()
    test_html_image_without_alt_text_fails()
    test_html_image_with_blank_alt_text_fails()
    test_reference_style_image_counts_as_referenced()
    test_unused_docs_image_fails()
    test_external_and_anchor_links_are_ignored()
    test_valid_same_page_anchor_passes()
    test_missing_same_page_anchor_fails()
    test_headings_inside_fenced_code_do_not_create_anchors()
    test_valid_page_anchor_passes()
    test_vitepress_style_slash_anchor_passes()
    test_duplicate_heading_anchor_passes()
    test_missing_page_anchor_fails()
    test_valid_sidebar_links_pass()
    test_missing_sidebar_link_fails()
    test_raw_docs_asset_reference_passes()
    test_missing_raw_docs_asset_reference_fails()
    test_base_public_asset_reference_passes()
    test_missing_base_public_asset_reference_fails()
    print("Docs link regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
