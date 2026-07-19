#!/usr/bin/env python3
"""Offline unit tests for sanitize_cmd_vel_timeout_sec."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.safety_guards import sanitize_cmd_vel_timeout_sec


class TestCmdVelTimeout(unittest.TestCase):
    def test_default_passthrough(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec(0.5), 0.5)

    def test_none_default(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec(None), 0.5)

    def test_bool_rejected(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec(True), 0.5)
        self.assertEqual(sanitize_cmd_vel_timeout_sec(False), 0.5)

    def test_negative_zero(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec(0), 0.5)
        self.assertEqual(sanitize_cmd_vel_timeout_sec(-1), 0.5)

    def test_string_numeric(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec('1.25'), 1.25)

    def test_string_junk(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec('nope'), 0.5)

    def test_inf_nan(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec(float('inf')), 0.5)
        self.assertEqual(sanitize_cmd_vel_timeout_sec(float('nan')), 0.5)

    def test_clamp(self):
        self.assertEqual(sanitize_cmd_vel_timeout_sec(0.01), 0.05)
        self.assertEqual(sanitize_cmd_vel_timeout_sec(99), 30.0)


if __name__ == '__main__':
    unittest.main()
