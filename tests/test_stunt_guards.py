# -*- coding: utf-8 -*-
import math
import unittest

from utils.stunt_guards import battery_allows_stunt, clamp_battery_threshold


class TestStuntGuards(unittest.TestCase):
    def test_allows_at_and_above_minimum(self):
        self.assertTrue(battery_allows_stunt(20, 20))
        self.assertTrue(battery_allows_stunt(55, 20))
        self.assertTrue(battery_allows_stunt("30", 20))

    def test_denies_below_minimum(self):
        self.assertFalse(battery_allows_stunt(19, 20))
        self.assertFalse(battery_allows_stunt(0, 20))

    def test_fail_closed_on_junk(self):
        self.assertFalse(battery_allows_stunt(None, 20))
        self.assertFalse(battery_allows_stunt("low", 20))
        self.assertFalse(battery_allows_stunt(float("nan"), 20))
        self.assertFalse(battery_allows_stunt(math.inf, 20))

    def test_clamp_threshold(self):
        self.assertEqual(clamp_battery_threshold(20), 20)
        self.assertEqual(clamp_battery_threshold(-5), 0)
        self.assertEqual(clamp_battery_threshold(150), 100)
        self.assertEqual(clamp_battery_threshold("nope", default=25), 25)


if __name__ == "__main__":
    unittest.main()
