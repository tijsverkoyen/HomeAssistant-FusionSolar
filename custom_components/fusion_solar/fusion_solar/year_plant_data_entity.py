import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower, IRRADIATION_WATTS_PER_SQUARE_METER

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FusionSolarYearPlantDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarYearPlantDataSensor sensors."""

    def __init__(
            self,
            coordinator,
            station,
            attribute,
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._station = station
        self._attribute = attribute
        self._device_info = station.device_info()

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._station.code}-current_year-{self._attribute}'

    @property
    def state(self) -> float:
        key = key = f'{DOMAIN}-{self._station.code}'

        if key not in self.coordinator.data:
            return None

        highest_collect_time = 0
        latest_data = None

        for collect_time, data in self.coordinator.data[key].items():
            if collect_time > highest_collect_time:
                highest_collect_time = collect_time
                latest_data = data

        if self._attribute not in latest_data:
            return None

        if latest_data[self._attribute] is None:
            return None

        return float(latest_data[self._attribute])

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarYearPlantDataInstalledCapacitySensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Installed capacity"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.POWER

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfPower.KILO_WATT

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarYearPlantDataRadiationIntensitySensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Global irradiation"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.IRRADIANCE

    @property
    def unit_of_measurement(self) -> str:
        return IRRADIATION_WATTS_PER_SQUARE_METER

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL

    @property
    def state(self) -> float:
        super_state = super().state

        if super_state is None:
            return None

        return super_state * 1000


class FusionSolarYearPlantDataTheoryPowerSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Theoretical yield"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarYearPlantDataPerformanceRatioSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Performance ratio"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarYearPlantDataInverterPowerSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Inverter yield"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarYearPlantDataOngridPowerSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Feed-in energy"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarYearPlantDataUsePowerSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Consumption"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarYearPlantDataPowerProfitSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Revenue"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.MONETARY

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarYearPlantDataPerpowerRatioSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Specific energy"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarYearPlantDataReductionTotalCo2Sensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - CO2 emission reduction"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarYearPlantDataReductionTotalCoalSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Standard coal saved"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarYearPlantDataReductionTotalTreeSensor(FusionSolarYearPlantDataSensor):
    @property
    def name(self) -> str:
        return "Current Year - Equivalent tree planted"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


# @deprecated, use FusionSolarYearPlantDataInverterPowerSensor instead
class FusionSolarBackwardsCompatibilityTotalCurrentYear(FusionSolarYearPlantDataInverterPowerSensor):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._station.code}-total_current_year_energy'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Total Current Year Energy'
