from __future__ import annotations

import importlib.util
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


def test_aw_server_binary_prefers_rust_server_when_bundled():
    module = load_module()

    path = module.aw_server_binary(Path("/Applications/ActivityWatch.app"))

    assert path == Path("/Applications/ActivityWatch.app/Contents/Frameworks/aw-server-rust")


def test_lock_reclaims_dead_pid(tmp_path):
    module = load_module()
    lock_dir = tmp_path / "import.lock"
    lock_dir.mkdir()
    (lock_dir / "pid").write_text("999999\n", encoding="utf-8")

    with module.Lock(lock_dir):
        assert (lock_dir / "pid").read_text(encoding="utf-8").strip()
