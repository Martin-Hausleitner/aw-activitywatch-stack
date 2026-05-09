# OpenClaw Data Ingestion Plan

This is the canonical plan for ActivityWatch-related data ingestion on a local OpenClaw machine.

## Sources

### 1. ActivityWatch local API

- Primary API: `http://127.0.0.1:5600/api/0`
- Fallback: read-only SQLite copies only
- Never write directly to ActivityWatch SQLite.

Relevant buckets:

- `aw-watcher-afk_*`
- `aw-watcher-window_*`
- `aw-watcher-web-*`
- `aw-watcher-vscode_*`
- `aw-importer-whoop-*`
- `aw-import-screentime_ios_*`

### 2. WHOOP API importer

Repo: https://github.com/Martin-Hausleitner/aw-importer-whoop

- Secrets live in Keychain/env outside git.
- Tokens live in the importer's local application-support directory.
- Sleep and workouts are timeline events.
- Recovery and day strain should become daily metrics, not noisy timeline blocks.

### 3. WHOOP export emails

- Use targeted search only after a sample email has been inspected locally.
- Never crawl full mailboxes.
- Store raw exports under an ignored local path such as:
  `~/ActivityWatchImports/whoop-exports/`
- Commit matcher rules only, never messages or attachments.

### 4. Apple Screen Time imports

Repo: https://github.com/Martin-Hausleitner/aw-importer-apple-screentime

- Dropzone: `~/ActivityWatchImports/screentime/`
- Hourly launchd job imports new `.csv` / `.json` files.
- Idempotency is based on SHA-256 file hashes in local state.

### 5. OpenClaw analysis layer

Agents should read from ActivityWatch API and generated aggregate summaries.

Defaults:

- URLs: domain only
- window titles: category/app only
- email: matched rule only
- health data: daily aggregate only

Raw detail requires explicit user request.
