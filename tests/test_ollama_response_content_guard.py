# -*- coding: utf-8 -*-
"""Offline tests for OllamaClient response content fail-closed."""
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

_rospy = types.ModuleType("rospy")
_rospy._logs = []
_rospy.logerr = lambda msg, *a, **k: _rospy._logs.append(msg)
_rospy.loginfo = lambda msg, *a, **k: None
_rospy.logwarn = lambda msg, *a, **k: None
_rospy.logfatal = lambda msg, *a, **k: _rospy._logs.append(msg)
sys.modules["rospy"] = _rospy

# stub ollama package
_ollama = types.ModuleType("ollama")
class _Client:
    def __init__(self, *a, **k):
        pass
    def list(self):
        return {}
_ollama.Client = _Client
sys.modules["ollama"] = _ollama

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from llm_models.ollama_client import OllamaClient  # noqa: E402
from llm_models.base import LLMBase  # noqa: E402


class TestOllamaContentGuard(unittest.TestCase):
    def setUp(self):
        _rospy._logs.clear()
        with patch.object(OllamaClient, "_initialize", lambda self, **k: None):
            self.client = object.__new__(OllamaClient)
            self.client.model_name = "test-model"
            self.client.client = MagicMock()

    def test_happy(self):
        self.client.client.chat.return_value = {
            "message": {"content": "  go land  "},
            "total_duration": 2_000_000_000,
            "prompt_eval_count": 3,
            "eval_count": 4,
        }
        ok, text, err, dur, pt, ct = OllamaClient.query(self.client, "sys", "hi")
        self.assertTrue(ok)
        self.assertEqual(text, "  go land  ")
        self.assertEqual(err, "")
        self.assertEqual(dur, 2.0)
        self.assertEqual(pt, 3)
        self.assertEqual(ct, 4)

    def test_none_content(self):
        self.client.client.chat.return_value = {"message": {"content": None}}
        ok, text, err, dur, pt, ct = OllamaClient.query(self.client, "sys", "hi")
        self.assertFalse(ok)
        self.assertEqual(text, "")
        self.assertIn("non-str", err)

    def test_missing_message(self):
        self.client.client.chat.return_value = {}
        ok, text, err, _, _, _ = OllamaClient.query(self.client, "sys", "hi")
        self.assertFalse(ok)
        self.assertIn("message", err)

    def test_non_dict_response(self):
        self.client.client.chat.return_value = "nope"
        ok, text, err, _, _, _ = OllamaClient.query(self.client, "sys", "hi")
        self.assertFalse(ok)
        self.assertIn("non-dict", err)

    def test_chat_exception(self):
        self.client.client.chat.side_effect = RuntimeError("down")
        ok, text, err, _, _, _ = OllamaClient.query(self.client, "sys", "hi")
        self.assertFalse(ok)
        self.assertIn("down", err)


if __name__ == "__main__":
    unittest.main()
