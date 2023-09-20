import datetime

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTemperature, UnitOfElectricCurrent, \
    UnitOfElectricPotential, UnitOfFrequency

from .openapi.device import FusionSolarDevice
from ..const import DOMAIN


class FusionSolarRealtimeDeviceDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarRealtimeDeviceDataSensor sensors."""

    def __init__(
            self,
            coordinator,
            device: FusionSolarDevice,
            name: str,
            attribute: str
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._device = device
        self._name = name
        self._attribute = attribute
        self._data_name = f'{DOMAIN}-{device.device_id}'
        self._device_info = device.device_info()
        self._state = '__NOT_INITIALIZED__'

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-{self._attribute}'

    @property
    def name(self) -> str:
        return f'{self._device.name} - {self._name}'

    @property
    def native_value(self) -> float:
        if self._state == '__NOT_INITIALIZED__':
            # check if data is available
            self._handle_coordinator_update()

        if self._state is None or self._state == '__NOT_INITIALIZED__':
            return None

        return float(self._state)

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

        self.async_write_ha_state()


class FusionSolarRealtimeDeviceDataTranslatedSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def state(self) -> int:
        if self._state == '__NOT_INITIALIZED__':
            # check if data is available
            self._handle_coordinator_update()

        if self._state is None or self._state == '__NOT_INITIALIZED__':
            return None

        return int(self._state)

    @property
    def translation_key(self) -> str:
        return self._attribute


class FusionSolarRealtimeDeviceDataVoltageSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.VOLTAGE

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfElectricPotential.VOLT

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataCurrentSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.CURRENT

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfElectricCurrent.AMPERE

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataEnergySensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL


class FusionSolarRealtimeDeviceDataEnergyTotalIncreasingSensor(FusionSolarRealtimeDeviceDataEnergySensor):
    @property
    def state_class(self) -> str:
        return SensorStateClass.TOTAL_INCREASING


class FusionSolarRealtimeDeviceDataTemperatureSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataPowerFactorSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.POWER_FACTOR

    @property
    def native_unit_of_measurement(self) -> str:
        return PERCENTAGE

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> str:
        native_value = super().native_value

        if native_value is None:
            return None

        return native_value * 100


class FusionSolarRealtimeDeviceDataFrequencySensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.FREQUENCY

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfFrequency.HERTZ

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataPowerSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.POWER

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfPower.KILO_WATT

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataPowerInWattSensor(FusionSolarRealtimeDeviceDataPowerSensor):
    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfPower.WATT


class FusionSolarRealtimeDeviceDataReactivePowerSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.REACTIVE_POWER

    @property
    def native_unit_of_measurement(self) -> str:
        return 'var'

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float:
        native_value = super().native_value

        if native_value is None:
            return None

        return native_value * 1000



class FusionSolarRealtimeDeviceDataReactivePowerInVarSensor(FusionSolarRealtimeDeviceDataReactivePowerSensor):
    @property
    def native_unit_of_measurement(self) -> str:
        return 'var'


class FusionSolarRealtimeDeviceDataApparentPowerSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return 'apparent_power'

    @property
    def native_unit_of_measurement(self) -> str:
        return 'kVA'

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataWindSpeedSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return 'wind_speed'

    @property
    def native_unit_of_measurement(self) -> str:
        return 'm/s'

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataBatterySensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.BATTERY

    @property
    def native_unit_of_measurement(self) -> str:
        return PERCENTAGE

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataTimestampSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.TIMESTAMP

    @property
    def state(self) -> datetime:
        state = super().native_value

        if state is None:
            return None

        return datetime.datetime.fromtimestamp(state / 1000)


class FusionSolarRealtimeDeviceDataPercentageSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def native_unit_of_measurement(self) -> str | None:
        return PERCENTAGE

    @property
    def state_class(self) -> str:
        return SensorStateClass.MEASUREMENT


class FusionSolarRealtimeDeviceDataBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for all FusionSolarRealtimeDeviceDataBinarySensor sensors."""

    def __init__(
            self,
            coordinator,
            device: FusionSolarDevice,
            name: str,
            attribute: str
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._device = device
        self._name = name
        self._attribute = attribute
        self._data_name = f'{DOMAIN}-{device.device_id}'
        self._device_info = device.device_info()
        self._state = '__NOT_INITIALIZED__'

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-{self._attribute}'

    @property
    def name(self) -> str:
        return f'{self._device.name} - {self._name}'

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
        else:
            self._state = float(self.coordinator.data[self._data_name][self._attribute])

        self.async_write_ha_state()


class FusionSolarRealtimeDeviceDataStateBinarySensor(FusionSolarRealtimeDeviceDataBinarySensor):
    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool:
        if self._state == '__NOT_INITIALIZED__':
            # check if data is available
            self._handle_coordinator_update()

        if self._state is None or self._state == '__NOT_INITIALIZED__':
            return None

        if self._state == 0:
            return False
        if self._state == 1:
            return True

        return None
