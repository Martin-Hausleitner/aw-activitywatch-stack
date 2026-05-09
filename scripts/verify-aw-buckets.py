#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

base_url = os.environ.get("AW_SERVER_URL", "http://127.0.0.1:5600").rstrip("/")
url = f"{base_url}/api/0/buckets/"

try:
    with urllib.request.urlopen(url, timeout=3) as response:
        buckets = json.load(response)
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"ActivityWatch is not reachable at {base_url}: {exc}", file=sys.stderr)
    sys.exit(1)

found = False
for key, value in sorted(buckets.items()):
    if any(term in key.lower() for term in ("whoop", "screentime", "import")):
        found = True
        print(key, value.get("type"), value.get("created"))

if not found:
    print("No WHOOP/Screen Time/import buckets found.")
