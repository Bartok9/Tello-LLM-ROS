"""Offline tests: CustomApiClient import path + timeout clamp (no network)."""
import importlib.util
import math
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_custom_api():
    # Stub rospy if missing
    if "rospy" not in sys.modules:
        rospy = types.ModuleType("rospy")
        rospy.logerr = lambda *a, **k: None
        rospy.logwarn = lambda *a, **k: None
        rospy.loginfo = lambda *a, **k: None
        rospy.logfatal = lambda *a, **k: None
        sys.modules["rospy"] = rospy
    # Ensure package path
    if "llm_models" not in sys.modules:
        pkg = types.ModuleType("llm_models")
        pkg.__path__ = [str(ROOT / "llm_models")]
        sys.modules["llm_models"] = pkg
    spec = importlib.util.spec_from_file_location(
        "llm_models.custom_api_client",
        ROOT / "llm_models" / "custom_api_client.py",
    )
    mod = importlib.util.module_from_spec(spec)
    # base deps
    base_spec = importlib.util.spec_from_file_location(
        "llm_models.base", ROOT / "llm_models" / "base.py"
    )
    base = importlib.util.module_from_spec(base_spec)
    sys.modules["llm_models.base"] = base
    base_spec.loader.exec_module(base)
    sys.modules["llm_models.custom_api_client"] = mod
    # parent package relative import ".base"
    mod.__package__ = "llm_models"
    spec.loader.exec_module(mod)
    return mod


class TestCustomApiTimeout(unittest.TestCase):
    def setUp(self):
        self.mod = _load_custom_api()

    def test_default_timeout_60(self):
        c = self.mod.CustomApiClient("m", server_url="http://127.0.0.1:8080")
        self.assertEqual(c.timeout, 60.0)
        self.assertTrue(c.api_endpoint.endswith("/v1/chat/completions"))

    def test_timeout_clamped_high(self):
        c = self.mod.CustomApiClient("m", server_url="http://x", timeout=9999)
        self.assertEqual(c.timeout, 600.0)

    def test_timeout_clamped_low(self):
        c = self.mod.CustomApiClient("m", server_url="http://x", timeout=0.1)
        self.assertEqual(c.timeout, 1.0)

    def test_timeout_nan_falls_back(self):
        c = self.mod.CustomApiClient("m", server_url="http://x", timeout=float("nan"))
        self.assertEqual(c.timeout, 60.0)

    def test_timeout_bad_type_falls_back(self):
        c = self.mod.CustomApiClient("m", server_url="http://x", timeout="nope")
        self.assertEqual(c.timeout, 60.0)

    def test_post_uses_instance_timeout(self):
        c = self.mod.CustomApiClient("m", server_url="http://127.0.0.1:9", timeout=12.5)
        fake_resp = mock.Mock()
        fake_resp.raise_for_status = mock.Mock()
        fake_resp.json.return_value = {
            "success": True,
            "data": {
                "plan_text": "ok",
                "duration_s": 0.1,
                "usage": {"prompt_tokens": 1, "completion_tokens": 2},
            },
        }
        with mock.patch.object(self.mod.requests, "post", return_value=fake_resp) as post:
            ok, text, err, *_ = c.query("sys", "user")
            self.assertTrue(ok)
            self.assertEqual(text, "ok")
            kwargs = post.call_args.kwargs
            self.assertEqual(kwargs.get("timeout"), 12.5)


class TestServiceNodeImport(unittest.TestCase):
    def test_source_imports_custom_api(self):
        src = (ROOT / "scripts" / "llm_service_node.py").read_text()
        self.assertIn("from llm_models.custom_api_client import CustomApiClient", src)
        self.assertIn("timeout=self.timeout", src)


if __name__ == "__main__":
    unittest.main()
