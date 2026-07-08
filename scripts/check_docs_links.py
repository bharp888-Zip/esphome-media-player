#!/usr/bin/env python3
"""Validate local Markdown links and image references in docs."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
VITEPRESS_CONFIG = DOCS / ".vitepress" / "config.js"
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
REF_LINK_RE = re.compile(r"(!?)\[([^\]]+)\]\[([^\]]*)\]")
REF_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s+(\S+)", re.M)
HTML_LINK_RE = re.compile(r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"']", re.I)
HTML_IMAGE_RE = re.compile(r"<img\b(?P<attrs>[^>]*)>", re.I)
HTML_ATTR_RE = re.compile(r"\b(?P<name>[a-zA-Z:-]+)=[\"'](?P<value>[^\"']*)[\"']")
SIDEBAR_LINK_RE = re.compile(r"link: '(/[^']*)'")
RAW_DOCS_ASSET_RE = re.compile(
    r"https://raw\.githubusercontent\.com/jtenniswood/esphome-media-player/main/docs/([^'\"\s]+)"
)
BASE_PUBLIC_ASSET_RE = re.compile(r"\$\{base\}([^`'\"\s]+\.[a-zA-Z0-9]+)")


class DocsLinkError(RuntimeError):
    pass


def is_external(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme or parsed.netloc)


def strip_target(target: str) -> str:
    return unquote(target.split("#", 1)[0].split("?", 1)[0])


def target_anchor(target: str) -> str:
    if "#" not in target:
        return ""
    return unquote(target.split("#", 1)[1].split("?", 1)[0])


def heading_slug(heading: str) -> str:
    slug = heading.strip().lower()
    slug = re.sub(r"`([^`]+)`", r"\1", slug)
    slug = re.sub(r"<[^>]+>", "", slug)
    slug = slug.replace("/", "-")
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug


def markdown_without_fenced_code(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        match = re.match(r"^\s*(```+|~~~+)", line)
        if match:
            marker = match.group(1)
            marker_kind = marker[0]
            if not in_fence:
                in_fence = True
                fence_marker = marker_kind
            elif marker_kind == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def markdown_without_code(text: str) -> str:
    return re.sub(r"`[^`\n]*`", "", markdown_without_fenced_code(text))


def page_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    for line in markdown_without_code(path.read_text()).splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            slug = heading_slug(match.group(1))
            count = seen.get(slug, 0)
            anchors.add(slug if count == 0 else f"{slug}-{count}")
            seen[slug] = count + 1
    return anchors


def page_candidates(target: str, source: Path, docs_dir: Path = DOCS) -> list[Path]:
    if target.startswith("/"):
        target_path = docs_dir / target.removeprefix("/")
    else:
        target_path = source.parent / target

    if target_path.suffix:
        return [target_path]
    return [
        target_path.with_suffix(".md"),
        target_path / "index.md",
    ]


def image_candidates(target: str, source: Path, docs_dir: Path = DOCS) -> list[Path]:
    if target.startswith("/"):
        return [docs_dir / "public" / target.removeprefix("/"), docs_dir / target.removeprefix("/")]
    return [source.parent / target]


def path_label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def reference_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.strip()).lower()


def reference_definitions(text: str) -> tuple[dict[str, str], set[str]]:
    definitions: dict[str, str] = {}
    duplicates: set[str] = set()
    for label, target in REF_DEF_RE.findall(text):
        ref = reference_label(label)
        if ref in definitions:
            duplicates.add(ref)
        else:
            definitions[ref] = target
    return definitions, duplicates


def html_attrs(text: str) -> dict[str, str]:
    return {match.group("name").lower(): match.group("value") for match in HTML_ATTR_RE.finditer(text)}


def check_markdown_target(
    source: Path,
    raw_target: str,
    is_image: bool,
    referenced_images: set[Path],
    errors: list[str],
    docs_dir: Path,
) -> None:
    raw = raw_target.strip()
    target = strip_target(raw)
    anchor = target_anchor(raw)
    if is_external(raw) or raw.startswith("mailto:"):
        return

    if not target and anchor and not is_image:
        existing_path = source
    elif not target:
        return
    else:
        candidates = image_candidates(target, source, docs_dir) if is_image else page_candidates(target, source, docs_dir)
        existing_path = next((path for path in candidates if path.exists()), None)
        if existing_path is None:
            kind = "image" if is_image else "link"
            candidate_labels = ", ".join(path_label(path) for path in candidates)
            errors.append(f"{path_label(source)} has broken {kind} {raw_target!r}; expected one of {candidate_labels}")
            return
        if not is_within(existing_path, docs_dir):
            kind = "image" if is_image else "link"
            errors.append(
                f"{path_label(source)} has {kind} {raw_target!r} that points outside docs: "
                f"{path_label(existing_path)}"
            )
            return

    if is_image:
        referenced_images.add(existing_path.resolve())

    if not is_image and anchor and anchor not in page_anchors(existing_path):
        errors.append(
            f"{path_label(source)} has broken anchor {raw_target!r}; "
            f"{path_label(existing_path)} has no heading #{anchor}"
        )


def validate_docs_links(docs_dir: Path = DOCS) -> None:
    errors: list[str] = []
    referenced_images: set[Path] = set()
    for source in sorted(docs_dir.rglob("*.md")):
        text = markdown_without_code(source.read_text())
        for is_image, label, raw_target in LINK_RE.findall(text):
            if is_image and not label.strip():
                errors.append(f"{path_label(source)} has Markdown image {raw_target!r} without alt text")
            check_markdown_target(source, raw_target, bool(is_image), referenced_images, errors, docs_dir)

        for raw_target in HTML_LINK_RE.findall(text):
            check_markdown_target(source, raw_target, False, referenced_images, errors, docs_dir)
        for image_match in HTML_IMAGE_RE.finditer(text):
            attrs = html_attrs(image_match.group("attrs"))
            raw_target = attrs.get("src", "")
            if not raw_target:
                errors.append(f"{path_label(source)} has HTML image without src")
                continue
            if not attrs.get("alt", "").strip():
                errors.append(f"{path_label(source)} has HTML image {raw_target!r} without alt text")
            check_markdown_target(source, raw_target, True, referenced_images, errors, docs_dir)

        reference_defs, duplicate_refs = reference_definitions(text)
        for ref in sorted(duplicate_refs):
            errors.append(f"{path_label(source)} has duplicate reference link definition [{ref}]")
        for is_image, label, raw_ref in REF_LINK_RE.findall(text):
            ref = reference_label(raw_ref or label)
            if is_image and not label.strip():
                errors.append(f"{path_label(source)} has reference-style Markdown image [{ref}] without alt text")
            raw_target = reference_defs.get(ref)
            if raw_target is None:
                errors.append(f"{path_label(source)} has missing reference link definition [{ref}]")
                continue
            check_markdown_target(source, raw_target, bool(is_image), referenced_images, errors, docs_dir)

    config_path = docs_dir / ".vitepress" / "config.js"
    if config_path.exists():
        config_text = config_path.read_text()
        for raw_target in SIDEBAR_LINK_RE.findall(config_text):
            target = strip_target(raw_target.strip())
            if not target:
                continue

            candidates = page_candidates(target, config_path, docs_dir)
            if not any(path.exists() for path in candidates):
                candidate_labels = ", ".join(path_label(path) for path in candidates)
                errors.append(
                    f"{path_label(config_path)} has broken sidebar link {raw_target!r}; "
                    f"expected one of {candidate_labels}"
                )

        for raw_asset in RAW_DOCS_ASSET_RE.findall(config_text):
            asset_path = docs_dir / raw_asset
            if not asset_path.exists():
                errors.append(
                    f"{path_label(config_path)} references missing raw docs asset "
                    f"{raw_asset!r}; expected {path_label(asset_path)}"
                )

        for raw_asset in BASE_PUBLIC_ASSET_RE.findall(config_text):
            asset_path = docs_dir / "public" / raw_asset
            if not asset_path.exists():
                errors.append(
                    f"{path_label(config_path)} references missing public asset "
                    f"{raw_asset!r}; expected {path_label(asset_path)}"
                )

    image_dir = docs_dir / "images"
    if image_dir.exists():
        for image_path in sorted(path for path in image_dir.iterdir() if path.is_file()):
            if image_path.resolve() not in referenced_images:
                errors.append(f"{path_label(image_path)} is not referenced by any docs Markdown image")

    if errors:
        raise DocsLinkError("\n".join(errors))


def main() -> int:
    try:
        validate_docs_links()
    except DocsLinkError as exc:
        print(f"Docs link check failed:\n{exc}", file=sys.stderr)
        return 1

    print("Docs link checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
