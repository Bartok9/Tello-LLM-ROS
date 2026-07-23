# -*- coding: utf-8 -*-
"""Offline unit tests for OpenAI message content guards."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def _ensure_repo_on_path():
    root = Path(__file__).resolve().parents[1]
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)


_ensure_repo_on_path()
from utils.openai_content_guards import normalize_message_content  # noqa: E402


class TestNormalizeMessageContent(unittest.TestCase):
    def test_none_fail_closed(self):
        ok, text, err = normalize_message_content(None)
        self.assertFalse(ok)
        self.assertEqual(text, "")
        self.assertIn("None", err)

    def test_non_str_fail_closed(self):
        for bad in (123, ["a"], {"c": 1}, b"bytes", True):
            ok, text, err = normalize_message_content(bad)
            self.assertFalse(ok, msg=repr(bad))
            self.assertEqual(text, "")
            self.assertIn("unexpected type", err)

    def test_empty_and_whitespace_ok(self):
        ok, text, err = normalize_message_content("")
        self.assertTrue(ok)
        self.assertEqual(text, "")
        self.assertEqual(err, "")

        ok, text, err = normalize_message_content("  \n\t  ")
        self.assertTrue(ok)
        self.assertEqual(text, "")

    def test_normal_strip(self):
        ok, text, err = normalize_message_content("  takeoff\nland  ")
        self.assertTrue(ok)
        self.assertEqual(text, "takeoff\nland")
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
