# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.tello_boot import safe_tello_connect, safe_tello_streamon


class _OkTello(object):
    def connect(self):
        self.connected = True

    def streamon(self):
        self.streaming = True


class _BoomConnect(object):
    def connect(self):
        raise RuntimeError("radio offline")

    def streamon(self):
        pass


class _BoomStream(object):
    def connect(self):
        pass

    def streamon(self):
        raise OSError("stream busy")


class TestTelloBoot(unittest.TestCase):
    def test_connect_ok(self):
        t = _OkTello()
        ok, err = safe_tello_connect(t)
        self.assertTrue(ok)
        self.assertEqual(err, "")
        self.assertTrue(t.connected)

    def test_connect_none(self):
        ok, err = safe_tello_connect(None)
        self.assertFalse(ok)
        self.assertIn("None", err)

    def test_connect_raises(self):
        ok, err = safe_tello_connect(_BoomConnect())
        self.assertFalse(ok)
        self.assertIn("radio", err)

    def test_streamon_ok(self):
        t = _OkTello()
        ok, err = safe_tello_streamon(t)
        self.assertTrue(ok)
        self.assertTrue(t.streaming)

    def test_streamon_raises(self):
        ok, err = safe_tello_streamon(_BoomStream())
        self.assertFalse(ok)
        self.assertIn("stream", err)

    def test_missing_methods(self):
        ok, err = safe_tello_connect(object())
        self.assertFalse(ok)
        ok2, err2 = safe_tello_streamon(object())
        self.assertFalse(ok2)


if __name__ == "__main__":
    unittest.main()
