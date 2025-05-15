"""Example integration using DataUpdateCoordinator."""

import logging

from pyess.aio_ess import ESSAuthException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.common import get_common_sensors
from .sensors.home import get_home_sensors
from .sensors.system import get_system_sensors

from .const import DOMAIN
from .coordinator import (
    CommonCoordinator,
    HomeCoordinator,
    SystemInfoCoordinator,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    ess = hass.data[DOMAIN][config_entry.entry_id]
    common_coordinator = CommonCoordinator(hass, ess)
    system_coordinator = SystemInfoCoordinator(hass, ess)
    home_coordinator = HomeCoordinator(hass, ess)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    try:
        await common_coordinator.async_config_entry_first_refresh()
        await system_coordinator.async_config_entry_first_refresh()
        await home_coordinator.async_config_entry_first_refresh()
    except ESSAuthException as e:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        raise ConfigEntryAuthFailed from e

    device_info = DeviceInfo(
        configuration_url=None,
        connections=set(),
        entry_type=None,
        hw_version=None,
        identifiers={(DOMAIN, config_entry.entry_id)},
        manufacturer="LG",
        model=system_coordinator.data["pms"]["model"],
        name=config_entry.title,
        serial_number=system_coordinator.data["pms"]["serialno"],
        suggested_area=None,
        sw_version=system_coordinator.data["version"]["pcs_version"],
        via_device=None,
    )

    async_add_entities(
        get_home_sensors(home_coordinator, device_info)
        + get_common_sensors(common_coordinator, device_info)
        + get_system_sensors(system_coordinator, device_info)
    )
