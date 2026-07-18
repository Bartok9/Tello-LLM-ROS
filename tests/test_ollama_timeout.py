# -*- coding: utf-8 -*-
"""Offline unit tests for sanitize_ollama_timeout (no ollama/rospy required)."""
import importlib.util
import math
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_sanitize():
    """Load sanitize helper without importing ollama/rospy via full package."""
    path = ROOT / "llm_models" / "ollama_client.py"
    src = path.read_text(encoding="utf-8")
    # Extract function body by execing only the pure function definition
    ns = {}
    # Minimal: compile pure function from file text between def sanitize and class
    start = src.index("def sanitize_ollama_timeout")
    end = src.index("class OllamaClient")
    exec(compile(src[start:end], str(path), "exec"), ns)
    return ns["sanitize_ollama_timeout"]


class TestSanitizeOllamaTimeout(unittest.TestCase):
    def setUp(self):
        self.fn = _load_sanitize()

    def test_default_when_none(self):
        self.assertEqual(self.fn(None), 150.0)

    def test_valid(self):
        self.assertEqual(self.fn(30), 30.0)
        self.assertEqual(self.fn("45.5"), 45.5)

    def test_bool_rejected(self):
        self.assertEqual(self.fn(True), 150.0)
        self.assertEqual(self.fn(False), 150.0)

    def test_negative_and_zero(self):
        self.assertEqual(self.fn(0), 150.0)
        self.assertEqual(self.fn(-1), 150.0)

    def test_nan_inf(self):
        self.assertEqual(self.fn(float("nan")), 150.0)
        self.assertEqual(self.fn(float("inf")), 150.0)

    def test_out_of_range(self):
        self.assertEqual(self.fn(0.5), 150.0)
        self.assertEqual(self.fn(601), 150.0)

    def test_bounds_inclusive(self):
        self.assertEqual(self.fn(1.0), 1.0)
        self.assertEqual(self.fn(600.0), 600.0)

    def test_gibberish(self):
        self.assertEqual(self.fn("nope"), 150.0)
        self.assertEqual(self.fn(object()), 150.0)


if __name__ == "__main__":
    unittest.main()
