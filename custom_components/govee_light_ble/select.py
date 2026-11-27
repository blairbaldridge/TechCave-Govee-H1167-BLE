"""Home Assistant mode dropdown for the Govee H1167 Light Show Box."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GoveeCoordinator
from .h1167_modes import H1167_LEGACY_MODE_NAMES, H1167_MODE_OPTIONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add the mode dropdown only to Govee H1167 boxes."""
    coordinator: GoveeCoordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    if coordinator.power_only:
        async_add_entities([GoveeH1167ModeSelect(coordinator)])


class GoveeH1167ModeSelect(CoordinatorEntity[GoveeCoordinator], SelectEntity, RestoreEntity):
    """Choose among the recorded H1167 modes.

    The H1167's mode readback is not decoded yet. The selected option is the
    last one sent by Home Assistant, not a verified live mode reported by BLE.
    """

    _attr_has_entity_name = True
    _attr_name = "Show Mode"
    _attr_icon = "mdi:animation-play"
    _attr_options = H1167_MODE_OPTIONS

    def __init__(self, coordinator: GoveeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_address}_h1167_mode"
        self._attr_current_option: str | None = None
        self._attr_device_info = DeviceInfo(
            manufacturer="GOVEE",
            model=coordinator.device_name,
            serial_number=coordinator.device_address,
            identifiers={(DOMAIN, coordinator.device_address)},
        )

    async def async_added_to_hass(self) -> None:
        """Restore the last HA-selected mode without issuing BLE writes."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            # Existing installations may have an old numbered mode saved.
            restored_option = H1167_LEGACY_MODE_NAMES.get(
                last_state.state, last_state.state
            )
            if restored_option in H1167_MODE_OPTIONS:
                self._attr_current_option = restored_option
                self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Send the recorded mode packet and then update dropdown state."""
        await self.coordinator.async_set_h1167_mode(option)
        self._attr_current_option = option
        self.async_write_ha_state()
