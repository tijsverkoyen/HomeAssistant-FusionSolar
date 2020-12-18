"""FusionSolar Kiosk sensor."""
import logging
_LOGGER = logging.getLogger(__name__)

from datetime import timedelta
import json
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    POWER_WATT,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

import homeassistant.helpers.config_validation as cv
from requests import post
import sys
from typing import Any, Callable, Dict, Optional
import voluptuous as vol

from .const import (
    ATTR_ID,
    ATTR_NAME,
    ATTR_REALTIME_POWER,
    ATTR_TOTAL_CURRENT_DAY_ENERGY,
    ATTR_TOTAL_CURRENT_MONTH_ENERGY,
    ATTR_TOTAL_CURRENT_YEAR_ENERGY,
    ATTR_TOTAL_LIFETIME_ENERGY,
)

SCAN_INTERVAL = timedelta(minutes=1)

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

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    sensors = [FusionSolarKioskSensor(kiosk['id'], kiosk['name']) for kiosk in config[CONF_KIOSKS]]
    async_add_entities(sensors, update_before_add=True)

class FusionSolarKioskSensor(Entity):
    """Representation of a FusionSolar Kiosk sensor."""
    def __init__(self, id, name):
        super().__init__()
        self._id = id
        self._name = name
        self._state = None
        self._available = True
        self.attrs: Dict[str, Any] = {ATTR_ID: self._id, ATTR_NAME: self._name}

        self._icon = "mdi:solar-power"
        self._unit = POWER_WATT

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def async_update(self):
        _LOGGER.debug('async update')

        url = "https://eu5.fusionsolar.huawei.com/kiosk/getRealTimeKpi"
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
        }
        data = {"kk":self._id}

        try:
            response = post(url, headers=headers, data=json.dumps(data))
            data = json.loads(response.text)
            _LOGGER.debug(data['data'])

            self._available = data["success"]
            self.attrs[ATTR_REALTIME_POWER] = data["data"][ATTR_REALTIME_POWER]
            self.attrs[ATTR_TOTAL_CURRENT_DAY_ENERGY] = data["data"][ATTR_TOTAL_CURRENT_DAY_ENERGY]
            self.attrs[ATTR_TOTAL_CURRENT_MONTH_ENERGY] = data["data"][ATTR_TOTAL_CURRENT_MONTH_ENERGY]
            self.attrs[ATTR_TOTAL_CURRENT_YEAR_ENERGY] = data["data"][ATTR_TOTAL_CURRENT_YEAR_ENERGY]
            self.attrs[ATTR_TOTAL_LIFETIME_ENERGY] = data["data"][ATTR_TOTAL_LIFETIME_ENERGY]

            if not data["success"]:
                failCode = data["failCode"]
                raise RuntimeError(f'Retrieving the data failed with failCode: {failCode}')
        except RuntimeError as error:
            _LOGGER.error(error)
            _LOGGER.debug(response.text)
        except:
            self._available = False
            _LOGGER.error('Unknown error while retrieving data.')
            _LOGGER.debug(response.text)
            _LOGGER.debug(sys.exc_info()[0])
