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

## Apple Health sync

Optional launchd label:

```text
ai.servas.aw-apple-health-sync
```

Dropzones:

```text
~/health-sync/raw/
~/ActivityWatchImports/apple-health/
```

Manual run after installing `sync-apple-health-folder.sh` locally:

```bash
~/Library/Application\ Support/aw-activitywatch-stack/sync-apple-health-folder.sh
```

A `not loaded` Apple Health launchd job is acceptable until the iPhone Health producer is paired.

## Repair checklist

1. Check ActivityWatch is running.
2. Run `scripts/aw-stack-doctor.py`.
3. Check launchd logs.
4. Run importer dry-runs before importing new files.
5. Run `python3 scripts/validate-openclaw-ingestion-config.py config/openclaw-ingestion.example.json` after config-schema edits.
6. Run `scripts/secret-scan.py` before committing changes.
