import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower, IRRADIATION_WATTS_PER_SQUARE_METER

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FusionSolarLifetimePlantDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarLifetimePlantDataSensor sensors."""

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
        return f'{DOMAIN}-{self._station.code}-lifetime-{self._attribute}'

    @property
    def state(self) -> float:
        key = f'{DOMAIN}-{self._station.code}'

        if key not in self.coordinator.data:
            return None

        total = None

        for collect_time, data in self.coordinator.data[key].items():
            if self._attribute in data and data[self._attribute] is not None:
                if total is None:
                    total = 0
                total = total + float(data[self._attribute])

        return total

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarLifetimePlantDataInverterPowerSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Inverter yield"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarLifetimePlantDataOngridPowerSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Feed-in energy"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarLifetimePlantDataUsePowerSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Consumption"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarLifetimePlantDataPowerProfitSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Revenue"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.MONETARY

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarLifetimePlantDataPerpowerRatioSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Specific energy"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarLifetimePlantDataReductionTotalCo2Sensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - CO2 emission reduction"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarLifetimePlantDataReductionTotalCoalSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Standard coal saved"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarLifetimePlantDataReductionTotalTreeSensor(FusionSolarLifetimePlantDataSensor):
    @property
    def name(self) -> str:
        return "Lifetime - Equivalent tree planted"

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING
