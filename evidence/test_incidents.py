import io
import json
import pathlib
import unittest

from incidents import process


FIXTURE = pathlib.Path(__file__).parents[1] / "contracts/fixtures/events.sample.jsonl"


class IncidentTests(unittest.TestCase):
    def setUp(self):
        with FIXTURE.open() as stream:
            self.output = process(stream)

    def test_mission_fixture(self):
        self.assertEqual([item["event_count"] for item in self.output], [2, 2, 2, 4, 1, 1])
        self.assertEqual(self.output[1]["severity"], "urgent")
        self.assertEqual((self.output[2]["state"], self.output[2]["event_count"]), ("escalated", 2))
        self.assertEqual(self.output[3]["frames_never_stored"], 333540)

    def test_ledger_is_exact_for_every_incident(self):
        source_events = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
        self.assertEqual(sum(item["frames_never_stored"] for item in self.output),
                         sum(event["discarded_frames"] for event in source_events))

    def test_low_confidence_events_are_surfaced(self):
        low_timestamps = {"2026-09-15T11:47:33Z", "2026-09-16T04:14:02Z"}
        covered = {timestamp for item in self.output for timestamp in
                   (item["opened_ts"], item["last_ts"])}
        self.assertTrue(low_timestamps <= covered)

    def test_arrival_order_does_not_change_output(self):
        lines = FIXTURE.read_text().splitlines()
        self.assertEqual(self.output, process(io.StringIO("\n".join(reversed(lines)))))

    def test_interleaved_event_does_not_split_stove_incident(self):
        events = [
            {"type": "stove_unattended", "room": "kitchen", "ts": "2026-09-15T18:20:05Z", "confidence": .9, "discarded_frames": 10},
            {"type": "fall", "room": "hallway", "ts": "2026-09-15T18:30:00Z", "confidence": .8, "discarded_frames": 20},
            {"type": "stove_unattended", "room": "kitchen", "ts": "2026-09-15T18:50:05Z", "confidence": .9, "discarded_frames": 30},
        ]
        output = process(io.StringIO("\n".join(json.dumps(item) for item in events)))
        self.assertEqual((output[0]["event_count"], output[0]["state"], output[0]["frames_never_stored"]),
                         (2, "escalated", 40))


if __name__ == "__main__":
    unittest.main()
