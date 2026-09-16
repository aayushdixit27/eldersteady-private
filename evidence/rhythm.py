#!/usr/bin/env python3
"""Aggregate one-second board trend samples into a per-minute day record."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime, time as clock_time, timedelta, timezone
from pathlib import Path


FIELD_RE = re.compile(r"\b([a-z_]+)=([^\s]+)")
STATES = ("standing", "sitting", "floor", "close", "absent")
POSTURE = {"upright": "standing", "bent": "standing", **{state: state for state in STATES}}
WANDER_COOLDOWN = timedelta(minutes=30)


def parse_start(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed


def read_samples(path: Path) -> list[tuple[str, int]]:
    samples: list[tuple[str, int]] = []
    latest_poses = 0
    with path.open(errors="replace") as stream:
        for line in stream:
            fields = dict(FIELD_RE.findall(line))
            if line.startswith("frame "):
                try:
                    latest_poses = int(fields.get("poses", "0"))
                except ValueError:
                    latest_poses = 0
            elif line.startswith("trend "):
                posture = fields.get("posture", "absent")
                view = fields.get("view")
                if view == "close":
                    posture = "close"
                elif view in {"none", "absent"}:
                    posture = "absent"
                state = POSTURE.get(posture, "absent")
                try:
                    poses = int(fields.get("poses", latest_poses))
                except ValueError:
                    poses = 0
                samples.append((state, poses))
    return samples


def aggregate(path: Path, start: datetime | None = None) -> dict:
    samples = read_samples(path)
    if start is None:
        end = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
        start = end - timedelta(seconds=max(0, len(samples) - 1))

    buckets: dict[datetime, list[tuple[str, int]]] = defaultdict(list)
    for index, sample in enumerate(samples):
        minute = (start + timedelta(seconds=index)).replace(second=0, microsecond=0)
        buckets[minute].append(sample)

    minutes = []
    minute_frames: dict[datetime, int] = {}
    for minute in sorted(buckets):
        values = buckets[minute]
        minute_frames[minute] = len(values)
        counts = Counter(state for state, _ in values)
        # Stable contract order resolves the rare equal-count minute.
        state = max(STATES, key=lambda item: (counts[item], -STATES.index(item)))
        company = sum(poses >= 2 for _, poses in values) / len(values) >= 0.30
        minutes.append({"m": minute.strftime("%H:%M"), "state": state, "company": company})

    first_seen = next((item["m"] for item in minutes if item["state"] != "absent"), None)
    totals = {f"{state}_min": sum(item["state"] == state for item in minutes) for state in STATES}
    totals["company_min"] = sum(item["company"] for item in minutes)
    totals["visits"] = count_visits([item["company"] for item in minutes])
    day = min(buckets).date() if buckets else start.date()
    events = find_wanders(minutes, minute_frames)
    return {"date": day.isoformat(), "first_seen": first_seen, "minutes": minutes,
            "totals": totals, "events": events}


def parse_night(value: str) -> tuple[clock_time, clock_time]:
    try:
        start, end = value.split("-", 1)
        return (clock_time.fromisoformat(start), clock_time.fromisoformat(end))
    except ValueError as error:
        raise ValueError("WATCH_NIGHT must look like 23:00-06:00") from error


def in_night(moment: datetime, window: tuple[clock_time, clock_time]) -> bool:
    current = moment.time().replace(tzinfo=None)
    start, end = window
    if start <= end:
        return start <= current < end
    return current >= start or current < end


def utc_timestamp(moment: datetime) -> str:
    if moment.tzinfo is None:
        moment = moment.astimezone()
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def find_wanders(minutes: list[dict], minute_frames: dict[datetime, int]) -> list[dict]:
    """Return one event per qualifying episode, subject to the cooldown."""
    offset_present = "WATCH_CLOCK_OFFSET_MIN" in os.environ
    try:
        offset = int(os.environ.get("WATCH_CLOCK_OFFSET_MIN", "0"))
    except ValueError as error:
        raise ValueError("WATCH_CLOCK_OFFSET_MIN must be an integer") from error
    window = parse_night(os.environ.get("WATCH_NIGHT", "23:00-06:00"))
    ordered = sorted(minute_frames)
    night_minutes = [minute for minute in ordered if in_night(minute + timedelta(minutes=offset), window)]
    states = {minute: item["state"] for minute, item in zip(ordered, minutes)}
    standing = sum(states[minute] == "standing" for minute in night_minutes)
    confidence = standing / len(night_minutes) if night_minutes else 0.0

    events: list[dict] = []
    run: list[datetime] = []
    episode_emitted = False
    last_event: datetime | None = None
    for minute in ordered:
        state = states[minute]
        is_night = in_night(minute + timedelta(minutes=offset), window)
        consecutive = bool(run) and minute - run[-1] == timedelta(minutes=1)
        compatible = state in {"standing", "absent"}
        if not is_night or not compatible or (run and not consecutive):
            run = []
            episode_emitted = False
        if not is_night or not compatible:
            continue
        if run and state == states[run[-1]] and state != "standing":
            run = []
            episode_emitted = False
        run.append(minute)
        all_standing = len(run) >= 3 and all(states[item] == "standing" for item in run[-3:])
        recent = run[-3:]
        alternating = len(recent) == 3 and all(
            states[recent[index]] != states[recent[index - 1]] for index in range(1, 3)
        )
        if (all_standing or alternating) and not episode_emitted:
            if last_event is None or minute - last_event >= WANDER_COOLDOWN:
                relevant = run[-3:]
                event = {"type": "wander", "room": "living_room", "ts": utc_timestamp(minute),
                         "confidence": confidence,
                         "discarded_frames": sum(minute_frames[item] for item in relevant)}
                if offset_present:
                    event["demo_clock"] = True
                events.append(event)
                last_event = minute
            episode_emitted = True
    return events


def count_visits(company: list[bool]) -> int:
    visits = 0
    for index in range(5, len(company) - 1):
        if not any(company[index - 5:index]) and company[index] and company[index + 1]:
            visits += 1
    return visits


def write_atomic(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(record, stream, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def refresh(log_path: Path, out_path: Path, start: datetime | None = None) -> dict:
    record = aggregate(log_path, start)
    previous_events = []
    if out_path.exists():
        try:
            previous = json.loads(out_path.read_text())
            if previous.get("date") == record["date"]:
                previous_events = previous.get("events", [])
        except (OSError, ValueError, AttributeError):
            previous_events = []
    known = {(event.get("type"), event.get("ts")) for event in previous_events}
    new_events = [event for event in record["events"]
                  if (event.get("type"), event.get("ts")) not in known]
    record["events"] = previous_events + new_events
    if new_events:
        with log_path.open("a") as stream:
            for event in new_events:
                stream.write(json.dumps(event, separators=(",", ":")) + "\n")
    write_atomic(out_path, record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", type=parse_start)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    while True:
        refresh(args.log, args.out, args.start)
        if args.once:
            return 0
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
