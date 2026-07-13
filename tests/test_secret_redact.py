# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.secrets import redact_secret


class TestRedactSecret(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(redact_secret(None))

    def test_empty(self):
        self.assertEqual(redact_secret(''), '')

    def test_short(self):
        self.assertEqual(redact_secret('abcd'), '***')

    def test_long(self):
        self.assertEqual(redact_secret('sk-abcdefghijklmnop'), '***mnop')
        self.assertNotIn('sk-abcdef', redact_secret('sk-abcdefghijklmnop'))


if __name__ == '__main__':
    unittest.main()
