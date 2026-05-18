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

The five-hour job previews the last 72 hours and inserts only missing ActivityWatch event signatures, so overlapping runs do not duplicate existing events.

Manual run:

```bash
~/Library/Application\ Support/aw-activitywatch-stack/sync_screentime_folder.py
```

The importer expects the ActivityWatch API on `127.0.0.1:5600`; if it is down, the Python runner opens ActivityWatch before importing.

If this returns no events, check that Screen Time “Share Across Devices” is enabled and that `/Users/mh/aw-import-screentime/.venv/bin/aw-import-screentime devices --paths` lists iOS devices with recent files.

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
