from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_POWER, POWER_KILO_WATT

from .const import ATTR_DATA_REALKPI
from ..const import DOMAIN


class FusionSolarKioskPowerEntity(CoordinatorEntity, Entity):
    """Base class for all FusionSolarKioskPower entities."""

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
        return float(self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI][self._attribute]) if \
            self.coordinator.data[self._kioskId][ATTR_DATA_REALKPI] else None

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._kioskId}-{self._idSuffix}'

    @property
    def unit_of_measurement(self):
        return POWER_KILO_WATT


class FusionSolarKioskSensorRealtimePower(FusionSolarKioskPowerEntity):
    pass
