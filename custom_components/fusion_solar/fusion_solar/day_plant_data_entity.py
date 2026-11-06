import logging
from datetime import time

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy
from homeassistant.util import dt as dt_util

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ONE_DAY_IN_MS = 24 * 60 * 60 * 1000


class FusionSolarDayPlantDataSensor(CoordinatorEntity, SensorEntity):
    """Base class for all FusionSolarDayPlantDataSensor sensors."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    # The values reset every day, so total_increasing is the right state class for the energy dashboard.
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(
            self,
            coordinator,
            station,
    ):
        """Initialize the entity"""
        super().__init__(coordinator)
        self._station = station
        self._device_info = station.device_info()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # The data is only fetched every hour, so re-evaluate at midnight to stop showing yesterday's totals.
        self.async_on_remove(
            async_track_time_change(self.hass, self._async_handle_midnight, hour=0, minute=0, second=0)
        )

    @callback
    def _async_handle_midnight(self, now) -> None:
        self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._station.code}-current_day-{self._attribute}'

    @property
    def native_value(self) -> float:
        key = f'{DOMAIN}-{self._station.code}'

        if not self.coordinator.data or key not in self.coordinator.data:
            return None

        # The API returns one record per day of the current month, keyed by the start of the day (in the timezone of
        # the plant). Use the most recent record that has started.
        now = dt_util.utcnow()
        now_in_ms = round(now.timestamp() * 1000)
        highest_collect_time = 0
        latest_data = None

        for collect_time, data in self.coordinator.data[key].items():
            if highest_collect_time < collect_time <= now_in_ms:
                highest_collect_time = collect_time
                latest_data = data

        if latest_data is None or not self._is_today(highest_collect_time, now):
            return None

        if latest_data.get(self._attribute) is None:
            return None

        return float(latest_data[self._attribute])

    @staticmethod
    def _is_today(collect_time: int, now) -> bool:
        start_of_record = dt_util.as_local(dt_util.utc_from_timestamp(collect_time / 1000))

        # When the plant is in the same timezone as Home Assistant the record starts at local midnight, so compare
        # calendar dates; this also handles the 23 and 25 hour days of a daylight saving time switch.
        if start_of_record.time() == time(0, 0):
            return start_of_record.date() == dt_util.as_local(now).date()

        # Different timezones: we don't know the plant's timezone, so fall back to the age of the record.
        return round(now.timestamp() * 1000) - collect_time < ONE_DAY_IN_MS

    @property
    def device_info(self) -> dict:
        return self._device_info


class FusionSolarDayPlantDataInverterPowerSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'inverter_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Inverter yield'


class FusionSolarDayPlantDataOngridPowerSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'ongrid_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Feed-in energy'


class FusionSolarDayPlantDataUsePowerSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'use_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Consumption'


class FusionSolarDayPlantDataBuyPowerSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'buy_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Energy from grid'


class FusionSolarDayPlantDataSelfUsePowerSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'self_use_power'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Self-consumption'


class FusionSolarDayPlantDataChargeCapSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'charge_cap'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Battery charged energy'


class FusionSolarDayPlantDataDischargeCapSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'discharge_cap'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Battery discharged energy'


class FusionSolarDayPlantDataPowerProfitSensor(FusionSolarDayPlantDataSensor):
    _attribute = 'power_profit'
    # The currency is configured in FusionSolar and not returned by the API, so no monetary device class.
    _attr_device_class = None
    _attr_native_unit_of_measurement = None
    _attr_icon = 'mdi:cash'

    @property
    def name(self) -> str:
        return f'{self._station.readable_name} - Current Day - Revenue'
