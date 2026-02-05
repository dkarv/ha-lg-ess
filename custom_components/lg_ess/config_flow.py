"""Config flow for LG ESS integration."""

import logging
from typing import Any

from pyess.aio_ess import ESS, ESSAuthException, ESSException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _ess_schema(
    host: str | None = None,
    pw: str | None = None,
):
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=host): str,
            vol.Required(CONF_PASSWORD, default=pw): str,
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    ess = await ESS.create(None, data[CONF_PASSWORD], data[CONF_HOST])
    info = await ess.get_systeminfo()
    serialno = info["pms"]["serialno"]

    # Return info that you want to store in the config entry.
    return {"serialno": serialno}


class EssConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LG ESS."""

    def __init__(self) -> None:
        """Initialize the ESS config flow."""
        self.discovery_schema: vol.Schema | None = None

    VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info["serialno"])
                user_input["serialno"] = info["serialno"]
                return self.async_create_entry(
                    title=f"LG ESS {info['serialno']}", data=user_input
                )
            except ESSAuthException:
                _LOGGER.exception("Wrong password")
                errors["base"] = "invalid_auth"
            except ESSException:
                _LOGGER.exception("Generic error setting up the ESS Api")
                errors["base"] = "unknown"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=self.discovery_schema or _ess_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Manual reconfiguration to change a setting."""
        current = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info["serialno"])
                self.hass.config_entries.async_update_entry(
                    current, data=user_input)
                await self.hass.config_entries.async_reload(current.entry_id)
                return self.async_abort(reason="reconfiguration_successful")
            except ESSAuthException:
                _LOGGER.exception("Wrong password")
                errors["base"] = "invalid_auth"
            except ESSException:
                _LOGGER.exception("Generic error setting up the ESS Api")
                errors["base"] = "unknown"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_ess_schema(
                host=current.data[CONF_HOST],
                pw=current.data[CONF_PASSWORD],
            ),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle the zeroconf discovery."""
        # Search for IPv4 address as there were frequent issues with IPv6
        ip_address = next(
            (x for x in discovery_info.ip_addresses if x.version == 4), None
        )
        if ip_address is None:
            _LOGGER.warning("No IPv4 address found for %s", discovery_info)
            return self.async_abort(reason="no_ipv4_address")

        if ip_address.version == 6:
            host = f"[{ip_address}]"
        else:
            host = str(ip_address)

        serialno = discovery_info.hostname.replace(".local.", "")

        _LOGGER.info(
            "Discovered device %s with serialno %s and info %s",
            host,
            serialno,
            discovery_info,
        )
        data = {CONF_HOST: host}

        await self.async_set_unique_id(serialno)
        self._abort_if_unique_id_configured()

        self._async_abort_entries_match(data)

        self.discovery_schema = _ess_schema(host)

        return await self.async_step_user()
