import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from evidence.rhythm import aggregate, write_atomic


class RhythmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.log = Path(self.temp.name) / "board.log"

    def make_log(self, minutes):
        lines = []
        frame = 0
        for states, company_count in minutes:
            for index, state in enumerate(states):
                poses = 2 if index < company_count else 1
                lines.extend((f"frame {frame} posture={state} poses={poses}\n",
                              f"trend posture={state} company_s=0\n"))
                frame += 1
        self.log.write_text("".join(lines))

    def test_minute_states_company_first_seen_totals_and_visits(self):
        minute = lambda state: [state] * 60
        minutes = [(minute("absent"), 0)] * 5 + [
            (minute("upright"), 18),
            (minute("bent"), 60),
            (minute("sitting"), 0),
            (minute("floor"), 0),
            (minute("close"), 0),
        ]
        self.make_log(minutes)
        result = aggregate(self.log, datetime.fromisoformat("2026-09-16T07:00:00-07:00"))
        self.assertEqual(result["date"], "2026-09-16")
        self.assertEqual(result["first_seen"], "07:05")
        self.assertEqual([item["state"] for item in result["minutes"]],
                         ["absent"] * 5 + ["standing", "standing", "sitting", "floor", "close"])
        self.assertEqual([item["company"] for item in result["minutes"]][5:8], [True, True, False])
        self.assertEqual(result["totals"], {"standing_min": 2, "sitting_min": 1,
                         "floor_min": 1, "close_min": 1, "absent_min": 5,
                         "company_min": 2, "visits": 1})

    def test_dominant_posture_and_atomic_output(self):
        states = ["sitting"] * 31 + ["upright"] * 29
        self.make_log([(states, 17)])
        result = aggregate(self.log, datetime.fromisoformat("2026-09-16T08:00:00-07:00"))
        self.assertEqual(result["minutes"][0], {"m": "08:00", "state": "sitting", "company": False})
        output = Path(self.temp.name) / "live" / "day.json"
        write_atomic(output, result)
        self.assertEqual(json.loads(output.read_text()), result)


if __name__ == "__main__":
    unittest.main()
