# ActivityWatch Health + Screen Time Stack

Public setup repo for Martin's local ActivityWatch extensions.

It documents and wires together:

- WHOOP → ActivityWatch importer
- Apple/iPhone Screen Time → ActivityWatch importer
- launchd autostart jobs on macOS
- privacy-safe WHOOP export email handling

## Repositories

- WHOOP importer: https://github.com/Martin-Hausleitner/aw-importer-whoop
- Apple Screen Time importer: https://github.com/Martin-Hausleitner/aw-importer-apple-screentime

## Local ActivityWatch buckets

Expected buckets include:

- `aw-importer-whoop-sleep`
- `aw-importer-whoop-workout`
- `aw-importer-whoop-cycle`
- `aw-importer-whoop-recovery`
- `aw-import-screentime_ios_*`

## Recommended model

- WHOOP sleep/workouts: timeline events
- WHOOP recovery/day strain: daily metrics, not noisy timeline blocks
- iPhone Screen Time: app-usage timeline events
- ActivityWatch desktop usage: baseline work timeline

## Autostart jobs

This repo ships templates in `launchd/`.

Local install should copy scripts to:

```text
~/Library/Application Support/aw-activitywatch-stack/
```

and launchd plists to:

```text
~/Library/LaunchAgents/
```

Jobs:

- `ai.servas.aw-whoop-sync` runs WHOOP sync continuously every 15 minutes internally.
- `ai.servas.aw-screentime-hourly` runs once per hour and imports new CSV/JSON files from:
  `~/ActivityWatchImports/screentime/`

## Screen Time hourly sync

Put exports here:

```text
~/ActivityWatchImports/screentime/
```

Accepted formats:

- `.csv`
- `.json`

Already imported files are tracked by SHA-256 in local state:

```text
~/Library/Application Support/aw-activitywatch-stack/screentime-imported-files.txt
```

## WHOOP credentials

Never commit secrets.

The local WHOOP job should read:

- client id from local script/env
- client secret from macOS Keychain
- refresh/access tokens from the WHOOP importer's local config dir

## WHOOP export emails

See `docs/whoop-export-email-policy.md`.

Important: agents must not broadly fetch mailboxes. They should only fetch messages matching the confirmed WHOOP export email pattern.

## Verify

```bash
curl -fsS http://127.0.0.1:5600/api/0/info
python3 scripts/verify-aw-buckets.py

## Current local status

On Martin's MacBook this stack currently sees:

- ActivityWatch server on `127.0.0.1:5600`
- WHOOP import buckets for sleep/workout/cycle/recovery
- Apple Screen Time buckets named `aw-import-screentime_ios_*`
- hourly Screen Time launchd job: `ai.servas.aw-screentime-hourly`
- continuous WHOOP launchd job: `ai.servas.aw-whoop-sync`
```

## Security

Do not commit:

- tokens
- client secrets
- exported health/screen-time files
- `.eml` / `.em1` samples
- mailbox config
- logs containing private app usage
