import logging
import math

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy

from .const import ATTR_TOTAL_LIFETIME_ENERGY, ATTR_REALTIME_POWER

_LOGGER = logging.getLogger(__name__)


def isfloat(num) -> bool:
    try:
        float(num)
        return True
    except ValueError:
        return False


class FusionSolarEnergySensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarEnergySensor sensors."""

    def __init__(
            self,
            coordinator,
            unique_id,
            name,
            attribute,
            data_name,
            device_info=None
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._name = name
        self._attribute = attribute
        self._data_name = data_name
        self._device_info = device_info

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def native_value(self) -> float:
        # It seems like Huawei Fusion Solar returns some invalid data for the lifetime energy just before midnight
        # Therefore we validate if the new value is higher than the current value
        if ATTR_TOTAL_LIFETIME_ENERGY == self._attribute:
            # Grab the current data
            entity = self.hass.states.get(self.entity_id)

            if entity is not None:
                current_value = entity.state
                if current_value == 'unavailable':
                    _LOGGER.info(f'{self.entity_id}: not available.')
                    return

                realtime_power = self.coordinator.data[self._data_name][ATTR_REALTIME_POWER]
                if math.isclose(float(realtime_power), 0, abs_tol = 0.001):
                    _LOGGER.info(f'{self.entity_id}: not producing any power, so no energy update to prevent glitches.')
                    return float(current_value)

        if self._data_name not in self.coordinator.data:
            return None

        if self._attribute not in self.coordinator.data[self._data_name]:
            return None

        return float(self.coordinator.data[self._data_name][self._attribute])

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarEnergySensorTotalCurrentDay(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalCurrentMonth(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalCurrentYear(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalLifetime(FusionSolarEnergySensor):
    pass
