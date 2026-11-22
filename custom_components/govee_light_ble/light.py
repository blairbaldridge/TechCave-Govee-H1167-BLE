"""Home Assistant light entity for Govee BLE / H1167."""

from __future__ import annotations

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GoveeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GoveeCoordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities([GoveeBluetoothLight(coordinator)])


class GoveeBluetoothLight(CoordinatorEntity[GoveeCoordinator], LightEntity):
    """Preserves old MAC-based unique ID to avoid breaking automations."""

    def __init__(self, coordinator: GoveeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = coordinator.device_name
        self._attr_unique_id = coordinator.device_address
        self._attr_device_info = DeviceInfo(
            manufacturer="GOVEE",
            model=coordinator.device_name,
            serial_number=coordinator.device_address,
            identifiers={(DOMAIN, coordinator.device_address)},
        )
        if coordinator.power_only:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF
        else:
            self._attr_supported_color_modes = {ColorMode.RGB}
            self._attr_color_mode = ColorMode.RGB

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.state

    @property
    def brightness(self) -> int | None:
        if self.coordinator.power_only:
            return None
        return self.coordinator.data.brightness

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        if self.coordinator.power_only:
            return None
        return self.coordinator.data.color

    async def async_turn_on(self, **kwargs) -> None:
        if self.coordinator.power_only:
            await self.coordinator.async_set_light(True)
        else:
            await self.coordinator.async_set_light(
                True,
                brightness=kwargs.get(ATTR_BRIGHTNESS),
                rgb=kwargs.get(ATTR_RGB_COLOR),
            )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_light(False)
