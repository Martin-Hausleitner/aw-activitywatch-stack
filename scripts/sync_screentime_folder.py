#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_AW_BASE_URL = "http://127.0.0.1:5600/api/0"
DEFAULT_SINCE = "all"
ACTIVITYWATCH_APP = Path("/Applications/ActivityWatch.app")


class Config:
    def __init__(
        self,
        biome_importer_dir: Path,
        aw_base_url: str,
        state_dir: Path,
        since: str,
        file_limit: int,
        storefronts: list[str],
        platform: int,
    ) -> None:
        self.biome_importer_dir = biome_importer_dir
        self.aw_base_url = aw_base_url
        self.state_dir = state_dir
        self.since = since
        self.file_limit = file_limit
        self.storefronts = storefronts
        self.platform = platform

    @classmethod
    def from_env(cls) -> "Config":
        home = Path.home()
        storefronts_raw = os.environ.get("SCREENTIME_STOREFRONTS", "at,us")
        storefronts = [item.strip() for item in storefronts_raw.split(",") if item.strip()]
        return cls(
            biome_importer_dir=Path(os.environ.get("SCREENTIME_BIOME_IMPORTER_DIR", home / "aw-import-screentime")).expanduser(),
            aw_base_url=os.environ.get("ACTIVITYWATCH_API_URL", DEFAULT_AW_BASE_URL).rstrip("/"),
            state_dir=Path(os.environ.get("SCREENTIME_STATE_DIR", home / "Library" / "Application Support" / "aw-activitywatch-stack")).expanduser(),
            since=os.environ.get("SCREENTIME_SINCE", DEFAULT_SINCE),
            file_limit=int(os.environ.get("SCREENTIME_FILE_LIMIT", "0")),
            storefronts=storefronts,
            platform=int(os.environ.get("SCREENTIME_PLATFORM", "2")),
        )


class Lock:
    def __init__(self, path: Path, stale_after_seconds: int = 21600) -> None:
        self.path = path
        self.stale_after_seconds = stale_after_seconds
        self.acquired = False

    def __enter__(self) -> "Lock":
        try:
            self.path.mkdir()
            self._write_pid()
            self.acquired = True
            return self
        except FileExistsError:
            if self._pid_is_dead():
                self._remove()
                self.path.mkdir()
                self._write_pid()
                self.acquired = True
                return self
            age = time.time() - self.path.stat().st_mtime
            if age <= self.stale_after_seconds:
                print("another Screen Time import appears to be running; exiting")
                raise SystemExit(0)
            self._remove()
            self.path.mkdir()
            self._write_pid()
            self.acquired = True
            return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.acquired:
            self._remove()

    def _write_pid(self) -> None:
        (self.path / "pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

    def _pid_is_dead(self) -> bool:
        pid_path = self.path / "pid"
        if not pid_path.exists():
            return False
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
        except ValueError:
            return True
        if pid <= 0:
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        return False

    def _remove(self) -> None:
        try:
            (self.path / "pid").unlink(missing_ok=True)
            self.path.rmdir()
        except OSError:
            pass


def log(message: str) -> None:
    print(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {message}", flush=True)


def aw_ready(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url}/info", timeout=5) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def aw_server_binary(app_path: Path = ACTIVITYWATCH_APP) -> Path:
    rust_server = app_path / "Contents" / "Frameworks" / "aw-server-rust"
    if rust_server.exists():
        return rust_server
    return app_path / "Contents" / "MacOS" / "aw-server"


def start_bundled_aw_server() -> None:
    executable = aw_server_binary()
    if not executable.exists():
        return
    log(f"starting bundled ActivityWatch server: {executable}")
    log_dir = Path.home() / "Library" / "Logs" / "aw-activitywatch-stack"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = (log_dir / "aw-server-autostart.log").open("ab")
    subprocess.Popen(
        [str(executable)],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )


def ensure_activitywatch(base_url: str) -> None:
    if aw_ready(base_url):
        return
    log(f"ActivityWatch API not reachable at {base_url}; trying to open ActivityWatch")
    subprocess.run(["/usr/bin/open", "-gj", "-a", "ActivityWatch"], check=False)
    for attempt in range(18):
        time.sleep(5)
        if aw_ready(base_url):
            return
        if attempt == 2:
            start_bundled_aw_server()
    raise RuntimeError(f"ActivityWatch API still not reachable at {base_url}")


def ensure_biome_importer(config: Config) -> Path:
    if not config.biome_importer_dir.is_dir():
        raise RuntimeError(f"Biome Screen Time importer directory not found: {config.biome_importer_dir}")
    executable = config.biome_importer_dir / ".venv" / "bin" / "aw-import-screentime"
    if executable.exists() and os.access(executable, os.X_OK):
        return executable
    log(f"Screen Time Biome importer executable missing; running uv sync in {config.biome_importer_dir}")
    subprocess.run(["/opt/homebrew/bin/uv", "sync"], cwd=config.biome_importer_dir, check=True)
    if not executable.exists():
        raise RuntimeError(f"Biome Screen Time importer executable still missing: {executable}")
    return executable


def is_full_history(value: str) -> bool:
    return value.strip().lower() in {"", "all", "full", "everything", "0"}


def preview_command(config: Config, executable: Path) -> list[str]:
    command = [
        str(executable),
        "events",
        "preview",
        "--limit",
        str(config.file_limit),
        "--platform",
        str(config.platform),
    ]
    if not is_full_history(config.since):
        command += ["--since", config.since]
    for storefront in config.storefronts:
        command += ["--storefront", storefront]
    return command


def run_preview(config: Config, executable: Path) -> list[dict[str, Any]]:
    command = preview_command(config, executable)
    result = subprocess.run(command, cwd=config.biome_importer_dir, check=True, capture_output=True, text=True)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
    payload = json.loads(result.stdout or "[]")
    if not isinstance(payload, list):
        raise RuntimeError("aw-import-screentime preview returned non-list JSON")
    return payload


def parse_since_window(value: str) -> datetime:
    value = value.strip().lower()
    now = datetime.now(timezone.utc)
    if value.endswith("h") and value[:-1].isdigit():
        return now - timedelta(hours=int(value[:-1]))
    if value.endswith("d") and value[:-1].isdigit():
        return now - timedelta(days=int(value[:-1]))
    if value in {"today", "yesterday"}:
        day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return day if value == "today" else day - timedelta(days=1)
    parsed = datetime.fromisoformat(value.replace("z", "+00:00").replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def parse_event_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("z", "+00:00").replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def existing_query_window(preview_events: list[dict[str, Any]], since: str) -> tuple[datetime, datetime]:
    spans: list[tuple[datetime, datetime]] = []
    for event in preview_events:
        if not event.get("timestamp"):
            continue
        start = parse_event_timestamp(str(event["timestamp"]))
        spans.append((start, start + timedelta(seconds=_duration(event))))
    if spans:
        starts = [start for start, _ in spans]
        ends = [end for _, end in spans]
        return min(starts) - timedelta(seconds=1), max(ends) + timedelta(seconds=1)
    start = datetime.now(timezone.utc) - timedelta(minutes=5) if is_full_history(since) else parse_since_window(since)
    return start, datetime.now(timezone.utc) + timedelta(minutes=10)


def bucket_id_for_device(device_id: str) -> str:
    return f"aw-import-screentime_ios_ios-{device_id}"


def request_json(url: str, *, method: str = "GET", payload: Any | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def ensure_bucket(base_url: str, device_id: str) -> str:
    bucket = bucket_id_for_device(device_id)
    hostname = f"ios-{device_id}"
    url = f"{base_url}/buckets/{urllib.parse.quote(bucket, safe='')}"
    payload = {"client": "aw-import-screentime-five-hour", "type": "app", "hostname": hostname}
    try:
        request_json(url, method="POST", payload=payload)
    except urllib.error.HTTPError as exc:
        if exc.code not in {304, 409}:
            raise
    return bucket


def fetch_existing_events(base_url: str, bucket: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"start": start.isoformat(), "end": end.isoformat(), "limit": 100000})
    url = f"{base_url}/buckets/{urllib.parse.quote(bucket, safe='')}/events?{query}"
    try:
        payload = request_json(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("events"), list):
        return payload["events"]
    return []


def _duration(event: dict[str, Any]) -> float:
    raw = event.get("duration", event.get("duration_seconds", 0))
    return round(float(raw), 6)


def event_signature(event: dict[str, Any]) -> tuple[str, float, str]:
    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    return (str(event.get("timestamp")), _duration(event), str(data.get("app") or ""))


def normalize_preview_event(event: dict[str, Any]) -> dict[str, Any]:
    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    return {"timestamp": str(event["timestamp"]), "duration": _duration(event), "data": dict(data)}


def filter_new_events(preview_events: list[dict[str, Any]], existing_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing_signatures = {event_signature(event) for event in existing_events}
    new_events: list[dict[str, Any]] = []
    for event in preview_events:
        normalized = normalize_preview_event(event)
        if event_signature(normalized) not in existing_signatures:
            new_events.append(normalized)
    return new_events


def insert_events(base_url: str, bucket: str, events: list[dict[str, Any]]) -> None:
    if not events:
        return
    url = f"{base_url}/buckets/{urllib.parse.quote(bucket, safe='')}/events"
    request_json(url, method="POST", payload=events)


def sync(config: Config) -> int:
    config.state_dir.mkdir(parents=True, exist_ok=True)
    with Lock(config.state_dir / "screentime-import.lock"):
        log("starting Biome Screen Time import scan")
        executable = ensure_biome_importer(config)
        ensure_activitywatch(config.aw_base_url)
        preview = run_preview(config, executable)
        total_inserted = 0
        for device_summary in preview:
            device_id = str(device_summary.get("device_id") or "")
            preview_events = device_summary.get("events") if isinstance(device_summary.get("events"), list) else []
            if not device_id:
                continue
            bucket = ensure_bucket(config.aw_base_url, device_id)
            start, end = existing_query_window(preview_events, config.since)
            existing = fetch_existing_events(config.aw_base_url, bucket, start, end)
            new_events = filter_new_events(preview_events, existing)
            insert_events(config.aw_base_url, bucket, new_events)
            total_inserted += len(new_events)
            print(
                "device="
                f"{device_id} files_scanned={device_summary.get('files_scanned', 0)} "
                f"preview_events={len(preview_events)} existing_events={len(existing)} inserted_events={len(new_events)}"
            )
        log(f"finished Biome Screen Time import scan inserted_events={total_inserted}")
        return total_inserted


def main() -> int:
    try:
        sync(Config.from_env())
        return 0
    except Exception as exc:
        print(f"Screen Time import failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
