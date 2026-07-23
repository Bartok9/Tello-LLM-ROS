# -*- coding: utf-8 -*-
"""Offline unit tests for Gemini model_name path sanitize."""

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
from utils.model_name_guards import sanitize_gemini_model_id  # noqa: E402


class TestSanitizeGeminiModelId(unittest.TestCase):
    def test_simple_ok(self):
        for mid in ("gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro", "foo_bar.v1"):
            ok, cleaned, err = sanitize_gemini_model_id(mid)
            self.assertTrue(ok, msg=mid)
            self.assertEqual(cleaned, mid)
            self.assertEqual(err, "")

    def test_models_prefix_stripped(self):
        ok, cleaned, err = sanitize_gemini_model_id("models/gemini-1.5-flash")
        self.assertTrue(ok)
        self.assertEqual(cleaned, "gemini-1.5-flash")

    def test_none_empty_non_str(self):
        ok, _, err = sanitize_gemini_model_id(None)
        self.assertFalse(ok)
        self.assertIn("None", err)

        ok, _, err = sanitize_gemini_model_id("   ")
        self.assertFalse(ok)

        ok, _, err = sanitize_gemini_model_id(123)
        self.assertFalse(ok)
        self.assertIn("unexpected type", err)

    def test_path_traversal_and_separators(self):
        for bad in (
            "../evil",
            "foo/bar",
            "models/foo/bar",
            "models/../x",
            "a\\b",
            "models/",
        ):
            ok, cleaned, err = sanitize_gemini_model_id(bad)
            self.assertFalse(ok, msg=repr(bad))
            self.assertEqual(cleaned, "")

    def test_query_and_whitespace(self):
        for bad in (
            "gemini?key=1",
            "gemini#frag",
            "gemini flash",
            "gemini%2Fxx",
            "gemini&x=1",
            "gemini:pro",
        ):
            ok, cleaned, err = sanitize_gemini_model_id(bad)
            self.assertFalse(ok, msg=repr(bad))
            self.assertEqual(cleaned, "")


if __name__ == "__main__":
    unittest.main()
