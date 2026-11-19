"""API client for FusionSolar Kiosk."""
import logging
import html
import json

from ..const import (
    REQUEST_TIMEOUT,
    ATTR_DATA,
    ATTR_FAIL_CODE,
    ATTR_SUCCESS,
    ATTR_DATA_REALKPI,
)

from requests import get, RequestException

_LOGGER = logging.getLogger(__name__)


class FusionSolarKioskApi:
    def __init__(self, host):
        self._host = host

    def getRealTimeKpi(self, id: str):
        url = self._host + '/rest/pvms/web/kiosk/v1/station-kiosk-file?kk=' + id
        headers = {
            'accept': 'application/json',
        }

        try:
            response = get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            jsonData = response.json()

            if jsonData is None or ATTR_SUCCESS not in jsonData or not jsonData[ATTR_SUCCESS]:
                raise FusionSolarKioskApiError(f'Retrieving the data failed. Raw response: {response.text}')

            # convert encoded html string to JSON
            jsonData[ATTR_DATA] = json.loads(html.unescape(jsonData[ATTR_DATA]))
            _LOGGER.debug('Received data for ' + id + ': ')
            _LOGGER.debug(jsonData[ATTR_DATA][ATTR_DATA_REALKPI])
            return jsonData[ATTR_DATA][ATTR_DATA_REALKPI]

        except KeyError as error:
            _LOGGER.error(error)
            _LOGGER.error(response.text)

        except FusionSolarKioskApiError as error:
            _LOGGER.error(error)
            _LOGGER.debug(response.text)

        except RequestException as error:
            _LOGGER.error(f'Request to {url} failed: {error}')

        return {
            ATTR_SUCCESS: False
        }


class FusionSolarKioskApiError(Exception):
    pass
