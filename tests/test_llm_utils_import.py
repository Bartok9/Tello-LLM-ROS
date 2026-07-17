# -*- coding: utf-8 -*-
import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Avoid importing real rospy (may be missing offline): inject a stub before utils.
sys.modules.setdefault("rospy", types.SimpleNamespace(logerr=lambda *a, **k: None, loginfo=lambda *a, **k: None, logwarn=lambda *a, **k: None))

from utils.llm_utils import try_import


class TestTryImport(unittest.TestCase):
    def test_stdlib_ok(self):
        ok, err = try_import("json")
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_missing_package(self):
        ok, err = try_import("definitely_not_a_real_package_xyz_987654")
        self.assertFalse(ok)
        self.assertTrue(err)

    def test_mocked_import_module_raises_other(self):
        with mock.patch("importlib.import_module", side_effect=RuntimeError("boom")):
            ok, err = try_import("json")
            self.assertFalse(ok)
            self.assertIn("boom", err)


if __name__ == "__main__":
    unittest.main()
