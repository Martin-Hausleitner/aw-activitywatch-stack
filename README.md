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

## ✨ What This Is

This repo is the public operating manual and automation layer for a local ActivityWatch-based health and lifelog stack.

It publishes the safe, reusable parts:

- 🧭 architecture and operating notes
- 🛠️ installer scripts
- 🚀 launchd templates
- ✅ validation tools
- 🤖 agent contracts
- 🔒 privacy rules
- 📱 iPhone Screen Time automation
- 💓 WHOOP and health data integration notes

It does **not** contain private health exports, Screen Time exports, WHOOP tokens, OAuth secrets, mailbox credentials, or ActivityWatch databases.

<p align="center">
  <img src="docs/assets/data-model-radar.svg" alt="ActivityWatch data model" width="100%">
</p>

## 🚀 Quickstart

```bash
git clone https://github.com/Martin-Hausleitner/aw-activitywatch-stack.git
cd aw-activitywatch-stack
python3 scripts/aw-stack-doctor.py
scripts/install-local-stack.sh
```

That installs or refreshes the iPhone Screen Time LaunchAgent:

```text
~/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist
```

The installed job runs:

- immediately at login
- whenever macOS writes local Screen Time Biome updates
- every 5 hours as a fallback

## 🤖 Agent Quickstart

Agents working in this repo should use this flow:

```bash
cd /Users/mh/.openclaw/workspace/aw-activitywatch-stack
python3 scripts/aw-stack-doctor.py
scripts/install-local-stack.sh
launchctl print "gui/$UID/ai.servas.aw-screentime-hourly"
python3 scripts/secret-scan.py
```

When reporting success, verify the real local state first:

```bash
plutil -p "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist"
sqlite3 "$HOME/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db" \
  "select b.id, count(e.id), min(e.timestamp), max(e.timestamp) from bucketmodel b left join eventmodel e on e.bucket_id=b.key where b.id like 'aw-import-screentime_ios_%' group by b.id;"
```

Agent rules:

- 🔒 Never commit private exports, app usage logs, ActivityWatch DBs, OAuth files, or mailbox samples.
- ✅ Run `python3 scripts/secret-scan.py` before every push.
- 📍 Prefer local paths and `127.0.0.1`; do not upload private telemetry.
- 🧪 Verify launchd status and ActivityWatch buckets before saying the sync works.
- 🧹 Stage only files related to the current task; leave unrelated local work alone.

## 📱 iPhone Screen Time Sync

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
- listens for local Biome file updates with launchd `WatchPaths`
- keeps `StartInterval = 18000` seconds as a 5-hour fallback

The first run is a full backfill. Later runs are incremental in effect, because existing ActivityWatch events are checked before inserts.

## 🧠 How The Sync Really Works

The Mac does not pull live data from the iPhone for every tap. The flow is:

```text
iPhone Screen Time
  -> Apple/iCloud/Biome sync
  -> local Mac Biome files
  -> LaunchAgent WatchPaths trigger
  -> aw-import-screentime preview
  -> ActivityWatch bucket insert
```

The best local timing source is:

```text
~/Library/Biome/sync/sync.db
```

Useful sync metadata:

- `DevicePeer.last_sync_date`: per-device last sync time, stored as Unix epoch seconds
- `SyncSessionLog`: sync sessions, stored as Apple `CFAbsoluteTime`
- `SyncMessageLog`: per-peer sync messages, stored as Apple `CFAbsoluteTime`

For `CFAbsoluteTime`, add `978307200` seconds before converting to Unix time.

## 🛡️ ActivityWatch Fallback

The runner uses the ActivityWatch HTTP API when it is available:

```text
http://127.0.0.1:5600/api/0
```

If the API is not reachable, it writes to the local ActivityWatch SQLite database:

```text
~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db
```

That keeps imports working even when the tray app or HTTP server is not currently alive. The data is present for the next ActivityWatch UI/API start.

## 🧰 Install Details

The installer copies scripts into:

```text
~/Library/Application Support/aw-activitywatch-stack/
```

It renders the LaunchAgent into:

```text
~/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist
```

The LaunchAgent watches:

```text
~/Library/Biome/streams/restricted/App.InFocus/remote
~/Library/Biome/streams/restricted/App.InFocus/remote/<device-id>
```

Manual install commands:

```bash
mkdir -p "$HOME/Library/Application Support/aw-activitywatch-stack"
mkdir -p "$HOME/Library/Logs/aw-activitywatch-stack"

cp scripts/sync_screentime_folder.py "$HOME/Library/Application Support/aw-activitywatch-stack/"
cp scripts/sync-screentime-folder.sh "$HOME/Library/Application Support/aw-activitywatch-stack/"

python3 scripts/render_screentime_launchagent.py \
  launchd/ai.servas.aw-screentime-hourly.plist.template \
  "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist" \
  --home "$HOME"

launchctl bootout "gui/$UID" "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$UID" "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist"
launchctl kickstart -k "gui/$UID/ai.servas.aw-screentime-hourly"
```

Unload:

```bash
launchctl bootout "gui/$UID/ai.servas.aw-screentime-hourly"
```

## ✅ Verify

Run the core checks:

```bash
pytest tests/test_sync_screentime_folder.py tests/test_render_screentime_launchagent.py -q
python3 scripts/secret-scan.py
plutil -lint launchd/ai.servas.aw-screentime-hourly.plist.template
```

Check the installed job:

```bash
plutil -p "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist"
launchctl print "gui/$UID/ai.servas.aw-screentime-hourly"
```

Check imported iPhone Screen Time buckets:

```bash
sqlite3 "$HOME/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db" \
  "select b.id, count(e.id), min(e.timestamp), max(e.timestamp), round(sum(e.duration)/60.0, 2) from bucketmodel b left join eventmodel e on e.bucket_id=b.key where b.id like 'aw-import-screentime_ios_%' group by b.id;"
```

Check recent Apple Biome sync timing:

```bash
sqlite3 "$HOME/Library/Biome/sync/sync.db" \
  "select device_identifier, platform, datetime(last_sync_date, 'unixepoch', 'localtime') from DevicePeer order by last_sync_date desc;"
```

## 🗂️ Repo Layout

```text
scripts/   Import, verification, validation, and agent helpers
launchd/   macOS LaunchAgent templates
docs/      Privacy, data-source, and OpenClaw operating notes
config/    Non-secret example configuration
```

## 🔗 Related Repositories

- WHOOP importer: https://github.com/Martin-Hausleitner/aw-importer-whoop
- Apple Screen Time importer: https://github.com/Martin-Hausleitner/aw-importer-apple-screentime
- Biome Screen Time importer: https://github.com/ActivityWatch/aw-import-screentime

## 📊 Expected ActivityWatch Buckets

- `aw-importer-whoop-sleep`
- `aw-importer-whoop-workout`
- `aw-importer-whoop-cycle`
- `aw-importer-whoop-recovery`
- `aw-import-screentime_ios_*`

Recommended model:

- WHOOP sleep/workouts: timeline events
- WHOOP recovery/day strain: daily metrics
- iPhone Screen Time: app-usage timeline events
- ActivityWatch desktop usage: baseline work timeline

## 🧭 OpenClaw Integration

OpenClaw agents should treat this repo as the operating contract for local ActivityWatch health and lifelog data.

Key docs:

- `docs/openclaw-agent-contract.md` — what agents may inspect, update, publish, or must keep private
- `docs/openclaw-data-ingestion-plan.md` — canonical source and ingestion plan
- `docs/openclaw-agent-safety-contract.md` — explicit agent safety rules
- `docs/data-retention-and-exports.md` — what stays local vs public
- `docs/activitywatch-data-model.md` — bucket and event semantics
- `docs/operations.md` — local runbook and repair checklist
- `docs/data-sources.md` — WHOOP, Screen Time, ActivityWatch, and future daily summary model
- `docs/whoop-export-email-policy.md` — privacy-safe targeted email export discovery

## 🔧 Useful Environment Overrides

```text
SCREENTIME_BIOME_IMPORTER_DIR=/Users/mh/aw-import-screentime
SCREENTIME_SINCE=all
SCREENTIME_FILE_LIMIT=0
SCREENTIME_STOREFRONTS=at,us
ACTIVITYWATCH_API_URL=http://127.0.0.1:5600/api/0
ACTIVITYWATCH_SQLITE_PATH=~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db
```

Use `SCREENTIME_SINCE=72h` only for a deliberately smaller diagnostic run. The production default is `all`, because it syncs as much local iPhone Screen Time history as macOS has downloaded.

## 🔐 Security

Do not commit:

- tokens
- client secrets
- exported health or Screen Time files
- `.eml` / `.em1` samples
- mailbox config
- logs containing private app usage
- ActivityWatch SQLite databases

Privacy default: aggregate by app/category unless detailed titles are explicitly requested and locally appropriate.
