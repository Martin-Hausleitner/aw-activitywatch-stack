#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

AW = os.environ.get("AW_SERVER_URL", "http://127.0.0.1:5600").rstrip("/")
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))


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
    check("WHOOP buckets", bool(whoop), f"{len(whoop)} found")
    check("Screen Time buckets", bool(st), f"{len(st)} found")
except Exception as exc:
    check("Bucket listing", False, str(exc))

for label in ("ai.servas.aw-whoop-sync", "ai.servas.aw-screentime-hourly"):
    ok, detail = launchd(label)
    check(f"launchd {label}", ok, detail)

check("Screen Time dropzone", Path.home().joinpath("ActivityWatchImports/screentime").exists(), "~/ActivityWatchImports/screentime")
check("Stack state dir", Path.home().joinpath("Library/Application Support/aw-activitywatch-stack").exists(), "~/Library/Application Support/aw-activitywatch-stack")

failed = False
for name, ok, detail in CHECKS:
    icon = "✅" if ok else "❌"
    print(f"{icon} {name}: {detail}")
    failed = failed or not ok

sys.exit(1 if failed else 0)
