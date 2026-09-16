#!/usr/bin/env python3
"""Small dependency-free validator for the round-1 watch.event schema."""

from __future__ import annotations

import json
import re
import sys


TYPES = {"fall", "wander", "stove_unattended"}
RFC3339_Z = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$")


def validate(event: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(event, dict):
        return ["event is not an object"]
    expected = {"type", "room", "ts", "confidence", "discarded_frames"}
    extra = set(event) - expected
    missing = expected - set(event)
    if extra:
        errors.append(f"unexpected keys: {sorted(extra)}")
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")
    if event.get("type") not in TYPES:
        errors.append("type is not in schema enum")
    if not isinstance(event.get("room"), str):
        errors.append("room is not a string")
    if not isinstance(event.get("ts"), str) or not RFC3339_Z.match(event["ts"]):
        errors.append("ts is not RFC3339 UTC Z")
    confidence = event.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        errors.append("confidence is not in [0, 1]")
    discarded = event.get("discarded_frames")
    if not isinstance(discarded, int) or discarded < 0:
        errors.append("discarded_frames is not a non-negative integer")
    return errors


def main() -> int:
    failed = False
    for line_no, line in enumerate(sys.stdin, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError as exc:
            print(f"line {line_no}: invalid JSON: {exc}", file=sys.stderr)
            failed = True
            continue
        errors = validate(event)
        if errors:
            for error in errors:
                print(f"line {line_no}: {error}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
