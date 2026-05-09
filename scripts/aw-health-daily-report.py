#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

AW = "http://127.0.0.1:5600/api/0"
TZ = ZoneInfo("Europe/Vienna")
OUT = Path("outputs/health-daily")


def get_json(path: str):
    return json.load(urllib.request.urlopen(AW + path, timeout=10))


def events(bucket: str, start: datetime, end: datetime, limit: int = 100000):
    qs = urllib.parse.urlencode({"start": start.isoformat(), "end": end.isoformat(), "limit": limit})
    try:
        return get_json(f"/buckets/{bucket}/events?{qs}")
    except Exception:
        return []


def latest(bucket: str):
    try:
        ev = get_json(f"/buckets/{bucket}/events?limit=1")
        return ev[0] if ev else None
    except Exception:
        return None


def summarize_day(day: datetime):
    local_start = datetime(day.year, day.month, day.day, tzinfo=TZ)
    local_end = local_start + timedelta(days=1)
    start = local_start.astimezone(timezone.utc)
    end = local_end.astimezone(timezone.utc)
    buckets = get_json("/buckets/")

    out = {
        "date": local_start.date().isoformat(),
        "generated_at": datetime.now(TZ).isoformat(),
        "activitywatch": {"active_minutes": 0, "top_apps": [], "late_minutes_after_18": 0},
        "whoop": {},
        "screen_time": {"total_minutes": 0, "top_apps": []},
        "apple_health": {"configured": False, "bucket_count": 0},
        "recommendations": [],
        "data_quality": {"missing": [], "warnings": []},
    }

    # Desktop active time from AFK not-afk durations.
    afk = next((b for b in buckets if b.startswith("aw-watcher-afk_")), None)
    if afk:
        active = 0.0
        late = 0.0
        for ev in events(afk, start, end):
            if ev.get("data", {}).get("status") != "not-afk":
                continue
            dur = float(ev.get("duration") or 0)
            active += dur
            ts = datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00")).astimezone(TZ)
            if ts.hour >= 18:
                late += dur
        out["activitywatch"]["active_minutes"] = round(active / 60)
        out["activitywatch"]["late_minutes_after_18"] = round(late / 60)
    else:
        out["data_quality"]["missing"].append("afk_bucket")

    win = next((b for b in buckets if b.startswith("aw-watcher-window_")), None)
    if win:
        apps = Counter()
        for ev in events(win, start, end):
            app = ev.get("data", {}).get("app") or "unknown"
            apps[app] += float(ev.get("duration") or 0)
        out["activitywatch"]["top_apps"] = [(k, round(v / 3600, 2)) for k, v in apps.most_common(8)]

    # WHOOP latest source statuses.
    for kind in ("recovery", "sleep", "workout", "cycle"):
        bid = f"aw-importer-whoop-{kind}"
        if bid in buckets:
            ev = latest(bid)
            out["whoop"][kind] = {"last_event": ev.get("timestamp") if ev else None, "available": bool(ev)}
        else:
            out["data_quality"]["missing"].append(bid)

    # Screen Time top apps from active iOS buckets.
    st_apps = Counter()
    for bid in buckets:
        if not bid.startswith("aw-import-screentime"):
            continue
        for ev in events(bid, start, end):
            data = ev.get("data", {})
            app = data.get("app") or data.get("name") or data.get("bundle_id") or "unknown"
            st_apps[app] += float(ev.get("duration") or 0)
    out["screen_time"]["total_minutes"] = round(sum(st_apps.values()) / 60)
    out["screen_time"]["top_apps"] = [(k, round(v / 60)) for k, v in st_apps.most_common(8)]

    ah = [b for b in buckets if b.startswith("aw-importer-apple-health")]
    out["apple_health"] = {"configured": bool(ah), "bucket_count": len(ah), "buckets": sorted(ah)}
    if not ah:
        out["data_quality"]["warnings"].append("Apple Health not configured yet")

    active_min = out["activitywatch"]["active_minutes"]
    late_min = out["activitywatch"]["late_minutes_after_18"]
    if late_min > 120:
        out["recommendations"].append("Heute Abend früher runterfahren: gestern/spät viel Aktivität nach 18 Uhr.")
    if active_min > 480:
        out["recommendations"].append("Hohe aktive Zeit: heute Fokusblöcke schützen und Pausen bewusst setzen.")
    if not ah:
        out["recommendations"].append("Apple Health verbinden, damit Schritte/HRV/Schlaf in Leo-Briefings einfließen.")
    if not out["recommendations"]:
        out["recommendations"].append("Datenlage stabil: heute einen klaren Fokusblock planen.")
    return out


def to_markdown(report: dict) -> str:
    lines = [f"# Health Daily Report — {report['date']}", ""]
    lines += ["## ActivityWatch", f"- Active: {report['activitywatch']['active_minutes']} min", f"- After 18:00: {report['activitywatch']['late_minutes_after_18']} min"]
    lines.append("- Top apps: " + ", ".join(f"{a} {h}h" for a, h in report['activitywatch']['top_apps']))
    lines += ["", "## WHOOP"]
    for k, v in report["whoop"].items():
        lines.append(f"- {k}: {'ok' if v['available'] else 'missing'} · {v['last_event']}")
    lines += ["", "## Screen Time", f"- Total: {report['screen_time']['total_minutes']} min"]
    lines.append("- Top apps: " + ", ".join(f"{a} {m}m" for a, m in report['screen_time']['top_apps']))
    lines += ["", "## Apple Health", f"- Configured: {report['apple_health']['configured']}", f"- Buckets: {report['apple_health']['bucket_count']}"]
    lines += ["", "## Recommendations"] + [f"- {r}" for r in report["recommendations"]]
    if report["data_quality"]["warnings"] or report["data_quality"]["missing"]:
        lines += ["", "## Data quality"]
        lines += [f"- Missing: {x}" for x in report["data_quality"]["missing"]]
        lines += [f"- Warning: {x}" for x in report["data_quality"]["warnings"]]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD, default today local")
    ap.add_argument("--write-output", action="store_true")
    args = ap.parse_args()
    day = datetime.fromisoformat(args.date).replace(tzinfo=TZ) if args.date else datetime.now(TZ)
    report = summarize_day(day)
    if args.write_output:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{report['date']}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
        (OUT / f"{report['date']}.md").write_text(to_markdown(report))
        (OUT / "latest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
        (OUT / "latest.md").write_text(to_markdown(report))
    print(to_markdown(report))


if __name__ == "__main__":
    main()
