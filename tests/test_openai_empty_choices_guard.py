# -*- coding: utf-8 -*-
"""Offline tests: empty/missing OpenAI choices fail closed."""
from __future__ import annotations

import os
import sys
import unittest
from types import SimpleNamespace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.openai_choices_guards import extract_chat_plan_text  # noqa: E402


class TestExtractChatPlanText(unittest.TestCase):
    def test_none_response(self):
        ok, text, err = extract_chat_plan_text(None)
        self.assertFalse(ok)
        self.assertEqual(text, "")
        self.assertIn("None", err)

    def test_empty_choices(self):
        ok, text, err = extract_chat_plan_text(SimpleNamespace(choices=[]))
        self.assertFalse(ok)
        self.assertIn("no choices", err)

    def test_missing_choices_attr(self):
        ok, text, err = extract_chat_plan_text(SimpleNamespace())
        self.assertFalse(ok)
        self.assertIn("no choices", err)

    def test_dict_empty_choices(self):
        ok, text, err = extract_chat_plan_text({"choices": []})
        self.assertFalse(ok)
        self.assertIn("no choices", err)

    def test_no_message(self):
        ok, text, err = extract_chat_plan_text(SimpleNamespace(choices=[SimpleNamespace()]))
        self.assertFalse(ok)
        self.assertIn("no message", err)

    def test_none_content(self):
        msg = SimpleNamespace(content=None)
        ok, text, err = extract_chat_plan_text(
            SimpleNamespace(choices=[SimpleNamespace(message=msg)])
        )
        self.assertFalse(ok)
        self.assertIn("None", err)

    def test_non_str_content(self):
        msg = SimpleNamespace(content={"a": 1})
        ok, text, err = extract_chat_plan_text(
            SimpleNamespace(choices=[SimpleNamespace(message=msg)])
        )
        self.assertFalse(ok)
        self.assertIn("unexpected type", err)

    def test_empty_str(self):
        msg = SimpleNamespace(content="   ")
        ok, text, err = extract_chat_plan_text(
            SimpleNamespace(choices=[SimpleNamespace(message=msg)])
        )
        self.assertFalse(ok)
        self.assertIn("empty", err)

    def test_happy(self):
        msg = SimpleNamespace(content="  takeoff  ")
        ok, text, err = extract_chat_plan_text(
            SimpleNamespace(choices=[SimpleNamespace(message=msg)])
        )
        self.assertTrue(ok)
        self.assertEqual(text, "takeoff")
        self.assertEqual(err, "")

    def test_dict_shape(self):
        ok, text, err = extract_chat_plan_text(
            {"choices": [{"message": {"content": "land"}}]}
        )
        self.assertTrue(ok)
        self.assertEqual(text, "land")


if __name__ == "__main__":
    unittest.main()
