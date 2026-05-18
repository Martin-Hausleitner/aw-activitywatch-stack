# Data Sources

## ActivityWatch desktop data

Source: local ActivityWatch watchers.

Useful buckets:

- `aw-watcher-afk_*`
- `aw-watcher-window_*`
- `aw-watcher-web-brave_*`
- `aw-watcher-vscode_*`
- `aw-watcher-input_*`

Use for:

- active/away time
- app/window context
- browser context
- coding/editor activity

Privacy default: aggregate by app/category unless detailed titles are explicitly requested.

## WHOOP API

Repo: https://github.com/Martin-Hausleitner/aw-importer-whoop

Use for:

- ongoing sync
- recent sleep/workouts/cycles/recovery
- refresh-token based automation

Recommended model:

- sleep and workouts as timeline events
- recovery and cycle/day strain as daily metrics in future revisions

## WHOOP export email

Use only targeted search rules after a sample `.eml` / `.em1` file is inspected.

Do not fetch broad mailbox history.

Matching rules should use:

- confirmed sender
- confirmed subject marker
- confirmed attachment filename pattern
- narrow date windows when possible

## Apple/iPhone Screen Time

Importer repo: https://github.com/ActivityWatch/aw-import-screentime

Local path:

```text
/Users/mh/aw-import-screentime
```

Current automation:

- reads macOS Biome `App.InFocus` files from `~/Library/Biome/streams/restricted/App.InFocus/remote/<device-id>/`
- runs via launchd at login, on local Biome file updates, and every five hours as a fallback
- previews all locally available Biome history by default and inserts only ActivityWatch events whose `(timestamp, duration, app)` signature is not already present
- uses the ActivityWatch HTTP API when available and the local ActivityWatch SQLite database as a fallback

Use for:

- phone app usage timeline
- distraction analysis
- cross-device daily summaries

macOS receives iPhone Screen Time through Apple's local Biome sync layer; the ActivityWatch importer reads after that local sync has written files. The best local timing source is `~/Library/Biome/sync/sync.db`:

- `DevicePeer.last_sync_date`: per-device last sync time, stored as Unix epoch seconds
- `SyncSessionLog`: recent sync sessions, stored as Apple `CFAbsoluteTime`
- `SyncMessageLog`: per-peer sync messages, stored as Apple `CFAbsoluteTime`

Add `978307200` seconds to `CFAbsoluteTime` values before converting them to Unix timestamps.

## Local daily summary

`scripts/aw-health-daily-report.py` generates a local Markdown/JSON daily summary. Generated outputs under `outputs/health-daily/` are private local artifacts and should not be committed.

A future ActivityWatch `aw-health-daily` bucket should combine:

- ActivityWatch active time
- iPhone Screen Time totals
- WHOOP sleep score/duration
- WHOOP recovery/HRV/RHR
- WHOOP day strain
- workout summary

This should be a daily metric bucket, not timeline noise.
