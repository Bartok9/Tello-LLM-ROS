"""Offline tests for http URL guard + ollama host wiring (no network)."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _ensure_rospy():
    if "rospy" not in sys.modules:
        rospy = types.ModuleType("rospy")
        rospy.logerr = lambda *a, **k: None
        rospy.logwarn = lambda *a, **k: None
        rospy.loginfo = lambda *a, **k: None
        rospy.logfatal = lambda *a, **k: None
        sys.modules["rospy"] = rospy


class TestHttpUrlGuards(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            "utils.http_url_guards", ROOT / "utils" / "http_url_guards.py"
        )
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_none_default(self):
        self.assertIsNone(self.mod.sanitize_http_base_url(None))
        self.assertEqual(self.mod.sanitize_http_base_url(None, default="x"), "x")

    def test_http_ok(self):
        self.assertEqual(
            self.mod.sanitize_http_base_url("http://127.0.0.1:11434"),
            "http://127.0.0.1:11434",
        )

    def test_https_strip_slash(self):
        self.assertEqual(
            self.mod.sanitize_http_base_url("https://ollama.example/"),
            "https://ollama.example",
        )

    def test_file_rejected(self):
        self.assertIsNone(self.mod.sanitize_http_base_url("file:///etc/passwd"))

    def test_empty_rejected(self):
        self.assertIsNone(self.mod.sanitize_http_base_url("   "))

    def test_non_str_rejected(self):
        self.assertIsNone(self.mod.sanitize_http_base_url(12345))


class TestOllamaClientHost(unittest.TestCase):
    def test_client_receives_host(self):
        _ensure_rospy()
        # stub ollama package
        fake_ollama = types.ModuleType("ollama")
        instances = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                instances.append(self)

            def list(self):
                return {"models": []}

        fake_ollama.Client = FakeClient
        sys.modules["ollama"] = fake_ollama

        if "llm_models" not in sys.modules:
            pkg = types.ModuleType("llm_models")
            pkg.__path__ = [str(ROOT / "llm_models")]
            sys.modules["llm_models"] = pkg
        base_spec = importlib.util.spec_from_file_location(
            "llm_models.base", ROOT / "llm_models" / "base.py"
        )
        base = importlib.util.module_from_spec(base_spec)
        sys.modules["llm_models.base"] = base
        base_spec.loader.exec_module(base)

        # utils package
        if "utils" not in sys.modules:
            up = types.ModuleType("utils")
            up.__path__ = [str(ROOT / "utils")]
            sys.modules["utils"] = up

        spec = importlib.util.spec_from_file_location(
            "llm_models.ollama_client",
            ROOT / "llm_models" / "ollama_client.py",
        )
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "llm_models"
        sys.modules["llm_models.ollama_client"] = mod
        spec.loader.exec_module(mod)

        c = mod.OllamaClient(
            "llama3",
            timeout=30.0,
            base_url="http://192.168.1.50:11434/",
        )
        self.assertEqual(c.host, "http://192.168.1.50:11434")
        self.assertEqual(instances[-1].kwargs.get("host"), "http://192.168.1.50:11434")
        self.assertEqual(instances[-1].kwargs.get("timeout"), 30.0)

    def test_invalid_host_omitted(self):
        _ensure_rospy()
        fake_ollama = types.ModuleType("ollama")
        instances = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                instances.append(self)

            def list(self):
                return {}

        fake_ollama.Client = FakeClient
        sys.modules["ollama"] = fake_ollama

        if "llm_models" not in sys.modules:
            pkg = types.ModuleType("llm_models")
            pkg.__path__ = [str(ROOT / "llm_models")]
            sys.modules["llm_models"] = pkg
        if "llm_models.base" not in sys.modules:
            base_spec = importlib.util.spec_from_file_location(
                "llm_models.base", ROOT / "llm_models" / "base.py"
            )
            base = importlib.util.module_from_spec(base_spec)
            sys.modules["llm_models.base"] = base
            base_spec.loader.exec_module(base)
        if "utils" not in sys.modules:
            up = types.ModuleType("utils")
            up.__path__ = [str(ROOT / "utils")]
            sys.modules["utils"] = up

        # force reload ollama client mod
        name = "llm_models.ollama_client"
        if name in sys.modules:
            del sys.modules[name]
        spec = importlib.util.spec_from_file_location(
            name, ROOT / "llm_models" / "ollama_client.py"
        )
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "llm_models"
        sys.modules[name] = mod
        spec.loader.exec_module(mod)

        c = mod.OllamaClient("m", timeout=10.0, base_url="ftp://bad")
        self.assertIsNone(c.host)
        self.assertNotIn("host", instances[-1].kwargs)

    def test_service_forwards_base_url(self):
        src = (ROOT / "scripts" / "llm_service_node.py").read_text()
        self.assertIn("base_url=base_url or self.base_url", src)


if __name__ == "__main__":
    unittest.main()
