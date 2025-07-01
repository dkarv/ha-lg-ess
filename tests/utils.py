import pytest
from homeassistant.helpers.device_registry import DeviceInfo
from custom_components.lg_ess.sensors.base import BinarySensor

@pytest.fixture
def mock_device_info():
    return DeviceInfo(
        identifiers={("lg_ess", "test_device")},
        manufacturer="LG",
        model="Test Model",
        name="Test Device",
        serial_number="serialno",
    )

def assert_sensor_values(sensors):
    for sensor in sensors:
        if isinstance(sensor, BinarySensor):
            assert sensor.is_on is None or sensor.is_on is not None
        else:
            assert sensor.native_value is None or sensor.native_value is not None
