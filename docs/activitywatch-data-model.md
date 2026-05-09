# ActivityWatch Data Model

This stack uses ActivityWatch as the local timeline hub.

## Bucket naming

Stable current buckets:

- `aw-importer-whoop-sleep`
- `aw-importer-whoop-workout`
- `aw-importer-whoop-cycle`
- `aw-importer-whoop-recovery`
- `aw-import-screentime_ios_*`

New code should avoid renaming existing buckets unless a migration script is provided.

## Timeline events

Use timeline events only for things with real start/end/duration:

- sleep
- workouts
- iPhone app usage
- desktop app/window activity

## Daily metrics

Use daily metric/summary events for point-in-time or day-level health context:

- recovery score
- HRV
- resting heart rate
- day strain
- daily phone totals
- sleep score summary

Recommended future bucket:

```text
aw-health-daily
```

Recommended timestamp semantics:

- timestamp: local day start or sleep-end anchor
- duration: `0` for point metric, or `86400` only if the UI benefits from full-day display
- data: normalized metrics, source ids, and source timestamps

## Privacy defaults

- aggregate by app/category/day
- hide raw URLs and window titles unless requested
- never publish raw health or app-usage exports
