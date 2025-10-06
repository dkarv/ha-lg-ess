"""Coordinator to fetch the data once for all sensors."""

from datetime import timedelta
import logging

from pyess.aio_ess import ESS

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)


class ESSCoordinator(DataUpdateCoordinator):
    """LG ESS basic coordinator."""

    _ess: ESS

    def __init__(
        self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry, name: str, interval: timedelta
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=name,
            update_interval=interval,
        )
        self._ess = ess


class CommonCoordinator(ESSCoordinator):
    """LG ESS common coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS common",
            interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        data = await self._ess.get_common()
        _LOGGER.debug("Common data: %s", data)
        return data


class SystemInfoCoordinator(ESSCoordinator):
    """LG ESS system info coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS system info",
            interval=timedelta(minutes=10),
        )

    async def _async_update_data(self):
        data = await self._ess.get_systeminfo()
        _LOGGER.debug("System info data: %s", data)
        return data


class HomeCoordinator(ESSCoordinator):
    """LG ESS system info coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS home",
            interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        data = await self._ess.get_home()
        _LOGGER.debug("Home data: %s", data)
        return data
