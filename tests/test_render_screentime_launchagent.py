from __future__ import annotations

import importlib.util
import plistlib
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "render_screentime_launchagent.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_screentime_launchagent", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_biome_watch_paths_include_root_and_device_dirs(tmp_path):
    module = load_module()
    home = tmp_path / "home"
    remote = home / "Library/Biome/streams/restricted/App.InFocus/remote"
    (remote / "device-b").mkdir(parents=True)
    (remote / "device-a").mkdir()

    assert module.biome_watch_paths(home) == [
        str(remote),
        str(remote / "device-a"),
        str(remote / "device-b"),
    ]


def test_render_plist_replaces_home_and_adds_watchpaths(tmp_path):
    module = load_module()
    template = tmp_path / "agent.plist.template"
    template.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.servas.aw-screentime-hourly</string>
  <key>ProgramArguments</key><array><string>/Users/YOU/bin/run.py</string></array>
</dict></plist>
""",
        encoding="utf-8",
    )
    output = tmp_path / "agent.plist"

    module.render_plist(template, output, Path("/Users/example"), ["/tmp/watch-a", "/tmp/watch-b"])

    payload = plistlib.loads(output.read_bytes())
    assert payload["ProgramArguments"] == ["/Users/example/bin/run.py"]
    assert payload["WatchPaths"] == ["/tmp/watch-a", "/tmp/watch-b"]
