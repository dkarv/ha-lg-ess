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
from .coordinator import SettingsCoordinator, ESSCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities from config entry and keep them synced via SettingsCoordinator."""
    base: EssBase = hass.data[DOMAIN][config_entry.entry_id]
    await base.first_refresh()

    async_add_entities([
        EssSwitch(base, base.settings_coordinator, "winter_setting", 
                  lambda d: _get_bool(d, ["winter_setting"]), 
                  lambda ess, s: _set_bool(ess, s, "wintermode")),
        EssSwitch(base, base.settings_coordinator, "auto_charge", 
                  lambda d: _get_bool(d, ["auto_charge"]), 
                  lambda ess, s: _set_bool(ess, s, "autocharge", ["1", "0"])),

        EssSwitch(base, base.home_coordinator, "operation", 
                  lambda d: _get_bool(d, ["operation", "status"]),
                  _switch_operation),

        # TODO make DateEntity
        # Known values:
        # - '1101'
        # - '0228'
        # EssSwitch(base, "startdate"),
        # EssSwitch(base, "stopdate"),


        # TODO known values:
        # - 'connected'
        # EssSwitch(base, "internet_connection"),

        # EssSwitch(base, "enervu_activated"),
        # EssSwitch(base, "enervu_upload"),
    ])

class EssSwitch(EssEntity, CoordinatorEntity[ESSCoordinator], SwitchEntity):
    """Switch entity that reflects a setting from the ESSCoordinator."""

    def __init__(self, ess: EssBase, coordinator: ESSCoordinator, key: str, extractor, setter):
        """Initialize the EssSwitch."""
        super().__init__(coordinator, ess.device_info, extractor, key)
        self._setter = setter
        self._ess = ess
        self._key = key
        self._attr_is_on = self._extractor(self.coordinator.data)
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self._extractor(self.coordinator.data)
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        await self._setter(self._ess, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._setter(self._ess, False)
        await self.coordinator.async_request_refresh()

async def _set_bool(ess: EssBase, value: bool, key: str, set_val: list = ["on", "off"]):
    dto = {key: set_val[1] if value else set_val[0]}
    _LOGGER.info("set_batt_settings %s", dto)
    await ess.ess.set_batt_settings(dto)

async def _switch_operation(ess: EssBase, value: bool):
    _LOGGER.info("Switching system operation to %s", "ON" if value else "OFF")
    if value:
        await ess.ess.switch_on()
    else:
        await ess.ess.switch_off()
