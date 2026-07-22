# -*- coding: utf-8 -*-
"""Offline unit tests for media path confinement."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


def _ensure_repo_on_path():
    root = Path(__file__).resolve().parents[1]
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)


_ensure_repo_on_path()
from utils.path_guards import resolve_confined_media_dir  # noqa: E402


class TestPathGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tello_path_guards_")
        self.root = os.path.join(self.tmp, ".ros")
        os.makedirs(self.root, exist_ok=True)

    def test_none_and_empty_use_default(self):
        d = resolve_confined_media_dir(None, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.join(self.root, "tello_captures"))
        d2 = resolve_confined_media_dir("  ", "tello_videos", allowed_root=self.root)
        self.assertEqual(d2, os.path.join(self.root, "tello_videos"))

    def test_non_str_uses_default(self):
        d = resolve_confined_media_dir(123, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.join(self.root, "tello_captures"))

    def test_absolute_inside_root_ok(self):
        inside = os.path.join(self.root, "custom_caps")
        d = resolve_confined_media_dir(inside, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.abspath(inside))

    def test_absolute_outside_root_rejected(self):
        outside = os.path.join(self.tmp, "evil")
        d = resolve_confined_media_dir(outside, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.join(self.root, "tello_captures"))

    def test_relative_escape_rejected(self):
        # Path that abspath-escapes allowed_root via ..
        raw = os.path.join(self.root, "..", "outside_leak")
        d = resolve_confined_media_dir(raw, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.join(self.root, "tello_captures"))

    def test_nested_subdir_ok(self):
        nested = os.path.join(self.root, "a", "b")
        d = resolve_confined_media_dir(nested, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.abspath(nested))

    def test_prefix_sibling_not_accepted(self):
        # /tmp/foo.ros vs allowed /tmp/foo — commonpath must not sibling-match
        sibling = self.root + "_sibling"
        d = resolve_confined_media_dir(sibling, "tello_captures", allowed_root=self.root)
        self.assertEqual(d, os.path.join(self.root, "tello_captures"))


if __name__ == "__main__":
    unittest.main()
