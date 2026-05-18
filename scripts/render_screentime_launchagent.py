#!/usr/bin/env python3
from __future__ import annotations

import argparse
import plistlib
from pathlib import Path


def biome_remote_dir(home: Path) -> Path:
    return home / "Library" / "Biome" / "streams" / "restricted" / "App.InFocus" / "remote"


def biome_watch_paths(home: Path) -> list[str]:
    remote = biome_remote_dir(home)
    paths = [str(remote)]
    if remote.is_dir():
        paths.extend(str(path) for path in sorted(remote.iterdir()) if path.is_dir())
    return paths


def replace_home(value, home: Path):
    if isinstance(value, str):
        return value.replace("/Users/YOU", str(home))
    if isinstance(value, list):
        return [replace_home(item, home) for item in value]
    if isinstance(value, dict):
        return {key: replace_home(item, home) for key, item in value.items()}
    return value


def render_plist(template_path: Path, output_path: Path, home: Path, watch_paths: list[str]) -> None:
    payload = plistlib.loads(template_path.read_bytes())
    payload = replace_home(payload, home)
    payload["WatchPaths"] = watch_paths
    output_path.write_bytes(plistlib.dumps(payload, sort_keys=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the Screen Time LaunchAgent with local Biome WatchPaths.")
    parser.add_argument("template", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args()

    render_plist(args.template, args.output, args.home.expanduser(), biome_watch_paths(args.home.expanduser()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
