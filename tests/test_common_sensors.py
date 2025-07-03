import json
import pytest
import os
from mock import patch, Mock
from homeassistant.const import UnitOfPower, PERCENTAGE
from custom_components.lg_ess.sensors.common import get_common_sensors
from custom_components.lg_ess.coordinator import CommonCoordinator
from custom_components.lg_ess.sensors.base import BinarySensor
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorEntity
from .utils import assert_sensor_values, mock_device_info, list_files


def mock_coordinator(data):
    hass = Mock()

    class MockCommonCoordinator(CommonCoordinator):
        def __init__(self, hass, data):
            super().__init__(hass, None)
            self.data = data

    return MockCommonCoordinator(hass, data)


base_path = "raw_data/common"


def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        metafunc.parametrize("data", os.listdir(base_path), indirect=True)


@pytest.fixture
def data(request):
    with open(os.path.join(base_path, request.param)) as file:
        return json.load(file)


def test_common_sensors(data, mock_device_info):
    coordinator = mock_coordinator(data)
    sensors = get_common_sensors(coordinator, mock_device_info)
    assert_sensor_values(sensors)
