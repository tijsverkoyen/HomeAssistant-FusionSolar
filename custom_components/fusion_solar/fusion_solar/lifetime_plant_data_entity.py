import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfMass

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FusionSolarLifetimePlantDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarLifetimePlantDataSensor sensors."""

    def __init__(
            self,
            coordinator,
            station,
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._station = station
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
    _attribute = 'inverter_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Inverter yield'

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
    _attribute = 'ongrid_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Feed-in energy'

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
    _attribute = 'use_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Consumption'

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
    _attribute = 'power_profit'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Revenue'

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.MONETARY

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarLifetimePlantDataPerpowerRatioSensor(FusionSolarLifetimePlantDataSensor):
    _attribute = 'perpower_ratio'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Specific energy'

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarLifetimePlantDataReductionTotalCo2Sensor(FusionSolarLifetimePlantDataSensor):
    _attribute = 'reduction_total_co2'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - CO2 emission reduction'

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.WEIGHT

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfMass.KILOGRAMS

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING

    @property
    def state(self) -> float:
        super_state = super().state

        if super_state is None:
            return None

        return super_state * 1000

    @property
    def icon(self) -> str | None:
        return "mdi:molecule-co2"


class FusionSolarLifetimePlantDataReductionTotalCoalSensor(FusionSolarLifetimePlantDataSensor):
    _attribute = 'reduction_total_coal'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Standard coal saved'

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.WEIGHT

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfMass.KILOGRAMS

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING

    @property
    def state(self) -> float:
        super_state = super().state

        if super_state is None:
            return None

        return super_state * 1000


class FusionSolarLifetimePlantDataReductionTotalTreeSensor(FusionSolarLifetimePlantDataSensor):
    _attribute = 'reduction_total_tree'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Lifetime - Equivalent tree planted'

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING

    @property
    def icon(self) -> str | None:
        return "mdi:tree"
