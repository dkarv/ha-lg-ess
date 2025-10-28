"""Set up switch entities and keep them updated from the SettingsCoordinator."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .ess import EssBase
from .sensors.util import _get_bool

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
        # TODO startdate / stopdate
        # 1101
        # 0228

        EssSwitch(base, "winter_setting", "wintermode"),
        # TODO make boolean entity
        # EssSwitch(base, "winter_status"),
        EssSwitch(base, "backup_setting", "backupmode"),
        # TODO make boolean entity
        # EssSwitch(base, "backup_status"),

        # TODO Known values:
        # - battery_care / 1
        # EssSwitch(base, "alg_setting", "alg_setting"),

        # TODO Known values:
        # - 1
        # EssSwitch(base, "charging_from_grid_to_keep_soc"),

        # TODO Known values:
        # - '1101'
        # - '0228'
        # EssSwitch(base, "startdate"),
        # EssSwitch(base, "stopdate"),

        EssSwitch(base, "auto_charge", "autocharge", ["1", "0"]),

        # TODO known values:
        # - 'connected'
        # EssSwitch(base, "internet_connection"),

        # EssSwitch(base, "enervu_activated"),
        # EssSwitch(base, "enervu_upload"),
    ])

class EssSwitch(EssEntity, CoordinatorEntity[SettingsCoordinator], SwitchEntity):
    """Switch entity that reflects a setting from the SettingsCoordinator."""

    def __init__(self, ess: EssBase, key: str, set_key: str, set_val: list = ["on", "off"]):
        """Initialize the EssSwitch."""
        super().__init__(ess.settings_coordinator, ess.device_info, lambda d: _get_bool(d, [key]), key)
        self.entity_id = f"switch.${DOMAIN}_${key}"
        self._ess = ess
        self._key = key
        self._set_key = set_key
        self._set_val = set_val
        self._attr_is_on = self._extractor(self.coordinator.data)
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self._extractor(self.coordinator.data)
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        await self._ess.ess.set_batt_settings({self._set_key: self._set_val[0]})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._ess.ess.set_batt_settings({self._set_key: self._set_val[1]})
        await self.coordinator.async_request_refresh()
