"""Captured H1167 mode commands, in the Govee app selection order.

These are 20-byte BLE GATT Write Without Response packets recorded on
2026-11-14. Keep them byte-for-byte; Carnival packets have extra parameters.
Lightshow 8 uses 0x0B rather than the sequential 0x07 mode ID.
Names are positional placeholders; do not imply verified scene names.
"""

from __future__ import annotations

from .api_utils import valid_frame

H1167_MODE_FRAMES: dict[str, bytes] = {
    "Lightshow 1": bytes.fromhex("33 60 02 01 00 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1C"),
    "Lightshow 2": bytes.fromhex("33 60 02 01 01 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1D"),
    "Lightshow 3": bytes.fromhex("33 60 02 01 02 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1E"),
    "Lightshow 4": bytes.fromhex("33 60 02 01 03 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1F"),
    "Lightshow 5": bytes.fromhex("33 60 02 01 04 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 18"),
    "Lightshow 6": bytes.fromhex("33 60 02 01 05 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 19"),
    "Lightshow 7": bytes.fromhex("33 60 02 01 06 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1A"),
    "Lightshow 8": bytes.fromhex("33 60 02 01 0B 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 17"),
    "Lightshow 9": bytes.fromhex("33 60 02 01 07 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 1B"),
    "Lightshow 10": bytes.fromhex("33 60 02 01 08 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 14"),
    "Lightshow 11": bytes.fromhex("33 60 02 01 09 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 15"),
    "Lightshow 12": bytes.fromhex("33 60 02 01 0A 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 16"),
    "Carnival 1": bytes.fromhex("33 60 02 02 20 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 3F"),
    "Carnival 2": bytes.fromhex("33 60 02 02 21 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3F"),
    "Carnival 3": bytes.fromhex("33 60 02 02 22 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3C"),
    "Carnival 4": bytes.fromhex("33 60 02 02 23 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 3C"),
    "Carnival 5": bytes.fromhex("33 60 02 02 24 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3A"),
    "Carnival 6": bytes.fromhex("33 60 02 02 25 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 3B"),
    "Carnival 7": bytes.fromhex("33 60 02 02 26 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 39"),
    "Carnival 8": bytes.fromhex("33 60 02 02 27 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 38"),
    "Carnival 9": bytes.fromhex("33 60 02 02 28 00 01 4C 00 00 00 00 00 00 00 00 00 00 00 36"),
    "Carnival 10": bytes.fromhex("33 60 02 02 29 00 00 4C 00 00 00 00 00 00 00 00 00 00 00 36"),
}

for _name, _frame in H1167_MODE_FRAMES.items():
    if not valid_frame(_frame):
        raise ValueError(f"Invalid captured H1167 mode packet for {_name}")

H1167_MODE_OPTIONS: list[str] = list(H1167_MODE_FRAMES)
