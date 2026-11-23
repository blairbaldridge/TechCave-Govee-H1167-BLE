"""Ensure stable branch exposes only verified H1167 Lightshow modes."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "govee_light_ble"


def load_module(module_name, file):
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestFrames(unittest.TestCase):
    def test_preserved_mode_frames(self):
        pkg = types.ModuleType("govee_light_ble")
        pkg.__path__ = [str(COMPONENT)]
        sys.modules["govee_light_ble"] = pkg
        utils = load_module("govee_light_ble.api_utils", COMPONENT / "api_utils.py")
        modes = load_module("govee_light_ble.h1167_modes", COMPONENT / "h1167_modes.py")
        self.assertEqual(len(modes.H1167_MODE_FRAMES), 12)
        self.assertEqual(
            modes.H1167_MODE_OPTIONS,
            [f"Lightshow {i}" for i in range(1, 13)],
        )
        self.assertFalse(
            any(name.startswith("Carnival ") for name in modes.H1167_MODE_FRAMES)
        )
        self.assertTrue(all(utils.valid_frame(f) for f in modes.H1167_MODE_FRAMES.values()))
        self.assertEqual(modes.H1167_MODE_FRAMES["Lightshow 8"][4], 0x0B)
        source = (COMPONENT / "h1167_modes.py").read_text(encoding="utf-8")
        for num in range(1, 11):
            self.assertIn(f'# "Carnival {num}": bytes.fromhex(', source)


if __name__ == "__main__":
    unittest.main()
