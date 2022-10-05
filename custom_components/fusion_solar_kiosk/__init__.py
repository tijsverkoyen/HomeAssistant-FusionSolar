"""
Custom integration to integrate FusionSolar Kiosk with Home Assistant.
"""
import logging

from homeassistant.core import Config, HomeAssistant
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (
    ATTR_DATA_REALKPI,
    ATTR_TOTAL_LIFETIME_ENERGY,
    DOMAIN,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up the FusionSolar Kiosk component."""
    return True

def isfloat(num) -> bool:
    try:
        float(num)
        return True
    except ValueError:
        return False

class FusionSolarKioskEnergyEntity(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarKioskEnergy entities."""
    def __init__(
        self,
        coordinator,
        kioskId,
        kioskName,
        idSuffix,
        nameSuffix,
        attribute,
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._kioskId = kioskId
        self._kioskName = kioskName
        self._idSuffix = idSuffix
        self._nameSuffix = nameSuffix
        self._attribute = attribute

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_ENERGY

    @property
    def name(self) -> str:
        return f'{self._kioskName} ({self._kioskId}) - {self._nameSuffix}'

    @property
    def state(self) -> float:
        # It seems like Huawei Fusion Solar returns some invalid data for the lifetime energy just before midnight
        # Therefore we validate if the new value is higher than the current value
        if ATTR_TOTAL_LIFETIME_ENERGY == self._attribute:
            # Grab the current data
            entity = self.hass.states.get(self.entity_id)

            if entity is not None:
                current_value = entity.state
                new_value = self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI][self._attribute]
                if not isfloat(new_value):
                    _LOGGER.warning(f'{self.entity_id}: new value ({new_value}) is not a float, so not updating.')
                    return float(current_value)

                if not isfloat(current_value):
                    _LOGGER.warning(f'{self.entity_id}: current value ({current_value}) is not a float, send 0.')
                    return 0

                if float(new_value) < float(current_value):
                    _LOGGER.debug(f'{self.entity_id}: new value ({new_value}) is smaller then current value ({entity.state}), so not updating.')
                    return float(current_value)

        return float(self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI][self._attribute]) if self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI] else None

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._kioskId}-{self._idSuffix}'

    @property
    def unit_of_measurement(self) -> str:
        return ENERGY_KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def native_value(self) -> str:
        return self.state if self.state else ''

    @property
    def native_unit_of_measurement(self) -> str:
        return self.unit_of_measurement


class FusionSolarKioskPowerEntity(CoordinatorEntity, Entity):
    """Base class for all FusionSolarKioskEnergy entities."""
    def __init__(
        self,
        coordinator,
        kioskId,
        kioskName,
        idSuffix,
        nameSuffix,
        attribute,
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._kioskId = kioskId
        self._kioskName = kioskName
        self._idSuffix = idSuffix
        self._nameSuffix = nameSuffix
        self._attribute = attribute

    @property
    def device_class(self):
        return DEVICE_CLASS_POWER

    @property
    def name(self):
        return f'{self._kioskName} ({self._kioskId}) - {self._nameSuffix}'

    @property
    def state(self):
        return float(self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI][self._attribute]) if self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI] else None

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._kioskId}-{self._idSuffix}'

    @property
    def unit_of_measurement(self):
        return POWER_KILO_WATT
