#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

AW = os.environ.get("AW_SERVER_URL", "http://127.0.0.1:5600").rstrip("/")
CHECKS: list[tuple[str, bool, str, bool]] = []


def check(name: str, ok: bool, detail: str = "", optional: bool = False) -> None:
    CHECKS.append((name, ok, detail, optional))


def launchd(label: str) -> tuple[bool, str]:
    p = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{label}"], capture_output=True, text=True)
    if p.returncode != 0:
        return False, "not loaded"
    state = "unknown"
    for line in p.stdout.splitlines():
        if "state =" in line:
            state = line.strip()
            break
    return True, state

try:
    info = json.load(urllib.request.urlopen(f"{AW}/api/0/info", timeout=3))
    check("ActivityWatch API", True, f"{info.get('version')} {info.get('hostname')}")
except Exception as exc:
    check("ActivityWatch API", False, str(exc))

try:
    buckets = json.load(urllib.request.urlopen(f"{AW}/api/0/buckets/", timeout=3))
    whoop = [k for k in buckets if k.startswith("aw-importer-whoop")]
    st = [k for k in buckets if k.startswith("aw-import-screentime")]
    apple_health = [k for k in buckets if k.startswith("aw-importer-apple-health")]
    check("WHOOP buckets", bool(whoop), f"{len(whoop)} found")
    check("Screen Time buckets", bool(st), f"{len(st)} found")
    check("Apple Health buckets", bool(apple_health), f"{len(apple_health)} found", optional=True)
except Exception as exc:
    check("Bucket listing", False, str(exc))

for label in ("ai.servas.aw-whoop-sync", "ai.servas.aw-screentime-hourly", "ai.servas.aw-apple-health-sync"):
    ok, detail = launchd(label)
    if label in {"ai.servas.aw-screentime-hourly", "ai.servas.aw-apple-health-sync"} and ok:
        # Short-lived interval jobs are OK when loaded but currently not running.
        check(f"launchd {label}", True, detail)
    elif label == "ai.servas.aw-apple-health-sync":
        check(f"launchd {label}", ok, detail, optional=True)
    else:
        check(f"launchd {label}", ok, detail)

check("Screen Time Biome stream", Path.home().joinpath("Library/Biome/streams/restricted/App.InFocus/remote").exists(), "~/Library/Biome/streams/restricted/App.InFocus/remote")
check("Screen Time Biome importer", Path.home().joinpath("aw-import-screentime/.venv/bin/aw-import-screentime").exists(), "~/aw-import-screentime/.venv/bin/aw-import-screentime")
check("Apple Health raw dropzone", Path.home().joinpath("health-sync/raw").exists(), "~/health-sync/raw")
check("Apple Health export fallback", Path.home().joinpath("ActivityWatchImports/apple-health").exists(), "~/ActivityWatchImports/apple-health")
check("Apple Health state", Path.home().joinpath("Library/Application Support/aw-importer-apple-health/state.json").exists(), "~/Library/Application Support/aw-importer-apple-health/state.json", optional=True)
check("Stack state dir", Path.home().joinpath("Library/Application Support/aw-activitywatch-stack").exists(), "~/Library/Application Support/aw-activitywatch-stack")

failed = False
for name, ok, detail, optional in CHECKS:
    icon = "✅" if ok else ("⚠️" if optional else "❌")
    suffix = " (not configured yet)" if optional and not ok else ""
    print(f"{icon} {name}: {detail}{suffix}")
    failed = failed or (not ok and not optional)

sys.exit(1 if failed else 0)
