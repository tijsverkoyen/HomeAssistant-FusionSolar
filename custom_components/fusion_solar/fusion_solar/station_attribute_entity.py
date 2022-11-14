from homeassistant.helpers.entity import Entity, EntityCategory

from .openapi.station import FusionSolarStation
from ..const import DOMAIN


class FusionSolarStationAttributeEntity(Entity):
    def __init__(
            self,
            station: FusionSolarStation,
            name,
            attribute,
            value
    ):
        """Initialize the entity"""
        self._station = station
        self._name = name
        self._attribute = attribute
        self._device_info = station.device_info()
        self._value = value

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._station.code}-{self._attribute}'

    @property
    def name(self):
        return f'{self._station.name} ({self._station.code}) - {self._name}'

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


class FusionSolarStationCapacityEntity(FusionSolarStationAttributeEntity):
    _attr_icon = 'mdi:lightning-bolt'


class FusionSolarStationContactPersonEntity(FusionSolarStationAttributeEntity):
    _attr_icon = 'mdi:account'


class FusionSolarStationContactPersonPhoneEntity(FusionSolarStationAttributeEntity):
    _attr_icon = 'mdi:card-account-phone'


class FusionSolarStationAddressEntity(FusionSolarStationAttributeEntity):
    _attr_icon = 'mdi:map-marker'
