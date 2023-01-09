from homeassistant.core import callback
from homeassistant.const import DEVICE_CLASS_POWER, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity


class FusionSolarPowerEntity(CoordinatorEntity, Entity):
    """Base class for all FusionSolarPowerEntity entities."""

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
        self._state = '__NOT_INITIALIZED__'

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
        if self._state == '__NOT_INITIALIZED__':
            # check if data is available
            self._handle_coordinator_update()

        if self._state is None or self._state == '__NOT_INITIALIZED__':
            return None

        return self._state

    @property
    def unit_of_measurement(self):
        return UnitOfPower.KILO_WATT

    @property
    def device_info(self) -> dict:
        return self._device_info

    @callback
    def _handle_coordinator_update(self):
        if self.coordinator.data is False:
            return
        if self._data_name not in self.coordinator.data:
            return
        if self._attribute not in self.coordinator.data[self._data_name]:
            return

        if self.coordinator.data[self._data_name][self._attribute] is None:
            self._state = None
        elif self.coordinator.data[self._data_name][self._attribute] == 'N/A':
            self._state = None
        else:
            self._state = float(self.coordinator.data[self._data_name][self._attribute])


class FusionSolarPowerEntityRealtime(FusionSolarPowerEntity):
    pass
