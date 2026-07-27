# -*- coding: utf-8 -*-
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.tools_config import load_tools_config


class TestLoadToolsConfig(unittest.TestCase):
    def test_missing_path(self):
        ok, cfg, err = load_tools_config("/no/such/tools.json")
        self.assertFalse(ok)
        self.assertIsNone(cfg)
        self.assertIn("not found", err)

    def test_empty_path(self):
        ok, cfg, err = load_tools_config("  ")
        self.assertFalse(ok)
        self.assertIsNone(cfg)

    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{not json")
            path = f.name
        try:
            ok, cfg, err = load_tools_config(path)
            self.assertFalse(ok)
            self.assertIn("JSON", err)
        finally:
            os.unlink(path)

    def test_valid_empty_tools(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"tools": []}, f)
            path = f.name
        try:
            ok, cfg, err = load_tools_config(path)
            self.assertTrue(ok)
            self.assertEqual(cfg["tools"], [])
            self.assertEqual(err, "")
        finally:
            os.unlink(path)

    def test_missing_tools_key_defaults(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"meta": 1}, f)
            path = f.name
        try:
            ok, cfg, err = load_tools_config(path)
            self.assertTrue(ok)
            self.assertEqual(cfg["tools"], [])
        finally:
            os.unlink(path)

    def test_tools_not_list(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"tools": {}}, f)
            path = f.name
        try:
            ok, cfg, err = load_tools_config(path)
            self.assertFalse(ok)
        finally:
            os.unlink(path)

    def test_preserves_tool(self):
        tool = {"name": "land", "parameters": []}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"tools": [tool]}, f)
            path = f.name
        try:
            ok, cfg, err = load_tools_config(path)
            self.assertTrue(ok)
            self.assertEqual(cfg["tools"][0]["name"], "land")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
