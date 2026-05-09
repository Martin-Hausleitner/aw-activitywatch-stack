#!/bin/zsh
set -euo pipefail

AW_WHOOP_DIR="${AW_WHOOP_DIR:-$HOME/.openclaw/workspace/aw-importer-whoop}"
CLIENT_ID="${WHOOP_CLIENT_ID:?set WHOOP_CLIENT_ID}"
KEYCHAIN_SERVICE="${WHOOP_KEYCHAIN_SERVICE:-aw-importer-whoop-client-secret}"
CLIENT_SECRET="$(/usr/bin/security find-generic-password -a "$USER" -s "$KEYCHAIN_SERVICE" -w)"

if [[ ! -d "$AW_WHOOP_DIR" ]]; then
  echo "WHOOP importer directory not found: $AW_WHOOP_DIR" >&2
  exit 1
fi

if [[ ! -x "$AW_WHOOP_DIR/.venv/bin/aw-importer-whoop" ]]; then
  echo "WHOOP importer executable not found. Did you install the importer venv?" >&2
  exit 1
fi

cd "$AW_WHOOP_DIR"
exec .venv/bin/aw-importer-whoop sync --client-id "$CLIENT_ID" --client-secret "$CLIENT_SECRET" --interval "${WHOOP_SYNC_INTERVAL:-900}"
