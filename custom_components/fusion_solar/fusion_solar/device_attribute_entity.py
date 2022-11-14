from homeassistant.helpers.entity import Entity, EntityCategory

from .openapi.device import FusionSolarDevice
from ..const import DOMAIN


class FusionSolarDeviceAttributeEntity(Entity):
    def __init__(
            self,
            device: FusionSolarDevice,
            name,
            attribute,
            value
    ):
        """Initialize the entity"""
        self._device = device
        self._name = name
        self._attribute = attribute
        self._device_info = device.device_info()
        self._value = value

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-{self._attribute}'

    @property
    def name(self):
        if not self._device.esn_code:
            return f'{self._device.name} ({self._device.esn_code}) - {self._name}'

        return f'{self._device.name} - {self._name}'

    @property
    def state(self):
        return self._value

    @property
    def device_info(self) -> dict:
        return self._device_info

    @property
    def entity_category(self) -> str:
        return EntityCategory.DIAGNOSTIC

    @property
    def should_poll(self) -> bool:
        return False


class FusionSolarDeviceLatitudeEntity(FusionSolarDeviceAttributeEntity):
    _attr_icon = 'mdi:latitude'


class FusionSolarDeviceLongitudeEntity(FusionSolarDeviceAttributeEntity):
    _attr_icon = 'mdi:longitude'
