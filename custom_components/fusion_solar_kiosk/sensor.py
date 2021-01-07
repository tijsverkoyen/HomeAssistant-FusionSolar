"""FusionSolar Kiosk sensor."""
import async_timeout
import homeassistant.helpers.config_validation as cv
import logging
import voluptuous as vol

from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from typing import Any, Callable, Dict, Optional

from .const import DOMAIN

CONF_KIOSKS = "kiosks"
KIOSK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KIOSKS): vol.All(cv.ensure_list, [KIOSK_SCHEMA]),
    }
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#     api = hass.data[DOMAIN][entry.entry_id]

    async def async_update_data():
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # try:
        #     # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        #     # handled by the data update coordinator.
        #     async with async_timeout.timeout(10):
        #         return await api.fetch_data()
        # except ApiError as err:
        #     raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="FusionSolarKiosk",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    async_add_entities(
        FusionSolarKioskSensorRealtimePower(coordinator, kiosk['id'], kiosk['name']) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalCurrentDayEnergy(coordinator, kiosk['id'], kiosk['name']) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalCurrentMonthEnergy(coordinator, kiosk['id'], kiosk['name']) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalCurrentYearEnergy(coordinator, kiosk['id'], kiosk['name']) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalLifetimeEnergy(coordinator, kiosk['id'], kiosk['name']) for kiosk in config[CONF_KIOSKS]
    )


class FusionSolarKioskSensorRealtimePower(CoordinatorEntity, Entity):
    """Representation of the real-time power of the installation"""
    def __init__(self, coordinator, id, name):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.kioskId = id
        self.kioskName = name

    @property
    def device_class(self):
        return DEVICE_CLASS_POWER

    @property
    def name(self):
        return f'{self.kioskName} ({self.kioskId}) - Realtime Power'

    @property
    def state(self):
        return 100

    @property
    def unique_id(self):
        return f'fusion_solar_{self.kioskId})_realtime_power'

    @property
    def unit_of_measurement(self):
        return POWER_KILO_WATT

class FusionSolarKioskSensorTotalCurrentDayEnergy(CoordinatorEntity, Entity):
    """Representation of the daily energy of the installation"""
    def __init__(self, coordinator, id, name):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.kioskId = id
        self.kioskName = name

    @property
    def device_class(self):
        return DEVICE_CLASS_ENERGY

    @property
    def name(self):
        return f'{self.kioskName} ({self.kioskId}) - Current Day Energy'

    @property
    def state(self):
        return 100

    @property
    def unique_id(self):
        return f'fusion_solar_{self.kioskId})_current_day_energy'

    @property
    def unit_of_measurement(self):
        return ENERGY_KILO_WATT_HOUR


class FusionSolarKioskSensorTotalCurrentMonthEnergy(CoordinatorEntity, Entity):
    """Representation of the monthly energy of the installation"""
    def __init__(self, coordinator, id, name):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.kioskId = id
        self.kioskName = name

        _LOGGER.debug(self)
 
    @property
    def device_class(self):
        return DEVICE_CLASS_ENERGY

    @property
    def name(self):
        return f'{self.kioskName} ({self.kioskId}) - Current Month Energy'

    @property
    def state(self):
        return 100

    @property
    def unique_id(self):
        return f'fusion_solar_{self.kioskId})_current_month_energy'

    @property
    def unit_of_measurement(self):
        return ENERGY_KILO_WATT_HOUR

class FusionSolarKioskSensorTotalCurrentYearEnergy(CoordinatorEntity, Entity):
    """Representation of the annual energy of the installation"""
    def __init__(self, coordinator, id, name):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.kioskId = id
        self.kioskName = name

    @property
    def device_class(self):
        return DEVICE_CLASS_ENERGY

    @property
    def name(self):
        return f'{self.kioskName} ({self.kioskId}) - Current Year Energy'

    @property
    def state(self):
        return 100

    @property
    def unique_id(self):
        return f'fusion_solar_{self.kioskId})_current_year_energy'

    @property
    def unit_of_measurement(self):
        return ENERGY_KILO_WATT_HOUR

class FusionSolarKioskSensorTotalLifetimeEnergy(CoordinatorEntity, Entity):
    """Representation of the lifetime energy of the installation"""
    def __init__(self, coordinator, id, name):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.kioskId = id
        self.kioskName = name

    @property
    def device_class(self):
        return DEVICE_CLASS_ENERGY

    @property
    def name(self):
        return f'{self.kioskName} ({self.kioskId}) - Lifetime Energy'

    @property
    def state(self):
        return 100

    @property
    def unique_id(self):
        return f'fusion_solar_{self.kioskId})_lifetime_energy'

    @property
    def unit_of_measurement(self):
        return ENERGY_KILO_WATT_HOUR
