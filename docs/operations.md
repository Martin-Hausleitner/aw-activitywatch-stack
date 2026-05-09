# Operations Runbook

## Daily health check

```bash
python3 scripts/aw-stack-doctor.py
python3 scripts/aw-health-report.py
```

## Screen Time imports

Drop CSV/JSON exports into:

```text
~/ActivityWatchImports/screentime/
```

The hourly job imports unchanged files only once by SHA-256.

Manual run:

```bash
~/Library/Application\ Support/aw-activitywatch-stack/sync-screentime-folder.sh
```

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
