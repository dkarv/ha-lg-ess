"""Coordinator to fetch the data once for all sensors."""

from datetime import datetime, timedelta
import logging

from aiohttp import ClientError
from pyess.aio_ess import ESS, ESSException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import dt as dt_util


_LOGGER = logging.getLogger(__name__)

# The device writes a graph row every 15 minutes, no need to poll the graph endpoints more often.
GRAPH_INTERVAL = timedelta(minutes=5)


def _last_row(response: dict | None) -> dict | None:
    """Return the newest row of a graph response, or None if the device has no data for that period."""
    if not response or response.get("db") != "success" or not response.get("loginfo"):
        return None
    return max(response["loginfo"], key=lambda row: row["time"])


def dst_shift_this_month(now: datetime) -> bool:
    """Whether the UTC offset of the HA time zone changed since the start of the current month."""
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return month_start.utcoffset() != now.utcoffset()


async def fetch_month_graph(ess: ESS, now: datetime) -> dict | None:
    """Fetch the month totals for the month the device is currently in.

    The month_* counters of the common endpoint are reset by the device on daylight saving time
    changes, the month graph is not. The device returns no data for months it has not reached yet,
    so trying the next month first covers a device clock that is ahead of HA. If the device is behind,
    the current month has no data and the sensors fall back to the month_* counters.
    """
    month = now.date().replace(day=1)
    next_month = (month + timedelta(days=32)).replace(day=1)
    for m in (next_month, month):
        pv = _last_row(await ess.get_graph("pv", "month", m))
        if pv is not None:
            return {
                "pv": pv,
                "load": _last_row(await ess.get_graph("load", "month", m)),
                "batt": _last_row(await ess.get_graph("batt", "month", m)),
            }
    return None


class ESSCoordinator(DataUpdateCoordinator):
    """LG ESS basic coordinator."""

    _ess: ESS

    def __init__(
        self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry, name: str, interval: timedelta
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=name,
            update_interval=interval,
        )
        self._ess = ess


class CommonCoordinator(ESSCoordinator):
    """LG ESS common coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS common",
            interval=timedelta(seconds=30),
        )
        self._graph = None
        self._graph_fetched: datetime | None = None

    async def _async_update_data(self):
        data = await self._ess.get_common()
        _LOGGER.debug("Common data: %s", data)
        now = dt_util.now()
        if not dst_shift_this_month(now):
            # The month_* counters are only wrong after a daylight saving time shift
            self._graph = None
        elif self._graph_fetched is None or now - self._graph_fetched >= GRAPH_INTERVAL:
            self._graph_fetched = now
            try:
                self._graph = await fetch_month_graph(self._ess, now)
            except (ESSException, ClientError, KeyError, ValueError) as e:
                # Keep the last graph data, falling back to the reset month_* counters would count the
                # month total twice once the graph is available again
                _LOGGER.warning("Could not fetch month graph data: %s", e)
            _LOGGER.debug("Month graph data: %s", self._graph)
        data["GRAPH"] = self._graph
        return data


class SystemInfoCoordinator(ESSCoordinator):
    """LG ESS system info coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS system info",
            interval=timedelta(minutes=10),
        )

    async def _async_update_data(self):
        data = await self._ess.get_systeminfo()
        _LOGGER.debug("System info data: %s", data)
        return data


class HomeCoordinator(ESSCoordinator):
    """LG ESS home coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS home",
            interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        data = await self._ess.get_home()
        _LOGGER.debug("Home data: %s", data)
        return data


class SettingsCoordinator(ESSCoordinator):
    """LG ESS settings coordinator."""

    def __init__(self, hass: HomeAssistant, ess: ESS, config_entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            ess,
            config_entry=config_entry,
            name="LG ESS settings",
            interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        data = await self._ess.get_batt_settings()
        _LOGGER.debug("Settings data: %s", data)
        return data
    
    async def update_settings(self, new_settings: dict) -> None:
        """Update battery settings."""
        await self._ess.set_batt_settings(new_settings)
        await self.async_refresh()
