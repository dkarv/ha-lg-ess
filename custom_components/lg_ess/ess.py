"""ESS base."""

from .const import DOMAIN
from pyess.aio_ess import ESS
from .coordinator import HomeCoordinator, SystemInfoCoordinator, CommonCoordinator, SettingsCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.config_entries import ConfigEntry

import logging
_LOGGER = logging.getLogger(__name__)

class EssBase:
    ess: ESS
    entry: ConfigEntry
    home_coordinator: HomeCoordinator
    system_coordinator: SystemInfoCoordinator
    common_coordinator: CommonCoordinator
    settings_coordinator: SettingsCoordinator
    device_info: DeviceInfo

    def __init__(self, hass: HomeAssistant, ess: ESS, entry: ConfigEntry) -> None:
        self.entry = entry
        self.ess = ess
        self.home_coordinator = HomeCoordinator(hass, ess, entry)
        self.system_coordinator = SystemInfoCoordinator(hass, ess, entry)
        self.common_coordinator = CommonCoordinator(hass, ess, entry)
        self.settings_coordinator = SettingsCoordinator(hass, ess, entry)

    async def close(self) -> None:
        """Close the API connection."""
        await self.ess.destruct()

    async def first_refresh(self) -> None:
        if self.common_coordinator.data is None:
            await self.common_coordinator.async_config_entry_first_refresh()
        if self.system_coordinator.data is None:
            await self.system_coordinator.async_config_entry_first_refresh()
        if self.home_coordinator.data is None:
            await self.home_coordinator.async_config_entry_first_refresh()
        if self.settings_coordinator.data is None:
            await self.settings_coordinator.async_config_entry_first_refresh()
        
        self.device_info = DeviceInfo(
            configuration_url=None,
            connections=set(),
            entry_type=None,
            hw_version=None,
            identifiers={(DOMAIN, self.entry.entry_id)},
            manufacturer="LG",
            model=self.system_coordinator.data["pms"]["model"],
            name=self.entry.title,
            serial_number=self.system_coordinator.data["pms"]["serialno"],
            suggested_area=None,
            sw_version=self.system_coordinator.data["version"]["pcs_version"],
            via_device=None,
        )
