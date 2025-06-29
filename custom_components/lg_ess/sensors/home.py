from .util import _calculate_directional, _get, _or, _mul
from .base import (
    _BACKUP,
    _BATTERYHALF,
    _BATTERYHOME,
    _BATTERYLOAD,
    _BATTERYSTATUS,
    _CHARGING,
    _DISCHARGING,
    _EV,
    _FROMGRID,
    _GRID,
    _HEATPUMP,
    _LOAD,
    _PV,
    _TOGRID,
    _WINTER,
    BinarySensor,
    EssSensor,
    MeasurementSensor,
)
from ..coordinator import (
    HomeCoordinator,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
)
from homeassistant.helpers.device_registry import DeviceInfo


def get_home_sensors(
    home_coordinator: HomeCoordinator, device_info: DeviceInfo
) -> list[EssSensor]:
    """
    Returns a list of sensors that use the system_coordinator.
    """
    return [
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "pcs_pv_total_power"]),
                lambda: _mul(_get(d, ["statistics", "pv_total_power_01kW"]), 100),
            ),
            "statistics_pcs_pv_total_power",
            icon=_PV,
            unit=UnitOfPower.WATT,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "batconv_power"]),
                lambda: _mul(_get(d, ["statistics", "batt_conv_power_01kW"]), 100),
            ),
            "statistics_batconv_power",
            icon=_BATTERYLOAD,
            unit=UnitOfPower.WATT,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "bat_use"]),
            ),
            "statistics_bat_use",
            icon=_BATTERYHOME,
        ),
        # 1: CHARGING, 2: DISCHARGING
        EssSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "bat_status"]),
            ),
            "statistics_bat_status",
            icon=_BATTERYSTATUS,
        ),  # unknown enum
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "bat_user_soc"]),
            ),
            "statistics_bat_user_soc",
            PERCENTAGE,
            icon=_BATTERYHALF,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "load_power"]),
                lambda: _mul(_get(d, ["statistics", "load_power_01kW"]), 100),
            ),
            "statistics_load_power",
            UnitOfPower.WATT,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "ac_output_power"]),
                lambda: _mul(_get(d, ["statistics", "ac_active_power_01kW"]), 100),
            ),
            "statistics_ac_output_power",
            unit=UnitOfPower.KILO_WATT,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "load_today"]),
            ),
            "statistics_load_today",
            icon=_LOAD,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "grid_power"]),
                lambda: _mul(_get(d, ["statistics", "grid_power_01kW"]), 100),
            ),
            "statistics_grid_power",
            UnitOfPower.WATT,
            icon=_GRID,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["statistics", "current_day_self_consumption"]),
            ),
            "statistics_current_day_self_consumption",
            PERCENTAGE,
            icon=_PV,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_direct_consuming_"]),
            ),
            "direction_is_direct_consuming_",
            icon=_PV,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_battery_charging_"]),
            ),
            "direction_is_battery_charging_",
            icon=_CHARGING,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_battery_discharging_"]),
            ),
            "direction_is_battery_discharging_",
            icon=_DISCHARGING,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_grid_selling_"]),
            ),
            "direction_is_grid_selling_",
            icon=_TOGRID,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_grid_buying_"]),
            ),
            "direction_is_grid_buying_",
            icon=_FROMGRID,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_charging_from_grid_"]),
            ),
            "direction_is_charging_from_grid_",
            icon=_CHARGING,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["direction", "is_discharging_to_grid_"]),
            ),
            "direction_is_discharging_to_grid_",
            icon=_DISCHARGING,
        ),
        EssSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["operation", "status"]),
            ),
            "operation_status",
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["operation", "mode"]),
            ),
            "operation_mode",
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["operation", "pcs_standbymode"]),
            ),
            "operation_pcs_standbymode",
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["operation", "drm_mode0"]),
            ),
            "operation_drm_mode0",
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["operation", "remote_mode"]),
            ),
            "operation_remote_mode",
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["operation", "drm_control"]),
            ),
            "operation_drm_control",
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["wintermode", "winter_status"]),
            ),
            "wintermode_winter_status",
            icon=_WINTER,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["wintermode", "backup_status"]),
            ),
            "wintermode_backup_status",
            icon=_BACKUP,
        ),
        EssSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["pcs_fault", "pcs_status"]),
            ),
            "pcs_fault_pcs_status",
        ),
        EssSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["pcs_fault", "pcs_op_status"]),
            ),
            "pcs_fault_pcs_op_status",
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["heatpump", "heatpump_protocol"]),
            ),
            "heatpump_heatpump_protocol",
            icon=_HEATPUMP,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["heatpump", "heatpump_activate"]),
            ),
            "heatpump_heatpump_activate",
            icon=_HEATPUMP,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["heatpump", "current_temp"]),
            ),
            "heatpump_current_temp",
            icon=_HEATPUMP,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["heatpump", "heatpump_working"]),
            ),
            "heatpump_heatpump_working",
            icon=_HEATPUMP,
        ),
        BinarySensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["evcharger", "ev_activate"]),
            ),
            "evcharger_ev_activate",
            icon=_EV,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["evcharger", "ev_power"]),
            ),
            "evcharger_ev_power",
            UnitOfPower.WATT,
            icon=_EV,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: d["gridWaitingTime"],
            "gridWaitingTime",
        ),
        EssSensor(
            home_coordinator,
            device_info,
            lambda d: d["backupmode"],
            "backupmode",
            icon=_BACKUP,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _calculate_directional(
                d["direction"]["is_battery_charging_"],
                d["statistics"]["batconv_power"],
            ),
            "batt_directional",
            UnitOfPower.WATT,
        ),
        MeasurementSensor(
            home_coordinator,
            device_info,
            lambda d: _calculate_directional(
                d["direction"]["is_grid_selling_"], d["statistics"]["grid_power"]
            ),
            "grid_directional",
            UnitOfPower.WATT,
        ),
    ]
