# Media Player Subscription Lifecycle

This note documents how the firmware follows the selected Home Assistant media
player entity. It is intended for maintainers changing
`common/device/media_player_select.yaml`, `common/device/sensors.yaml`, or the
device `api.on_client_connected` blocks.

## Runtime Flow

1. The main `Media Player` and optional `Linked Media Player` settings are
   stored as ESPHome template text entities with `restore_value: true`.
2. When Home Assistant connects to the ESPHome API, each device runs:
   - `subscribe_media_player`
   - `subscribe_linked_media_player`
   - `subscribe_day_night_sensor`
3. Each media-player subscription script rejects empty values and values that do
   not start with `media_player.`.
4. If the entity is already subscribed during this boot, the script exits
   without registering duplicate callbacks.
5. When a new valid entity is accepted, the script resets the relevant media
   state, bumps a generation counter, and registers Home Assistant state
   callbacks for the entity and its attributes.
6. Each callback captures the generation value from the moment it was
   registered. If a later entity change bumps the generation, stale callbacks
   return without publishing state.
7. Saving a valid entity while Home Assistant is connected triggers a short
   delay, preference sync, and safe reboot. This is intentional: dynamically
   added Home Assistant state subscriptions are reliably picked up during the
   API subscription exchange after reconnect.

The linked media player follows the same pattern, but only subscribes to the
attributes needed for TV or line-in linked playback state.

## Invariants To Preserve

- Empty entity values must not reboot the device.
- Invalid entity values must not reboot the device and must not register Home
  Assistant callbacks.
- Re-saving the same entity during a reconnect must not register duplicate
  callbacks.
- Callback generation checks must remain in place for both main and linked media
  players.
- The first-time setup prompt should only be hidden once a valid main media
  player is configured.
- The old `Sonos Tv Source` migration should keep copying to `Linked Media
  Player` until the project intentionally drops that compatibility path.

## Manual Regression Checklist

Run these checks on at least one S3 device and one P4 device before changing the
subscription flow:

- Fresh install with empty `Media Player`: setup prompt is shown, no reboot loop
  occurs, and logs do not show repeated subscription attempts.
- Save an invalid value such as `speaker.kitchen`: warning is logged, the device
  does not reboot, and playback UI remains in setup/unconfigured state.
- Save a valid main media player while connected to Home Assistant: device
  reboots once, reconnects, and then shows title, artist, artwork, position,
  duration, volume, source, and group members where available.
- Re-save the same main media player and reconnect Home Assistant: logs show the
  already-subscribed guard rather than duplicate subscription registration.
- Change from one valid main media player to another: old callbacks stop
  updating visible state, and the new entity updates the screen after reboot.
- Set and clear `Linked Media Player`: TV or line-in linked mode follows the
  linked entity when set and falls back cleanly when empty.
- Reboot Home Assistant while the device stays powered: after reconnect, the
  device resubscribes without duplicate callback growth or a device reboot loop.
- Upgrade a device that still has the old `Sonos Tv Source` value: the value is
  copied once to `Linked Media Player`, then the old text value is cleared.
