import json
import os
import pytest
from mock import Mock

from custom_components.lg_ess.switch import EssSwitch
from custom_components.lg_ess.sensors.util import _get_bool
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
async def test_settings_switches(data, mock_device_info):
    # prepare a minimal base object expected by EssSwitch
    base = Mock()
    settings_coordinator = Mock()
    settings_coordinator.data = data
    # provide an awaitable async_request_refresh used by the entities
    async def _async_request_refresh():
        return None
    settings_coordinator.async_request_refresh = _async_request_refresh

    base.settings_coordinator = settings_coordinator
    base.device_info = mock_device_info

    # ensure the ess client has an async set_batt_settings callable
    async def _set_batt_settings(payload):
        return None
    base.ess = Mock()
    base.ess.set_batt_settings = _set_batt_settings

    # determine root settings mapping (some files nest under "settings")
    root = settings_coordinator.data.get("settings", settings_coordinator.data) if isinstance(settings_coordinator.data, dict) else {}

    switches = []
    for key, val in root.items():
        if isinstance(val, bool):
            # set_key == key, default set_val used
            switches.append(EssSwitch(base, key, key))

    # validate entity state matches underlying data and exercise turn_on/turn_off
    for s in switches:
        expected = _get_bool(settings_coordinator.data, [s._key])
        assert s.is_on == expected
        # exercise toggles (should not raise)
        await s.async_turn_on()
        await s.async_turn_off()