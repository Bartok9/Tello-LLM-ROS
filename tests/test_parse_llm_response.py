# -*- coding: utf-8 -*-
"""Offline unit tests for parse_llm_response null/type guards."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


def _ensure_repo_on_path():
    root = Path(__file__).resolve().parents[1]
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)


def _stub_rospy():
    if "rospy" in sys.modules:
        return sys.modules["rospy"]
    mock = types.ModuleType("rospy")
    mock.loginfo = MagicMock()
    mock.logwarn = MagicMock()
    mock.logerr = MagicMock()
    mock.logfatal = MagicMock()
    sys.modules["rospy"] = mock
    return mock


_ensure_repo_on_path()
_ROSPY = _stub_rospy()
from utils.llm_utils import parse_llm_response  # noqa: E402


class TestParseLlmResponse(unittest.TestCase):
    def setUp(self):
        _ROSPY.logwarn.reset_mock()
        _ROSPY.logerr.reset_mock()
        _ROSPY.loginfo.reset_mock()

    def test_none_returns_empty(self):
        self.assertEqual(parse_llm_response(None), [])
        _ROSPY.logwarn.assert_called()

    def test_non_str_returns_empty(self):
        self.assertEqual(parse_llm_response(123), [])
        self.assertEqual(parse_llm_response(["takeoff"]), [])
        _ROSPY.logwarn.assert_called()

    def test_empty_and_whitespace(self):
        self.assertEqual(parse_llm_response(""), [])
        self.assertEqual(parse_llm_response("   \n\t  "), [])

    def test_start_end_block(self):
        text = (
            "thinking...\n"
            "[START_COMMANDS]\n"
            "takeoff\n"
            "land\n"
            "[END_COMMANDS]\n"
            "extra"
        )
        self.assertEqual(parse_llm_response(text), ["takeoff", "land"])

    def test_fallback_with_direct_parser(self):
        def parser(line):
            if line.strip() == "takeoff":
                return "takeoff", {}
            return None, None

        plan = "noise\ntakeoff\nbogus step"
        self.assertEqual(parse_llm_response(plan, parser), ["takeoff"])

    def test_fallback_without_parser(self):
        self.assertEqual(parse_llm_response("takeoff\nland", None), [])
        _ROSPY.logerr.assert_called()


if __name__ == "__main__":
    unittest.main()
