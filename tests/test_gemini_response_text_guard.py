# -*- coding: utf-8 -*-
import os
import sys
import types
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# lightweight rospy stub for offline unit tests
_rospy = types.ModuleType("rospy")
_rospy.logerr = lambda *a, **k: None
_rospy.loginfo = lambda *a, **k: None
_rospy.logwarn = lambda *a, **k: None
sys.modules.setdefault("rospy", _rospy)

from llm_models.gemini_client import extract_gemini_plan_text


class TestGeminiPlanText(unittest.TestCase):
    def test_ok_strip(self):
        data = {"candidates": [{"content": {"parts": [{"text": "  plan  "}]}}]}
        self.assertEqual(extract_gemini_plan_text(data), "plan")

    def test_null_text(self):
        data = {"candidates": [{"content": {"parts": [{"text": None}]}}]}
        with self.assertRaises(ValueError):
            extract_gemini_plan_text(data)

    def test_non_str(self):
        data = {"candidates": [{"content": {"parts": [{"text": 123}]}}]}
        with self.assertRaises(ValueError):
            extract_gemini_plan_text(data)

    def test_missing(self):
        with self.assertRaises(ValueError):
            extract_gemini_plan_text({"candidates": []})


if __name__ == "__main__":
    unittest.main()
