from .base import EssSensor, MeasurementSensor
from .util import _parse_date, _get, _or, _mul
from ..coordinator import (
    SystemInfoCoordinator,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
)


def get_system_sensors(
    system_coordinator: SystemInfoCoordinator, device_info: DeviceInfo
) -> list[EssSensor]:
    """
    Returns a list of sensors that use the system_coordinator.
    """

    _parse_date(
        _or(
            lambda: _get(system_coordinator.data, [
                "batt", "install_date"]),
            lambda: _get(system_coordinator.data, [
                "ess", 0, "batt_info", "install_date"]),
        )
    )

    return [
        EssSensor(
            system_coordinator,
            device_info,
            lambda d:  _get(d, ["pms", "model"]),
            "pms_model",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["pms", "serialno"]),
            "pms_serialno",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["pms", "ac_input_power"]),
                lambda: _get(d, ["pms", "pv_capacity_power"]),
            ),
            "pms_ac_input_power",
            unit=UnitOfPower.WATT,
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["pms", "ac_output_power"]),
                lambda: _get(d, ["ess", 0, "ac_output_power"]),
            ),
            "pms_ac_output_power",
            unit=UnitOfPower.KILO_WATT,
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _parse_date(d["pms"]["install_date"]),
            "pms_install_date",
        ),
        MeasurementSensor(
            system_coordinator,
            device_info,
            lambda d: _or(
                lambda: _mul(_get(d, ["batt", "capacity"]), 100),
                lambda: _get(d, ["ess", 0, "batt_info", "capacity"]),
            ),
            "batt_capacity",
            UnitOfEnergy.WATT_HOUR,
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["batt", "type"]),
            "batt_type",
        ),
        MeasurementSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["ess", 0, "batt_info", "charged_energy"]),
            "0_batt_charged",
            UnitOfEnergy.WATT_HOUR,
        ),
        MeasurementSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["ess", 0, "batt_info", "discharged_energy"]),
            "0_batt_discharged",
            UnitOfEnergy.WATT_HOUR,
        ),
        MeasurementSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["ess", 0, "batt_info", "discharged_energy"]),
            "0_batt_discharged",
            UnitOfEnergy.WATT_HOUR,
        ),
        MeasurementSensor(
            system_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["batt", "hbc_cycle_count_1"]),
                lambda: _get(d, ["ess", 0, "batt_info", "cycle_count"]),
            ),
            "batt_hbc_cycle_count_1",
        ),
        MeasurementSensor(
            system_coordinator,
            device_info,
            lambda d: _or(
                lambda: _get(d, ["batt", "hbc_cycle_count_2"]),
                lambda: _get(d, ["ess", 0, "batt_info", "cycle_count_dup"]),
            ),
            "batt_hbc_cycle_count_2",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _parse_date(
                _or(
                    lambda: _get(d, ["batt", "install_date"]),
                    lambda: _get(d, ["ess", 0, "batt_info", "install_date"]),
                )
            ),
            "batt_install_date",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["version", "pms_version"]),
            "version_pms_version",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["version", "pms_build_date"]),
            "version_pms_build_date",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["version", "pcs_version"]),
            "version_pcs_version",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["version", "bms_version"]),
            "version_bms_version",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["version", "bms_unit1_version"]),
            "version_bms_unit1_version",
        ),
        EssSensor(
            system_coordinator,
            device_info,
            lambda d: _get(d, ["version", "bms_unit2_version"]),
            "version_bms_unit2_version",
        ),
    ]
