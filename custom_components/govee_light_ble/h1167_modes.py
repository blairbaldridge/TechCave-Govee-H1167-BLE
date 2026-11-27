"""Captured H1167 mode commands, in the Govee app selection order.

These are 20-byte BLE GATT Write Without Response packets recorded on
2026-11-14. Keep them byte-for-byte; Carnival packets have extra parameters.
Lightshow 8 uses 0x0B rather than the sequential 0x07 mode ID.
The labels below are the corresponding Govee app names, matched to the
previous numbered scenes. Keep captured BLE packets byte-for-byte.
"""

from __future__ import annotations

from .api_utils import valid_frame

H1167_MODE_FRAMES: dict[str, bytes] = {
    "Rhythm": bytes.fromhex("33 60 02 01 00 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1C"),
    "Sprouting": bytes.fromhex("33 60 02 01 01 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1D"),
    "Shiny": bytes.fromhex("33 60 02 01 02 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1E"),
    "Beat": bytes.fromhex("33 60 02 01 03 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1F"),
    "Waves": bytes.fromhex("33 60 02 01 04 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 18"),
    "Spectrum": bytes.fromhex("33 60 02 01 05 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 19"),
    "Rolling": bytes.fromhex("33 60 02 01 06 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1A"),
    "Hopping": bytes.fromhex("33 60 02 01 0B 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 17"),
    "Starlight": bytes.fromhex("33 60 02 01 07 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1B"),
    "Piano Keys": bytes.fromhex("33 60 02 01 08 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 14"),
    "Jumping": bytes.fromhex("33 60 02 01 09 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 15"),
    "Luminous": bytes.fromhex("33 60 02 01 0A 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 16"),
    "Brilliant": bytes.fromhex("33 60 02 02 20 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 3F"),
    "Pulsate": bytes.fromhex("33 60 02 02 21 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3F"),
    "Dazzle": bytes.fromhex("33 60 02 02 22 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3C"),
    "Fascination": bytes.fromhex("33 60 02 02 23 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 3C"),
    "Aspiring": bytes.fromhex("33 60 02 02 24 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3A"),
    "Cadence": bytes.fromhex("33 60 02 02 25 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3B"),
    "Revel": bytes.fromhex("33 60 02 02 26 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 39"),
    "Fluctuate": bytes.fromhex("33 60 02 02 27 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 38"),
    "Funny": bytes.fromhex("33 60 02 02 28 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 36"),
    "Shimmer": bytes.fromhex("33 60 02 02 29 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 36"),
}


# Backward compatibility for the previous numeric option labels. These aliases
# are used to restore saved dropdown state; only app names appear as options.
H1167_LEGACY_MODE_NAMES: dict[str, str] = {
    "Lightshow 1": "Rhythm",
    "Lightshow 2": "Sprouting",
    "Lightshow 3": "Shiny",
    "Lightshow 4": "Beat",
    "Lightshow 5": "Waves",
    "Lightshow 6": "Spectrum",
    "Lightshow 7": "Rolling",
    "Lightshow 8": "Hopping",
    "Lightshow 9": "Starlight",
    "Lightshow 10": "Piano Keys",
    "Lightshow 11": "Jumping",
    "Lightshow 12": "Luminous",
    "Carnival 1": "Brilliant",
    "Carnival 2": "Pulsate",
    "Carnival 3": "Dazzle",
    "Carnival 4": "Fascination",
    "Carnival 5": "Aspiring",
    "Carnival 6": "Cadence",
    "Carnival 7": "Revel",
    "Carnival 8": "Fluctuate",
    "Carnival 9": "Funny",
    "Carnival 10": "Shimmer",
}

for _name, _frame in H1167_MODE_FRAMES.items():
    if not valid_frame(_frame):
        raise ValueError(f"Invalid captured H1167 mode packet for {_name}")

H1167_MODE_OPTIONS: list[str] = list(H1167_MODE_FRAMES)
