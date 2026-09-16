#!/usr/bin/env python3
"""Fixture inventory for the fixed eval; does not implement or grade product logic."""
import json
from pathlib import Path

fixture = Path(__file__).parents[1] / "contracts/fixtures/events.sample.jsonl"
events = [json.loads(line) for line in fixture.read_text().splitlines() if line]

groups = {
    "bathroom_duplicate": [events[2], events[3]],
    "kitchen_escalation": [events[4], events[5]],
    "night_run": [events[6], events[7], events[8], events[9]],
}
print(f"fixture={fixture} events={len(events)}")
for name, members in groups.items():
    print(f"{name}: events={len(members)} discarded_frames={sum(e['discarded_frames'] for e in members)}")
low = [e for e in events if e["confidence"] < 0.5]
print("low_confidence:", ", ".join(f"{e['ts']}={e['confidence']}" for e in low))
print("implementation: evidence/ ABSENT; no product output generated")

