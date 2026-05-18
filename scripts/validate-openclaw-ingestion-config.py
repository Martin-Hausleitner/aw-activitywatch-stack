#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: validate-openclaw-ingestion-config.py config/openclaw-ingestion.local.json|config/openclaw-ingestion.example.json", file=sys.stderr)
    sys.exit(64)

path = Path(sys.argv[1])
is_example = path.name.endswith(".example.json")
if not path.exists():
    print(f"Config not found: {path}", file=sys.stderr)
    sys.exit(1)

text = path.read_text()
if re.search(r"(access_token|refresh_token|client_secret|gho_)", text, re.I):
    print("Config appears to contain a secret/token; refusing.", file=sys.stderr)
    sys.exit(1)

cfg = json.loads(text)
privacy = cfg.get("privacy", {})
if privacy.get("allow_email_search_without_confirmation") is not False:
    print("allow_email_search_without_confirmation must be false", file=sys.stderr)
    sys.exit(1)
if privacy.get("allow_raw_health_export_read_without_confirmation") is not False:
    print("allow_raw_health_export_read_without_confirmation must be false", file=sys.stderr)
    sys.exit(1)

api_url = cfg.get("activitywatch", {}).get("api_url", "http://127.0.0.1:5600/api/0").rstrip("/")
if not is_example:
    try:
        urllib.request.urlopen(f"{api_url}/info", timeout=3).read()
    except Exception as exc:
        print(f"ActivityWatch API not reachable at {api_url}: {exc}", file=sys.stderr)
        sys.exit(1)

    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if tracked.returncode == 0:
        print(f"Local config is tracked by git and should not be: {path}", file=sys.stderr)
        sys.exit(1)

print("openclaw_ingestion_config_ok")
