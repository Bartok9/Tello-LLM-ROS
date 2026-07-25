# -*- coding: utf-8 -*-
"""Offline tests for fail-closed tools file load in get_system_prompts."""
import json
import os
import sys
import tempfile
import types
import unittest

# Minimal rospy shim before importing utils.llm_utils
_rospy = types.ModuleType("rospy")
_rospy._logs = []

def _logerr(msg, *a, **k):
    _rospy._logs.append(("err", msg))

def _loginfo(msg, *a, **k):
    _rospy._logs.append(("info", msg))

def _logwarn(msg, *a, **k):
    _rospy._logs.append(("warn", msg))

_rospy.logerr = _logerr
_rospy.loginfo = _loginfo
_rospy.logwarn = _logwarn
sys.modules["rospy"] = _rospy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.llm_utils import get_system_prompts  # noqa: E402


class TestGetSystemPromptsToolsGuard(unittest.TestCase):
    def setUp(self):
        _rospy._logs.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.prefix = os.path.join(self.tmp.name, "prefix.txt")
        with open(self.prefix, "w", encoding="utf-8") as f:
            f.write("PREFIX\n")

    def test_good_json_tools(self):
        tools = os.path.join(self.tmp.name, "tools.json")
        with open(tools, "w", encoding="utf-8") as f:
            json.dump({"tools": [{"name": "takeoff", "description": "go up", "parameters": []}]}, f)
        out = get_system_prompts(self.prefix, tools)
        self.assertTrue(out.startswith("PREFIX\n"))
        self.assertIn("takeoff", out)
        self.assertNotIn("[]", out.split("PREFIX\n", 1)[1][:5])  # not empty-only

    def test_missing_tools_json(self):
        tools = os.path.join(self.tmp.name, "missing.json")
        out = get_system_prompts(self.prefix, tools)
        self.assertEqual(out, "PREFIX\n[]")
        self.assertTrue(any("Failed to load tools" in m for _, m in _rospy._logs))

    def test_bad_json(self):
        tools = os.path.join(self.tmp.name, "bad.json")
        with open(tools, "w", encoding="utf-8") as f:
            f.write("{not json")
        out = get_system_prompts(self.prefix, tools)
        self.assertEqual(out, "PREFIX\n[]")

    def test_tools_not_list(self):
        tools = os.path.join(self.tmp.name, "nolist.json")
        with open(tools, "w", encoding="utf-8") as f:
            json.dump({"tools": "nope"}, f)
        out = get_system_prompts(self.prefix, tools)
        self.assertEqual(out, "PREFIX\n[]")

    def test_txt_missing(self):
        tools = os.path.join(self.tmp.name, "missing.txt")
        out = get_system_prompts(self.prefix, tools)
        self.assertEqual(out, "PREFIX\n[]")

    def test_txt_ok(self):
        tools = os.path.join(self.tmp.name, "tools.txt")
        with open(tools, "w", encoding="utf-8") as f:
            f.write("TOOLDOCS")
        out = get_system_prompts(self.prefix, tools)
        self.assertEqual(out, "PREFIX\nTOOLDOCS")


if __name__ == "__main__":
    unittest.main()
