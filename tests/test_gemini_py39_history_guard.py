# -*- coding: utf-8 -*-
"""Offline tests for gemini_client_for_py39+ history + plan_text guards."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]


def _load_py39_module():
    """Load gemini_client_for_py39+.py without importing google.genai / rospy hardware."""
    # stub rospy
    rospy = types.ModuleType("rospy")
    rospy.loginfo = lambda *a, **k: None
    rospy.logerr = lambda *a, **k: None
    rospy.logwarn = lambda *a, **k: None
    sys.modules["rospy"] = rospy

    # stub google.genai
    google = types.ModuleType("google")
    genai = types.ModuleType("google.genai")
    genai.Client = MagicMock
    google.genai = genai
    sys.modules["google"] = google
    sys.modules["google.genai"] = genai

    # stub package base
    pkg = types.ModuleType("llm_models")
    pkg.__path__ = [str(ROOT / "llm_models")]
    sys.modules["llm_models"] = pkg

    base_path = ROOT / "llm_models" / "base.py"
    spec_base = importlib.util.spec_from_file_location("llm_models.base", base_path)
    base_mod = importlib.util.module_from_spec(spec_base)
    sys.modules["llm_models.base"] = base_mod
    spec_base.loader.exec_module(base_mod)

    path = ROOT / "llm_models" / "gemini_client_for_py39+.py"
    spec = importlib.util.spec_from_file_location(
        "llm_models.gemini_client_for_py39", path
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["llm_models.gemini_client_for_py39"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestPackAndExtract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_py39_module()

    def test_pack_history_appends_user(self):
        pack = self.mod.pack_gemini_contents
        out = pack("fly home", history=["takeoff", "ok", "move_forward 1m"])
        self.assertEqual(out[-1], "fly home")
        self.assertEqual(out[0], "takeoff")
        self.assertEqual(len(out), 4)

    def test_pack_skips_blank_history(self):
        pack = self.mod.pack_gemini_contents
        out = pack("land", history=["", None, "  "])
        self.assertEqual(out, ["land"])

    def test_extract_plan_text_ok(self):
        r = types.SimpleNamespace(text="  takeoff\nland  ")
        self.assertEqual(self.mod.extract_plan_text(r), "takeoff\nland")

    def test_extract_plan_text_empty(self):
        self.assertIsNone(self.mod.extract_plan_text(types.SimpleNamespace(text="")))
        self.assertIsNone(self.mod.extract_plan_text(types.SimpleNamespace(text=None)))
        self.assertIsNone(self.mod.extract_plan_text(types.SimpleNamespace()))


class TestQueryAcceptsHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_py39_module()

    def test_query_kw_history_no_typeerror(self):
        client = self.mod.GeminiClient.__new__(self.mod.GeminiClient)
        client.model_name = "gemini-test"
        models = MagicMock()
        gen = MagicMock()
        gen.text = "[START_COMMANDS]\ntakeoff\n[END_COMMANDS]"
        token = MagicMock()
        token.total_tokens = 3
        models.generate_content.return_value = gen
        models.count_tokens.return_value = token
        client.client = MagicMock()
        client.client.models = models

        ok, plan, err, *_ = client.query("sys", "go up", history=["hi", "hello"])
        self.assertTrue(ok)
        self.assertIn("takeoff", plan)
        self.assertEqual(err, "")
        kwargs = models.generate_content.call_args.kwargs
        self.assertIn("hi", kwargs["contents"])
        self.assertEqual(kwargs["contents"][-1], "go up")

    def test_query_empty_text_fail_closed(self):
        client = self.mod.GeminiClient.__new__(self.mod.GeminiClient)
        client.model_name = "gemini-test"
        models = MagicMock()
        models.generate_content.return_value = types.SimpleNamespace(text="")
        client.client = MagicMock()
        client.client.models = models

        ok, plan, err, *_ = client.query("sys", "x", history=None)
        self.assertFalse(ok)
        self.assertEqual(plan, "")
        self.assertIn("empty", err.lower())


if __name__ == "__main__":
    unittest.main()
