# OpenClaw Agent Safety Contract

## Allowed by default

- Query the local ActivityWatch API.
- List bucket names and event counts.
- Aggregate by app/category/day.
- Generate local summaries.
- Read public repo docs/scripts.

## Requires explicit confirmation

- Reading raw browser URLs or window titles.
- Opening raw WHOOP exports.
- Searching email.
- Writing reports containing private data.
- Installing/changing launchd jobs.
- Changing importer configs.

## Forbidden for normal analysis

- Committing secrets or export files.
- Reading full mailboxes.
- Posting private health/activity summaries externally.
- Writing directly to ActivityWatch SQLite.
- Deleting, compacting, or migrating ActivityWatch data.

## Redaction defaults

- URLs → domain only
- window titles → app/category
- email → sender domain + matched rule
- WHOOP → daily aggregate
- Screen Time → app/category totals
