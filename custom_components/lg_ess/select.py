"""Set up switch entities and keep them updated from the SettingsCoordinator."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from typing import Optional, Mapping

from .ess import EssBase
from .sensors.util import _get

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
        EssSelect(base, "backup_setting", "backupmode", ["on", "simple", "off"]),



        # battery_care
        EssSelect(base, "alg_setting", "alg_setting", ["battery_care", "fast_charge", "weather_forecast"], {"battery_care": "0", "fast_charge": "1", "weather_forecast": "2"}),
    ])

class EssSelect(EssEntity, CoordinatorEntity[SettingsCoordinator], SelectEntity):
    """Select entity that reflects a setting from the SettingsCoordinator."""

    def __init__(self, ess: EssBase, key: str, set_key: str, get_val: list[str], set_val: Optional[Mapping[str, str]] = None):
        """Initialize the EssSelect."""
        super().__init__(ess.settings_coordinator, ess.device_info, lambda d: _get(d, [key]), key)
        self._ess = ess
        self._key = key
        self._set_key = set_key
        self._get_val = get_val
        self._set_val = set_val if set_val is not None else {v: v for v in get_val}
        self._attr_options = get_val
        self._attr_current_option = self._extractor(self.coordinator.data)
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_current_option = self._extractor(self.coordinator.data)
        self.async_write_ha_state()
    
    async def async_select_option(self, option: str) -> None:
        dto = {self._set_key: self._set_val[option]}
        _LOGGER.info("set_batt_settings %s", dto)
        await self._ess.ess.set_batt_settings(dto)
        await self.coordinator.async_request_refresh()
