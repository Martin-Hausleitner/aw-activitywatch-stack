#!/bin/zsh
set -euo pipefail
# Template: copy outside git and fill via env/keychain.
AW_WHOOP_DIR="${AW_WHOOP_DIR:-$HOME/.openclaw/workspace/aw-importer-whoop}"
CLIENT_ID="${WHOOP_CLIENT_ID:?set WHOOP_CLIENT_ID}"
CLIENT_SECRET="${WHOOP_CLIENT_SECRET:?set WHOOP_CLIENT_SECRET or read it from Keychain}"
cd "$AW_WHOOP_DIR"
exec .venv/bin/aw-importer-whoop sync --client-id "$CLIENT_ID" --client-secret "$CLIENT_SECRET" --interval "${WHOOP_SYNC_INTERVAL:-900}"
