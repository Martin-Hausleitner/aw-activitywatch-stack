# Operations Runbook

## Daily health check

```bash
python3 scripts/aw-stack-doctor.py
python3 scripts/aw-health-report.py
```

## Screen Time imports

The Screen Time job reads local macOS Biome data synced from iPhone Screen Time:

```text
~/Library/Biome/streams/restricted/App.InFocus/remote/<device-id>/
```

The LaunchAgent starts at login, watches the local Biome Screen Time directories for changes, and keeps a five-hour interval as a fallback. Each run previews all locally available Biome history by default and inserts only missing ActivityWatch event signatures, so overlapping runs do not duplicate existing events.

Manual run:

```bash
~/Library/Application\ Support/aw-activitywatch-stack/sync_screentime_folder.py
```

The importer expects the ActivityWatch API on `127.0.0.1:5600`; if it is down, the Python runner opens ActivityWatch before importing.

If the API still is not reachable, the runner writes to the local ActivityWatch SQLite database at:

```text
~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db
```

This uses the same bucket/event schema as ActivityWatch, so the data is present for the next ActivityWatch UI/API start.

If this returns no events, check that Screen Time “Share Across Devices” is enabled and that `/Users/mh/aw-import-screentime/.venv/bin/aw-import-screentime devices --paths` lists iOS devices with recent files.

Use `SCREENTIME_SINCE=72h` for a deliberately smaller diagnostic run. Leave it unset in production so the LaunchAgent backfills as much local history as macOS has.

Check the installed LaunchAgent:

```bash
plutil -p "$HOME/Library/LaunchAgents/ai.servas.aw-screentime-hourly.plist"
launchctl print "gui/$UID/ai.servas.aw-screentime-hourly"
```

The plist should include `WatchPaths` for the Biome `App.InFocus/remote` root and existing iOS device directories, plus `StartInterval = 18000`.

To inspect when macOS itself last synced Biome data, query the local sync database without copying raw event data:

```bash
sqlite3 "$HOME/Library/Biome/sync/sync.db" \
  "select device_identifier, platform, datetime(last_sync_date, 'unixepoch', 'localtime') from DevicePeer order by last_sync_date desc;"
```

`DevicePeer.last_sync_date` is Unix epoch time. `SyncSessionLog` and `SyncMessageLog` use Apple `CFAbsoluteTime`; add `978307200` seconds before converting to wall-clock time.

## WHOOP sync

Launchd label:

```text
ai.servas.aw-whoop-sync
```

Status:

```bash
launchctl print "gui/$UID/ai.servas.aw-whoop-sync"
```

Logs:

```text
~/Library/Logs/aw-activitywatch-stack/whoop.out.log
~/Library/Logs/aw-activitywatch-stack/whoop.err.log
```

## Repair checklist

1. Check ActivityWatch is running.
2. Run `scripts/aw-stack-doctor.py`.
3. Check launchd logs.
4. Run importer dry-runs before importing new files.
5. Run `scripts/secret-scan.py` before committing changes.
