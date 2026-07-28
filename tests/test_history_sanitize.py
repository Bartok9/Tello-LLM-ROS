# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.history_sanitize import sanitize_chat_history


class TestHistorySanitize(unittest.TestCase):
    def test_none(self):
        self.assertEqual(sanitize_chat_history(None), [])

    def test_bad_container(self):
        self.assertEqual(sanitize_chat_history("nope"), [])
        self.assertEqual(sanitize_chat_history({"a": 1}), [])

    def test_filter_types(self):
        out = sanitize_chat_history([" hi ", "", None, 3, 2.5, True, False, {"x": 1}, "ok"])
        self.assertEqual(out, ["hi", "3", "2.5", "ok"])

    def test_non_finite(self):
        self.assertEqual(sanitize_chat_history([float("nan"), float("inf")]), [])

    def test_max_items(self):
        out = sanitize_chat_history(["a", "b", "c", "d"], max_items=2)
        self.assertEqual(out, ["a", "b"])

    def test_max_chars(self):
        out = sanitize_chat_history(["abcdefghij"], max_chars=4)
        self.assertEqual(out, ["abcd"])

    def test_tuple(self):
        self.assertEqual(sanitize_chat_history(("x", "y")), ["x", "y"])


if __name__ == "__main__":
    unittest.main()
