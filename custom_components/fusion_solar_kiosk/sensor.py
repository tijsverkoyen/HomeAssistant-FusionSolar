"""FusionSolar Kiosk sensor."""
import async_timeout
import json
import homeassistant.helpers.config_validation as cv
import logging
import sys
import voluptuous as vol

from . import FusionSolarKioskEnergyEntity, FusionSolarKioskPowerEntity

from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from requests import post
from .const import *

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
    async def async_update_data():
        #try:
        #     # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        #     # handled by the data update coordinator.
        #     async with async_timeout.timeout(10):
        #         return await api.fetch_data()
        # except ApiError as err:
        #     raise UpdateFailed(f"Error communicating with API: {err}")

        url = "https://eu5.fusionsolar.huawei.com/kiosk/getRealTimeKpi"
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
        }

        data = {}

        for kiosk in config[CONF_KIOSKS]:
            requestBody = {"kk": kiosk['id']}
            data[kiosk['id']] = {}

            try:
                response = post(url, headers=headers, data=json.dumps(requestBody))
                responseData = json.loads(response.text)

                data[kiosk['id']][ATTR_SUCCESS] = responseData["success"]
                data[kiosk['id']][ATTR_REALTIME_POWER] = responseData["data"][ATTR_REALTIME_POWER]
                data[kiosk['id']][ATTR_TOTAL_CURRENT_DAY_ENERGY] = responseData["data"][ATTR_TOTAL_CURRENT_DAY_ENERGY]
                data[kiosk['id']][ATTR_TOTAL_CURRENT_MONTH_ENERGY] = responseData["data"][ATTR_TOTAL_CURRENT_MONTH_ENERGY]
                data[kiosk['id']][ATTR_TOTAL_CURRENT_YEAR_ENERGY] = responseData["data"][ATTR_TOTAL_CURRENT_YEAR_ENERGY]
                data[kiosk['id']][ATTR_TOTAL_LIFETIME_ENERGY] = responseData["data"][ATTR_TOTAL_LIFETIME_ENERGY]

                if not responseData["success"]:
                    failCode = responseData["failCode"]
                    raise RuntimeError(f'Retrieving the data failed with failCode: {failCode}')
            except RuntimeError as error:
                _LOGGER.error(error)
                _LOGGER.debug(response.text)
            except:
                # self._available = False
                _LOGGER.error('Unknown error while retrieving data.')
                _LOGGER.debug(response.text)
                _LOGGER.debug(sys.exc_info()[0])

        return data


    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="FusionSolarKiosk",
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
