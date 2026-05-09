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

Repo: https://github.com/Martin-Hausleitner/aw-importer-apple-screentime

Current automation:

- reads CSV/JSON from `~/ActivityWatchImports/screentime/`
- runs hourly via launchd
- imports only files not already seen by SHA-256

Use for:

- phone app usage timeline
- distraction analysis
- cross-device daily summaries

## Future unified daily summary

A future `aw-health-daily` layer should combine:

- ActivityWatch active time
- iPhone Screen Time totals
- WHOOP sleep score/duration
- WHOOP recovery/HRV/RHR
- WHOOP day strain
- workout summary

This should be a daily metric bucket, not timeline noise.
