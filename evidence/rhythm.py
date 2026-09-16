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
from datetime import datetime, timedelta
from pathlib import Path


FIELD_RE = re.compile(r"\b([a-z_]+)=([^\s]+)")
STATES = ("standing", "sitting", "floor", "close", "absent")
POSTURE = {"upright": "standing", "bent": "standing", **{state: state for state in STATES}}


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
    for minute in sorted(buckets):
        values = buckets[minute]
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
    return {"date": day.isoformat(), "first_seen": first_seen, "minutes": minutes, "totals": totals}


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", type=parse_start)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    while True:
        write_atomic(args.out, aggregate(args.log, args.start))
        if args.once:
            return 0
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
