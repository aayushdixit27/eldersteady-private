#!/usr/bin/env python3
"""Mic- and model-free tests for evidence.voice."""

import sys
import unittest
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evidence.voice import format_board_line, phrase_to_keyword


class VoiceTests(unittest.TestCase):
    def test_phrase_mapping(self):
        expected = {
            "help": "help",
            "i have fallen": "fallen",
            "i am okay": "okay",
            "i'm okay": "okay",
            "okay": "okay",
            "": "none",
            "[unk]": "none",
            "something else": "none",
        }
        for phrase, keyword in expected.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(phrase_to_keyword(phrase), keyword)

    def test_board_line_format(self):
        self.assertEqual(
            format_board_line("fallen", 12.34, "i have fallen"),
            'voice keyword=fallen heard_s=12.3 recorded_s=0 text="i have fallen"',
        )
        self.assertEqual(
            format_board_line("none", 60, None),
            'voice keyword=none heard_s=60.0 recorded_s=0 text="none"',
        )

    def test_board_line_is_one_line(self):
        line = format_board_line("none", 1, 'noise\n"noise"')
        self.assertNotIn("\n", line)
        self.assertEqual(line.count("voice keyword="), 1)


if __name__ == "__main__":
    unittest.main()
