# -*- coding: utf-8 -*-
"""Offline tests: GenericOpenAIClient honors timeout=."""
import math
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sanitize_openai_timeout(value, default=60.0, min_s=1.0, max_s=600.0):
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


class TestOpenAITimeoutSanitize(unittest.TestCase):
    def test_defaultish(self):
        self.assertEqual(sanitize_openai_timeout(45), 45.0)
        self.assertEqual(sanitize_openai_timeout(0), 60.0)
        self.assertEqual(sanitize_openai_timeout(-1), 60.0)

    def test_bounds(self):
        self.assertEqual(sanitize_openai_timeout(0.5), 1.0)
        self.assertEqual(sanitize_openai_timeout(900), 600.0)

    def test_non_finite_and_bad(self):
        self.assertEqual(sanitize_openai_timeout(float("nan")), 60.0)
        self.assertEqual(sanitize_openai_timeout(float("inf")), 60.0)
        self.assertEqual(sanitize_openai_timeout(True), 60.0)
        self.assertEqual(sanitize_openai_timeout("x"), 60.0)


class TestGenericOpenAIClientTimeoutKw(unittest.TestCase):
    def test_client_gets_timeout(self):
        # mock openai.OpenAI and rospy
        with mock.patch.dict(sys.modules, {"rospy": mock.MagicMock(), "openai": mock.MagicMock()}):
            import importlib
            # clear cached module
            for name in list(sys.modules):
                if name.startswith("llm_models"):
                    del sys.modules[name]
            import llm_models.openai_protocol_client as opc
            importlib.reload(opc)
            fake_openai = sys.modules["openai"]
            client_ctor = fake_openai.OpenAI
            client_ctor.return_value = mock.MagicMock()
            os.environ["GENERIC_OPENAI_API_KEY"] = "test-key-not-real"
            try:
                c = opc.GenericOpenAIClient(
                    "gpt-test",
                    api_key="test-key-not-real",
                    base_url="https://example.invalid/v1",
                    timeout=42,
                )
            finally:
                os.environ.pop("GENERIC_OPENAI_API_KEY", None)
            self.assertTrue(client_ctor.called)
            kwargs = client_ctor.call_args.kwargs
            self.assertIn("timeout", kwargs)
            self.assertEqual(kwargs["timeout"], 42.0)


if __name__ == "__main__":
    unittest.main()
