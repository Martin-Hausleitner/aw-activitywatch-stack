#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: discover-whoop-export-email-rules.py sample.eml", file=sys.stderr)
    sys.exit(64)

path = Path(sys.argv[1])
if not path.exists() or not path.is_file():
    print(f"Sample email not found: {path}", file=sys.stderr)
    sys.exit(1)

msg = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
print("Do not commit this sample email. Extract matcher rules only.\n")
print(f"From: {msg.get('From', '')}")
print(f"Subject: {msg.get('Subject', '')}")
print("Attachments:")
for part in msg.iter_attachments():
    print(f"- {part.get_filename() or '(unnamed)'}")

body = msg.get_body(preferencelist=("plain", "html"))
if body:
    content = body.get_content()[:500]
    digest = hashlib.sha256(content.encode(errors="ignore")).hexdigest()[:16]
    snippet = " ".join(content.split())[:160]
    print(f"Body snippet hash: {digest}")
    print(f"Body snippet candidate: {snippet}")
