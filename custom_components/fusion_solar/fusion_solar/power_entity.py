from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_POWER, POWER_KILO_WATT


class FusionSolarPowerEntity(CoordinatorEntity, Entity):
    """Base class for all FusionSolarPowerEntity entities."""

    def __init__(
            self,
            coordinator,
            unique_id,
            name,
            attribute,
            data_name,
            device_info
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._name = name
        self._attribute = attribute
        self._data_name = data_name
        self._device_info = device_info

    @property
    def device_class(self):
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        if self._data_name not in self.coordinator.data:
            return None
        if self._attribute not in self.coordinator.data[self._data_name]:
            return None

        return float(self.coordinator.data[self._data_name][self._attribute])

    @property
    def unit_of_measurement(self):
        return POWER_KILO_WATT

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarPowerEntityRealtime(FusionSolarPowerEntity):
    pass
