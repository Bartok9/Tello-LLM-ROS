# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from llm_models.gemini_payload import pack_gemini_payload


class TestPackGeminiPayload(unittest.TestCase):
    def test_empty_history(self):
        p = pack_gemini_payload("sys", "hello", None)
        self.assertEqual(p["systemInstruction"]["parts"][0]["text"], "sys")
        self.assertEqual(len(p["contents"]), 1)
        self.assertEqual(p["contents"][0]["role"], "user")
        self.assertEqual(p["contents"][0]["parts"][0]["text"], "hello")

    def test_history_roles(self):
        p = pack_gemini_payload("sys", "next", ["u1", "a1", "u2"])
        roles = [c["role"] for c in p["contents"]]
        self.assertEqual(roles, ["user", "model", "user", "user"])
        self.assertEqual(p["contents"][1]["parts"][0]["text"], "a1")

    def test_none_prompts_str(self):
        p = pack_gemini_payload(None, None, [])
        self.assertEqual(p["systemInstruction"]["parts"][0]["text"], "")
        self.assertEqual(p["contents"][0]["parts"][0]["text"], "")


if __name__ == "__main__":
    unittest.main()
