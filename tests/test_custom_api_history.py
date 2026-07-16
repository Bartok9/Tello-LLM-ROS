# -*- coding: utf-8 -*-
import unittest

from llm_models.message_history import pack_chat_messages


class TestPackChatMessages(unittest.TestCase):
    def test_no_history(self):
        msgs = pack_chat_messages("sys", "hi", history=None)
        self.assertEqual(
            msgs,
            [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "hi"},
            ],
        )

    def test_empty_history(self):
        msgs = pack_chat_messages("sys", "hi", history=[])
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[-1]["role"], "user")

    def test_alternating_history(self):
        hist = ["go left", "ok left", "then land"]
        msgs = pack_chat_messages("sys", "and take photo", history=hist)
        self.assertEqual(msgs[0], {"role": "system", "content": "sys"})
        self.assertEqual(msgs[1], {"role": "user", "content": "go left"})
        self.assertEqual(msgs[2], {"role": "assistant", "content": "ok left"})
        self.assertEqual(msgs[3], {"role": "user", "content": "then land"})
        self.assertEqual(msgs[4], {"role": "user", "content": "and take photo"})

    def test_none_prompts_become_empty_str(self):
        msgs = pack_chat_messages(None, None, history=None)
        self.assertEqual(msgs[0]["content"], "")
        self.assertEqual(msgs[1]["content"], "")


if __name__ == "__main__":
    unittest.main()
