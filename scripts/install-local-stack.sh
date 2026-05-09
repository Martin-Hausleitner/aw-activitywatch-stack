#!/bin/zsh
set -euo pipefail

APP_SUPPORT="$HOME/Library/Application Support/aw-activitywatch-stack"
LOG_DIR="$HOME/Library/Logs/aw-activitywatch-stack"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

mkdir -p "$APP_SUPPORT" "$LOG_DIR" "$LAUNCH_AGENTS" "$HOME/ActivityWatchImports/screentime" "$HOME/ActivityWatchImports/whoop-exports"
cp "$ROOT/scripts/sync-screentime-folder.sh" "$APP_SUPPORT/sync-screentime-folder.sh"
chmod 700 "$APP_SUPPORT/sync-screentime-folder.sh"

if [[ -f "$ROOT/scripts/sync-whoop-keychain.example.sh" ]]; then
  cp "$ROOT/scripts/sync-whoop-keychain.example.sh" "$APP_SUPPORT/sync-whoop-keychain.sh.example"
fi

cp "$ROOT/launchd/ai.servas.aw-screentime-hourly.plist.template" "$LAUNCH_AGENTS/ai.servas.aw-screentime-hourly.plist"
/usr/bin/sed -i '' "s#/Users/YOU#$HOME#g" "$LAUNCH_AGENTS/ai.servas.aw-screentime-hourly.plist"

launchctl bootout "gui/$UID" "$LAUNCH_AGENTS/ai.servas.aw-screentime-hourly.plist" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$UID" "$LAUNCH_AGENTS/ai.servas.aw-screentime-hourly.plist"
launchctl kickstart -k "gui/$UID/ai.servas.aw-screentime-hourly"

echo "installed_screen_time_hourly=ok"
echo "dropzone=$HOME/ActivityWatchImports/screentime"
echo "logs=$LOG_DIR"
