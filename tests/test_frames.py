"""Verify Govee app mode names preserve all captured H1167 BLE frames."""
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
        expected_names = [
            "Rhythm",
            "Sprouting",
            "Shiny",
            "Beat",
            "Waves",
            "Spectrum",
            "Rolling",
            "Hopping",
            "Starlight",
            "Piano Keys",
            "Jumping",
            "Luminous",
            "Brilliant",
            "Pulsate",
            "Dazzle",
            "Fascination",
            "Aspiring",
            "Cadence",
            "Revel",
            "Fluctuate",
            "Funny",
            "Shimmer",
        ]
        self.assertEqual(modes.H1167_MODE_OPTIONS, expected_names)
        self.assertEqual(list(modes.H1167_MODE_FRAMES), expected_names)
        expected_legacy_names = dict([
        ("Lightshow 1", "Rhythm"),
        ("Lightshow 2", "Sprouting"),
        ("Lightshow 3", "Shiny"),
        ("Lightshow 4", "Beat"),
        ("Lightshow 5", "Waves"),
        ("Lightshow 6", "Spectrum"),
        ("Lightshow 7", "Rolling"),
        ("Lightshow 8", "Hopping"),
        ("Lightshow 9", "Starlight"),
        ("Lightshow 10", "Piano Keys"),
        ("Lightshow 11", "Jumping"),
        ("Lightshow 12", "Luminous"),
        ("Carnival 1", "Brilliant"),
        ("Carnival 2", "Pulsate"),
        ("Carnival 3", "Dazzle"),
        ("Carnival 4", "Fascination"),
        ("Carnival 5", "Aspiring"),
        ("Carnival 6", "Cadence"),
        ("Carnival 7", "Revel"),
        ("Carnival 8", "Fluctuate"),
        ("Carnival 9", "Funny"),
        ("Carnival 10", "Shimmer"),
        ])
        self.assertEqual(modes.H1167_LEGACY_MODE_NAMES, expected_legacy_names)
        # Byte-for-byte regression against the original 22 captured packets.
        expected_hex_frames = {
            "Rhythm": "33 60 02 01 00 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1C",
            "Sprouting": "33 60 02 01 01 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1D",
            "Shiny": "33 60 02 01 02 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1E",
            "Beat": "33 60 02 01 03 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1F",
            "Waves": "33 60 02 01 04 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 18",
            "Spectrum": "33 60 02 01 05 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 19",
            "Rolling": "33 60 02 01 06 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1A",
            "Hopping": "33 60 02 01 0B 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 17",
            "Starlight": "33 60 02 01 07 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1B",
            "Piano Keys": "33 60 02 01 08 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 14",
            "Jumping": "33 60 02 01 09 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 15",
            "Luminous": "33 60 02 01 0A 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 16",
            "Brilliant": "33 60 02 02 20 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 3F",
            "Pulsate": "33 60 02 02 21 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3F",
            "Dazzle": "33 60 02 02 22 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3C",
            "Fascination": "33 60 02 02 23 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 3C",
            "Aspiring": "33 60 02 02 24 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3A",
            "Cadence": "33 60 02 02 25 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3B",
            "Revel": "33 60 02 02 26 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 39",
            "Fluctuate": "33 60 02 02 27 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 38",
            "Funny": "33 60 02 02 28 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 36",
            "Shimmer": "33 60 02 02 29 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 36",
        }
        self.assertEqual(
            {name: frame.hex(" ").upper() for name, frame in modes.H1167_MODE_FRAMES.items()},
            expected_hex_frames,
        )
        self.assertTrue(all(utils.valid_frame(f) for f in modes.H1167_MODE_FRAMES.values()))
        self.assertEqual(modes.H1167_MODE_FRAMES["Hopping"][4], 0x0B)
        self.assertEqual(modes.H1167_MODE_FRAMES["Shimmer"][4], 0x29)


if __name__ == "__main__":
    unittest.main()
