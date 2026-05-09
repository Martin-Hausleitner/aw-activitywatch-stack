#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from collections import defaultdict

BASE = "http://127.0.0.1:5600/api/0"
PREFIXES = ("aw-importer-whoop", "aw-import-screentime")


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def main() -> None:
    info = get_json(f"{BASE}/info")
    print(f"ActivityWatch: {info.get('version')} host={info.get('hostname')}")
    buckets = get_json(f"{BASE}/buckets/")
    grouped: dict[str, list[str]] = defaultdict(list)
    for bucket_id, meta in sorted(buckets.items()):
        if bucket_id.startswith("aw-importer-whoop"):
            grouped["WHOOP"].append(f"{bucket_id} ({meta.get('type')})")
        elif bucket_id.startswith("aw-import-screentime"):
            grouped["Screen Time"].append(f"{bucket_id} ({meta.get('type')})")
    for group in ("WHOOP", "Screen Time"):
        print(f"\n{group} buckets:")
        for line in grouped.get(group, []):
            print(f"- {line}")
        if not grouped.get(group):
            print("- none found")


if __name__ == "__main__":
    main()
