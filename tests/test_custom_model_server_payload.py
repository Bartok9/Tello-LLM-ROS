# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.chat_completion_payload import parse_chat_completion_payload


class TestChatCompletionPayload(unittest.TestCase):
    def test_ok(self):
        ok, err, f = parse_chat_completion_payload({
            "model": "m",
            "system_prompt": "sys",
            "user_prompt": " go ",
        })
        self.assertTrue(ok)
        self.assertEqual(f["user_prompt"], "go")
        self.assertEqual(err, "")

    def test_not_dict(self):
        self.assertFalse(parse_chat_completion_payload(None)[0])
        self.assertFalse(parse_chat_completion_payload([])[0])

    def test_bad_types(self):
        self.assertFalse(parse_chat_completion_payload({"user_prompt": 1})[0])
        self.assertFalse(parse_chat_completion_payload({"user_prompt": "x", "system_prompt": 3})[0])
        self.assertFalse(parse_chat_completion_payload({"user_prompt": "x", "model": {"a": 1}})[0])

    def test_empty_user(self):
        self.assertFalse(parse_chat_completion_payload({"user_prompt": "  "})[0])


if __name__ == '__main__':
    unittest.main()
