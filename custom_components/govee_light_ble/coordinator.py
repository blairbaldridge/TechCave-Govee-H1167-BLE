"""Coordinator for H1167 / Govee Bluetooth device state."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GoveeAPI
from .const import DOMAIN
from .h1167_modes import H1167_MODE_FRAMES

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class GoveeApiData:
    state: bool | None = None
    brightness: int | None = None
    color: tuple[int, int, int] | None = None


class GoveeCoordinator(DataUpdateCoordinator[GoveeApiData]):
    """Track state with BLE notification updates and periodic readback."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.device_name: str = entry.data[CONF_NAME]
        self.device_address: str = entry.data[CONF_ADDRESS].upper()
        self.device_segmented: bool = entry.data.get("segmented", False)
        stored_model = entry.data.get("model")
        self.power_only: bool = (
            stored_model == "H1167"
            if stored_model is not None
            else "H1167" in self.device_name.upper()
        )
        self._api = GoveeAPI(
            hass,
            self.device_address,
            self._async_push_data,
            segmented=self.device_segmented,
            write_only=self.power_only,
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({self.device_address})",
            config_entry=entry,
            update_interval=timedelta(seconds=45),
        )

    def _snapshot(self) -> GoveeApiData:
        return GoveeApiData(
            state=self._api.state,
            brightness=self._api.brightness,
            color=self._api.color,
        )

    @callback
    def _async_push_data(self) -> None:
        self.async_set_updated_data(self._snapshot())

    async def _async_update_data(self) -> GoveeApiData:
        try:
            await self._api.request_state(power_only=self.power_only)
        except Exception as err:
            raise UpdateFailed(
                f"Unable to read Govee BLE {self.device_address}: {err}"
            ) from err
        return self._snapshot()

    async def async_set_light(
        self,
        on: bool,
        *,
        brightness: int | None = None,
        rgb: tuple[int, int, int] | None = None,
    ) -> None:
        try:
            await self._api.set_light(on, brightness=brightness, rgb=rgb)
        except Exception as err:
            raise HomeAssistantError(
                f"Unable to control Govee BLE {self.device_address}: {err}"
            ) from err

    async def async_set_h1167_mode(self, option: str) -> None:
        """Send the exact captured H1167 scene packet."""
        if not self.power_only:
            raise HomeAssistantError("Mode selection is supported only for H1167")
        frame = H1167_MODE_FRAMES.get(option)
        if frame is None:
            raise HomeAssistantError(f"Unknown H1167 mode: {option}")
        try:
            await self._api.set_h1167_mode(frame)
        except Exception as err:
            raise HomeAssistantError(
                f"Unable to select {option} on Govee BLE {self.device_address}: {err}"
            ) from err

    async def async_close(self) -> None:
        await self._api.async_close()
