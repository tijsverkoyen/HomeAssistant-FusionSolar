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
        api = FusionSolarKioksApi('https://eu5.fusionsolar.huawei.com')
        data = {}
        for kiosk in config[CONF_KIOSKS]:
            data[kiosk['id']] = {
                ATTR_DATA_REALKPI: await hass.async_add_executor_job(api.getRealTimeKpi, kiosk['id'])
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

    async_add_entities(
        FusionSolarKioskSensorRealtimePower(
            coordinator,
            kiosk['id'],
            kiosk['name'],
            ID_REALTIME_POWER,
            NAME_REALTIME_POWER,
            ATTR_REALTIME_POWER,
        ) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalCurrentDayEnergy(
            coordinator,
            kiosk['id'],
            kiosk['name'],
            ID_TOTAL_CURRENT_DAY_ENERGY,
            NAME_TOTAL_CURRENT_DAY_ENERGY,
            ATTR_TOTAL_CURRENT_DAY_ENERGY,
        ) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalCurrentMonthEnergy(
            coordinator,
            kiosk['id'],
            kiosk['name'],
            ID_TOTAL_CURRENT_MONTH_ENERGY,
            NAME_TOTAL_CURRENT_MONTH_ENERGY,
            ATTR_TOTAL_CURRENT_MONTH_ENERGY,
        ) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalCurrentYearEnergy(
            coordinator,
            kiosk['id'],
            kiosk['name'],
            ID_TOTAL_CURRENT_YEAR_ENERGY,
            NAME_TOTAL_CURRENT_YEAR_ENERGY,
            ATTR_TOTAL_CURRENT_YEAR_ENERGY,
        ) for kiosk in config[CONF_KIOSKS]
    )
    async_add_entities(
        FusionSolarKioskSensorTotalLifetimeEnergy(
            coordinator,
            kiosk['id'],
            kiosk['name'],
            ID_TOTAL_LIFETIME_ENERGY,
            NAME_TOTAL_LIFETIME_ENERGY,
            ATTR_TOTAL_LIFETIME_ENERGY,
        ) for kiosk in config[CONF_KIOSKS]
    )


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
