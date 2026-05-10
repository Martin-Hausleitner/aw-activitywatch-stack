#!/bin/zsh
set -euo pipefail
setopt NULL_GLOB

IMPORT_DIR="${APPLE_HEALTH_IMPORT_DIR:-$HOME/health-sync/raw}"
FALLBACK_DIR="${APPLE_HEALTH_EXPORT_DIR:-$HOME/ActivityWatchImports/apple-health}"
IMPORTER_DIR="${APPLE_HEALTH_IMPORTER_DIR:-$HOME/.openclaw/workspace/aw-importer-apple-health}"
LOG_DIR="$HOME/Library/Logs/aw-activitywatch-stack"
STATE_DIR="$HOME/Library/Application Support/aw-activitywatch-stack"
STATE_FILE="$STATE_DIR/apple-health-imported-files.txt"

mkdir -p "$IMPORT_DIR" "$FALLBACK_DIR" "$LOG_DIR" "$STATE_DIR"
touch "$STATE_FILE"

if [[ ! -d "$IMPORTER_DIR" ]]; then
  echo "Apple Health importer directory not found: $IMPORTER_DIR" >&2
  exit 1
fi

if [[ ! -x "$IMPORTER_DIR/.venv/bin/aw-importer-apple-health" ]]; then
  echo "Apple Health importer executable not found. Did you install the importer venv?" >&2
  exit 1
fi

import_once() {
  local file="$1"
  local mode="$2"
  local key
  key="$(/usr/bin/shasum -a 256 "$file" | /usr/bin/awk '{print $1}')  $file"
  if /usr/bin/grep -Fxq "$key" "$STATE_FILE"; then
    echo "skip already imported: $file"
    return 0
  fi

  echo "importing: $file"
  cd "$IMPORTER_DIR"
  if [[ "$mode" == "json" ]]; then
    .venv/bin/aw-importer-apple-health import-json "$file"
  else
    .venv/bin/aw-importer-apple-health import-export "$file"
  fi
  echo "$key" >> "$STATE_FILE"
}

found=0
for file in "$IMPORT_DIR"/*.json; do
  [[ -e "$file" ]] || continue
  found=1
  import_once "$file" json
done

for file in "$FALLBACK_DIR"/*.zip "$FALLBACK_DIR"/*.xml "$FALLBACK_DIR"/*.xml.gz; do
  [[ -e "$file" ]] || continue
  found=1
  import_once "$file" export
done

if [[ "$found" == 0 ]]; then
  echo "no Apple Health JSON/XML/ZIP files in $IMPORT_DIR or $FALLBACK_DIR"
fi
