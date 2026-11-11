# Code review: HA best practices

Review of the integration against Home Assistant's integration guidelines (Integration Quality Scale and developer docs), as of 2026-11-11 (v1.0.3, commit `9beff63`). All findings come from reading the code; nothing was run.

Already in good shape: config flow, zeroconf discovery, reconfigure step, `has_entity_name` with translation keys, a coordinator per endpoint, unique IDs migrated per serial number, tests on real device data.

## Likely bugs

- [ ] **Winter mode and auto-charge switches may send the inverted value.** `switch.py:83-84`: `_set_bool` sends `set_val[1] if value else set_val[0]`. With the default `["on", "off"]`, turning the switch on sends `"off"`, and auto-charge sends `"0"` for on. If that's not the device's real behavior, the switches do the opposite of what's asked. No test covers the setter (`tests/test_settings_switches.py` only checks reading). The default argument is also a mutable list.
- [ ] **Binary sensors are added through the sensor platform.** `BinarySensor` objects go into the `get_*_sensors()` lists and are registered by `sensor.py`. `Platform.BINARY_SENSOR` isn't in `PLATFORMS`, so they end up as `sensor.*` entities showing "on"/"off" text, without `BinarySensorDeviceClass` or proper history. Move them to their own `binary_sensor.py`. This changes entity IDs, so it needs a registry migration.
- [ ] **`BinarySensor` sets `self.is_on = ...` directly** (`sensors/base.py:111,118`). Use `_attr_is_on`; writing to the property name sidesteps HA's cached-property handling.
- [ ] **Wrong unit or device class on several sensors:**
  - `0_batt_charged` / `0_batt_discharged`: Wh, but `device_class=POWER` with `MEASUREMENT`. Should be `ENERGY` with `TOTAL_INCREASING`.
  - `statistics_ac_output_power`: the fallback `ac_active_power_01kW * 100` gives W, but the unit is `KILO_WATT`.
  - `statistics_pcs_pv_total_power`, `statistics_batconv_power`, `statistics_load_power`, `statistics_grid_power`: W units but no `device_class=POWER`.
  - `batt_capacity`: Wh with `MEASUREMENT`. Should be `ENERGY_STORAGE` or have no state class.
  - `pms_ac_input_power` / `pms_ac_output_power`: plain `EssSensor`s with a unit but no device class or state class.
- [ ] **Coordinator errors aren't wrapped in `UpdateFailed`.** `_async_update_data` lets `ESSException` / `aiohttp.ClientError` escape, so the coordinator logs a full traceback every 10 s while the device is offline. Wrap the calls and raise `UpdateFailed`.
- [ ] **Authentication failures don't lead anywhere.** A changed password should raise `ConfigEntryAuthFailed` in the coordinators, backed by an `async_step_reauth` flow. Today it retries forever.
- [ ] **`async_migrate_entry` v1→v2 never closes its `ESS` instance** (`__init__.py:69`), so the session leaks. It also crashes instead of returning `False` when the device can't be reached.

## Deviations from HA best practices

### Setup and lifecycle

- [ ] Use `entry.runtime_data` with a typed `ConfigEntry` alias instead of `hass.data[DOMAIN][entry_id]` (Bronze requirement).
- [ ] Each platform calls `await base.first_refresh()` again. The refresh already happens in `async_setup_entry`; remove it from the platforms.
- [ ] The 4 coordinators' first refreshes run one after another, and each already raises `ConfigEntryNotReady`, so the `except ESSException` wrapper adds nothing. Consider `asyncio.gather`.
- [ ] `ESS.create(None, ...)` makes pyess open its own aiohttp session. Pass `async_get_clientsession(hass)` (with `verify_ssl=False` if needed) so HA manages it. Check that pyess supports this.
- [ ] `_LOGGER.exception` before `ConfigEntryNotReady` logs a traceback on every retry. Use `raise ConfigEntryNotReady(str(e)) from e` and let HA log it.

### Config flow

- [ ] `async_step_user` sets the unique ID but never calls `self._abort_if_unique_id_configured()`, so the same device can be added twice manually.
- [ ] Reconfigure: call `self._abort_if_unique_id_mismatch()` and `return self.async_update_reload_and_abort(current, data_updates=user_input)` instead of updating and reloading by hand.
- [ ] Connection errors raise `ESSException`, which maps to `"unknown"` although `cannot_connect` exists in `strings.json`. Catch `ESSException` and `ClientError` as `cannot_connect`.
- [ ] The password field is a plain `str`, and the reconfigure form pre-fills it in clear text. Use `TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))`.
- [ ] Zeroconf: set `title_placeholders` so the discovery card names the device, and consider a confirm step showing the host instead of falling into the user step. The IPv6 branch at `config_flow.py:133` can never run, since only IPv4 addresses are selected.
- [ ] Zeroconf should update the host of an existing entry when the IP changes: `self._abort_if_unique_id_configured(updates={CONF_HOST: host})`.
- [ ] `user_input["serialno"]` is stored in the entry data but duplicates `entry.unique_id`.

### Entities

- [ ] Model, serial number, version and install-date sensors duplicate `DeviceInfo`. Give them `EntityCategory.DIAGNOSTIC`, and consider `entity_registry_enabled_default=False`.
- [ ] Number and select entities should use `EntityCategory.CONFIG`. The SoC numbers should use `native_unit_of_measurement=PERCENTAGE` and `NumberMode.SLIDER` or `BOX`.
- [ ] Write actions (`set_batt_settings`, `switch_on`/`switch_off`) should catch `ESSException` and raise `HomeAssistantError` with a translation key.
- [ ] `SettingsCoordinator.update_settings` is never used; entities call `ess.set_batt_settings` directly. Use the coordinator method or delete it.
- [ ] Icons are hardcoded via `_attr_icon`. Move them to `icons.json` keyed by translation key (this also supports per-state icons).
- [ ] Sensor descriptions are lambdas passed positionally. The idiomatic pattern is a `@dataclass(frozen=True, kw_only=True)` subclass of `SensorEntityDescription` with a `value_fn`, plus one generic entity class. That makes unit and device-class mistakes harder and shrinks `sensors/common.py` / `sensors/home.py` a lot.
- [ ] Entity classes list `CoordinatorEntity[...]` again although `EssEntity` already inherits it, and `EssEntity` also inherits plain `Entity`. Both are redundant.
- [ ] `_attr_has_entity_name = True` and similar constants belong at class level, not in `__init__`.
- [ ] String-code sensors (`statistics_bat_status`, `BATT_status`, `operation_mode`, `pcs_fault_*`) should use `SensorDeviceClass.ENUM` with `options` and translated states.
- [ ] `_parse_date(d["pms"]["install_date"])` raises `KeyError` / `ValueError` on missing or odd data because it indexes the dict directly instead of using `_get`, so one entity's error can break setup for all of them.

### Other

- [ ] `PARALLEL_UPDATES = 0` (or 1 for platforms with write actions) is missing from the platform modules (Bronze/Silver check).
- [ ] No `diagnostics.py`. A diagnostics download with the password redacted would help a lot with bug reports.
- [ ] The statistics repair task changes statistics silently apart from a log warning. Consider an `ir.async_create_issue` notice. Minor.

## Packaging and CI

- [ ] **CI is missing hassfest.** Add `home-assistant/actions/hassfest@master` to `validate.yaml`; it catches manifest, strings and translation mistakes. Keep `translations/en.json` in sync with `strings.json`, ideally with a script.
- [ ] `hacs.json` should declare `"homeassistant": "<min version>"`. `ConfigFlowResult`, `config_entry=` on the coordinator and `homeassistant.helpers.service_info.zeroconf` need roughly 2025.1 or later.
- [ ] `manifest.json`: drop the empty `"homekit": {}`, `"ssdp": []` and `"dependencies": []`; add `"loggers": ["pyess"]`.
- [ ] `requirements.txt` doesn't pin `homeassistant`, so a new HA release can break CI unpredictably. Use `pytest-homeassistant-custom-component`, which pins a matching HA and provides the `hass` fixture, to test setup, unload, coordinators and the config flow end to end.
- [ ] Workflows mix `actions/checkout@v3` and `@v4`. Add `ruff` to catch unused imports (`SwitchEntity` and `DeviceInfo` in `number.py`, unused `BinarySensorEntity` imports, and others) and outdated docstrings (`"Example integration using DataUpdateCoordinator."`; `number.py` and `select.py` saying "switch entities").

## Suggested order

1. Check the switch inversion and fix the units and device classes. These affect what users see right now.
2. Add `UpdateFailed` handling plus `ConfigEntryAuthFailed` and a reauth flow.
3. Move to `runtime_data`, fix the config-flow unique-ID checks, use `async_update_reload_and_abort`, add hassfest.
4. Move binary sensors to their own platform, bundled with a v3→v4 entity migration.
5. Refactor to `EntityDescription`s, `icons.json`, entity categories and diagnostics.
