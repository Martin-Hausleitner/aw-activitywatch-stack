#!/bin/zsh
set -euo pipefail
setopt NULL_GLOB
IMPORT_DIR="${SCREENTIME_IMPORT_DIR:-$HOME/ActivityWatchImports/screentime}"
IMPORTER_DIR="${SCREENTIME_IMPORTER_DIR:-$HOME/.openclaw/workspace/aw-importer-apple-screentime}"
BUCKET="${SCREENTIME_BUCKET:-aw-import-screentime_ios_manual}"
LOG_DIR="$HOME/Library/Logs/aw-activitywatch-stack"
STATE_DIR="$HOME/Library/Application Support/aw-activitywatch-stack"
mkdir -p "$IMPORT_DIR" "$LOG_DIR" "$STATE_DIR"

if [[ ! -d "$IMPORTER_DIR" ]]; then
  echo "Screen Time importer directory not found: $IMPORTER_DIR" >&2
  exit 1
fi

if [[ ! -x "$IMPORTER_DIR/.venv/bin/aw-importer-apple-screentime" ]]; then
  echo "Screen Time importer executable not found. Did you install the importer venv?" >&2
  exit 1
fi

STATE_FILE="$STATE_DIR/screentime-imported-files.txt"
touch "$STATE_FILE"
cd "$IMPORTER_DIR"
found=0
for file in "$IMPORT_DIR"/*.csv "$IMPORT_DIR"/*.json; do
  [[ -e "$file" ]] || continue
  found=1
  key="$(/usr/bin/shasum -a 256 "$file" | /usr/bin/awk '{print $1}')  $file"
  if /usr/bin/grep -Fxq "$key" "$STATE_FILE"; then
    echo "skip already imported: $file"
    continue
  fi
  echo "importing: $file"
  .venv/bin/aw-importer-apple-screentime import-file "$file" --bucket "$BUCKET"
  echo "$key" >> "$STATE_FILE"
done
if [[ "$found" == 0 ]]; then
  echo "no Screen Time CSV/JSON files in $IMPORT_DIR"
fi
