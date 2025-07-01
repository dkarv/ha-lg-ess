import json
import pytest
from mock import patch, Mock
from homeassistant.const import UnitOfPower, PERCENTAGE
from custom_components.lg_ess.sensors.common import get_common_sensors
from custom_components.lg_ess.coordinator import CommonCoordinator
from custom_components.lg_ess.sensors.base import BinarySensor
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorEntity
from .utils import assert_sensor_values, mock_device_info

@pytest.fixture
def input_data_1():
    with open("raw_data/common/v1.json") as f:
        return json.load(f)

@pytest.fixture
def input_data_2():
    with open("raw_data/common/v2.json") as f:
        return json.load(f)

def mock_common_coordinator(data):
    hass = Mock()
    # no_ldap.return_value = Mock(search_s=search_s)
    class MockCommonCoordinator(CommonCoordinator):
        def __init__(self, hass, data):
            super().__init__(hass, None)
            self.data = data

    return MockCommonCoordinator(hass, data)

def test_common_sensors_v1(input_data_1, mock_device_info):
    # Test with input_data_1
    coordinator_1 = mock_common_coordinator(input_data_1)
    sensors_1 = get_common_sensors(coordinator_1, mock_device_info)

    assert_sensor_values(sensors_1)

def test_common_sensors_v2(input_data_2, mock_device_info):
    # Test with input_data_2
    coordinator_2 = mock_common_coordinator(input_data_2)
    sensors_2 = get_common_sensors(coordinator_2, mock_device_info)

    assert_sensor_values(sensors_2)
