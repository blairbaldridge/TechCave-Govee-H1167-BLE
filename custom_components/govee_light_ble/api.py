"""Connection handling and control for Govee BLE lights, including H1167."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from bleak import BleakClient
from bleak_retry_connector import establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .api_utils import (
    LedColorType,
    LedPacketCmd,
    LedPacketHead,
    generate_frame,
    valid_frame,
)
from .const import READ_CHARACTERISTIC_UUID, WRITE_CHARACTERISTIC_UUID

_LOGGER = logging.getLogger(__name__)

# The uploaded original sent each power and request command three times.
REPEAT_COUNT = 3


class GoveeAPI:
    """Send commands over BLE and track responses from the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        update_callback: Callable[[], None],
        *,
        segmented: bool = False,
        write_only: bool = False,
    ) -> None:
        self.hass = hass
        self.address = address.upper()
        self.segmented = segmented
        # H1167 notification setup can invalidate BlueZ GATT object paths.
        self.write_only = write_only
        self.state: bool | None = None
        self.brightness: int | None = None
        self.color: tuple[int, int, int] | None = None
        self._update_callback = update_callback
        self._client: BleakClient | None = None
        self._write_characteristic = None
        self._write_with_response = False
        self._notify_enabled = False
        self._lock = asyncio.Lock()

    @staticmethod
    def _gatt_summary(client: BleakClient) -> str:
        """List actual GATT characteristics to aid BLE/proxy diagnosis."""
        summary = []
        for service in client.services:
            for characteristic in service.characteristics:
                properties = ",".join(characteristic.properties)
                summary.append(f"{characteristic.uuid} [{properties}]")
        return "; ".join(summary) or "No characteristics reported"

    async def _ensure_connected(self) -> BleakClient:
        client = self._client
        if client is not None and client.is_connected:
            return client
        # Discard GATT characteristics belonging to a disconnected session.
        self._client = None
        self._write_characteristic = None
        self._notify_enabled = False

        # Advertisements from passive-only scanners cannot be used for GATT.
        device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if device is None:
            raise ConnectionError(
                f"Govee BLE {self.address} not seen by a connectable "
                "Bluetooth adapter/proxy"
            )

        client = await establish_connection(
            BleakClient, device, device.name or self.address, max_attempts=3
        )
        try:
            # The H1167 may be reachable without exposing the legacy 2b10
            # notification characteristic on some adapters/proxies.
            # Do NOT require notifications to be able to send power commands.
            write_char = client.services.get_characteristic(
                WRITE_CHARACTERISTIC_UUID
            )
            if write_char is None:
                raise ConnectionError(
                    f"Govee BLE {self.address}: required WRITE characteristic "
                    f"{WRITE_CHARACTERISTIC_UUID} not found. "
                    f"Discovered GATT: {self._gatt_summary(client)}"
                )
            props = set(write_char.properties)
            if "write-without-response" in props:
                write_with_response = False
            elif "write" in props:
                write_with_response = True
            else:
                raise ConnectionError(
                    f"Govee BLE {self.address}: characteristic "
                    f"{WRITE_CHARACTERISTIC_UUID} has no write property "
                    f"(properties={sorted(props)}). "
                    f"Discovered GATT: {self._gatt_summary(client)}"
                )

            self._notify_enabled = False
            if not self.write_only:
                notify_char = client.services.get_characteristic(
                    READ_CHARACTERISTIC_UUID
                )
                if notify_char is not None and (
                    "notify" in notify_char.properties
                    or "indicate" in notify_char.properties
                ):
                    try:
                        await client.start_notify(
                            notify_char, self._handle_notification
                        )
                        self._notify_enabled = True
                    except Exception as err:
                        _LOGGER.warning(
                            "Govee BLE %s cannot enable notifications (%s); "
                            "continuing in write-only mode (power status will "
                            "be optimistic)", self.address, err,
                        )
                else:
                    _LOGGER.warning(
                        "Govee BLE %s: notification characteristic %s is "
                        "missing or lacks notify/indicate. Continuing in "
                        "write-only mode. Discovered GATT: %s",
                        self.address,
                        READ_CHARACTERISTIC_UUID,
                        self._gatt_summary(client),
                    )

            self._write_characteristic = write_char
            self._write_with_response = write_with_response
            self._client = client
            _LOGGER.debug(
                "Connected to Govee BLE %s; notifications=%s, "
                "write_with_response=%s",
                self.address, self._notify_enabled, self._write_with_response,
            )
            return client
        except Exception:
            self._write_characteristic = None
            self._notify_enabled = False
            try:
                await client.disconnect()
            except Exception:
                _LOGGER.debug("Disconnect after setup error", exc_info=True)
            raise

    def _handle_notification(self, _sender, raw: bytearray) -> None:
        """Handle read-characteristic notification (on the HA event loop)."""
        data = bytes(raw)
        if not valid_frame(data):
            _LOGGER.debug("Ignoring invalid BLE frame from %s: %s", self.address, data.hex())
            return
        if data[0] != LedPacketHead.REQUEST:
            return

        cmd = data[1]
        payload = data[2:19]
        changed = False
        if cmd == LedPacketCmd.POWER:
            new_state = payload[0] == 0x01
            changed = self.state != new_state
            self.state = new_state
        elif cmd == LedPacketCmd.BRIGHTNESS:
            value = round(payload[0] * 255 / 100) if self.segmented else payload[0]
            changed = self.brightness != value
            self.brightness = value
        elif cmd == LedPacketCmd.COLOR:
            value = (payload[1], payload[2], payload[3])
            changed = self.color != value
            self.color = value
        elif cmd == LedPacketCmd.SEGMENT:
            value = (payload[2], payload[3], payload[4])
            changed = self.color != value
            self.color = value
        if changed:
            self._update_callback()

    @staticmethod
    def _command(cmd: LedPacketCmd, payload: bytes = b"") -> bytes:
        return generate_frame(LedPacketHead.COMMAND, cmd, payload)

    @staticmethod
    def _request(cmd: LedPacketCmd, payload: bytes = b"") -> bytes:
        return generate_frame(LedPacketHead.REQUEST, cmd, payload)

    async def _reset_connection(self) -> None:
        """Discard GATT paths and disconnect after a failed BLE operation."""
        client, self._client = self._client, None
        self._write_characteristic = None
        self._notify_enabled = False
        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                _LOGGER.debug("Error closing failed BLE connection", exc_info=True)

    @staticmethod
    def _is_stale_gatt_error(err: Exception) -> bool:
        """Only retry connection/GATT invalidation, not protocol errors."""
        message = str(err).lower()
        return any(
            fragment in message
            for fragment in (
                "service discovery has not been performed",
                "org.freedesktop.dbus.error.unknownobject",
                "org.bluez.error.notconnected",
                "not connected",
                "device has been disconnected",
                "connection abort",
            )
        )

    async def _send(self, packets: list[bytes], *, request_only: bool = False) -> None:
        """Send command batch, reconnecting once for stale BlueZ GATT state."""
        # H1167 has no reliable notification readback. Avoid a BLE connection
        # every 45 seconds for unobservable polls that can disrupt writes.
        if request_only and self.write_only:
            return
        async with self._lock:
            for attempt in range(2):
                try:
                    client = await self._ensure_connected()
                    if request_only and not self._notify_enabled:
                        return
                    for frame in packets:
                        await client.write_gatt_char(
                            self._write_characteristic,
                            frame,
                            response=self._write_with_response,
                        )
                    return
                except Exception as err:
                    retry = attempt == 0 and self._is_stale_gatt_error(err)
                    await self._reset_connection()
                    if not retry:
                        raise
                    _LOGGER.warning(
                        "Govee BLE %s lost GATT services (%s); "
                        "reconnecting once before retrying command",
                        self.address, err,
                    )
                    await asyncio.sleep(0.4)

    def _request_packets(self, *, power_only: bool) -> list[bytes]:
        packets = [self._request(LedPacketCmd.POWER)] * REPEAT_COUNT
        if not power_only:
            packets.extend([self._request(LedPacketCmd.BRIGHTNESS)] * REPEAT_COUNT)
            if self.segmented:
                color_request = self._request(LedPacketCmd.SEGMENT, b"\x01")
            else:
                color_request = self._request(LedPacketCmd.COLOR)
            packets.extend([color_request] * REPEAT_COUNT)
        return packets

    async def request_state(self, *, power_only: bool = True) -> None:
        """Request current device state; notification updates the coordinator."""
        await self._send(
            self._request_packets(power_only=power_only), request_only=True
        )

    async def set_light(
        self,
        on: bool,
        *,
        brightness: int | None = None,
        rgb: tuple[int, int, int] | None = None,
    ) -> None:
        """Write power and optionally brightness/color as one atomic batch.

        H1167 intentionally only uses the power command. Other devices retain
        the brightness/color commands from the original HACS integration.
        """
        power_frame = self._command(LedPacketCmd.POWER, bytes([int(on)]))
        packets = [power_frame] * REPEAT_COUNT
        packets.extend([self._request(LedPacketCmd.POWER)] * REPEAT_COUNT)

        if brightness is not None:
            brightness = max(0, min(255, int(brightness)))
            value = round(brightness * 100 / 255) if self.segmented else brightness
            packets.extend(
                [self._command(LedPacketCmd.BRIGHTNESS, bytes([value]))] * REPEAT_COUNT
            )
            packets.extend([self._request(LedPacketCmd.BRIGHTNESS)] * REPEAT_COUNT)

        if rgb is not None:
            r, g, b = (max(0, min(255, int(c))) for c in rgb)
            if self.segmented:
                payload = bytes([LedColorType.SEGMENTS, 1, r, g, b, 0, 0, 0, 0, 0, 0xFF, 0xFF])
                packets.extend([self._command(LedPacketCmd.COLOR, payload)] * REPEAT_COUNT)
                packets.extend([self._request(LedPacketCmd.SEGMENT, b"\x01")] * REPEAT_COUNT)
            else:
                packets.extend([self._command(LedPacketCmd.COLOR, bytes([LedColorType.SINGLE, r, g, b]))] * REPEAT_COUNT)
                packets.extend([self._command(LedPacketCmd.COLOR, bytes([LedColorType.LEGACY, r, g, b]))] * REPEAT_COUNT)
                packets.extend([self._request(LedPacketCmd.COLOR)] * REPEAT_COUNT)

        await self._send(packets)
        self.state = on
        if brightness is not None:
            self.brightness = brightness
        if rgb is not None:
            self.color = tuple(rgb)
        self._update_callback()

    async def set_h1167_mode(self, frame: bytes) -> None:
        """Write one recorded 20-byte H1167 mode frame."""
        if not valid_frame(frame):
            raise ValueError("Invalid H1167 BLE mode frame")
        await self._send([frame])

    async def async_close(self) -> None:
        """Release the BLE connection when the HA integration unloads."""
        async with self._lock:
            await self._reset_connection()
