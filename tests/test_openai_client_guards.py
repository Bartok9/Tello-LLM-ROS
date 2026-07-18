# -*- coding: utf-8 -*-
"""Offline tests for OpenAI client timeout/base_url guards (no network)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "llm_models" / "openai_protocol_client.py"
    src = path.read_text(encoding="utf-8")
    start = src.index("def sanitize_openai_timeout")
    end = src.index("class GenericOpenAIClient")
    ns = {}
    exec(compile(src[start:end], str(path), "exec"), ns)
    return ns["sanitize_openai_timeout"], ns["validate_openai_base_url"]


class TestOpenAIGuards(unittest.TestCase):
    def setUp(self):
        self.to, self.bu = _load()

    def test_timeout_default(self):
        self.assertEqual(self.to(None), 60.0)
        self.assertEqual(self.to(True), 60.0)

    def test_timeout_valid(self):
        self.assertEqual(self.to(30), 30.0)
        self.assertEqual(self.to("12.5"), 12.5)

    def test_timeout_bad(self):
        self.assertEqual(self.to(0), 60.0)
        self.assertEqual(self.to(-5), 60.0)
        self.assertEqual(self.to(float("nan")), 60.0)
        self.assertEqual(self.to(9999), 60.0)

    def test_base_url_ok(self):
        self.assertEqual(self.bu("https://api.openai.com/v1"), "https://api.openai.com/v1")
        self.assertEqual(self.bu("  http://localhost:8000/v1  "), "http://localhost:8000/v1")

    def test_base_url_bad(self):
        with self.assertRaises(ValueError):
            self.bu(None)
        with self.assertRaises(ValueError):
            self.bu("")
        with self.assertRaises(ValueError):
            self.bu("ftp://x")
        with self.assertRaises(ValueError):
            self.bu("not-a-url")


if __name__ == "__main__":
    unittest.main()
