# ActivityWatch Health + iPhone Screen Time Stack

<p align="center">
  <img src="docs/assets/stack-architecture.svg" alt="ActivityWatch local lifelog stack architecture" width="100%">
</p>

<p align="center">
  <b>Local-first lifelog infrastructure for ActivityWatch, WHOOP, and iPhone Screen Time.</b><br>
  Health, recovery, app usage, and focus signals stay local, verifiable, and ready for agent workflows.
</p>

<p align="center">
  <a href="https://github.com/Martin-Hausleitner/aw-activitywatch-stack/actions"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/Martin-Hausleitner/aw-activitywatch-stack/ci.yml?branch=main&label=stack%20ci"></a>
  <a href="https://github.com/Martin-Hausleitner/aw-importer-whoop"><img alt="WHOOP importer" src="https://img.shields.io/badge/WHOOP-importer-17324d"></a>
  <a href="https://github.com/Martin-Hausleitner/aw-importer-apple-screentime"><img alt="Screen Time importer" src="https://img.shields.io/badge/Apple%20Screen%20Time-importer-335c43"></a>
  <img alt="Privacy" src="https://img.shields.io/badge/privacy-local--first-d6a84f">
</p>

## What This Is

This repo is the **public operating manual and automation layer** for a local ActivityWatch-based health and lifelog stack.

It does not try to put private life data into GitHub. It publishes the safe parts:

- architecture
- installer scripts
- launchd templates
- validation tools
- OpenClaw agent contracts
- privacy rules
- links to importer repos
- a macOS LaunchAgent that keeps iPhone Screen Time synced every five hours

<p align="center">
  <img src="docs/assets/data-model-radar.svg" alt="ActivityWatch data model" width="100%">
</p>

## Design Principles

- **ActivityWatch is the local timeline hub** — no cloud dependency for analysis.
- **Private data stays private** — exports, emails, tokens, and raw events are ignored/local only.
- **Data model must make sense** — timeline blocks only for real intervals; daily metrics for scores/readiness.
- **Agents can help safely** — OpenClaw gets explicit rules, redaction defaults, and verification scripts.
- **Every change should verify** — doctor script, CI, secret scan, ActivityWatch queries, and launchd status checks.

## System Map

- **WHOOP API** → sleep/workout timeline + recovery/strain context
- **Apple Screen Time importer** → iPhone app-usage timeline from local Biome sync data
- **ActivityWatch watchers** → Mac app/window/browser/editor activity
- **WHOOP export email** → future targeted backfill path, never broad mailbox crawling
- **OpenClaw agents** → read aggregate local data, update docs/code, never publish private exports

## iPhone Screen Time Sync

The Screen Time job imports the real local Apple Biome stream:

```text
~/Library/Biome/streams/restricted/App.InFocus/remote/<device-id>/
```

It uses the upstream Biome importer at:

```text
/Users/mh/aw-import-screentime/.venv/bin/aw-import-screentime
```

Default behavior:

- scans all locally available Biome `App.InFocus` history
- creates one ActivityWatch bucket per iOS device
- inserts only missing `(timestamp, duration, app)` signatures
- runs at login, on local Biome file updates, and then every 5 hours as a fallback via launchd

That means the first run is a full backfill. Later runs are incremental in effect, because existing ActivityWatch events are checked before inserts.

If the ActivityWatch API is not reachable, the runner falls back to the local ActivityWatch SQLite database:

```text
~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db
```

That keeps the import working even when the tray app or HTTP server is not currently alive.

## Quickstart

```bash
git clone https://github.com/Martin-Hausleitner/aw-activitywatch-stack.git
cd aw-activitywatch-stack
python3 scripts/aw-stack-doctor.py
```

Install or refresh the five-hour Screen Time job:

```bash
scripts/install-local-stack.sh
```

The installer renders the LaunchAgent with `WatchPaths` for:

```text
~/Library/Biome/streams/restricted/App.InFocus/remote
~/Library/Biome/streams/restricted/App.InFocus/remote/<device-id>
```

When macOS writes newly synced iPhone Screen Time files, launchd starts the importer quickly. The five-hour interval stays in place because file watches can be missed while the Mac is asleep and because new device directories may appear after install.

## Agent safety rules

- Do not read broad mailbox history.
- Do not upload or commit health, sleep, workout, email, or app-usage exports.
- Prefer local-only paths and `127.0.0.1`.
- Verify ActivityWatch buckets with `scripts/verify-aw-buckets.py` before reporting success.
- Run `scripts/secret-scan.py` before every push.

## What This Repo Does Not Contain

This repo does not contain health exports, Screen Time exports, WHOOP tokens, OAuth secrets, mailbox credentials, or ActivityWatch databases.

## Repo Layout

```text
scripts/   Import, verification, validation, and agent helpers
launchd/   macOS LaunchAgent templates
docs/      Privacy, data-source, and OpenClaw operating notes
config/    Non-secret example configuration
```

## Repositories

- WHOOP importer: https://github.com/Martin-Hausleitner/aw-importer-whoop
- Apple Screen Time importer: https://github.com/Martin-Hausleitner/aw-importer-apple-screentime
- Biome Screen Time importer: https://github.com/ActivityWatch/aw-import-screentime

## Local ActivityWatch Buckets

Expected buckets include:

- `aw-importer-whoop-sleep`
- `aw-importer-whoop-workout`
- `aw-importer-whoop-cycle`
- `aw-importer-whoop-recovery`
- `aw-import-screentime_ios_*`

## Recommended Model

- WHOOP sleep/workouts: timeline events
- WHOOP recovery/day strain: daily metrics, not noisy timeline blocks
- iPhone Screen Time: app-usage timeline events
- ActivityWatch desktop usage: baseline work timeline


## OpenClaw integration

OpenClaw agents should treat this repo as the operating contract for local ActivityWatch health/lifelog data.

Key docs:

- `docs/openclaw-agent-contract.md` — what agents may inspect, update, publish, or must keep private
- `docs/openclaw-data-ingestion-plan.md` — canonical source and ingestion plan
- `docs/openclaw-agent-safety-contract.md` — explicit agent safety rules
- `docs/data-retention-and-exports.md` — what stays local vs public
- `docs/activitywatch-data-model.md` — bucket and event semantics
- `docs/operations.md` — local runbook and repair checklist
- `docs/data-sources.md` — WHOOP, Screen Time, ActivityWatch, and future daily summary model
- `docs/whoop-export-email-policy.md` — privacy-safe targeted email export discovery

Useful commands:

```bash
python3 scripts/aw-health-report.py
python3 scripts/secret-scan.py
```

## Autostart Jobs

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
- `ai.servas.aw-screentime-hourly` runs at login, when local Biome Screen Time files change, and every five hours as a fallback. It imports iPhone Screen Time from local macOS Biome `App.InFocus` sync data via `/Users/mh/aw-import-screentime`.

## Screen Time Biome Sync

The Screen Time job reads the real Apple Biome stream synced by macOS:

```text
~/Library/Biome/streams/restricted/App.InFocus/remote/<device-id>/
```

It shells out to:

```text
/Users/mh/aw-import-screentime/.venv/bin/aw-import-screentime events preview --limit 0
```

Then it checks existing ActivityWatch events and inserts only missing event signatures, so overlapping five-hour runs do not duplicate data.

The job does not pull directly from the iPhone. Apple syncs Screen Time into the Mac's local Biome store first; the LaunchAgent then reacts to those local file updates. To inspect macOS' own sync timing, check:

```text
~/Library/Biome/sync/sync.db
```

`DevicePeer.last_sync_date` stores per-device sync time as Unix epoch seconds. `SyncSessionLog`, `SyncMessageLog`, and many stream tables use Apple `CFAbsoluteTime`; add `978307200` seconds to compare them with Unix timestamps.

Useful environment overrides:

```text
SCREENTIME_BIOME_IMPORTER_DIR=/Users/mh/aw-import-screentime
SCREENTIME_SINCE=all
SCREENTIME_FILE_LIMIT=0
SCREENTIME_STOREFRONTS=at,us
ACTIVITYWATCH_SQLITE_PATH=~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db
```

Use `SCREENTIME_SINCE=72h` only when deliberately testing a smaller window. The default `all` setting is the production path because it syncs as much local iPhone Screen Time history as macOS has downloaded.


## Install Launchd Jobs

Screen Time five-hour sync example:

```bash
mkdir -p "$HOME/Library/Application Support/aw-activitywatch-stack"
mkdir -p "$HOME/Library/Logs/aw-activitywatch-stack"

cp scripts/sync_screentime_folder.py "$HOME/Library/Application Support/aw-activitywatch-stack/"
cp scripts/sync-screentime-folder.sh "$HOME/Library/Application Support/aw-activitywatch-stack/"
python3 scripts/render_screentime_launchagent.py \
  launchd/ai.servas.aw-screentime-hourly.plist.template \
  "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist" \
  --home "$HOME"

launchctl bootstrap "gui/$UID" "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist"
launchctl kickstart -k "gui/$UID/ai.servas.aw-screentime-hourly"
```

Unload:

```bash
launchctl bootout "gui/$UID/ai.servas.aw-screentime-hourly"
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
```

## Current local status

A healthy local setup should show:

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
