"""20-byte Govee BLE frame encoding and decoding.

This is the same 0x33 / 0xaa protocol found in the uploaded, working
`govee_light_ble` custom integration. A frame is 19 data bytes plus one
XOR checksum byte.
"""

from enum import IntEnum


class LedPacketHead(IntEnum):
    COMMAND = 0x33
    REQUEST = 0xAA


class LedPacketCmd(IntEnum):
    POWER = 0x01
    BRIGHTNESS = 0x04
    COLOR = 0x05
    SEGMENT = 0xA5


class LedColorType(IntEnum):
    SEGMENTS = 0x15
    SINGLE = 0x02
    LEGACY = 0x0D


def generate_frame(head: int, cmd: int, payload: bytes = b"") -> bytes:
    """Build a fixed-size packet with XOR checksum."""
    packet = bytes((head, cmd)) + bytes(payload)
    if len(packet) > 19:
        raise ValueError("Govee BLE packet payload is too large")
    packet = packet.ljust(19, b"\x00")
    checksum = 0
    for byte in packet:
        checksum ^= byte
    return packet + bytes((checksum,))


def valid_frame(packet: bytes) -> bool:
    """Validate the 20-byte packet XOR checksum."""
    if len(packet) != 20:
        return False
    checksum = 0
    for byte in packet:
        checksum ^= byte
    return checksum == 0
