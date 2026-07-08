# Speaker Grouping Parser Notes

This note documents the string formats consumed by
`common/addon/speaker_group.yaml`. Use it before changing the parser, slot
arrays, or speaker grouping UI.

## Speaker Discovery Sensor

The firmware reads `sensor.speaker_group` attribute `data`. The Home Assistant
template emits a pipe-delimited string:

```text
speaker_one,speaker_two|Kitchen,Living Room|0.35,0.70
```

Music Assistant templates can add a fourth manufacturer section:

```text
speaker_one,speaker_two|Kitchen,Living Room|0.35,0.70|Sonos,Sonos
```

The parser currently expects:

- section 1: entity IDs without the `media_player.` prefix
- section 2: display names
- section 3: volume levels from `0.0` to `1.0`
- section 4: optional manufacturer names used to filter incompatible Music
  Assistant players
- up to 16 speakers
- comma-separated values, with simple leading/trailing spaces trimmed

The firmware restores the `media_player.` prefix before comparing entries with
the selected media player entity.

## Group Members Attribute

The firmware subscribes to the selected media player's `group_members`
attribute. Home Assistant commonly sends it as comma-separated entity IDs:

```text
media_player.kitchen, media_player.living_room
```

The parser also tolerates Python-style list strings with brackets and quotes:

```text
['media_player.kitchen', 'media_player.living_room']
```

Empty list strings and Home Assistant no-data states such as `None`, `unknown`,
and `unavailable` are treated as no grouped members.

`common/addon/speaker_group_helpers.h` owns this parsing so it can be checked
outside firmware builds. Run `npm run check:speaker-group` after changing
accepted `group_members` formats.

Each parsed member is compared with the internal speaker slot entity IDs to set
the grouped/ungrouped button state.

## Invariants To Preserve

- Slot 0 must remain the selected main media player.
- Empty, `None`, and `unknown` discovery data must fall back to the single
  volume control.
- If the selected media player is missing from the discovery sensor, the UI must
  fall back to the single volume control.
- Volume values must be clamped to `0.0` through `1.0`.
- Pending local volume changes must continue to ignore stale Home Assistant
  echoes for the short optimistic-update window.
- Music Assistant manufacturer filtering must not hide the selected speaker.
- Join calls must target the selected main player and pass the new member.
- Unjoin calls must target the speaker being removed.

## Manual Regression Checklist

Run these checks on a grouped speaker setup before changing the parser:

- Discovery sensor is missing, empty, `None`, or `unknown`: the settings panel
  shows the single volume control, not an empty or broken grid.
- Discovery sensor has one speaker: the single volume control is shown.
- Discovery sensor has two or more compatible speakers: the speaker grid is
  shown, and the selected player appears first.
- Names contain spaces: labels render without leading/trailing whitespace.
- Volume values are missing or invalid: the UI uses `0%` rather than crashing or
  showing stale values.
- `group_members` is a plain comma-separated string: grouped states update.
- `group_members` is a bracketed/quoted list string: grouped states update.
- `group_members` is empty, `None`, `unknown`, or `unavailable`: no extra
  speakers are marked as grouped.
- Join a speaker: Home Assistant receives `media_player.join` with the selected
  player as `entity_id` and the added speaker as `group_members`.
- Remove a speaker: Home Assistant receives `media_player.unjoin` for the
  removed speaker.
- Adjust per-speaker and group volume: the UI updates immediately and then
  settles to Home Assistant's reported volume without jumping backward.
- Music Assistant setup with mixed manufacturers: only compatible speakers are
  shown for the selected player.
