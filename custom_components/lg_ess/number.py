"""Set up switch entities and keep them updated from the SettingsCoordinator."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .ess import EssBase
from .sensors.util import _get_int

from .sensors.base import EssEntity

from .const import DOMAIN
from .coordinator import SettingsCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities from config entry and keep them synced via SettingsCoordinator."""
    base = hass.data[DOMAIN][config_entry.entry_id]
    await base.first_refresh()

    async_add_entities([
        EssNumber(base, "safety_soc"),
        EssNumber(base, "backup_soc"),
    ])


class EssNumber(EssEntity, CoordinatorEntity[SettingsCoordinator], NumberEntity):
    """Number entity that reflects a setting from the SettingsCoordinator."""

    def __init__(self, ess: EssBase, key: str):
        """Initialize the EssNumber."""
        super().__init__(ess.settings_coordinator, ess.device_info, lambda d: _get_int(d, [key]), key)
        self.entity_id = f"number.${DOMAIN}_${key}"
        self._ess = ess
        self._key = key
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_value = self._extractor(self.coordinator.data)
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_value = self._extractor(self.coordinator.data)
        self.async_write_ha_state()
    
    async def async_set_native_value(self, value: float) -> None:
        await self._ess.ess.set_batt_settings({self._key: int(value)})
