# -*- coding: utf-8 -*-
import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_rospy = types.ModuleType("rospy")
_rospy.logerr = lambda *a, **k: None
_rospy.loginfo = lambda *a, **k: None
sys.modules.setdefault("rospy", _rospy)

from llm_models.custom_api_client import normalize_custom_plan_text


class TestCustomPlanText(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(normalize_custom_plan_text("go"), "go")

    def test_empty_ok(self):
        self.assertEqual(normalize_custom_plan_text(""), "")

    def test_none(self):
        with self.assertRaises(ValueError):
            normalize_custom_plan_text(None)

    def test_non_str(self):
        with self.assertRaises(ValueError):
            normalize_custom_plan_text(12)


if __name__ == "__main__":
    unittest.main()
