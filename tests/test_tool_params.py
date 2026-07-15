# -*- coding: utf-8 -*-
import math
import unittest

from utils.tool_params import coerce_finite_float, sanitize_history_length


class TestToolParams(unittest.TestCase):
    def test_coerce_ok(self):
        self.assertEqual(coerce_finite_float("1.5", "distance"), 1.5)
        self.assertEqual(coerce_finite_float(2, "x"), 2.0)

    def test_coerce_rejects(self):
        with self.assertRaises(ValueError):
            coerce_finite_float("nope", "distance")
        with self.assertRaises(ValueError):
            coerce_finite_float(float("nan"), "distance")
        with self.assertRaises(ValueError):
            coerce_finite_float(float("inf"), "angle")
        with self.assertRaises(ValueError):
            coerce_finite_float(None, "v")

    def test_history_length(self):
        self.assertEqual(sanitize_history_length(10), 10)
        self.assertEqual(sanitize_history_length(0), 10)
        self.assertEqual(sanitize_history_length(-3), 10)
        self.assertEqual(sanitize_history_length("5"), 5)
        self.assertEqual(sanitize_history_length("bad", 7), 7)
        self.assertEqual(sanitize_history_length(math.nan, 4), 4)


if __name__ == "__main__":
    unittest.main()
