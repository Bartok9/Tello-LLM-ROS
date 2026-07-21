# -*- coding: utf-8 -*-
"""Offline tests: Gemini HTTP timeout sanitize + use."""
import math
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sanitize_gemini_http_timeout(value, default=60.0, min_s=1.0, max_s=600.0):
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


class TestSanitizeGeminiTimeout(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(sanitize_gemini_http_timeout(30), 30.0)

    def test_bounds(self):
        self.assertEqual(sanitize_gemini_http_timeout(0.2), 1.0)
        self.assertEqual(sanitize_gemini_http_timeout(9999), 600.0)

    def test_bad(self):
        self.assertEqual(sanitize_gemini_http_timeout(0), 60.0)
        self.assertEqual(sanitize_gemini_http_timeout(float("nan")), 60.0)
        self.assertEqual(sanitize_gemini_http_timeout(True), 60.0)
        self.assertEqual(sanitize_gemini_http_timeout(None), 60.0)


class TestGeminiClientUsesTimeout(unittest.TestCase):
    def test_post_timeout_from_kw(self):
        with mock.patch.dict(sys.modules, {"rospy": mock.MagicMock(), "requests": mock.MagicMock()}):
            for name in list(sys.modules):
                if name.startswith("llm_models"):
                    del sys.modules[name]
            import importlib
            import llm_models.gemini_client as gc
            importlib.reload(gc)
            requests = sys.modules["requests"]
            resp = mock.MagicMock()
            resp.raise_for_status = mock.MagicMock()
            resp.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "ok"}]}}]
            }
            requests.post.return_value = resp
            client = gc.GeminiClient(
                "gemini-test",
                api_key="fake-key",
                base_url="https://example.invalid/v1",
                timeout=77,
            )
            self.assertEqual(client.timeout, 77.0)
            ok, text, err, *_ = client.query("sys", "user")
            self.assertTrue(ok)
            self.assertEqual(text, "ok")
            kwargs = requests.post.call_args.kwargs
            self.assertEqual(kwargs.get("timeout"), 77.0)


if __name__ == "__main__":
    unittest.main()
