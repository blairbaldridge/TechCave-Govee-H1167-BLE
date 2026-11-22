"""Govee H1167 setup: discover via Home Assistant Bluetooth or enter address."""

from __future__ import annotations

import re
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


class GoveeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a Govee H1167 box, without hard-coded addresses."""

    VERSION = 2

    def __init__(self) -> None:
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    def _discovered_devices(self) -> dict[str, str]:
        """Return nearby *connectable* H1167 advertisements as selector options."""
        already_configured = {
            (entry.unique_id or entry.data.get(CONF_ADDRESS, "")).upper()
            for entry in self._async_current_entries()
        }
        result = {}
        for info in bluetooth.async_discovered_service_info(
            self.hass, connectable=True
        ):
            name = info.name or ""
            address = info.address.upper()
            if not is_h1167_name(name) or address in already_configured:
                continue
            result[address] = f"{name} ({address})"
        return dict(sorted(result.items(), key=lambda item: item[1].lower()))

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
        """List nearby H1167 devices after installation from HACS."""
        if user_input is None:
            await bluetooth.async_request_active_scan(self.hass, duration=5)
        devices = self._discovered_devices()
        choices = {
            **devices,
            _REFRESH: "Scan again / refresh device list",
            _MANUAL: "Enter Bluetooth address manually",
        }
        errors = {}
        if user_input is not None:
            chosen = user_input[CONF_ADDRESS]
            if chosen == _MANUAL:
                return await self.async_step_manual()
            if chosen == _REFRESH:
                return await self.async_step_user()
            if chosen in devices:
                name = devices[chosen].rsplit(" (", 1)[0]
                return await self._async_create_h1167(chosen, name)
            errors[CONF_ADDRESS] = "device_not_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(choices)}),
            errors=errors,
            description_placeholders={"count": str(len(devices))},
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
