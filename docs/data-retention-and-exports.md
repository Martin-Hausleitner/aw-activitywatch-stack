# Data Retention and Exports

## Stays local

- Raw WHOOP exports
- Raw Apple Screen Time exports
- Email samples (`.eml`, `.em1`, `.mbox`)
- ActivityWatch databases
- OAuth tokens and client secrets
- Private reports

## Can be public

- Code
- Templates
- Empty config examples
- Aggregate examples with fake data
- Documentation

## Local ignored paths

Recommended local paths:

- `~/ActivityWatchImports/screentime/`
- `~/ActivityWatchImports/whoop-exports/`
- `~/Library/Application Support/aw-activitywatch-stack/`
- `~/Library/Logs/aw-activitywatch-stack/`

## Derived reports

- Public reports must contain no raw URLs, window titles, health details, email content, or app-usage exports.
- Private reports should stay under `reports/private/` or another ignored local folder.
