# Tech Debt Cleanup Backlog

Review date: 2026-07-07

Scope: original research-only scan of firmware YAML, shared packages, custom
ESPHome components, release automation, and the docs/web settings generator.
Cleanup progress is tracked below as items are addressed.

Current project state noted during review:

- The local `main` worktree is behind `origin/main` by 40 commits.
- There are existing local changes, including restored
  `guition-esp32-p4-jc1060p470` device files, docs edits, webserver source and
  generated webserver output edits, and release script changes.
- The restored JC1060 files have been re-added to the Git index, so they no
  longer appear as staged deletions plus duplicate untracked files.

Progress updates:

- 2026-07-07: Added ignore rules for Python caches, local worktrees, and
  VitePress cache output.
- 2026-07-07: Added `scripts/check_devices.py` and wired it into
  `npm run check:all` to catch drift between supported device metadata, release
  workflow entries, build files, web settings firmware manifests, and public
  docs install pages.
- 2026-07-07: Added maintenance notes for the vendored GSL3680 touchscreen
  driver.
- 2026-07-07: Added a host-side artwork URL regression check for Apple Music
  and Home Assistant proxy artwork URL rewriting.
- 2026-07-07: Tightened Apple Music artwork URL rewriting so capped concrete
  CDN URLs are forced to JPEG, matching the intended ESP32-safe decode format.
- 2026-07-07: Added a firmware artwork regression checklist for manual device
  validation before artwork component refactors.
- 2026-07-07: Extended the device metadata check to validate common setup
  prompt wrappers for every supported device.
- 2026-07-07: Added `devices/supported_devices.json` as the shared supported
  device registry for release tooling and generated web settings metadata.
- 2026-07-07: Added default ESPHome package filenames to the device registry and
  validated device docs against them.
- 2026-07-07: Documented the Home Assistant media player subscription lifecycle
  and manual regression checklist.
- 2026-07-07: Documented speaker grouping parser input formats and manual
  regression checklist.
- 2026-07-07: Added a generated webserver bundle smoke check for unreplaced
  template tokens and JavaScript syntax.
- 2026-07-07: Added public docs slugs, display names, and install summaries to
  the supported device registry and validated README/install/index/manual config
  references against it.
- 2026-07-07: Added an LVGL widget ID consistency check across supported device
  layouts.
- 2026-07-07: Added validation for shared API, OTA, media subscription, setup
  prompt, and screen rotation hooks in each supported device hardware file.
- 2026-07-07: Extended the generated webserver bundle check to validate public
  firmware manifest slugs and URLs against the supported device registry.
- 2026-07-07: Replaced the hand-maintained GitHub Actions release firmware
  matrix with registry-generated matrix output from `scripts/firmware_release.py
  list-matrix`.
- 2026-07-07: Added README supported-screen table size and buy-link metadata to
  the device registry and validated the public table rows against it.
- 2026-07-07: Hardened the release workflow sparse checkouts used by registry
  backed release helper commands.
- 2026-07-07: Tightened release asset verification so registered device
  manifests must use the chip family recorded in the supported-device registry.
- 2026-07-07: Tightened release asset verification so firmware manifests must
  keep the expected public firmware name.
- 2026-07-07: Removed an orphan tracked placeholder from an unregistered
  Waveshare device folder and added validation for unregistered device
  directories containing files.
- 2026-07-07: Split firmware update helper logic out of the large web settings
  template into `docs/webserver/src/firmware.template.js`.
- 2026-07-07: Split web settings default state, entity mapping, and number
  limits into `docs/webserver/src/settings.template.js`.
- 2026-07-07: Split web settings ESPHome API fetch/post, entity state, web
  activity, and firmware refresh helpers into `docs/webserver/src/api.template.js`.
- 2026-07-07: Split reusable web settings form/control helpers into
  `docs/webserver/src/controls.template.js`.
- 2026-07-07: Fixed a copied JC8012 device-page buy link and added validation
  so device pages, README rows, and the supported-device registry stay aligned.
- 2026-07-07: Hardened the supported-device registry validation to reject
  duplicate public docs slugs/display names and empty or whitespace-padded
  string fields.
- 2026-07-07: Added explicit schema validation for supported-device registry
  entries so missing, unknown, or wrong-type fields fail with clear messages.
- 2026-07-07: Extended device-page validation to require the registry display
  name in each page title and main heading.
- 2026-07-07: Added validation for stale `docs/devices/*.md` pages that are no
  longer represented in the supported-device registry.
- 2026-07-07: Added validation for stale `builds/*.yaml` files, while allowing
  registered device build variants that have matching `packages-*.yaml` files.
- 2026-07-07: Added validation that standard build YAML files include each
  device's registry default package and package-variant builds include their
  matching `packages-*.yaml` file.
- 2026-07-07: Added validation that factory build YAML files include the
  matching standard build file and the expected firmware project metadata.
- 2026-07-07: Added regression tests for device metadata drift checks covering
  stale docs pages, stale build files, missing package-variant builds, and
  wrong standard package imports.
- 2026-07-07: Extended device metadata regression tests to cover factory build
  core includes and release project metadata.
- 2026-07-07: Added a repo-wide Python syntax check to `npm run check:all`,
  with bytecode output redirected to `/tmp` to avoid local cache permission
  issues.
- 2026-07-07: Added a generated physical-device text audit and freshness check
  so hard-coded display text is visible for future translation review.
- 2026-07-07: Added regression tests for the device-text audit so cache paths,
  placeholders, icons, URLs, numeric values, and lambda text stay out of the
  report.
- 2026-07-07: Broadened the device-text audit to detect double-quoted,
  single-quoted, and plain YAML `text:` values.
- 2026-07-07: Tightened the device-text audit parser so `#` characters inside
  quoted device labels are preserved while real trailing comments are ignored.
- 2026-07-07: Hardened webserver generation to fail on missing or leaked
  template tokens and added regression tests for partial insertion.
- 2026-07-07: Added regression tests for generated webserver bundle metadata
  checks covering manifest slug drift, public base URL drift, and missing
  assignments.
- 2026-07-07: Tightened webserver generation so each required template token
  must appear exactly once, preventing accidental duplicated partial insertion.
- 2026-07-07: Added regression tests for LVGL widget ID validation, covering
  missing shared IDs, missing track-info widgets, and empty supported-device
  input.
- 2026-07-07: Tightened release changelog categorization so the supported
  device registry is grouped with supported-device installation changes instead
  of broad dashboard UI changes.
- 2026-07-07: Extracted speaker `group_members` parsing into a small tested
  helper and added a host-side regression check for common Home Assistant
  formats.
- 2026-07-07: Removed redundant per-device setup prompt wrapper files and
  included the shared setup screens directly from each device LVGL layout.
- 2026-07-07: Added release-helper regression coverage for resolving devices
  by release asset slug, public web slug, and build config name.
- 2026-07-07: Added each device's default `display_rotation` to the supported
  device registry and validate it against the default package file.
- 2026-07-07: Added an automated media subscription lifecycle check covering
  empty/invalid entity guards, duplicate-subscription guards, callback
  generation checks, and safe reboot behavior.
- 2026-07-07: Added speaker grouping slot alignment checks so common 16-slot
  arrays and device LVGL speaker widgets cannot drift silently.
- 2026-07-07: Added package-include validation so supported device packages
  must keep the shared base/web settings includes and expected device-local
  device, LVGL, font, icon, and theme includes. Devices that opt into
  warm-tone artwork processing must also include the warm-tones package.
- 2026-07-07: Extended the generated webserver bundle check so the special S3
  profile, public screen-rotation list, and track-info-duration support list
  must match the supported-device registry, with regression tests for stale
  generated values.
- 2026-07-07: Moved generated web settings device metadata into one registry
  helper so the webserver generator and generated bundle checker use the same
  manifest and capability profile mapping.
- 2026-07-07: Hardened supported-device registry validation for public slug
  formats, release/web slug alignment, default package filenames, supported
  chip names, and buy-link URLs.
- 2026-07-07: Extended device metadata validation to cover each device's
  ESPHome import wrapper package path and the release-versioning asset table.
- 2026-07-07: Extended device metadata validation to keep display-rotation docs
  aligned with registry default package paths and any `packages-*.yaml`
  variants.
- 2026-07-07: Extended device metadata validation to cover VitePress sidebar
  device links and the public browser installer device manifest map.
- 2026-07-07: Extended device metadata validation to keep Settings feature docs
  aligned with screen-tone and track-info-duration support metadata.
- 2026-07-07: Added webserver generator validation so extra unreferenced
  `docs/webserver/src/*.template.js` partials fail instead of becoming stale
  source files.
- 2026-07-07: Split generic web settings runtime helpers for escaping, DOM
  creation, banner display, log rendering, and event-stream setup into
  `docs/webserver/src/runtime.template.js`.
- 2026-07-07: Removed the duplicated generated-webserver placeholder list from
  the bundle checker so it now reuses `scripts/generate_webserver.py`'s token
  list.
- 2026-07-07: Split registry-backed web settings device capability helpers into
  `docs/webserver/src/device_profiles.template.js`.
- 2026-07-07: Consolidated the webserver generator's partial-template mapping
  so each source partial is registered once with its placeholder token.
- 2026-07-07: Added registry-backed Screen Tone support metadata so the web
  settings page hides P4-only warmth controls on devices that do not include
  the warm-tones package.
- 2026-07-07: Added registry-backed clock screen saver support metadata so the
  web settings page and package substitutions stay aligned if a future device
  cannot show the clock screen saver.
- 2026-07-07: Fixed the JC4880 public installer card and README supported-screen
  row to show the default landscape `800 x 480` install profile, and validated
  installer card size/resolution/aspect/shape metadata against the
  supported-device registry.
- 2026-07-07: Hardened the supported-device registry so README size text must
  match each device's install summary, preventing orientation/resolution drift
  before it reaches public docs.
- 2026-07-07: Hardened the supported-device registry so install summaries must
  use positive screen sizes and pixel dimensions.
- 2026-07-07: Tightened docs navigation and browser installer validation so
  stale extra device sidebar links or installer keys fail instead of only
  checking that current registry devices are present.
- 2026-07-07: Tightened release-versioning asset table validation so stale or
  missing release asset rows fail against the supported-device registry.
- 2026-07-07: Tightened README supported-screen and installation supported-device
  list validation so stale or missing public device entries fail against the
  supported-device registry.
- 2026-07-07: Added `scripts/generate_device_docs.py` so the README
  supported-screen table, installation supported-device list, and
  release-versioning asset table can be rebuilt directly from the
  supported-device registry, with a stale-output check and generator regression
  tests wired into `npm run check:all`.
- 2026-07-07: Centralized the generated device-docs output path list so every
  registry-generated docs target is covered by the same `--check` loop and
  regression test.
- 2026-07-07: Converted generated device-docs sections to data-driven
  definitions so each output path, anchor pair, replacement mode, and content
  builder is registered in one place.
- 2026-07-07: Tightened generated device-docs error handling so unsupported
  output paths fail with a clear generator error before any file read is
  attempted.
- 2026-07-07: Tightened docs home-page device-link validation so stale or
  missing `/devices/...` links fail against the supported-device registry.
- 2026-07-07: Tightened manual ESPHome Config package-example validation so
  stale or missing `files: [devices/.../packages*.yaml]` examples fail against
  the supported-device registry.
- 2026-07-07: Tightened device-page installer validation so each device page
  must contain exactly one `<InstallButton device="...">` tag matching its
  registry web slug.
- 2026-07-07: Tightened docs sidebar and home-page device-link validation so
  labels and screen sizes must match the supported-device registry, not just
  the target URL.
- 2026-07-07: Tightened browser installer card validation so each card's short
  label must match the registry-derived device label, and its visual grid slot
  count must match its column and row metadata.
- 2026-07-07: Tightened device-page validation so each page's main heading size
  and panel buy link must match the supported-device registry.
- 2026-07-07: Added local docs link and image-reference validation so stale
  internal Markdown links or missing docs images fail even though VitePress is
  configured to ignore dead links.
- 2026-07-07: Extended local docs link validation to cover VitePress sidebar
  links from `docs/.vitepress/config.js`.
- 2026-07-07: Extended local docs link validation to check VitePress-style
  heading anchors, including slash headings and duplicate heading suffixes.
- 2026-07-07: Extended local docs link validation to check same-page Markdown
  anchors such as `#section-heading`.
- 2026-07-07: Extended local docs link validation to cover reference-style
  Markdown links and images.
- 2026-07-07: Added duplicate reference-definition detection for reference-style
  Markdown links.
- 2026-07-07: Tightened docs link validation so links, images, reference
  definitions, and headings inside fenced code examples are ignored.
- 2026-07-07: Removed two unused tracked docs screenshots and extended docs
  link validation to fail on unreferenced files in `docs/images/`.
- 2026-07-07: Tightened docs package-path validation so user-facing advanced
  and device docs cannot mention stale `devices/.../packages*.yaml` files that
  no longer exist for supported devices.
- 2026-07-07: Extended docs link validation to cover raw GitHub docs asset
  references in VitePress config, including the social sharing image.
- 2026-07-07: Removed VitePress `ignoreDeadLinks: true` after local docs link
  validation covered internal pages, images, anchors, sidebar links, and raw
  docs assets.
- 2026-07-07: Extended docs link validation to cover VitePress `${base}...`
  public asset references, including the configured favicon.
- 2026-07-07: Added package-script validation so every `scripts/check_*.py`
  file is wired into a package check and every package check runs through
  `npm run check:all`.
- 2026-07-07: Extended package-script validation so standalone
  `scripts/*_tests.py` regression files must also be wired into package checks.
- 2026-07-07: Extended package-script validation so standalone
  `scripts/audit_*.py` checks must also be wired into package checks.
- 2026-07-07: Tightened setup include validation so commented-out
  `common/setup/*.yaml` includes cannot satisfy direct LVGL setup wiring checks.
- 2026-07-07: Tightened shared device behavior validation so commented-out
  API, subscription, OTA, or rotation hooks cannot satisfy required hook checks.
- 2026-07-07: Tightened release-critical YAML validation so commented-out build
  includes, package metadata, ESPHome import wrappers, factory metadata, and
  default rotation values cannot satisfy supported-device checks.
- 2026-07-07: Tightened media subscription lifecycle validation so commented-out
  YAML script calls or lambda guards cannot satisfy required subscription checks.
- 2026-07-07: Tightened speaker group slot validation so commented-out slot IDs
  cannot satisfy common array or per-device LVGL slot checks.
- 2026-07-07: Tightened package capability validation so commented-out warm-tone
  script settings or clock screen-saver substitutions cannot satisfy package
  capability checks.
- 2026-07-07: Tightened LVGL ID validation so commented-out widget IDs are
  ignored while active IDs with inline comments are still parsed.
- 2026-07-07: Tightened speaker group slot validation so the shared
  `speaker_top` array rejects duplicate top-slot IDs instead of only checking
  the final set of slot numbers.
- 2026-07-07: Added a dedicated supported-device registry check and regression
  tests for required fields, boolean types, duplicate public slugs, release/web
  slug alignment, README size drift, and buy-link URL validation.
- 2026-07-07: Tightened registry install summary validation so landscape,
  portrait, and square labels must match the recorded screen dimensions.
- 2026-07-07: Extended device package validation so every `!include` target in
  supported default and package-variant YAML files must exist.
- 2026-07-07: Tightened device package include parsing so commented-out
  `!include` examples are ignored while active includes with trailing comments
  are still validated.
- 2026-07-07: Tightened release changelog categorization so specific file paths
  such as device docs and release scripts win over generic subject keywords.
- 2026-07-07: Tightened release changelog keyword matching so release subjects
  are categorized by whole words instead of accidental substrings inside other
  words.
- 2026-07-07: Hardened generated device-doc section replacement so duplicated
  generated-section anchors fail instead of silently rewriting the wrong docs
  block.
- 2026-07-07: Tightened LVGL widget ID validation to detect duplicate real
  widget/page IDs while ignoring repeated action target IDs such as script
  calls and label updates.
- 2026-07-07: Added focused regression tests for the media player subscription
  lifecycle checker, covering empty/invalid entity guards, duplicate
  subscription guards, generation checks, and safe reboot documentation.
- 2026-07-07: Tightened generated webserver bundle validation so registry-backed
  metadata assignments must appear exactly once, preventing duplicated stale
  assignments from being silently ignored.
- 2026-07-07: Tightened generated webserver bundle validation so registry-backed
  metadata assignments must also have the expected JSON shape, preventing a
  malformed manifest map or capability list from failing later with a vague
  comparison error.
- 2026-07-07: Tightened package check wiring validation so `npm run check:all`
  fails if the same package check is accidentally listed more than once.
- 2026-07-07: Tightened supported-device registry validation so each device's
  chip field must match the ESP32 family marker in its config name.
- 2026-07-07: Extended docs link validation to cover local HTML `<a href>` and
  `<img src>` targets inside Markdown pages, not just Markdown link syntax.
- 2026-07-07: Tightened docs image validation so Markdown, reference-style, and
  HTML image references must include alt text, while inline-code examples are
  ignored like fenced code examples.
- 2026-07-07: Tightened supported-device registry validation so public docs
  slugs must match the device config name with the known vendor prefix removed.
- 2026-07-07: Tightened supported-device registry validation so browser
  installer web slugs must match the device config name with the known platform
  prefixes removed.
- 2026-07-07: Tightened supported-device registry validation so buy-link labels
  must match known store URL hosts.
- 2026-07-07: Tightened supported-device registry validation so public buy
  links must use `https`.
- 2026-07-07: Tightened supported-device registry validation so public display
  names must include the configured ESP32 chip family.
- 2026-07-07: Extended supported-device registry regression tests to cover
  unknown fields, wrong string types, whitespace-padded strings, malformed web
  slugs, invalid default package names, invalid default display rotations, and
  unsupported chip names.
- 2026-07-07: Extended the generated device-docs helper so VitePress device
  sidebar entries are rebuilt from the supported-device registry instead of
  being hand-maintained.
- 2026-07-07: Extended the generated device-docs helper so the docs homepage
  supported-device links are rebuilt from the supported-device registry while
  preserving the existing featured device images.
- 2026-07-07: Extended the generated device-docs helper so Settings track-info
  support text is rebuilt from the supported-device registry.
- 2026-07-07: Moved Settings track-info support wording into the
  supported-device registry helper and tightened validation so generated marker
  contents must exactly match the registry-derived phrase.
- 2026-07-07: Moved shared public device label formatting into the
  supported-device registry helper so docs generation and device metadata
  validation use the same size, sidebar, homepage, and installer labels.
- 2026-07-07: Tightened supported-device registry helper coverage so install
  summary parsing, size ordering, public labels, and installer card metadata
  are tested directly at the registry layer.
- 2026-07-07: Cached the generated webserver bundle inside device metadata
  validation so manifest and capability-profile checks share one generated
  bundle per run.
- 2026-07-07: Split web settings page and card assembly into
  `docs/webserver/src/ui_sections.template.js`, leaving the top-level app
  template focused on constants, state, partial insertion, and startup.
- 2026-07-07: Split web settings duration, screen-saver action, and timezone
  formatting helpers into `docs/webserver/src/formatters.template.js`.
- 2026-07-07: Removed unused web settings helper functions left behind by
  earlier UI source splits.
- 2026-07-07: Added a web settings template-source guardrail that fails when a
  declared helper function is not referenced by any template source.
- 2026-07-07: Removed stale web settings CSS selectors that only supported
  deleted number/status/section helper UI.
- 2026-07-07: Added a web settings stylesheet regression guard so those removed
  stale CSS selectors cannot be reintroduced accidentally.
- 2026-07-07: Centralized the docs homepage device-link order and added
  validation that it covers every supported device exactly once.
- 2026-07-07: Added validation that docs homepage featured-image metadata only
  references devices present in the homepage device order.
- 2026-07-07: Added validation that the docs homepage device-link order cannot
  contain duplicate device configs.
- 2026-07-07: Added generation-time validation for docs homepage featured-image
  Markdown and local image file paths.
- 2026-07-07: Added regression coverage for docs homepage featured-image
  remote, absolute, and path-traversal targets.
- 2026-07-07: Tightened docs homepage featured-image validation so generated
  images must have descriptive alt text and must live under `docs/images/`.
- 2026-07-07: Tightened package-script validation so `npm run check:all` must
  continue running the docs site build.
- 2026-07-07: Tightened package-script validation so malformed non-string
  `package.json` script commands fail clearly instead of being coerced to text.
- 2026-07-07: Tightened webserver generator validation so duplicate partial
  tokens or duplicate partial source files fail before bundle generation.
- 2026-07-07: Hardened speaker group member parsing so Home Assistant no-data
  states such as `None`, `unknown`, and `unavailable` are treated as no grouped
  members.
- 2026-07-07: Hardened speaker group member parsing so Home Assistant no-data
  states are treated case-insensitively.
- 2026-07-07: Tightened media subscription lifecycle validation so reconnect
  script names stay aligned between the YAML checks and lifecycle docs.
- 2026-07-07: Improved supported-device registry error handling so invalid JSON
  reports the file location before release or docs tooling uses it.
- 2026-07-07: Tightened LVGL ID validation so core media, volume, settings, and
  speaker-group widgets must exist on every supported layout.
- 2026-07-07: Tightened docs link validation so local Markdown and HTML links or
  images cannot resolve outside the docs tree.
- 2026-07-07: Tightened webserver generation so replacement tokens must exactly
  match the required template-token list.
- 2026-07-08: Tightened webserver generation so duplicate entries in the master
  template-token list fail clearly instead of being hidden by set comparisons.
- 2026-07-07: Tightened device metadata validation so generated webserver
  metadata assignments must appear exactly once.
- 2026-07-07: Tightened speaker group slot validation so duplicated slot IDs
  fail instead of being hidden by set-based checks.
- 2026-07-07: Tightened device package validation so old per-device setup
  wrapper includes cannot return through default or rotated package files.
- 2026-07-07: Tightened public device navigation and installer validation so
  duplicate sidebar links or duplicate installer keys fail instead of being
  hidden by set comparisons.
- 2026-07-07: Tightened public device docs validation so duplicate generated
  release rows, README rows, installation bullets, index links, and ESPHome
  package examples fail instead of being hidden by set comparisons.
- 2026-07-07: Tightened Settings feature docs validation so the generated
  track-info support text must appear in exactly the two intended settings
  rows.
- 2026-07-07: Tightened device package validation so commented-out package
  includes cannot satisfy required include or Screen Tone warm-tones checks.

## Critical Issues

### 1. Release workflow still builds a removed device

- Where: `.github/workflows/release.yml` lines 53-58, deleted local
  `builds/guition-esp32-p4-jc1060p470*.yaml`, deleted local
  `devices/guition-esp32-p4-jc1060p470/`, and `scripts/firmware_release.py`
  lines 48-72.
- Why it matters: the release workflow matrix still includes
  `media-player-jc1060p470`, but the helper script and local file tree no
  longer include that device. A published release would try to compile
  `builds/guition-esp32-p4-jc1060p470.factory.yaml` and fail before assets are
  published.
- Recommendation: make supported devices come from one source of truth. Short
  term, align the release workflow matrix with `scripts/firmware_release.py` and
  the actual `builds/` files. Longer term, generate the workflow matrix or have
  CI query `scripts/firmware_release.py` so a device cannot be removed in one
  place and left active in another.
- Status: fixed in the working tree and Git index.
  JC1060 build files, device files, public docs, firmware release metadata, and
  webserver firmware manifest metadata have been restored. The JC1060 factory
  firmware compile passed. The staged deletion/untracked duplicate mismatch has
  been resolved. The remaining task is to prepare the final branch, commit,
  push, and PR when the user is ready to package the cleanup work.
- Safe to fix now or wait: index mismatch fixed. PR finalization can happen
  when the cleanup scope is ready.

## Medium Cleanup Items

### 2. Device support metadata is duplicated across release, docs, firmware, and web settings

- Where: `scripts/firmware_release.py` lines 48-72,
  `.github/workflows/release.yml` lines 53-67,
  `docs/webserver/src/app.template.js` lines 37-43,
  `devices/*/packages.yaml` `device_slug` and `firmware_manifest_slug`,
  `docs/devices/*.md`, `docs/advanced/esphome-config.md`, and README device
  tables.
- Why it matters: adding, removing, or renaming a device currently requires
  coordinated edits in many places. The jc1060 release mismatch shows this is
  already becoming fragile. A missed edit can break firmware releases, public
  manifests, the browser installer, or the web settings update screen.
- Recommendation: introduce a small checked-in device registry, for example a
  JSON or YAML file with device id, display name, build config, asset slug, web
  slug, chip family, default package, docs path, and support status. Read that
  registry from release scripts and webserver generation. Use it to validate
  docs/device links and package slugs.
- Status: partially fixed. `devices/supported_devices.json` now drives
  `scripts/firmware_release.py` and generated web settings metadata for
  firmware manifest slugs, screen rotation support, and track-info-duration
  support. It also records clock screen saver support, Screen Tone support,
  public docs slugs, display names, install summaries, README table size/buy
  links, default ESPHome package files, and default display rotation values.
  `scripts/check_devices.py` validates the registry-backed release workflow,
  build YAML, package substitution, install button, README, installation page,
  docs index, manual ESPHome config, ESPHome import wrapper package path,
  display-rotation package examples, release-versioning asset table,
  VitePress sidebar links, browser installer manifest entries, device-page
  package references, Settings feature support notes, browser installer card
  metadata, and device-page buy links against that registry. Settings track-info
  support text must appear in exactly the two intended generated rows, so a
  copied or missing support note fails clearly. VitePress sidebar
  links and labels, browser installer keys, docs home-page device links and
  labels, browser installer card labels, manual ESPHome Config package
  examples, README supported-screen rows, installation supported-device bullets,
  and the release-versioning asset table must now exactly match the
  supported-device registry, so stale removed devices cannot linger in those
  public entry points. Duplicate VitePress device sidebar links and duplicate
  browser installer keys also fail explicitly instead of being hidden by
  set-based comparison. Duplicate release asset rows, README supported-screen
  rows, installation supported-device bullets, docs index device links, and
  manual ESPHome package examples also fail explicitly before registry
  comparison. VitePress device sidebar entries, docs homepage
  supported-device links, and Settings track-info support text are now also
  generated from the supported-device registry by
  `scripts/generate_device_docs.py`; the generated marker contents are now
  checked exactly against the registry-derived phrase. Public device label formatting for
  sidebar entries, homepage links, device-page headings, and installer cards now
  lives in `scripts/device_registry.py`, so docs generation and validation share
  the same label rules. Registry tests now cover those shared label and
  installer-card metadata helpers directly. Generated web settings metadata for
  firmware manifest slugs, clock screen saver support, screen rotation support,
  Screen Tone support, and track-info-duration support now comes from one
  `scripts/device_registry.py` mapping used by both `scripts/generate_webserver.py`
  and `scripts/check_webserver_bundle.py`. Device metadata validation now
  reuses one generated webserver bundle per run when checking manifest and
  capability-profile assignments, avoids repeated generator work for the same
  source files, and rejects missing or duplicated generated metadata
  assignments.
  Browser installer card grid metadata is also checked for
  internal consistency. It checks each device page title, main heading size, and
  panel buy link against the registry display metadata, and flags stale `docs/devices/*.md` pages and stale
  `builds/*.yaml` files that are not
  registered as supported devices or package variants. Device pages must also
  contain exactly one installer button for their registry web slug, preventing
  copied stale installer targets. User-facing advanced and device docs are
  checked so every documented `devices/.../packages*.yaml` path points to a
  package file that exists for a supported device. Build YAML files are
  also checked against registry default packages and matching package-variant
  files using active non-comment YAML lines, and factory builds are checked for
  matching core includes plus release project metadata using active non-comment
  YAML lines. `scripts/check_devices_tests.py` exercises the drift checks
  with temporary broken fixtures, including factory build metadata drift, so
  checker regressions are caught by `npm run check:all`. The registry loader
  now rejects duplicate public docs slugs/display names and empty or
  whitespace-padded string fields, and it reports missing, unknown, or
  wrong-type registry fields before release/web tooling uses them, and rejects
  invalid default display rotation values. `scripts/check_device_registry.py`
  now exercises those registry invariants directly, with regression coverage
  for invalid JSON diagnostics, missing fields, wrong boolean types, duplicate
  public slugs, asset/web slug mismatch, unknown fields, wrong string types,
  whitespace-padded strings, malformed web slugs, invalid default package names,
  invalid default display rotations, unsupported chip names, README size drift,
  install summary shape drift, chip/config mismatch, docs slug/config mismatch,
  web slug/config mismatch, and invalid buy-link URLs or labels. It also
  validates public slug formats, release asset slug alignment with browser
  installer slugs, docs slug alignment with device config names, web slug
  alignment with device config names, install summary shape, README size
  alignment, default package filenames, supported chip names, public display
  name chip labels, chip/config alignment, buy-label/store URL alignment, and
  buy-link URL structure before registry values can feed release assets, docs,
  or the browser installer.
  `scripts/generate_device_docs.py`
  now regenerates the README supported-screen table, installation
  supported-device list, and release-versioning asset table from the registry,
  with `npm run check:device-docs` and `scripts/check_device_docs_generator.py`
  protecting the generated sections. The generator's stale-output diff handling
  is also covered when paths are outside the repository root, matching how its
  regression tests use temporary fixtures, and duplicated generated-section
  anchors now fail clearly before any docs are rewritten. The generator's output
  paths are now held in one tested `GENERATED_PATHS` list so new generated docs
  targets are less likely to be left out of stale-output checks. Each generated
  section now also has one data-driven definition covering its path, anchors,
  replacement mode, and content builder. Unsupported generated-doc paths are
  rejected before file reads, so caller mistakes produce clear generator errors
  instead of raw missing-file failures. The docs homepage device-link order is
  now centralized in one tuple and checked against the supported-device
  registry, so adding or removing a device fails clearly unless the homepage
  order is updated too. Homepage featured-image metadata is also checked
  against that order, preventing stale image entries for removed devices from
  lingering in the generator. Duplicate configs in the homepage order are now
  rejected before duplicate public homepage links can be generated. Homepage
  featured images are now validated as local Markdown image links with
  descriptive alt text and existing files under `docs/images/` before docs are
  generated, and regression tests cover remote, absolute, path-traversal,
  empty-alt, and non-image-folder targets.
  `scripts/check_docs_links.py` now verifies local docs page links, image
  references, VitePress sidebar links, and local heading anchors, with
  regression tests for missing pages, missing images, stale sidebar links,
  slash-heading anchors, duplicate-heading anchors, same-page anchors,
  reference-style links and images, duplicate reference definitions,
  local HTML links and images, fenced-code examples, missing anchors, missing
  raw docs assets from VitePress config, local targets that escape the docs
  tree, and missing `${base}...` public assets
  such as the favicon.
  It also rejects
  unreferenced `docs/images/` files. VitePress no longer uses
  `ignoreDeadLinks: true`, so the site build and custom local checks now both
  fail on broken docs links. Two stale screenshots, `ha-device-settings.png`
  and `ha-tv-source.png`, were removed.
- Safe to fix now or wait: safe to continue in phases. The remaining cleanup is
  to move more docs/workflow output to generated or registry-derived sources
  only where that reduces maintenance burden without making the release process
  more opaque.

### 3. Large copied LVGL layouts make cross-device behavior hard to maintain

- Where: `devices/*/device/lvgl.yaml`; current files are roughly 2,470-2,490
  lines each. Examples reviewed: `devices/esp32-p4-86-panel/device/lvgl.yaml`
  and `devices/guition-esp32-p4-jc8012p4a1/device/lvgl.yaml`.
- Why it matters: most of the media dashboard structure appears repeated, while
  device differences are mixed into the copied files as coordinates, buffer
  settings, colors, and one-off boot handling. A fix to playback controls,
  speaker grouping, clock, settings panel, or screensaver can easily land on
  one device and be missed on another.
- Recommendation: extract shared LVGL sections into common include files where
  the widget IDs and behavior are identical, driven by layout substitutions for
  size and position. Keep truly device-specific display composition in each
  device folder.
- Status: partially fixed. `scripts/check_lvgl_ids.py` now validates that the
  supported device layouts keep the same shared LVGL widget IDs, while allowing
  the known device-specific container/icon differences. This gives future LVGL
  extraction work a guardrail before moving large layout blocks into common
  includes. It also requires a small core set of media, volume, settings, and
  speaker-group widget IDs on every supported layout, so copied layouts cannot
  all lose the same critical control unnoticed. `scripts/check_lvgl_ids_tests.py`
  now exercises the validation logic against small broken fixtures, and the
  checker now rejects duplicated real LVGL widget/page IDs without confusing
  repeated action target IDs for widget definitions. It also ignores
  commented-out widget IDs and still parses active IDs with inline comments.
- Safe to fix now or wait: safe to continue in phases. Start with a low-risk
  repeated section and compile every affected device after each extraction.

### 4. Hardware configuration mixes shared behavior with board-specific setup

- Where: `devices/*/device/device.yaml`; current files are roughly 755-852
  lines each. The P4 devices duplicate API setup, OTA behavior, globals, touch
  tracking, rotation select, and backlight/sleep integration alongside actual
  board pins and display bus settings.
- Why it matters: shared behavior changes need to be repeated in every device
  file, but hardware-specific changes must not accidentally affect all boards.
  That makes reviews harder and increases the chance of device-specific
  regressions.
- Recommendation: split device files into a small board hardware layer and
  common behavior includes. Good candidates for common ownership are API client
  hooks, OTA screen handling, rotation select behavior, touch gesture state, and
  shared globals. Leave pins, buses, PSRAM, display driver, touch controller,
  and board quirks in the device folders.
- Status: partially fixed. `scripts/check_devices.py` now validates that every
  supported device keeps the shared Home Assistant API reconnect hooks, old TV
  entity migration, media subscription scripts, day/night subscription,
  setup-prompt disconnect behavior, OTA pause/resume behavior, and screen
  rotation select hook using active non-comment YAML lines. It also validates
  that each supported device package keeps the shared base/web settings packages
  and required device-local package includes, that commented-out include
  examples do not count as active package wiring, that those active package
  include targets exist, that clock screen saver support substitutions are
  active, and that devices using an active warm-tone artwork script include the
  shared warm-tones package. The
  hardware YAML is still duplicated, but
  accidental drift in the highest-risk shared behavior and package wiring is now
  checked.
- Safe to fix now or wait: extracting these blocks into common includes should
  wait until the Git index is clean and every affected firmware can be compiled.

### 5. Web settings page still has a large bundled output, but source ownership is split

- Where: `docs/webserver/src/app.template.js`, now roughly 430 lines, plus
  split source partials in `docs/webserver/src/*.template.js` and generated
  `docs/public/webserver/app.js`.
- Why it matters: the file owns device detection, firmware update logic, entity
  fetching, settings rendering, validation, and UI composition in one place.
  That makes small settings changes risky and encourages more hard-coded device
  checks such as profile support lists and manifest slugs.
- Recommendation: split the source into small modules or generated sections:
  device metadata, ESPHome API helpers, firmware update state, settings schema,
  and UI rendering. Keep `scripts/generate_webserver.py` responsible for
  producing the single bundled `app.js` needed by ESPHome.
- Status: partially fixed. Device metadata sections are now generated from
  `devices/supported_devices.json`, and `scripts/check_webserver_bundle.py`
  verifies that generated `app.js` has no leaked template tokens and passes
  JavaScript syntax checking. It also verifies that the generated firmware
  manifest map and public firmware update URLs match the supported device
  registry. Firmware update helper logic now lives in
  `docs/webserver/src/firmware.template.js` and is inserted by
  `scripts/generate_webserver.py`. Default settings state, entity metadata, and
  numeric limits now live in `docs/webserver/src/settings.template.js`. ESPHome
  API fetch/post helpers, entity state application, web activity heartbeat, and
  firmware refresh timers now live in `docs/webserver/src/api.template.js`.
  Reusable form controls, cards, selectors, formatting helpers, and banner
  helpers now live in `docs/webserver/src/controls.template.js`.
  Generic runtime helpers for escaping, DOM element creation, banner display,
  log rendering, and event-stream setup now live in
  `docs/webserver/src/runtime.template.js`.
  Registry-backed device capability helpers for Track Info Duration, screen
  rotation, Screen Tone, and clock screen saver support now live in
  `docs/webserver/src/device_profiles.template.js`.
  Page and settings-card assembly now lives in
  `docs/webserver/src/ui_sections.template.js`, so the top-level app template
  no longer owns the full UI rendering tree.
  Duration labels, screen-saver action normalization, and timezone display
  formatting now live in `docs/webserver/src/formatters.template.js`, leaving
  `docs/webserver/src/controls.template.js` focused on input controls and card
  primitives. Dead helper functions for unused number fields, status rows,
  section titles/dividers, and combined clock-action checks have been removed
  from the split web settings source and generated bundle. The generator
  regression script now scans the split template sources for helper functions
  that are declared but never referenced, so future source splits are less
  likely to leave dead JavaScript behind. Stale CSS selectors for removed
  number-row, status-row, dot, section-title, and divider helper UI have also
  been removed from the web settings stylesheet and generated bundle, with a
  regression check preventing those known-dead selectors from returning.
  `scripts/generate_webserver.py` now fails early if a required template token
  is missing, duplicated, or still present after generation, and it rejects
  unreferenced `*.template.js` source partials. It also rejects duplicate
  partial tokens, duplicate partial source files, and missing or unexpected
  replacement tokens. Its source partials are now registered through one
  token-to-file mapping instead of repeated read and replacement lists.
  `scripts/check_generate_webserver.py` covers partial insertion behavior and
  extra partial detection.
  `scripts/check_webserver_bundle.py` now reuses the generator's template token
  list when checking for leaked placeholders, avoiding a second hard-coded list
  that could drift after future partial splits. It also rejects missing or
  duplicated generated metadata assignments instead of reading the first
  matching assignment and ignoring stale duplicates, and it validates that
  generated manifest metadata is a string-to-string map while generated
  capability metadata is a list of strings before comparing it with the
  supported-device registry.
  `scripts/check_webserver_bundle_tests.py` now covers generated metadata
  parsing and registry drift failures for firmware manifest slugs, public
  update URLs, the special S3 profile, screen-rotation support, and
  track-info-duration support, plus missing, duplicated, and malformed
  generated metadata assignments. Screen Tone visibility is now also generated
  from the registry so S3 devices do not show P4-only warmth controls, and
  clock screen saver visibility is no longer hard-coded in the web UI.
- Safe to fix now or wait: deeper splitting should wait until current webserver
  edits have landed to avoid conflicts.

### 6. Speaker grouping parsing is hand-written and duplicated inside lambdas

- Where: `common/addon/speaker_group.yaml` lines 350-400 and the repeated
  16-slot LVGL object arrays around lines 416 onward.
- Why it matters: group member parsing depends on a comma-separated string shape
  from Home Assistant. If Home Assistant changes formatting, or entity names
  include unexpected whitespace/quoting, grouping state can drift. The repeated
  16-entry arrays also make future UI changes noisy and easy to misalign.
- Recommendation: extract small helper functions for trimming/parsing group
  member lists and for working with speaker-slot arrays. Add comments or tests
  that document the accepted Home Assistant formats.
- Status: partially fixed. `docs/development/speaker-grouping-parser-notes.md`
  now documents the expected `sensor.speaker_group` attribute format, tolerated
  `group_members` strings, invariants, and manual regression scenarios.
  `common/addon/speaker_group_helpers.h` now owns the `group_members` parser
  used by the firmware lambda, and `scripts/check_speaker_group_helpers.py`
  covers common Home Assistant comma-separated and quoted-list formats on the
  host, plus empty list and no-data values such as `None`, `unknown`, and
  `unavailable`. `scripts/check_speaker_group_slots.py` now verifies the
  16-slot common arrays and per-device LVGL speaker widgets remain aligned,
  with regression tests for missing, duplicated, and commented-out slot IDs,
  including duplicate shared `speaker_top` entries.
- Safe to fix now or wait: safe to keep parser-format changes small and covered
  by the host checks. Wait on broader speaker-slot array extraction until
  grouped-speaker behavior can be verified on real Home Assistant data.

### 7. Runtime Home Assistant entity subscription logic is complex and reboot-dependent

- Where: `common/device/media_player_select.yaml` lines 109-165 and related
  linked media player subscription logic.
- Why it matters: changing the selected media player registers callbacks and
  then intentionally reboots so ESPHome picks up subscriptions cleanly. The
  code has useful guards against duplicate callbacks, but the behavior is
  subtle and can be painful to evolve when adding more attributes or linked
  entities.
- Recommendation: keep the current behavior for users, but document the
  subscription lifecycle in one place and extract duplicated main/linked
  subscription setup where ESPHome lambda constraints allow. Add a focused test
  or checklist for changing media player entity, reconnecting Home Assistant,
  and booting with empty/invalid entity IDs.
- Status: partially fixed. `docs/development/media-player-subscription-lifecycle.md`
  now explains the reboot-dependent subscription flow, the invariants to
  preserve, and a manual regression checklist for changing main or linked media
  player entities. `scripts/check_media_subscription.py` now verifies the YAML
  still contains the documented empty/invalid entity guards, duplicate
  subscription guards, callback generation checks, safe reboot path, and
  media-player reconnect script executions using active non-comment YAML/lambda
  text, while also requiring the lifecycle docs to name the full reconnect
  script flow.
  `scripts/check_media_subscription_tests.py` now exercises those checker
  failures directly and is wired into `npm run check:all`. The code still
  intentionally keeps the current runtime behavior.
- Safe to fix now or wait: wait on code extraction until there is a specific
  subscription bug or a hardware test window, because this flow is boot and
  Home Assistant connection sensitive. Smaller guardrail checks are safe now.

### 8. Custom artwork component needs stronger regression coverage before refactors

- Where: `components/artwork_image/*`, especially `artwork_image.cpp`,
  `image_decoder.*`, `jpeg_image.*`, `png_image.*`, and `artwork_url.h`.
- Why it matters: this component handles network artwork, local/private URLs,
  decoding, memory buffers, retries, and LVGL image updates. The implementation
  is defensive in places, but it is custom firmware code with many edge cases.
  Future cleanups could easily affect memory use, OTA stability, or artwork
  rendering.
- Recommendation: before simplifying the component, add small host-level tests
  for URL rewriting and parsing, plus firmware-level test notes for failed
  downloads, missing artwork, large artwork, HEIC/unsupported content, local
  Home Assistant artwork URLs, and rapid track changes.
- Status: fixed. `scripts/check_artwork_url.py` now compiles and
  tests `components/artwork_image/artwork_url.h` on the host for Home Assistant
  proxy URLs, Apple Music template URLs, concrete oversized artwork URLs, small
  artwork URLs, and unrelated URLs. `docs/development/artwork-regression-checklist.md`
  captures the firmware-level scenarios to verify before future artwork
  component refactors.
- Safe to fix now or wait: fixed.

### 9. Vendored touchscreen driver has limited ownership documentation

- Where: `components/gsl3680/README.md`, `components/gsl3680/gsl3680.cpp`,
  `components/gsl3680/gsl_point_id.cpp`, and `components/gsl3680/gsl3680_firmware.h`.
- Why it matters: this is vendored and modified hardware code. The README names
  the source commit, but does not explain what local changes exist, how to
  update it, or which device behavior must be retested after changes.
- Recommendation: add a short maintenance note covering upstream source, local
  patches, expected touch limits, retry/power-cycle behavior, and required
  hardware checks.
- Status: fixed. `components/gsl3680/README.md` now records the upstream
  baseline, local startup retry behavior, current touch-count handling, and
  required hardware checks before changing the driver.
- Safe to fix now or wait: fixed.

## Nice-to-Have Polish

### 10. Generated and cache artifacts can clutter reviews

- Where: untracked `components/artwork_image/__pycache__/`,
  `components/mipi_rgb/__pycache__/`, `components/mipi_rgb/models/__pycache__/`,
  local `.worktrees/`, the orphan tracked
  `devices/waveshare-esp32-p4-86-panel/assets/placeholder.png`, and tracked
  generated bundle `docs/public/webserver/app.js`.
- Why it matters: cache folders make status output noisy and can distract from
  real changes. The generated webserver bundle is intentionally tracked, but it
  means every source edit creates a large generated diff too.
- Recommendation: add ignore entries for Python cache files and local worktree
  folders. Keep generated `app.js` tracked if needed by the public docs, but
  continue enforcing `npm run check:generated` so source and generated output
  stay paired.
- Status: fixed. `.gitignore` now excludes Python caches, local `.worktrees/`,
  and VitePress cache output. The orphan unregistered Waveshare placeholder has
  been removed, and `scripts/check_devices.py` now flags unregistered device
  directories that contain files. Generated `app.js` remains tracked and
  checked by `npm run check:generated`.
- Safe to fix now or wait: fixed.

### 11. Setup prompt include pattern is improved but still leaves redundant per-device files

- Where: previously `devices/*/setup/*.yaml` and `common/setup/*.yaml`.
- Why it matters: most device setup files are now identical one-line includes,
  which is much better than copied setup screen content. The remaining wrapper
  files still add small review noise and can be forgotten when adding a device.
- Recommendation: if ESPHome package structure allows it, include
  `common/setup/*.yaml` directly from each device package instead of maintaining
  per-device wrapper files. If not, keep the wrappers but validate that every
  device has the same setup include set.
- Status: fixed. Supported device LVGL files now include
  `common/setup/*.yaml` directly, and the redundant per-device setup wrapper
  files have been removed. `scripts/check_devices.py` now validates the direct
  includes using active non-comment YAML lines, fails if old wrapper files
  return, and rejects package includes that point back at the removed
  per-device setup wrapper paths.
- Safe to fix now or wait: fixed.

### 12. Naming around display rotation and device orientation is uneven

- Where: `devices/guition-esp32-p4-jc4880p443/packages.yaml`,
  `devices/guition-esp32-p4-jc4880p443/packages-90.yaml`,
  `docs/devices/esp32-p4-jc4880p443.md`, and display rotation docs.
- Why it matters: the project supports default packages, rotated packages,
  `display_rotation`, and per-device layout substitutions. The meaning is clear
  once inspected, but a new contributor can easily confuse physical mounting,
  LVGL rotation, package variant, and browser installer defaults.
- Recommendation: after current device support changes settle, document the
  naming convention for package variants and add a small validation that docs
  reference the intended default package.
- Status: fixed. `docs/advanced/display-rotation.md` now explains the
  difference between `display_rotation`, default `packages.yaml` files, and
  orientation preset files such as `packages-90.yaml`. The device registry now
  records each device's default package file and default display rotation, and
  `scripts/check_devices.py` validates that each device page and the display
  rotation docs reference the expected package path, that package variants such
  as `packages-90.yaml` are documented, and that each default package sets the
  expected rotation.
- Safe to fix now or wait: fixed.

### 13. Release helper tests are good but narrow

- Where: `scripts/check_firmware_release.py`,
  `scripts/check_release_changelog.py`, and `package.json` `check:all`.
- Why it matters: there are useful smoke tests for release manifests and
  changelog generation, but no check currently catches the workflow matrix
  disagreeing with `scripts/firmware_release.py` or missing build YAML files.
- Recommendation: add a lightweight CI validation that compares release matrix
  entries, firmware helper devices, build YAML files, docs install buttons, and
  web manifest slugs.
- Status: fixed. The GitHub Actions release build matrix is now generated from
  `scripts/firmware_release.py list-matrix`, which reads the supported device
  registry. `scripts/check_devices.py` validates the registry-backed workflow,
  firmware helper devices, build YAML files, package substitutions, web manifest
  slugs, device docs install buttons, user-facing docs links, and release helper
  sparse-checkout requirements. `scripts/check_firmware_release.py` now also
  covers release asset slug, public web slug, and build config lookup aliases.
  Release changelog tests now also cover supported-device registry
  categorization. `scripts/check_package_scripts.py` now validates that every
  `scripts/check_*.py` file, every standalone `scripts/audit_*.py` check, and
  every standalone `scripts/*_tests.py` regression file is reachable through
  `package.json`, and that every package
  check is included in `npm run check:all`, with regression coverage in
  `scripts/check_package_scripts_tests.py`. It also rejects duplicated
  `check:all` entries so the growing check suite cannot silently become slower
  or noisier from repeated package checks, and now requires `check:all` to keep
  running the docs site build. Release changelog categorization now
  weights specific file paths more strongly than generic subject keywords, so
  device docs and release helper changes remain in the intended release note
  sections.
- Safe to fix now or wait: fixed.

## Suggested Order

1. Prepare the final feature branch/commit/PR when the cleanup scope is ready.
2. Start extracting the least risky repeated LVGL/device YAML sections once a
   clean feature branch and broad firmware compile coverage are available.
3. Split web settings source once current webserver edits have landed.
4. Continue migrating docs/workflow consumers toward the registry only where it
   reduces duplication without making releases harder to inspect.
5. Simplify Home Assistant entity subscription or broader speaker grouping UI
   arrays only when hardware/Home Assistant test data is available.

## Checks Run

- Reviewed git status and file structure.
- Searched for TODO/FIXME/security-sensitive patterns, generated caches, device
  metadata, firmware slugs, and duplicated setup/device files.
- Compared device YAML file sizes and selected diffs.
- Reviewed release workflow, Pages workflow, firmware release helper, webserver
  generator, web settings source, speaker grouping, media player subscription,
  artwork image component, and vendored GSL3680 touch component.
- Restored JC1060 support in the working tree and compiled
  `builds/guition-esp32-p4-jc1060p470.factory.yaml` successfully.
- Ran `python3 scripts/firmware_release.py list-slugs`.
- Ran `python3 scripts/firmware_release.py list-slugs --kind web`.
- Ran `python3 scripts/firmware_release.py list-matrix`.
- Ran `python3 scripts/check_devices.py`.
- Ran `python3 scripts/check_artwork_url.py`.
- Ran `python3 scripts/check_lvgl_ids.py`.
- Ran `python3 scripts/check_webserver_bundle.py`.
- Ran `npm run check:generated`.
- Ran `npm run check:all`.
- Ran `npm run check:speaker-group`.
- Compiled `builds/guition-esp32-s3-4848s040.factory.yaml` successfully after
  extracting the speaker grouping parser helper.
- Attempted `builds/guition-esp32-p4-jc8012p4a1.factory.yaml`; ESPHome accepted
  the shared helper include, then stopped on missing
  `network_adapter_esp32c6.bin`, which is unrelated to the parser change.
- Compiled `builds/guition-esp32-s3-4848s040.factory.yaml` successfully after
  removing per-device setup prompt wrappers and switching LVGL files to direct
  shared setup includes.
