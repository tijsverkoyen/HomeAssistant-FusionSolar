"""FusionSolar Kiosk sensor."""
from .fusion_solar_kiosk_api import *
import homeassistant.helpers.config_validation as cv
import logging
import voluptuous as vol

from . import FusionSolarKioskEnergyEntity, FusionSolarKioskPowerEntity

from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import *

import re
from urllib.parse import urlparse

KIOSK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_KIOSK_URL): cv.string,
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
    async def async_update_data():
        """Fetch data"""
        data = {}
        for kioskConfig in config[CONF_KIOSKS]:
            kiosk = Kiosk(kioskConfig['url'], kioskConfig['name'])
            api = FusionSolarKioksApi(kiosk.apiUrl())
            data[kiosk.id] = {
                ATTR_DATA_REALKPI: await hass.async_add_executor_job(api.getRealTimeKpi, kiosk.id)
            }
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarKiosk',
        update_method=async_update_data,
        update_interval=timedelta(seconds=300),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    for kioskConfig in config[CONF_KIOSKS]:
        kiosk = Kiosk(kioskConfig['url'], kioskConfig['name'])

        async_add_entities([
            FusionSolarKioskSensorRealtimePower(
                coordinator,
                kiosk.id,
                kiosk.name,
                ID_REALTIME_POWER,
                NAME_REALTIME_POWER,
                ATTR_REALTIME_POWER,
            ),
            FusionSolarKioskSensorTotalCurrentDayEnergy(
                coordinator,
                kiosk.id,
                kiosk.name,
                ID_TOTAL_CURRENT_DAY_ENERGY,
                NAME_TOTAL_CURRENT_DAY_ENERGY,
                ATTR_TOTAL_CURRENT_DAY_ENERGY,
            ),
            FusionSolarKioskSensorTotalCurrentMonthEnergy(
                coordinator,
                kiosk.id,
                kiosk.name,
                ID_TOTAL_CURRENT_MONTH_ENERGY,
                NAME_TOTAL_CURRENT_MONTH_ENERGY,
                ATTR_TOTAL_CURRENT_MONTH_ENERGY,
            ),
            FusionSolarKioskSensorTotalCurrentYearEnergy(
                coordinator,
                kiosk.id,
                kiosk.name,
                ID_TOTAL_CURRENT_YEAR_ENERGY,
                NAME_TOTAL_CURRENT_YEAR_ENERGY,
                ATTR_TOTAL_CURRENT_YEAR_ENERGY,
            ),
            FusionSolarKioskSensorTotalLifetimeEnergy(
                coordinator,
                kiosk.id,
                kiosk.name,
                ID_TOTAL_LIFETIME_ENERGY,
                NAME_TOTAL_LIFETIME_ENERGY,
                ATTR_TOTAL_LIFETIME_ENERGY,
            )
        ])

class Kiosk:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self._parseId()

    def _parseId(self):
        id = re.search("\?kk=(.*)", self.url).group(1)
        _LOGGER.debug('calculated KioskId: ' + id)
        self.id = id

    def apiUrl(self):
        url = urlparse(self.url)
        apiUrl = (url.scheme + "://" + url.netloc)
        _LOGGER.debug('calculated API base url for ' + self.id + ': ' + apiUrl)
        return apiUrl


class FusionSolarKioskSensorRealtimePower(FusionSolarKioskPowerEntity):
    pass

class FusionSolarKioskSensorTotalCurrentDayEnergy(FusionSolarKioskEnergyEntity):
    pass

class FusionSolarKioskSensorTotalCurrentMonthEnergy(FusionSolarKioskEnergyEntity):
    pass

class FusionSolarKioskSensorTotalCurrentYearEnergy(FusionSolarKioskEnergyEntity):
    pass

class FusionSolarKioskSensorTotalLifetimeEnergy(FusionSolarKioskEnergyEntity):
    pass
