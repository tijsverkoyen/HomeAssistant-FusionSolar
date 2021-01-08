"""API client for FusionSolar Kiosk."""
import logging

from .const import (
    ATTR_DATA,
    ATTR_FAIL_CODE,
    ATTR_SUCCESS,
)

from requests import post

_LOGGER = logging.getLogger(__name__)

class FusionSolarKioksApi:
    def __init__(self, host):
        self._host = host

    def getRealTimeKpi(self, id: str):
        url = self._host + '/kiosk/getRealTimeKpi'
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
        }
        payload = {'kk': id}

        try:
            response = post(url, headers=headers, json=payload)
            jsonData = response.json()

            if not jsonData[ATTR_SUCCESS]:
                raise FusionSolarKioskApiError(f'Retrieving the data failed with failCode: {jsonData[ATTR_FAIL_CODE]}, data: {jsonData[ATTR_DATA]}')

            return jsonData

        except FusionSolarKioskApiError as error:
            _LOGGER.error(error)
            _LOGGER.debug(response.text)

        except FusionSolarKioskApiError as error:
            _LOGGER.error(error)
            _LOGGER.debug(response.text)
    
        return {
            ATTR_SUCCESS: False
        }

class FusionSolarKioskApiError(Exception):
    pass