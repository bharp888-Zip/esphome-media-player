# Artwork Regression Checklist

Use this checklist before refactoring `components/artwork_image/` or changing
media artwork handling in `common/addon/music.yaml`.

## Host Checks

- Run `npm run check:artwork-url`.
- Confirm Apple Music proxy URLs are rewritten from Home Assistant proxy URLs to
  capped concrete JPEG CDN URLs.
- Confirm unrelated artwork URLs are left unchanged.

## Firmware Checks

Run on at least one supported device with album artwork visible on the main
screen.

- Normal artwork: start playback with a common JPEG/PNG artwork source and
  confirm the image appears, fits the artwork area, and updates when the track
  changes.
- Missing artwork: play media with no `entity_picture` and confirm the fallback
  state is shown without a reboot or blank locked screen.
- Failed download: temporarily block or break the artwork URL and confirm the
  UI stays responsive, logs an artwork download failure, and retries only within
  the configured retry limit.
- Large artwork: play a source that exposes high-resolution artwork and confirm
  memory remains stable and the image is capped/resized rather than exhausting
  heap.
- Unsupported format: play a source that exposes HEIC/HEIF artwork and confirm
  the device logs the unsupported format and keeps the previous/fallback image
  behavior stable.
- Local Home Assistant artwork: test `homeassistant.local`, local IP, and HTTPS
  local artwork URLs when `allow_insecure_local_artwork` is enabled for the
  device profile.
- Rapid track changes: skip tracks repeatedly and confirm stale artwork does not
  replace the latest track artwork after a delayed download finishes.
- OTA transition: start an OTA update after artwork has loaded and confirm the
  firmware releases artwork buffers before update work begins.
