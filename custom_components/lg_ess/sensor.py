"""Example integration using DataUpdateCoordinator."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.common import get_common_sensors
from .sensors.home import get_home_sensors
from .sensors.system import get_system_sensors

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    base = hass.data[DOMAIN][config_entry.entry_id]
    await base.first_refresh()
    async_add_entities(
        get_home_sensors(base.home_coordinator, base.device_info)
        + get_common_sensors(base.common_coordinator, base.device_info)
        + get_system_sensors(base.system_coordinator, base.device_info)
    )
