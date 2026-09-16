#!/usr/bin/env python3
"""Deterministically turn watch event JSONL into human-facing incident JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable, TextIO


# Duplicate fall detections arrive seconds apart; ten seconds joins retries while
# avoiding the much riskier act of merging separate falls minutes apart.
FALL_DUPLICATE_WINDOW = timedelta(seconds=10)
# A short movement trail through rooms is one human story, not one alert per room.
WANDER_TRAIL_WINDOW = timedelta(minutes=5)
# An immediately following fall is the end of a movement trail, not a new story.
WANDER_FALL_WINDOW = timedelta(minutes=5)
# Stove detections thirty minutes apart must remain one escalating safety issue.
STOVE_CONTINUATION_WINDOW = timedelta(minutes=45)
# Below this value an event is logged as watch rather than silently discarded.
NOTIFY_CONFIDENCE = 0.5
# Repeated stove evidence over this duration starts urgent escalation.
STOVE_ESCALATION_AGE = timedelta(minutes=30)
# Overnight wandering is more consequential than ordinary daytime movement.
NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 6


def parse_ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("ts must include a UTC offset")
    return parsed.astimezone(timezone.utc)


@dataclass
class Incident:
    events: list[dict] = field(default_factory=list)

    @property
    def first_dt(self) -> datetime:
        return parse_ts(self.events[0]["ts"])

    @property
    def last_dt(self) -> datetime:
        return parse_ts(self.events[-1]["ts"])

    @property
    def type(self) -> str:
        return self.events[0]["type"]


def validate_event(event: object, line_number: int) -> dict:
    if not isinstance(event, dict):
        raise ValueError(f"line {line_number}: event must be an object")
    required = {"type", "room", "ts", "confidence", "discarded_frames"}
    if set(event) != required:
        raise ValueError(f"line {line_number}: fields must be exactly {sorted(required)}")
    if event["type"] not in {"fall", "wander", "stove_unattended"}:
        raise ValueError(f"line {line_number}: unsupported event type")
    if not isinstance(event["room"], str) or not event["room"]:
        raise ValueError(f"line {line_number}: room must be a non-empty string")
    parse_ts(event["ts"])
    if isinstance(event["confidence"], bool) or not isinstance(event["confidence"], (int, float)) or not 0 <= event["confidence"] <= 1:
        raise ValueError(f"line {line_number}: confidence must be between 0 and 1")
    if isinstance(event["discarded_frames"], bool) or not isinstance(event["discarded_frames"], int) or event["discarded_frames"] < 0:
        raise ValueError(f"line {line_number}: discarded_frames must be a non-negative integer")
    return event


def read_events(stream: TextIO) -> list[dict]:
    events = []
    for line_number, line in enumerate(stream, 1):
        if line.strip():
            events.append(validate_event(json.loads(line), line_number))
    # Arrival order is not trusted because the board clock/transport may reorder events.
    return sorted(events, key=lambda event: (parse_ts(event["ts"]), json.dumps(event, sort_keys=True)))


def belongs(incident: Incident, event: dict) -> bool:
    age = parse_ts(event["ts"]) - incident.last_dt
    if incident.type == "fall":
        return event["type"] == "fall" and event["room"] == incident.events[-1]["room"] and age <= FALL_DUPLICATE_WINDOW
    if incident.type == "stove_unattended":
        return event["type"] == "stove_unattended" and event["room"] == incident.events[-1]["room"] and age <= STOVE_CONTINUATION_WINDOW
    if incident.type == "wander":
        if event["type"] == "wander":
            return age <= WANDER_TRAIL_WINDOW
        return event["type"] == "fall" and age <= WANDER_FALL_WINDOW
    return False


def group_events(events: Iterable[dict]) -> list[Incident]:
    incidents: list[Incident] = []
    for event in events:
        match = next((item for item in reversed(incidents) if belongs(item, event)), None)
        if match is None:
            incidents.append(Incident([event]))
        else:
            match.events.append(event)
    return incidents


def render(incident: Incident, number: int) -> dict:
    events = incident.events
    kind = incident.type
    rooms = [event["room"] for event in events]
    duration = incident.last_dt - incident.first_dt
    highest_confidence = max(event["confidence"] for event in events)
    has_fall = any(event["type"] == "fall" for event in events)
    overnight = incident.first_dt.hour >= NIGHT_START_HOUR or incident.first_dt.hour < NIGHT_END_HOUR
    room_name = rooms[-1].replace("_", " ")

    state = "open"
    if kind == "fall":
        severity = "urgent" if highest_confidence >= NOTIFY_CONFIDENCE else "watch"
        summary = f"Possible fall in the {room_name}."
    elif kind == "stove_unattended":
        if len(events) > 1 and duration >= STOVE_ESCALATION_AGE:
            severity, state = "urgent", "escalated"
            summary = f"Stove has been on and unattended for {int(duration.total_seconds() // 60)} minutes."
        else:
            severity = "notify" if highest_confidence >= NOTIFY_CONFIDENCE else "watch"
            summary = "Stove may be on and unattended."
    else:
        severity = "urgent" if has_fall or overnight else ("notify" if len(events) > 1 else "watch")
        if has_fall:
            summary = f"Movement through the home ended with a possible fall in the {room_name}."
        elif len(events) > 1:
            summary = f"Movement through the home reached the {room_name}."
        else:
            summary = f"Movement detected in the {room_name}."

    return {
        "incident_id": f"inc-{number:04d}",
        "type": kind,
        "room": "front_door" if "front_door" in rooms else rooms[-1],
        "opened_ts": events[0]["ts"],
        "last_ts": events[-1]["ts"],
        "severity": severity,
        "event_count": len(events),
        "frames_never_stored": sum(event["discarded_frames"] for event in events),
        "state": state,
        "summary": summary,
    }


def process(stream: TextIO) -> list[dict]:
    return [render(incident, index) for index, incident in enumerate(group_events(read_events(stream)), 1)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        for incident in process(sys.stdin):
            print(json.dumps(incident, separators=(",", ":")))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"incidents: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
