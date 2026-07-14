# -*- coding: utf-8 -*-
import math
import unittest

from utils.rc_limits import clamp_rc_channel


class TestClampRcChannel(unittest.TestCase):
    def test_in_range(self):
        self.assertEqual(clamp_rc_channel(0), 0)
        self.assertEqual(clamp_rc_channel(50.7), 50)
        self.assertEqual(clamp_rc_channel(-99.9), -99)

    def test_edges(self):
        self.assertEqual(clamp_rc_channel(-100), -100)
        self.assertEqual(clamp_rc_channel(100), 100)

    def test_overflow(self):
        self.assertEqual(clamp_rc_channel(250), 100)
        self.assertEqual(clamp_rc_channel(-250), -100)

    def test_non_finite(self):
        self.assertEqual(clamp_rc_channel(float("nan")), 0)
        self.assertEqual(clamp_rc_channel(float("inf")), 0)
        self.assertEqual(clamp_rc_channel(float("-inf")), 0)

    def test_bad_type(self):
        self.assertEqual(clamp_rc_channel(None), 0)
        self.assertEqual(clamp_rc_channel("nope"), 0)


if __name__ == "__main__":
    unittest.main()
