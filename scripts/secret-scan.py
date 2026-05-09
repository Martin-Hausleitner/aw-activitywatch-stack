#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = [
    re.compile(r"gho_[A-Za-z0-9_]+"),
    re.compile(r"refresh_token\s*[:=]", re.I),
    re.compile(r"access_token\s*[:=]", re.I),
    re.compile(r"client_secret\s*[:=]\s*['\"][0-9a-fA-F]{32,}"),
    re.compile(r"code=[A-Za-z0-9_.-]{20,}.*state=", re.I),
]
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv"}

hits: list[tuple[str, int, str]] = []
for path in Path(".").rglob("*"):
    if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
        continue
    text = path.read_text(errors="ignore")
    for line_no, line in enumerate(text.splitlines(), 1):
        if any(pattern.search(line) for pattern in PATTERNS):
            hits.append((str(path), line_no, line[:120]))

if hits:
    print("Potential secrets found:")
    for path, line_no, line in hits:
        print(f"- {path}:{line_no}: {line}")
    sys.exit(1)
print("secret_scan_ok")
