# -*- coding: utf-8 -*-
import math
import unittest

from utils.flight_guards import battery_allows_takeoff, clamp_battery_percent_param


class TestFlightGuards(unittest.TestCase):
    def test_allows_at_minimum(self):
        self.assertTrue(battery_allows_takeoff(10, 10))
        self.assertTrue(battery_allows_takeoff(10.0, 10))
        self.assertTrue(battery_allows_takeoff("55", 10))

    def test_rejects_below_minimum(self):
        self.assertFalse(battery_allows_takeoff(9, 10))
        self.assertFalse(battery_allows_takeoff(0, 10))

    def test_rejects_non_finite(self):
        self.assertFalse(battery_allows_takeoff(float("nan"), 10))
        self.assertFalse(battery_allows_takeoff(float("inf"), 10))
        self.assertFalse(battery_allows_takeoff(-float("inf"), 10))
        self.assertFalse(battery_allows_takeoff(None, 10))
        self.assertFalse(battery_allows_takeoff("nope", 10))

    def test_clamp_param(self):
        self.assertEqual(clamp_battery_percent_param(10), 10)
        self.assertEqual(clamp_battery_percent_param(-5), 0)
        self.assertEqual(clamp_battery_percent_param(150), 100)
        self.assertEqual(clamp_battery_percent_param("bad", 12), 12)
        self.assertEqual(clamp_battery_percent_param(math.nan, 8), 8)


if __name__ == "__main__":
    unittest.main()
