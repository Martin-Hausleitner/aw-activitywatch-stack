---
name: activity-watch
description: Use for read-only ActivityWatch analysis on macOS: locating local ActivityWatch data, querying the local API/SQLite buckets, summarizing active hours, app/browser usage, workday shape, and assessing 9-to-5 vs founder-style work patterns without modifying data.
---

# ActivityWatch Analysis

Use this skill when the user asks to inspect ActivityWatch data, work patterns, focus, 9-to-5 behavior, founder workload, app usage, browser usage, AFK/active time, or productivity rhythms.

## Safety

- Read-only only. Do not delete, compact, migrate, or write ActivityWatch databases.
- Prefer the local API if `aw-server` is running: `http://127.0.0.1:5600/api/0`.
- If API is down, inspect SQLite copies read-only:
  - `~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db`
  - `~/Library/Application Support/activitywatch/aw-server-rust/sqlite.db`
- Treat window titles and URLs as private. Summarize categories/apps unless the user explicitly asks for detailed titles/URLs.

## Data discovery

Run:

```bash
ps aux | grep -i '[a]ctivitywatch\|[a]w-'
lsof -nP -iTCP:5600 -sTCP:LISTEN
find "$HOME/Library/Application Support/activitywatch" -maxdepth 3 -type f -o -type d
```

Common buckets:

- `aw-watcher-afk_<host>` — `status: not-afk|afk`, best source for active/away time.
- `aw-watcher-window_<host>` — current foreground app/title.
- `aw-watcher-web-brave_<host>` / `aw-watcher-web-chrome_<host>` — browser tab title/URL.
- `aw-watcher-vscode_<host>` — editor activity.
- `aw-import-screentime_*` — imported iOS/app screen time when present.

## Recommended workflow

1. Discover buckets from `/api/0/buckets/`.
2. Pick the newest local host buckets for AFK/window/browser.
3. Query events with explicit start/end ISO timestamps.
4. Aggregate by local timezone (`${LOCAL_TIMEZONE:-Europe/Vienna}`).
5. Report:
   - active hours/day
   - first/last activity and work span
   - before 09:00, after 18:00, weekend activity
   - top apps/categories
   - caveats/artifacts
6. Assess:
   - work-pattern score: high if most active time is Mon-Fri 09:00-17:00, low evening/weekend spread.
   - independent/flexible-work score: high if irregular, evening/weekend, context switching, long spans, communication/dev/research mix.
   - Better: protect focus blocks, define shutdown, separate maker/manager time, reduce noisy apps.
   - Worse/risky: fragmented days, late-night work, always-on weekends, excessive chat/browser switching.

## Helper script

Use `scripts/aw_summary.py` for a quick read-only report:

```bash
python3 ~/.openclaw/workspace/skills/activity-watch/scripts/aw_summary.py --days 14
```

It only reads the local API and prints aggregate statistics. If the API is down, start/open ActivityWatch first or inspect SQLite manually.
