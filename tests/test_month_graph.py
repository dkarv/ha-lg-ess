import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from mock import Mock, patch

from custom_components.lg_ess.coordinator import CommonCoordinator, dst_shift_this_month, fetch_month_graph
from custom_components.lg_ess.sensors.common import get_common_sensors
from .utils import mock_device_info

base_path = "raw_data/graph"


def _load(name):
    with open(os.path.join(base_path, name)) as file:
        return json.load(file)


class FakeEss:
    """Answers graph requests like the device: "no data" for months it has no rows for."""

    def __init__(self, *months: str):
        self.months = months
        self.requests = []

    async def get_common(self):
        with open("raw_data/common/D010KE1N211.json") as file:
            return json.load(file)

    async def get_graph(self, device, timespan, day):
        assert timespan == "month"
        month = day.strftime("%Y%m")
        self.requests.append((device, month))
        if month in self.months:
            return _load(f"{device}_month_202610.json")
        return _load("no_data.json")


@pytest.mark.asyncio
async def test_current_month():
    ess = FakeEss("202610")
    graph = await fetch_month_graph(ess, datetime(2026, 10, 25, 12))
    assert graph["pv"]["total_generation"] == "568909"
    assert graph["load"]["total_consumption"] == "372408"
    assert graph["batt"]["total_charge"] == "215098"
    assert ess.requests == [("pv", "202611"), ("pv", "202610"), ("load", "202610"), ("batt", "202610")]


@pytest.mark.asyncio
async def test_device_behind_ha():
    # HA is already in November, the device is still in October: fall back to the counters
    assert await fetch_month_graph(FakeEss("202610"), datetime(2026, 11, 1, 0, 2)) is None


@pytest.mark.asyncio
async def test_device_ahead_of_ha():
    # HA is still in October, the device is in November already
    ess = FakeEss("202610", "202611")
    assert await fetch_month_graph(ess, datetime(2026, 10, 31, 23, 58)) is not None
    assert ess.requests == [("pv", "202611"), ("load", "202611"), ("batt", "202611")]


@pytest.mark.asyncio
async def test_year_boundary():
    ess = FakeEss()
    assert await fetch_month_graph(ess, datetime(2026, 12, 31, 12)) is None
    assert ess.requests == [("pv", "202701"), ("pv", "202612")]


BERLIN = ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize("now, expected", [
    (datetime(2026, 10, 25, 2, 30, tzinfo=BERLIN), False),  # still CEST, first 02:30
    (datetime(2026, 10, 25, 4, 0, tzinfo=BERLIN), True),
    (datetime(2026, 10, 31, 23, 59, tzinfo=BERLIN), True),
    (datetime(2026, 11, 1, 0, 1, tzinfo=BERLIN), False),
    (datetime(2026, 3, 29, 1, 59, tzinfo=BERLIN), False),
    (datetime(2026, 3, 29, 3, 0, tzinfo=BERLIN), True),
    (datetime(2026, 7, 15, 12, 0, tzinfo=BERLIN), False),
    (datetime(2026, 10, 25, 12, 0, tzinfo=ZoneInfo("UTC")), False),
])
def test_dst_shift_this_month(now, expected):
    assert dst_shift_this_month(now) == expected


@pytest.mark.parametrize("now, expected_requests", [
    (datetime(2026, 10, 25, 12, 0, tzinfo=BERLIN), 4),
    (datetime(2026, 10, 20, 12, 0, tzinfo=BERLIN), 0),
])
@pytest.mark.asyncio
async def test_coordinator_only_fetches_graph_after_dst_shift(now, expected_requests):
    ess = FakeEss("202610")
    coordinator = CommonCoordinator(Mock(), ess, Mock())
    with patch("custom_components.lg_ess.coordinator.dt_util.now", return_value=now):
        data = await coordinator._async_update_data()
    assert len(ess.requests) == expected_requests
    assert (data["GRAPH"] is not None) == (expected_requests > 0)


def _month_sensor_values(data, device_info):
    class MockCommonCoordinator(CommonCoordinator):
        def __init__(self):
            super().__init__(Mock(), None, Mock())
            self.data = data

    sensors = get_common_sensors(MockCommonCoordinator(), device_info)
    return {s._attr_translation_key: s.native_value for s in sensors if "month" in s._attr_translation_key}


@pytest.mark.asyncio
async def test_month_sensors_prefer_graph(mock_device_info):
    with open("raw_data/common/D010KE1N211.json") as file:
        data = json.load(file)
    data["GRAPH"] = await fetch_month_graph(FakeEss("202610"), datetime(2026, 10, 25, 12))
    values = _month_sensor_values(data, mock_device_info)
    assert values["pcs_month_pv_generation_sum"] == 568909
    assert values["pcs_month_grid_feed_in_energy"] == 231697
    assert values["load_month_pv_direct_consumption_energy"] == 122114
    assert values["load_month_load_consumption_sum"] == 372408
    assert values["load_month_grid_power_purchase_energy"] == 53064
    assert values["batt_month_batt_charge_energy"] == 215098
    assert values["batt_month_batt_discharge_energy"] == 197230
    # no graph equivalent
    assert values["pcs_month_co2_reduction_accum"] == "12402"


def test_month_sensors_fall_back_to_common(mock_device_info):
    with open("raw_data/common/D010KE1N211.json") as file:
        data = json.load(file)
    data["GRAPH"] = None
    values = _month_sensor_values(data, mock_device_info)
    assert values["pcs_month_pv_generation_sum"] == "17469"
    assert values["batt_month_batt_charge_energy"] == "9616"
