"""Govee H1167 setup: discover via Home Assistant Bluetooth or enter address."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import voluptuous as vol
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS, CONF_NAME

from .const import DOMAIN
from .discovery import is_h1167_name

_MAC_REGEX = re.compile(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\Z")
_MANUAL = "__manual__"
_REFRESH = "__refresh__"
_CONFIRM_H1167 = "confirm_h1167"


@dataclass(frozen=True)
class _DiscoveredDevice:
    """One BLE advertisement known to Home Assistant."""

    address: str
    name: str
    connectable: bool
    h1167_name: bool
    rssi: int | None = None

    @property
    def display_label(self) -> str:
        """Show an address even if the advertisement has no device name."""
        model = "H1167 name match" if self.h1167_name else "Other/unknown BLE"
        availability = "Connectable" if self.connectable else "Scan only (cannot control)"
        signal = f" | {self.rssi} dBm" if self.rssi is not None else ""
        return f"{self.name or 'Unnamed BLE device'} | {self.address} | {model} | {availability}{signal}"


class GoveeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a Govee H1167 box, without hard-coded addresses."""

    VERSION = 2

    def __init__(self) -> None:
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._pending_device: _DiscoveredDevice | None = None

    def _discovered_devices(self) -> dict[str, _DiscoveredDevice]:
        """Show all BLE advertisements, including scan-only and unnamed devices."""
        already_configured = {
            (entry.unique_id or entry.data.get(CONF_ADDRESS, "")).upper()
            for entry in self._async_current_entries()
        }
        connectable_addresses = {
            info.address.upper()
            for info in bluetooth.async_discovered_service_info(
                self.hass, connectable=True
            )
            if info.address
        }

        results: dict[str, _DiscoveredDevice] = {}
        for info in bluetooth.async_discovered_service_info(
            self.hass, connectable=False
        ):
            if not info.address:
                continue
            address = info.address.upper()
            if address in already_configured:
                continue
            name = (info.name or "").strip()
            rssi = getattr(info, "rssi", None)
            if isinstance(rssi, bool) or not isinstance(rssi, int):
                rssi = None
            results[address] = _DiscoveredDevice(
                address=address,
                name=name,
                connectable=address in connectable_addresses,
                h1167_name=is_h1167_name(name),
                rssi=rssi,
            )

        def priority(device: _DiscoveredDevice) -> tuple[int, int, str, str]:
            # Connectable first; within each group H1167, Govee, then others.
            model_priority = 0 if device.h1167_name else (
                1 if "govee" in device.name.lower() else 2
            )
            return (
                0 if device.connectable else 1,
                model_priority,
                device.name.lower(),
                device.address,
            )

        return dict(
            sorted(results.items(), key=lambda item: priority(item[1]))
        )

    async def _async_create_h1167(self, address: str, name: str):
        """Store the address from selection, not from bundled source code."""
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=name,
            data={
                CONF_ADDRESS: address,
                CONF_NAME: name,
                "model": "H1167",
                "segmented": False,
            },
        )

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        """Called by Home Assistant when a matching BLE advertisement is seen."""
        if not is_h1167_name(discovery_info.name or ""):
            return self.async_abort(reason="not_h1167")
        self._discovery_info = discovery_info
        await self.async_set_unique_id(discovery_info.address.upper())
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {
            "name": discovery_info.name,
            "address": discovery_info.address.upper(),
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        """Confirm automatic discovery; H1167 has no segmentation option."""
        info = self._discovery_info
        if info is None:
            return self.async_abort(reason="not_h1167")
        if user_input is not None:
            return await self._async_create_h1167(
                info.address.upper(), info.name or "Govee H1167"
            )
        return self.async_show_form(
            step_id="bluetooth_confirm", data_schema=vol.Schema({}),
            description_placeholders={
                "name": info.name or "Govee H1167",
                "address": info.address.upper(),
            },
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """List every currently seen BLE device in the setup dropdown."""
        if user_input is None:
            await bluetooth.async_request_active_scan(self.hass, duration=5)
        devices = self._discovered_devices()
        choices = {
            **{address: device.display_label for address, device in devices.items()},
            _REFRESH: "Scan again / refresh device list",
            _MANUAL: "Enter Bluetooth address manually",
        }
        errors: dict[str, str] = {}
        if user_input is not None:
            chosen = user_input[CONF_ADDRESS]
            if chosen == _MANUAL:
                return await self.async_step_manual()
            if chosen == _REFRESH:
                return await self.async_step_user()
            if chosen in devices:
                device = devices[chosen]
                if not device.connectable:
                    errors[CONF_ADDRESS] = "not_connectable"
                elif device.h1167_name:
                    return await self._async_create_h1167(
                        device.address, device.name
                    )
                else:
                    # Do not silently send H1167 commands to unrelated devices.
                    self._pending_device = device
                    return await self.async_step_confirm_device()
            else:
                errors[CONF_ADDRESS] = "device_not_found"

        count_connectable = sum(device.connectable for device in devices.values())
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(choices)}),
            errors=errors,
            description_placeholders={
                "count": str(len(devices)),
                "connectable_count": str(count_connectable),
                "scan_only_count": str(len(devices) - count_connectable),
            },
        )

    async def async_step_confirm_device(
        self, user_input: dict[str, Any] | None = None
    ):
        """Require explicit model confirmation for an unknown-name BLE device."""
        device = self._pending_device
        if device is None:
            return await self.async_step_user()
        schema = vol.Schema({
            vol.Required(_CONFIRM_H1167, default=False): bool,
        })
        placeholders = {
            "name": device.name or "Unnamed BLE device",
            "address": device.address,
        }
        if user_input is not None:
            if user_input.get(_CONFIRM_H1167) is True:
                return await self._async_create_h1167(
                    device.address,
                    device.name or f"Govee H1167 {device.address[-5:]}",
                )
            return self.async_show_form(
                step_id="confirm_device",
                data_schema=schema,
                errors={_CONFIRM_H1167: "confirmation_required"},
                description_placeholders=placeholders,
            )
        return self.async_show_form(
            step_id="confirm_device",
            data_schema=schema,
            description_placeholders=placeholders,
        )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None):
        """Fallback for devices that do not advertise their H1167 model name."""
        errors: dict[str, str] = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper().replace("-", ":")
            if not _MAC_REGEX.fullmatch(address):
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                name = (user_input.get(CONF_NAME) or "").strip()
                if not name:
                    name = f"Govee H1167 {address[-5:].replace(':', '')}"
                return await self._async_create_h1167(address, name)
        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): str,
                vol.Optional(CONF_NAME): str,
            }),
            errors=errors,
        )
