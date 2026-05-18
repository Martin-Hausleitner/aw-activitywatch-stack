from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sync_screentime_folder.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_screentime_folder", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_config_reads_biome_import_settings(monkeypatch, tmp_path):
    module = load_module()
    importer = tmp_path / "aw-import-screentime"
    monkeypatch.setenv("SCREENTIME_BIOME_IMPORTER_DIR", str(importer))
    monkeypatch.setenv("SCREENTIME_SINCE", "96h")
    monkeypatch.setenv("SCREENTIME_FILE_LIMIT", "17")
    monkeypatch.setenv("SCREENTIME_STOREFRONTS", "at,us")

    config = module.Config.from_env()

    assert config.biome_importer_dir == importer
    assert config.since == "96h"
    assert config.file_limit == 17
    assert config.storefronts == ["at", "us"]


def test_config_defaults_to_full_available_history(monkeypatch):
    module = load_module()
    monkeypatch.delenv("SCREENTIME_SINCE", raising=False)

    config = module.Config.from_env()

    assert config.since == "all"


def test_preview_command_omits_since_for_full_history(tmp_path):
    module = load_module()
    config = module.Config(
        biome_importer_dir=tmp_path,
        aw_base_url="http://127.0.0.1:5600/api/0",
        state_dir=tmp_path,
        since="all",
        file_limit=0,
        storefronts=["at"],
        platform=2,
        aw_sqlite_path=tmp_path / "activitywatch.db",
    )

    command = module.preview_command(config, tmp_path / ".venv/bin/aw-import-screentime")

    assert "--since" not in command
    assert command[-2:] == ["--storefront", "at"]


def test_existing_query_window_uses_preview_event_span():
    module = load_module()
    events = [
        {"timestamp": "2026-05-18T17:25:51.732000+00:00", "duration_seconds": 29.2, "data": {"app": "B"}},
        {"timestamp": "2025-06-28T07:45:47.000000+00:00", "duration_seconds": 10, "data": {"app": "A"}},
    ]

    start, end = module.existing_query_window(events, "all")

    assert start.isoformat() == "2025-06-28T07:45:46+00:00"
    assert end.isoformat() == "2026-05-18T17:26:21.932000+00:00"


def test_event_signature_uses_stable_activitywatch_fields():
    module = load_module()
    first = {
        "timestamp": "2026-05-18T17:23:58.060000+00:00",
        "duration": 61.429785,
        "data": {"app": "com.google.gemini", "title": "Google Gemini"},
    }
    second = {
        "timestamp": "2026-05-18T17:23:58.060000+00:00",
        "duration_seconds": "61.429785",
        "data": {"app": "com.google.gemini"},
    }

    assert module.event_signature(first) == module.event_signature(second)


def test_event_signature_normalizes_sqlite_timestamp_format():
    module = load_module()
    preview = {
        "timestamp": "2026-05-18T19:21:08.630000+00:00",
        "duration": 6.341978,
        "data": {"app": "com.apple.mobiletimer"},
    }
    sqlite_event = {
        "timestamp": "2026-05-18 19:21:08.630000+00:00",
        "duration": 6.341978,
        "data": {"app": "com.apple.mobiletimer"},
    }

    assert module.event_signature(preview) == module.event_signature(sqlite_event)


def test_filter_new_events_skips_existing_activitywatch_signatures():
    module = load_module()
    existing = [
        {
            "timestamp": "2026-05-18T17:23:58.060000+00:00",
            "duration": 61.429785,
            "data": {"app": "com.google.gemini"},
        }
    ]
    preview = [
        {
            "timestamp": "2026-05-18T17:23:58.060000+00:00",
            "duration_seconds": 61.429785,
            "data": {"app": "com.google.gemini", "title": "Google Gemini"},
        },
        {
            "timestamp": "2026-05-18T17:25:51.732000+00:00",
            "duration_seconds": 29.228586,
            "data": {"app": "com.automattic.beeper", "title": "Beeper"},
        },
    ]

    filtered = module.filter_new_events(preview, existing)

    assert filtered == [
        {
            "timestamp": "2026-05-18T17:25:51.732000+00:00",
            "duration": 29.228586,
            "data": {"app": "com.automattic.beeper", "title": "Beeper"},
        }
    ]


def test_aw_server_binary_prefers_activitywatch_app_server_when_bundled():
    module = load_module()

    path = module.aw_server_binary(Path("/Applications/ActivityWatch.app"))

    assert path == Path("/Applications/ActivityWatch.app/Contents/MacOS/aw-server")


def test_sqlite_fallback_inserts_and_deduplicates_activitywatch_events(tmp_path):
    module = load_module()
    db_path = tmp_path / "aw.db"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            create table bucketmodel (
                key integer not null primary key,
                id varchar(255) not null,
                created datetime not null,
                name varchar(255),
                type varchar(255) not null,
                client varchar(255) not null,
                hostname varchar(255) not null,
                datastr varchar(255)
            );
            create unique index bucketmodel_id on bucketmodel (id);
            create table eventmodel (
                id integer not null primary key,
                bucket_id integer not null,
                timestamp datetime not null,
                duration decimal(10, 5) not null,
                datastr varchar(255) not null
            );
            """
        )

    bucket_key = module.ensure_bucket_sqlite(db_path, "device-a")
    event = {
        "timestamp": "2026-05-18T19:21:08.630000+00:00",
        "duration": 6.341978,
        "data": {"app": "com.apple.mobiletimer", "title": "Clock"},
    }
    module.insert_events_sqlite(db_path, bucket_key, [event])

    existing = module.fetch_existing_events_sqlite(
        db_path,
        bucket_key,
        module.parse_event_timestamp("2026-05-18T19:21:00+00:00"),
        module.parse_event_timestamp("2026-05-18T19:22:00+00:00"),
    )

    assert module.filter_new_events([event], existing) == []


def test_lock_reclaims_dead_pid(tmp_path):
    module = load_module()
    lock_dir = tmp_path / "import.lock"
    lock_dir.mkdir()
    (lock_dir / "pid").write_text("999999\n", encoding="utf-8")

    with module.Lock(lock_dir):
        assert (lock_dir / "pid").read_text(encoding="utf-8").strip()
