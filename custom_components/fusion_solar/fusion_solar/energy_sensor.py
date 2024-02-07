import logging
import math

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy

from .const import ATTR_TOTAL_LIFETIME_ENERGY, ATTR_REALTIME_POWER

_LOGGER = logging.getLogger(__name__)


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
        # It seems like Huawei Fusion Solar returns some invalid data for the cumulativeEnergy just before midnight.
        # So we update the value only if the system is producing power at the moment.
        if ATTR_TOTAL_LIFETIME_ENERGY == self._attribute:
            # Grab the current data
            entity = self.hass.states.get(self.entity_id)
            if entity is not None:
                try:
                    current_value = float(entity.state)
                except ValueError:
                    _LOGGER.info(f'{self.entity_id}: not available, so no update to prevent issues.')
                    return

                # Return the current value if the system is not producing
                if not self.is_producing_at_the_moment():
                    _LOGGER.info(f'{self.entity_id}: not producing any power, so no update to prevent glitches.')
                    return current_value

        try:
            return self.get_float_value_from_coordinator(self._attribute)
        except FusionSolarEnergySensorException as e:
            _LOGGER.error(e)
            return None

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING

    @property
    def device_info(self) -> dict:
        return self._device_info

    def is_producing_at_the_moment(self) -> bool:
        try:
            realtime_power = self.get_float_value_from_coordinator(ATTR_REALTIME_POWER)
            return not math.isclose(realtime_power, 0, abs_tol=0.001)
        except FusionSolarEnergySensorException as e:
            _LOGGER.info(e)
            return False

    def get_float_value_from_coordinator(self, attribute_name: str) -> float:
        if self.coordinator.data is False:
            raise FusionSolarEnergySensorException('Coordinator data is False')
        if self._data_name not in self.coordinator.data:
            raise FusionSolarEnergySensorException(f'Attribute {self._data_name} not in coordinator data')
        if self._attribute not in self.coordinator.data[self._data_name]:
            raise FusionSolarEnergySensorException(f'Attribute {attribute_name} not in coordinator data')

        if self.coordinator.data[self._data_name][attribute_name] is None:
            raise FusionSolarEnergySensorException(f'Attribute {attribute_name} has value None')
        elif self.coordinator.data[self._data_name][attribute_name] == 'N/A':
            raise FusionSolarEnergySensorException(f'Attribute {attribute_name} has value N/A')

        try:
            return float(self.coordinator.data[self._data_name][attribute_name])
        except ValueError:
            raise FusionSolarEnergySensorException(
                f'Attribute {self._attribute} has value {self.coordinator.data[self._data_name][attribute_name]} which is not a float')


class FusionSolarEnergySensorTotalCurrentDay(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalCurrentMonth(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalCurrentYear(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorTotalLifetime(FusionSolarEnergySensor):
    pass


class FusionSolarEnergySensorException(Exception):
    pass
