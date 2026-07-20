# -*- coding: utf-8 -*-
import math
import os
import unittest


def sanitize_llm_service_timeout(value, default=150.0, min_s=1.0, max_s=600.0):
    """Mirror of scripts/llm_service_node.sanitize_llm_service_timeout."""
    try:
        if isinstance(value, bool):
            raise TypeError("bool not allowed")
        t = float(value)
        if not math.isfinite(t) or t <= 0:
            return float(default)
        if t < min_s:
            return float(min_s)
        if t > max_s:
            return float(max_s)
        return t
    except (TypeError, ValueError):
        return float(default)


class TestLlmServiceTimeout(unittest.TestCase):
    def test_default_none(self):
        self.assertEqual(sanitize_llm_service_timeout(None), 150.0)

    def test_bool_reject(self):
        self.assertEqual(sanitize_llm_service_timeout(True), 150.0)

    def test_negative(self):
        self.assertEqual(sanitize_llm_service_timeout(-5), 150.0)

    def test_zero(self):
        self.assertEqual(sanitize_llm_service_timeout(0), 150.0)

    def test_nan_inf(self):
        self.assertEqual(sanitize_llm_service_timeout(float("nan")), 150.0)
        self.assertEqual(sanitize_llm_service_timeout(float("inf")), 150.0)

    def test_string(self):
        self.assertEqual(sanitize_llm_service_timeout("nope"), 150.0)
        self.assertEqual(sanitize_llm_service_timeout("30"), 30.0)

    def test_clamp_low_high(self):
        self.assertEqual(sanitize_llm_service_timeout(0.5), 1.0)
        self.assertEqual(sanitize_llm_service_timeout(9999), 600.0)

    def test_valid(self):
        self.assertEqual(sanitize_llm_service_timeout(120.0), 120.0)

    def test_source_wired(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(root, "scripts", "llm_service_node.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("def sanitize_llm_service_timeout", src)
        self.assertIn("sanitize_llm_service_timeout(rospy.get_param", src)


if __name__ == "__main__":
    unittest.main()
