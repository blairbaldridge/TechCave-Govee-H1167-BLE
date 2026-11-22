"""Drop-in replacement for govee_light_ble, retaining existing entries."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import GoveeCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.LIGHT, Platform.SELECT]


@dataclass
class RuntimeData:
    coordinator: GoveeCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load existing H1167 config entry without re-pairing/reconfiguration."""
    address = entry.data[CONF_ADDRESS]
    if not bluetooth.async_ble_device_from_address(hass, address, connectable=True):
        raise ConfigEntryNotReady(
            f"Cannot reach Govee BLE {address} with a connectable Bluetooth adapter"
        )

    coordinator = GoveeCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = RuntimeData(coordinator)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        await coordinator.async_close()
        raise
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        data: RuntimeData | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if data is not None:
            await data.coordinator.async_close()
    return unloaded


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate version 1 data if an older entry is still installed."""
    if entry.version == 1:
        address = (entry.unique_id or entry.data.get(CONF_ADDRESS, "")).upper()
        if not address:
            return False
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_ADDRESS: address,
                CONF_NAME: entry.data.get(CONF_NAME, entry.title),
                "segmented": entry.data.get("segmented", True),
            },
            version=2,
        )
    return entry.version == 2
