import json
import os
import pytest
from mock import Mock

from custom_components.lg_ess.number import EssNumber
from custom_components.lg_ess.sensors.util import _get_int
from .utils import mock_device_info

base_path = "raw_data/settings"


def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        metafunc.parametrize("data", os.listdir(base_path), indirect=True)


@pytest.fixture
def data(request):
    with open(os.path.join(base_path, request.param)) as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_settings_numbers(data, mock_device_info):
    # prepare a minimal base object expected by EssNumber
    base = Mock()
    settings_coordinator = Mock()
    settings_coordinator.data = data
    async def _async_request_refresh():
        return None
    settings_coordinator.async_request_refresh = _async_request_refresh

    base.settings_coordinator = settings_coordinator
    base.device_info = mock_device_info

    # ensure the ess client has an async set_batt_settings callable used by async_set_native_value
    async def _set_batt_settings(payload):
        return None
    base.ess = Mock()
    base.ess.set_batt_settings = _set_batt_settings

    # determine root settings mapping (some files nest under "settings")
    root = settings_coordinator.data.get("settings", settings_coordinator.data) if isinstance(settings_coordinator.data, dict) else {}

    numbers = []
    for key, val in root.items():
        # consider integer-like entries for Number entities
        if isinstance(val, int):
            numbers.append(EssNumber(base, key))

    # validate entity values and exercise setting a new value
    for n in numbers:
        expected = _get_int(settings_coordinator.data, [n._key])
        # NumberEntity exposes native_value
        assert n.native_value == expected
        # exercise setting a new value (should not raise)
        await n.async_set_native_value(expected + 1)
