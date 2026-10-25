"""Repair long term statistics of the month sensors after a daylight saving time shift.

Before version 0.5.2 the month sensors used the month_* counters of the device, which the device resets on daylight
saving time changes. HA recorded that as a new cycle of the total_increasing sensors. Version 0.5.2 switched to the
month graph, which has the correct month totals: the jump from the reset counter back to the month total was counted
as consumption a second time. This finds such a jump and subtracts the double counted energy from the statistics.
"""

from datetime import datetime, timedelta
import logging

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import statistics_during_period
from homeassistant.const import Platform, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# The month sensors that read the month graph after a daylight saving time shift
MONTH_GRAPH_SENSORS = [
    "BATT_month_batt_discharge_energy",
    "BATT_month_batt_charge_energy",
    "LOAD_month_load_consumption_sum",
    "LOAD_month_pv_direct_consumption_energy",
    "LOAD_month_grid_power_purchase_energy",
    "PCS_month_pv_generation_sum",
    "PCS_month_grid_feed_in_energy",
]


def dst_shift_in_month(month_start: datetime) -> datetime | None:
    """Return the first full hour after the UTC offset of the time zone changed within the month, if it did."""
    offset = month_start.utcoffset()
    utc = month_start.astimezone(dt_util.UTC)
    hour = timedelta(hours=1)
    while (local := (utc := utc + hour).astimezone(month_start.tzinfo)).month == month_start.month:
        if local.utcoffset() != offset:
            return utc
    return None


def find_double_counted(rows: list[dict]) -> tuple[float, float] | None:
    """Find the double counted energy in hourly statistics rows of a month sensor.

    The rows span from before the daylight saving time shift to the end of that month at most. The first and last
    row must hold the correct month total: the month total can only grow, so the energy really consumed in between
    is the difference of their states. Anything the sum grew more was counted twice. The energy is only considered
    double counted if a single hour grew by more than half the month total from before the shift, which no real
    consumption does.

    Returns the start of the hour the sum jumped and the (negative) adjustment, or None if there is nothing to repair.
    """
    if len(rows) < 2 or any(row.get("state") is None or row.get("sum") is None for row in rows):
        return None
    first, last = rows[0], rows[-1]
    if first["state"] <= 0 or last["state"] < first["state"]:
        # The month total has not been restored yet, the sensor still shows the reset counter
        return None
    jump, jump_start = max((cur["sum"] - prev["sum"], cur["start"]) for prev, cur in zip(rows, rows[1:]))
    adjustment = (last["state"] - first["state"]) - (last["sum"] - first["sum"])
    threshold = first["state"] / 2
    if jump <= threshold or adjustment >= -threshold:
        return None
    return jump_start, adjustment


async def async_repair_statistics(hass: HomeAssistant, serial: str) -> None:
    """Remove energy counted twice after the last daylight saving time shift from the month sensors."""
    if "recorder" not in hass.config.components:
        return
    now = dt_util.now()
    this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    for month_start in (this_month, last_month):
        if (shift := dst_shift_in_month(month_start)) is not None:
            break
    else:
        return
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    # Leave some room around the shift and the month end, the device clock may differ from HA
    start = shift - timedelta(hours=2)
    end = min(now, next_month) - timedelta(hours=2)
    if end <= start:
        return

    registry = er.async_get(hass)
    entity_ids = {
        entity_id
        for key in MONTH_GRAPH_SENSORS
        if (entity_id := registry.async_get_entity_id(Platform.SENSOR, DOMAIN, f"{serial}_{key}".lower()))
    }
    if not entity_ids:
        return

    recorder = get_instance(hass)
    unit = UnitOfEnergy.KILO_WATT_HOUR
    stats = await recorder.async_add_executor_job(
        statistics_during_period, hass, start, end, entity_ids, "hour", {"energy": unit}, {"state", "sum"}
    )
    for entity_id, rows in stats.items():
        if (result := find_double_counted(rows)) is None:
            continue
        jump_start, adjustment = result
        _LOGGER.warning(
            "Removing %.3f %s counted twice after the daylight saving time shift from the statistics of %s",
            -adjustment,
            unit,
            entity_id,
        )
        recorder.async_adjust_statistics(entity_id, dt_util.utc_from_timestamp(jump_start), adjustment, unit)
