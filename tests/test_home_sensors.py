import json
import pytest
import os
from mock import patch, Mock
from homeassistant.const import UnitOfPower, PERCENTAGE
from custom_components.lg_ess.sensors.home import get_home_sensors
from custom_components.lg_ess.coordinator import HomeCoordinator
from custom_components.lg_ess.sensors.base import BinarySensor
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorEntity
from .utils import assert_sensor_values, mock_device_info, list_files


def mock_coordinator(data):
    hass = Mock()
    # no_ldap.return_value = Mock(search_s=search_s)

    class MockHomeCoordinator(HomeCoordinator):
        def __init__(self, hass, data):
            super().__init__(hass, None)
            self.data = data

    return MockHomeCoordinator(hass, data)


base_path = "raw_data/home"


def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        metafunc.parametrize("data", os.listdir(base_path), indirect=True)


@pytest.fixture
def data(request):
    with open(os.path.join(base_path, request.param)) as file:
        return json.load(file)


def test_home_sensors(data, mock_device_info):
    coordinator = mock_coordinator(data)
    sensors = get_home_sensors(coordinator, mock_device_info)
    assert_sensor_values(sensors)
