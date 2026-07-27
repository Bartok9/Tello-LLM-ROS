# -*- coding: utf-8 -*-
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.float_parse import safe_float_capture


class TestSafeFloatCapture(unittest.TestCase):
    def test_empty_none(self):
        self.assertIsNone(safe_float_capture(""))
        self.assertIsNone(safe_float_capture(None))
        self.assertIsNone(safe_float_capture("   "))

    def test_bad(self):
        self.assertIsNone(safe_float_capture("x"))
        self.assertIsNone(safe_float_capture("1.2.3"))

    def test_ok(self):
        self.assertEqual(safe_float_capture("1.5"), 1.5)
        self.assertEqual(safe_float_capture(" 2 "), 2.0)
        self.assertEqual(safe_float_capture("-3.25"), -3.25)

    def test_default(self):
        self.assertEqual(safe_float_capture("", default=10.0), 10.0)


class TestParseDirectPatternIntegration(unittest.TestCase):
    """Light integration without full ROS node init."""

    def test_pattern_float_optional_defaults(self):
        # Mimic tools.json record_video style without rospy
        import re
        from math import pi

        tool = {
            "name": "record_video",
            "direct_triggers": [
                {
                    "pattern": r"^(record video|record) ?(for )?(\d+\.?\d*)? ?(s|seconds)?$",
                    "params": [{"name": "duration", "group": 3}],
                }
            ],
            "parameters": [{"name": "duration", "default": 10.0}],
        }
        clean_input = "record video"
        match = re.match(tool["direct_triggers"][0]["pattern"], clean_input, re.IGNORECASE)
        self.assertIsNotNone(match)
        raw = match.group(3)
        val = safe_float_capture(raw)
        if val is None:
            val = float(tool["parameters"][0]["default"])
        self.assertEqual(val, 10.0)

    def test_cm_conversion_math(self):
        val = safe_float_capture("50")
        unit = "cm"
        if unit in ["cm", "centimeters"]:
            val /= 100.0
        self.assertAlmostEqual(val, 0.5)


if __name__ == "__main__":
    unittest.main()
