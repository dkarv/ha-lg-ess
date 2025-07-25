from .base import (
    _BACKUP,
    _BATTERYLOAD,
    _BATTERYSTATUS,
    _CHARGING,
    _CO2,
    _DISCHARGING,
    _FROMGRID,
    _GRID,
    _LOAD,
    _ONE,
    _PV,
    _THREE,
    _TOGRID,
    _TWO,
    _WINTER,
    BinarySensor,
    EssSensor,
    IncreasingSensor,
)
from .base import MeasurementSensor
from .base import IncreasingEnergySensor
from .util import _get, _or
from ..coordinator import CommonCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
)


def _sum_if_list(value):
    """
    If the value is a list, return the sum of its elements.
    Otherwise, return the value itself.
    """
    if isinstance(value, list):
        return sum(value)
    return value


def get_common_sensors(
    common_coordinator: CommonCoordinator, device_info: DeviceInfo
) -> list[EssSensor]:
    """
    Returns a list of sensors that use the system_coordinator.
    """
    return [
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "dc_power"]),
                lambda: _get(d, ["ess", 0, "sum_of_batt_dc_power"]),
            ),
            "BATT_dc_power",
            unit=UnitOfPower.WATT,
            icon=_BATTERYLOAD,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["LOAD", "load_power"]),
            ),
            "LOAD_load_power",
            unit=UnitOfPower.WATT,
            icon=_LOAD,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "today_self_consumption"]),
            ),
            "PCS_today_self_consumption",
            PERCENTAGE,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "today_batt_discharge_enery"]),
            ),
            "BATT_today_batt_discharge_energy",
            icon=_DISCHARGING,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "today_batt_charge_energy"]),
            ),
            "BATT_today_batt_charge_energy",
            icon=_CHARGING,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "month_batt_discharge_energy"]),
            ),
            "BATT_month_batt_discharge_energy",
            icon=_DISCHARGING,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "month_batt_charge_energy"]),
            ),
            "BATT_month_batt_charge_energy",
            icon=_CHARGING,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["LOAD", "today_load_consumption_sum"]),
            ),
            "LOAD_today_load_consumption_sum",
            icon=_LOAD,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["LOAD", "today_pv_direct_consumption_enegy"]),
            ),
            "LOAD_today_pv_direct_consumption_energy",
            icon=_PV,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["LOAD", "today_grid_power_purchase_energy"]),
            ),
            "LOAD_today_grid_power_purchase_energy",
            icon=_FROMGRID,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["LOAD", "month_load_consumption_sum"]),
            ),
            "LOAD_month_load_consumption_sum",
            icon=_LOAD,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(
                    d, ["LOAD", "month_pv_direct_consumption_energy"]),
            ),
            "LOAD_month_pv_direct_consumption_energy",
            icon=_PV,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["LOAD", "month_grid_power_purchase_energy"]),
            ),
            "LOAD_month_grid_power_purchase_energy",
            icon=_FROMGRID,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "today_pv_generation_sum"]),
            ),
            "PCS_today_pv_generation_sum",
            icon=_PV,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "today_grid_feed_in_energy"]),
            ),
            "PCS_today_grid_feed_in_energy",
            icon=_TOGRID,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "month_pv_generation_sum"]),
            ),
            "PCS_month_pv_generation_sum",
            icon=_PV,
        ),
        IncreasingEnergySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "month_grid_feed_in_energy"]),
            ),
            "PCS_month_grid_feed_in_energy",
            icon=_TOGRID,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv1_voltage"]),
                lambda: _get(d, ["ess", 0, "pv", 0, "voltage"]),
            ),
            "PV_pv1_voltage",
            UnitOfElectricPotential.VOLT,
            icon=_ONE,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv2_voltage"]),
                lambda: _get(d, ["ess", 0, "pv", 1, "voltage"]),
            ),
            "PV_pv2_voltage",
            UnitOfElectricPotential.VOLT,
            icon=_TWO,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv3_voltage"]),
                lambda: _get(d, ["ess", 0, "pv", 2, "voltage"]),
            ),
            "PV_pv3_voltage",
            UnitOfElectricPotential.VOLT,
            icon=_THREE,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv1_power"]),
                lambda: _get(d, ["ess", 0, "pv", 0, "power"]),
            ),
            "PV_pv1_power",
            UnitOfPower.WATT,
            icon=_ONE,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv2_power"]),
                lambda: _get(d, ["ess", 0, "pv", 1, "power"]),
            ),
            "PV_pv2_power",
            UnitOfPower.WATT,
            icon=_TWO,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv3_power"]),
                lambda: _get(d, ["ess", 0, "pv", 2, "power"]),
            ),
            "PV_pv3_power",
            UnitOfPower.WATT,
            icon=_THREE,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv1_current"]),
                lambda: _get(d, ["ess", 0, "pv", 0, "current"]),
            ),
            "PV_pv1_current",
            UnitOfElectricCurrent.AMPERE,
            icon=_ONE,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv2_current"]),
                lambda: _get(d, ["ess", 0, "pv", 1, "current"]),
            ),
            "PV_pv2_current",
            UnitOfElectricCurrent.AMPERE,
            icon=_TWO,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "pv3_current"]),
                lambda: _get(d, ["ess", 0, "pv", 2, "current"]),
            ),
            "PV_pv3_current",
            UnitOfElectricCurrent.AMPERE,
            icon=_THREE,
        ),
        IncreasingSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "month_co2_reduction_accum"]),
            ),
            "PCS_month_co2_reduction_accum",
            icon=_CO2,
        ),
        EssSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PV", "capacity"]),
                lambda: _get(d, ["ess", 0, "sum_of_pv_capacity"]),
            ),
            "PV_capacity",
            icon=_PV,
            unit=UnitOfPower.WATT,
        ),  # Wp
        EssSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "status"]),
            ),
            "BATT_status",
            icon=_BATTERYSTATUS,
        ),
        BinarySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "winter_setting"]),
                lambda: _get(d, ["winter_setting"]),
            ),
            "BATT_winter_setting",
            icon=_WINTER,
        ),
        BinarySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "winter_status"]),
                lambda: _get(d, ["winter_status"]),
            ),
            "BATT_winter_status",
            icon=_WINTER,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "safety_soc"]),
            ),
            "BATT_safety_soc",
            PERCENTAGE,
            icon=_WINTER,
        ),
        BinarySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "backup_setting"]),
            ),
            "BATT_backup_setting",
            icon=_BACKUP,
        ),
        BinarySensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "backup_status"]),
            ),
            "BATT_backup_status",
            icon=_BACKUP,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["BATT", "backup_soc"]),
            ),
            "BATT_backup_soc",
            PERCENTAGE,
            icon=_BACKUP,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["GRID", "total_active_power"]),  # v2
                lambda: _get(d, ["GRID", "active_power"]),  # v1
            ),
            "GRID_active_power",
            UnitOfPower.WATT,
            icon=_FROMGRID,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _sum_if_list(_get(d, ["GRID", "a_phase"])),
            "GRID_a_phase",
            UnitOfElectricPotential.VOLT,
            icon=_GRID,
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["GRID", "freq"]),
            ),
            "GRID_freq",
            UnitOfFrequency.HERTZ,
            icon=_GRID,
        ),
        EssSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "pcs_stauts"]),
            ),
            "PCS_pcs_status",
        ),
        MeasurementSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "feed_in_limitation"]),
            ),
            "PCS_feed_in_limitation",
            PERCENTAGE,
            icon=_TOGRID,
        ),
        EssSensor(
            common_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["PCS", "operation_mode"]),
            ),
            "PCS_operation_mode",
        ),
    ]
