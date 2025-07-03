"""Example integration using DataUpdateCoordinator."""

from datetime import date, datetime
import logging

from pyess.aio_ess import ESSAuthException

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity

from ..const import DOMAIN
from ..coordinator import ESSCoordinator

_LOGGER = logging.getLogger(__name__)

_WINTER = "mdi:snowflake"
_CHARGING = "mdi:battery-plus"
_DISCHARGING = "mdi:battery-minus"
_EV = "mdi:ev-station"
_BACKUP = "mdi:battery-lock"
_GRID = "mdi:transmission-tower"
_TOGRID = "mdi:transmission-tower-export"
_FROMGRID = "mdi:transmission-tower-import"
_ONE = "mdi:numeric-1-box"
_TWO = "mdi:numeric-2-box"
_THREE = "mdi:numeric-3-box"
_BATTERYSTATUS = "mdi:battery-check"
_BATTERYHALF = "mdi:battery-50"
_BATTERYHOME = "mdi:home-battery"
_BATTERYLOAD = "mdi:battery-charging"
_PV = "mdi:solar-power"
_CO2 = "mdi:molecule-co2"
_LOAD = "mdi:home-lightning-bolt"
_HEATPUMP = "mdi:heat-pump"

class EssEntity(CoordinatorEntity[ESSCoordinator], Entity):
    """Basic entity with common functionality."""

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        extractor,
        key: str,
        icon: str | None = None,
        unit: str | None = None,
    ) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._extractor = extractor
        self._attr_translation_key = key
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{device_info["serial_number"]}_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

class EssSensor(EssEntity, CoordinatorEntity[ESSCoordinator], SensorEntity):
    """Basic sensor with common functionality."""

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        extractor,
        key: str,
        icon: str | None = None,
        unit: str | None = None,
    ) -> None:
        """Initialize the sensor with the common coordinator."""
        EssEntity.__init__(self, coordinator, device_info, extractor, key, icon=icon, unit=unit)
        self.entity_id = f"sensor.{DOMAIN}_{key}"
        self._attr_native_value = self._extractor(self.coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_value = self._extractor(self.coordinator.data)
        _LOGGER.debug("%s : %s", self._attr_translation_key, new_value)
        self._attr_native_value = new_value
        self.async_write_ha_state()


def _convert_bool(val) -> bool:
    return (val == "on") | (val == "true") | (val == "1")


class BinarySensor(EssEntity, CoordinatorEntity[ESSCoordinator], BinarySensorEntity):
    """Binary sensor."""

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        extractor,
        key: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor with the coordinator."""
        EssEntity.__init__(self, coordinator, device_info, extractor, key, icon=icon)
        self.entity_id = f"binary_sensor.{DOMAIN}_{key}"
        self.is_on = _convert_bool(extractor(coordinator.data))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self._extractor(self.coordinator.data)
        _LOGGER.debug("%s : %s", self._attr_translation_key, val)
        self.is_on = _convert_bool(val)
        self.async_write_ha_state()


class MeasurementSensor(EssSensor):
    """Measurement sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        extractor,
        key: str,
        unit: str | None = None,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator, device_info, extractor, key, icon=icon, unit=unit)


class IncreasingSensor(EssSensor):
    """Increasing total sensor."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        extractor,
        key: str,
        unit=UnitOfEnergy.WATT_HOUR,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor with the coordinator."""
        super().__init__(coordinator, device_info, extractor, key, icon=icon, unit=unit)


class IncreasingEnergySensor(IncreasingSensor):
    """Increasing energy Wh sensor."""

    def __init__(
        self,
        coordinator,
        device_info: DeviceInfo,
        extractor,
        key: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the energy sensor with the coordinator."""
        super().__init__(
            coordinator, device_info, extractor, key, UnitOfEnergy.WATT_HOUR, icon=icon
        )
        self._attr_suggested_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
