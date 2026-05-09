# OpenClaw Agent Contract

This repo is the public operating contract for ActivityWatch-related local data in OpenClaw.

## Goal

OpenClaw agents should be able to ingest, verify, analyze, and improve the local lifelog stack without leaking private data or secrets.

## Data classes

- Public code/config templates:
  - safe to publish
  - examples, scripts, launchd templates, docs
- Local operational config:
  - machine-specific paths, launchd installed plists
  - safe to inspect locally, not safe to publish blindly
- Private data:
  - ActivityWatch event contents
  - WHOOP records
  - Apple Screen Time exports
  - email samples and attachments
  - never publish unless explicitly anonymized
- Secrets:
  - WHOOP client secret
  - OAuth access/refresh tokens
  - mailbox credentials
  - never print, send, or commit

## Agent workflow

Before changing anything:

- Verify ActivityWatch is reachable:
  `curl -fsS http://127.0.0.1:5600/api/0/info`
- List relevant buckets only:
  `python3 scripts/verify-aw-buckets.py`
- Check launchd jobs:
  - `ai.servas.aw-whoop-sync`
  - `ai.servas.aw-screentime-hourly`
- Run secret scan before every git push.

## Allowed actions

Agents may:

- update docs and templates
- add tests and verification scripts
- inspect bucket ids and aggregate counts
- run dry-runs
- push public repo improvements after tests pass

Agents must ask or stop before:

- publishing raw event exports
- sending emails/messages externally
- storing new credentials
- deleting ActivityWatch data
- changing broad mailbox fetch behavior

## Expected local import paths

Screen Time exports:

```text
~/ActivityWatchImports/screentime/
```

WHOOP token storage, owned by the WHOOP importer:

```text
~/Library/Application Support/aw-importer-whoop/tokens.json
```

Stack state:

```text
~/Library/Application Support/aw-activitywatch-stack/
```

## Reporting style

When reporting to Martin:

- say what changed
- say what was verified
- include repo links
- do not include private event contents unless asked
- include blockers plainly
