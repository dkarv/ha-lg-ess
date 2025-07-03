import pytest
import json
import os
from datetime import date
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
            print(
                f"Checking binary sensor {sensor._attr_translation_key} value: {sensor.is_on}")
            assert (
                sensor.is_on is None or
                sensor.is_on == True or
                sensor.is_on == False
            )
        else:
            print(
                f"Checking sensor {sensor._attr_translation_key} value: {sensor.native_value}")
            assert (
                sensor.native_value is None or
                isinstance(sensor.native_value, str) or
                isinstance(sensor.native_value, int) or
                isinstance(sensor.native_value, date)
            )


def list_files(directory: str):
    base_path = os.path.join("raw_data", directory)
    input = []
    for f in os.listdir(base_path):
        with open(os.path.join(base_path, f)) as file:
            input.append({'file': f, 'data': json.load(file)})
    return input
