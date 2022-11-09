from homeassistant.helpers.entity import Entity, EntityCategory


class FusionSolarAttributeEntity(Entity):
    """Base class for all FusionSolarAttributeEntity entities."""

    def __init__(
            self,
            unique_id,
            name,
            value,
            device_info=None
    ):
        """Initialize the entity"""
        self._unique_id = unique_id
        self._name = name
        self._value = value
        self._device_info = device_info

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self):
        return self._name

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


class FusionSolarCapacityEntity(FusionSolarAttributeEntity):
    _attr_icon = 'mdi:lightning-bolt'


class FusionSolarContactPersonEntity(FusionSolarAttributeEntity):
    _attr_icon = 'mdi:account'


class FusionSolarContactPersonPhoneEntity(FusionSolarAttributeEntity):
    _attr_icon = 'mdi:card-account-phone'


class FusionSolarAddressEntity(FusionSolarAttributeEntity):
    _attr_icon = 'mdi:map-marker'


class FusionSolarLatitudeEntity(FusionSolarAttributeEntity):
    _attr_icon = 'mdi:latitude'


class FusionSolarLongitudeEntity(FusionSolarAttributeEntity):
    _attr_icon = 'mdi:longitude'
