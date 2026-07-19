#!/usr/bin/env python3
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

# Stub rospy for importing client module constants... work pure helpers only via import side
# load helpers by parsing module without rospy - reimport pattern:
import importlib.util

# Inline import by executing helper functions from source without full class install
spec_path = os.path.join(ROOT, 'llm_models', 'custom_api_client.py')
src = open(spec_path, encoding='utf-8').read()
# eval helpers only - import full module with rospy stub
import types
sys.modules.setdefault('rospy', types.SimpleNamespace(
    loginfo=lambda *a, **k: None,
    logerr=lambda *a, **k: None,
    logwarn=lambda *a, **k: None,
))
# base
from llm_models.custom_api_client import (
    sanitize_custom_server_url,
    sanitize_request_timeout,
)


class TestCustomApiGuards(unittest.TestCase):
    def test_http_ok(self):
        self.assertEqual(
            sanitize_custom_server_url('http://127.0.0.1:5000/'),
            'http://127.0.0.1:5000',
        )

    def test_https_ok(self):
        self.assertTrue(sanitize_custom_server_url('https://models.example.com').startswith('https://'))

    def test_reject_file(self):
        with self.assertRaises(ValueError):
            sanitize_custom_server_url('file:///etc/passwd')

    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            sanitize_custom_server_url('  ')
        with self.assertRaises(ValueError):
            sanitize_custom_server_url(None)

    def test_reject_no_scheme(self):
        with self.assertRaises(ValueError):
            sanitize_custom_server_url('localhost:5000')

    def test_timeout_default(self):
        self.assertEqual(sanitize_request_timeout(None), 60.0)
        self.assertEqual(sanitize_request_timeout(True), 60.0)

    def test_timeout_clamp(self):
        self.assertEqual(sanitize_request_timeout(0.1), 1.0)
        self.assertEqual(sanitize_request_timeout(9999), 600.0)
        self.assertEqual(sanitize_request_timeout(30), 30.0)

    def test_timeout_nan(self):
        self.assertEqual(sanitize_request_timeout(float('nan')), 60.0)


if __name__ == '__main__':
    unittest.main()
