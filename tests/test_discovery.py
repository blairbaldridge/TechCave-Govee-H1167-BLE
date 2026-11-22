"""Offline model and setup-source tests (no HA installation needed)."""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import unittest

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "govee_light_ble"


def load_discovery():
    spec = importlib.util.spec_from_file_location("model_discovery", COMPONENT / "discovery.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestDiscovery(unittest.TestCase):
    def test_model_name_recognition(self):
        checker = load_discovery().is_h1167_name
        self.assertTrue(checker("Govee_H1167_1234"))
        self.assertTrue(checker("gvh1167 demo"))
        self.assertFalse(checker("Govee_H617C_1234"))
        self.assertFalse(checker("Other brand"))
        self.assertFalse(checker(""))

    def test_flow_has_scan_and_manual_fallback(self):
        source = (COMPONENT / "config_flow.py").read_text()
        tree = ast.parse(source)
        self.assertIn("async_discovered_service_info", source)
        for name in ("async_step_user", "async_step_manual", "async_step_bluetooth"):
            self.assertIn(name, [node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)])
        self.assertNotIn('default="E8:', source)


if __name__ == "__main__":
    unittest.main()
