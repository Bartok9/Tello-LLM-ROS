# -*- coding: utf-8 -*-
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.video_duration import sanitize_record_duration


class TestRecordVideoDuration(unittest.TestCase):
    def test_ok_mid(self):
        ok, d, msg = sanitize_record_duration(30)
        self.assertTrue(ok)
        self.assertEqual(d, 30.0)
        self.assertEqual(msg, "")

    def test_bounds(self):
        self.assertTrue(sanitize_record_duration(1)[0])
        self.assertTrue(sanitize_record_duration(120)[0])
        self.assertFalse(sanitize_record_duration(0)[0])
        self.assertFalse(sanitize_record_duration(121)[0])

    def test_non_finite(self):
        self.assertFalse(sanitize_record_duration(float('nan'))[0])
        self.assertFalse(sanitize_record_duration(float('inf'))[0])
        self.assertFalse(sanitize_record_duration(True)[0])
        self.assertFalse(sanitize_record_duration("nope")[0])
        self.assertFalse(sanitize_record_duration(None)[0])


if __name__ == '__main__':
    unittest.main()
