#!/usr/bin/env python3
"""Upload image files through PicGo GUI local server and print returned URLs.

Usage:
  python3 picgo_upload.py /abs/path/a.png [/abs/path/b.jpg ...]

Environment:
  PICGO_SERVER=http://127.0.0.1:36677   # optional
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

server = os.environ.get("PICGO_SERVER", "http://127.0.0.1:36677").rstrip("/")
files = [str(Path(p).expanduser().resolve()) for p in sys.argv[1:]]

if not files:
    print("Usage: picgo_upload.py /absolute/path/to/image [more...]", file=sys.stderr)
    sys.exit(2)

missing = [p for p in files if not Path(p).is_file()]
if missing:
    print("Missing file(s): " + ", ".join(missing), file=sys.stderr)
    sys.exit(2)

payload = json.dumps({"list": files}).encode("utf-8")
req = urllib.request.Request(
    server + "/upload",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8", errors="replace")
except urllib.error.URLError as e:
    print(f"PicGo upload failed: cannot reach {server}/upload: {e}", file=sys.stderr)
    sys.exit(1)

try:
    data = json.loads(body)
except json.JSONDecodeError:
    print("PicGo upload failed: non-JSON response:", body, file=sys.stderr)
    sys.exit(1)

if not data.get("success"):
    print("PicGo upload failed: " + json.dumps(data, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)

urls = data.get("result") or []
if not isinstance(urls, list) or not urls:
    print("PicGo upload failed: no result URL: " + json.dumps(data, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)

for url in urls:
    print(url)
