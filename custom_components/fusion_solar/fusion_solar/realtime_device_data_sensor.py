import datetime

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT, SensorEntity
from homeassistant.components.binary_sensor import DEVICE_CLASS_CONNECTIVITY, BinarySensorEntity
from homeassistant.const import DEVICE_CLASS_VOLTAGE, ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_CURRENT, \
    ELECTRIC_CURRENT_AMPERE, DEVICE_CLASS_ENERGY, ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, \
    DEVICE_CLASS_POWER_FACTOR, PERCENTAGE, DEVICE_CLASS_FREQUENCY, FREQUENCY_HERTZ, DEVICE_CLASS_POWER, \
    POWER_WATT, POWER_KILO_WATT, DEVICE_CLASS_TIMESTAMP, DEVICE_CLASS_BATTERY

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

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-{self._attribute}'

    @property
    def name(self) -> str:
        return f'{self._device.name} - {self._name}'

    @property
    def state(self) -> float:
        if self._data_name not in self.coordinator.data:
            return None

        if self._attribute not in self.coordinator.data[self._data_name]:
            return None

        if self.coordinator.data[self._data_name][self._attribute] is None:
            return None

        if self.coordinator.data[self._data_name][self._attribute] is None:
            return None

        if self.coordinator.data[self._data_name][self._attribute] == 'N/A':
            return None

        return float(self.coordinator.data[self._data_name][self._attribute])

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarRealtimeDeviceDataReadableInverterStateSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-readable-{self._attribute}'

    @property
    def state(self) -> str:
        state = super().state

        if state is None:
            return None

        if state == 0:
            return "Standby: initializing"
        if state == 1:
            return "Standby: insulation resistance detection"
        if state == 2:
            return "Standby: sunlight detection"
        if state == 3:
            return "Standby: power grid detection"
        if state == 256:
            return "Start"
        if state == 512:
            return "Grid connection"
        if state == 513:
            return "Grid connection: limited power"
        if state == 514:
            return "Grid connection: self-derating"
        if state == 768:
            return "Shutdown: unexpected shutdown"
        if state == 769:
            return "Shutdown: commanded shutdown"
        if state == 770:
            return "Shutdown: OVGR"
        if state == 771:
            return "Shutdown: communication disconnection"
        if state == 772:
            return "Shutdown: limited power"
        if state == 773:
            return "Shutdown: manual startup is required"
        if state == 774:
            return "Shutdown: DC switch disconnected"
        if state == 1025:
            return "Grid scheduling: cosψ-P curve"
        if state == 1026:
            return "Grid scheduling: Q-U curve"
        if state == 1280:
            return "Spot-check ready"
        if state == 1281:
            return "Spot-checking"
        if state == 1536:
            return "Inspecting"
        if state == 1792:
            return "AFCI self-check"
        if state == 2048:
            return "I-V scanning"
        if state == 2304:
            return "DC input detection"
        if state == 40960:
            return "Standby: no sunlight"
        if state == 45056:
            return "Communication disconnection (written by the SmartLogger)"
        if state == 49152:
            return "Loading (written by the SmartLogger)"

        return state


class FusionSolarRealtimeDeviceDataVoltageSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_VOLTAGE

    @property
    def unit_of_measurement(self) -> str:
        return ELECTRIC_POTENTIAL_VOLT

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataCurrentSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_CURRENT

    @property
    def unit_of_measurement(self) -> str:
        return ELECTRIC_CURRENT_AMPERE

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataEnergySensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return ENERGY_KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataTemperatureSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self) -> str:
        return TEMP_CELSIUS

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataPowerFactorSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_POWER_FACTOR

    @property
    def unit_of_measurement(self) -> str:
        return PERCENTAGE

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT

    @property
    def state(self) -> str:
        state = super().state

        if state is None:
            return None

        return state * 100


class FusionSolarRealtimeDeviceDataFrequencySensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_FREQUENCY

    @property
    def unit_of_measurement(self) -> str:
        return FREQUENCY_HERTZ

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataPowerSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_POWER

    @property
    def unit_of_measurement(self) -> str:
        return POWER_KILO_WATT

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataPowerInWattSensor(FusionSolarRealtimeDeviceDataPowerSensor):
    @property
    def unit_of_measurement(self) -> str:
        return POWER_WATT


class FusionSolarRealtimeDeviceDataReactivePowerSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return 'reactive_power'

    @property
    def unit_of_measurement(self) -> str:
        return 'kVar'

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataReactivePowerInVarSensor(FusionSolarRealtimeDeviceDataReactivePowerSensor):
    @property
    def unit_of_measurement(self) -> str:
        return 'Var'


class FusionSolarRealtimeDeviceDataApparentPowerSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return 'apparent_power'

    @property
    def unit_of_measurement(self) -> str:
        return 'kVA'

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataWindSpeedSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return 'wind_speed'

    @property
    def unit_of_measurement(self) -> str:
        return 'm/s'

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataBatterySensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_BATTERY

    @property
    def unit_of_measurement(self) -> str:
        return PERCENTAGE

    @property
    def state_class(self) -> str:
        return STATE_CLASS_MEASUREMENT


class FusionSolarRealtimeDeviceDataTimestampSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_TIMESTAMP

    @property
    def state(self) -> datetime:
        state = super().state

        if state is None:
            return None

        return datetime.datetime.fromtimestamp(state / 1000)


class FusionSolarRealtimeDeviceDataReadableRunStateSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-readable-{self._attribute}'

    @property
    def state(self) -> float:
        state = super().state

        if state is None:
            return None

        if state == 0:
            return "disconnected"
        if state == 1:
            return "connected"

        return None


class FusionSolarRealtimeDeviceDataReadableChargeDischargeModeSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-readable-{self._attribute}'

    @property
    def state(self) -> float:
        state = super().state

        if state is None:
            return None

        if state == 0:
            return "none"
        if state == 1:
            return "forced charge/discharge"
        if state == 2:
            return "time-of-use price"
        if state == 3:
            return "fixed charge/discharge"
        if state == 4:
            return "automatic charge/discharge"

        return None


class FusionSolarRealtimeDeviceDataReadableBatteryStatusSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-readable-{self._attribute}'

    @property
    def state(self) -> float:
        state = super().state

        if state is None:
            return None

        if state == 0:
            return "offline"
        if state == 1:
            return "standby"
        if state == 2:
            return "running"
        if state == 3:
            return "faulty"
        if state == 4:
            return "hibernation"

        return None


class FusionSolarRealtimeDeviceDataReadableMeterStatusSensor(FusionSolarRealtimeDeviceDataSensor):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-readable-{self._attribute}'

    @property
    def state(self) -> float:
        state = super().state

        if state is None:
            return None

        if state == 0:
            return "offline"
        if state == 1:
            return "normal"

        return None


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

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.device_id}-{self._attribute}'

    @property
    def name(self) -> str:
        return f'{self._device.name} - {self._name}'

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarRealtimeDeviceDataStateBinarySensor(FusionSolarRealtimeDeviceDataBinarySensor):
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_CONNECTIVITY

    @property
    def is_on(self) -> bool:
        if self._data_name not in self.coordinator.data:
            return None

        if self._attribute not in self.coordinator.data[self._data_name]:
            return None

        state = self.coordinator.data[self._data_name][self._attribute]

        if state == 0:
            return False
        if state == 1:
            return True

        return None
