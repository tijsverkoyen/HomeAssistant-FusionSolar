import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FusionSolarStationRealKpiSensor(CoordinatorEntity, SensorEntity):
    """Base class for sensors based on the real-time plant data (getStationRealKpi)."""

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
        return f'{DOMAIN}-{self._station.code}-{self._attribute}'

    @property
    def raw_value(self):
        key = f'{DOMAIN}-{self._station.code}'

        if not self.coordinator.data or key not in self.coordinator.data:
            return None

        return self.coordinator.data[key].get(self._attribute)

    @property
    def native_value(self) -> float:
        if self.raw_value is None:
            return None

        return float(self.raw_value)

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarStationRealKpiDayIncomeSensor(FusionSolarStationRealKpiSensor):
    _attribute = 'day_income'
    # The currency is configured in FusionSolar and not returned by the API, so no monetary device class.
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = 'mdi:cash'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Revenue Today'


class FusionSolarStationRealKpiTotalIncomeSensor(FusionSolarStationRealKpiSensor):
    _attribute = 'total_income'
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = 'mdi:cash'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Total Revenue'


class FusionSolarStationRealKpiHealthStateSensor(FusionSolarStationRealKpiSensor):
    _attribute = 'real_health_state'
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = 'real_health_state'
    # 1: disconnected, 2: faulty, 3: healthy
    _attr_options = ['1', '2', '3']
    _attr_icon = 'mdi:heart-pulse'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Health State'

    @property
    def native_value(self) -> str:
        if self.raw_value is None:
            return None

        value = str(int(float(self.raw_value)))
        if value not in self._attr_options:
            _LOGGER.debug(f'Unknown real_health_state value {self.raw_value} for station {self._station.code}')
            return None

        return value
