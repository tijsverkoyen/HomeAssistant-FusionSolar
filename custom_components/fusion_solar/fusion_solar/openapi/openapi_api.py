"""API client for FusionSolar OpenAPI."""
import logging

from requests import post

from ..const import ATTR_SUCCESS, ATTR_DATA, ATTR_FAIL_CODE, ATTR_MESSAGE, ATTR_STATION_CODE, ATTR_STATION_NAME
from .station import FusionSolarStation

_LOGGER = logging.getLogger(__name__)


class FusionSolarOpenApi:
    def __init__(self, host: str, username: str, password: str):
        self._host = host
        self._username = username
        self._password = password
        self._token = None

    def login(self) -> str:
        url = self._host + '/thirdData/login'
        headers = {
            'accept': 'application/json',
        }
        json = {
            'userName': self._username,
            'systemCode': self._password,
        }

        try:
            response = post(url, headers=headers, json=json)
            response.raise_for_status()

            if 'xsrf-token' in response.headers:
                self._token = response.headers['xsrf-token']
                return response.headers.get("xsrf-token")

            _LOGGER.debug(response.json())
            _LOGGER.debug(response.headers())
            raise FusionSolarOpenApiError(f'Could not login with given credentials')
        except Exception as error:
            raise FusionSolarOpenApiError(f'Could not login with given credentials')

    def get_station_list(self):
        if self._token is None:
            self.login()

        url = self._host + '/thirdData/getStationList'
        headers = {
            'accept': 'application/json',
            'xsrf-token': self._token,
        }
        json = {}

        try:
            response = post(url, headers=headers, json=json)
            response.raise_for_status()
            jsonData = response.json()
            _LOGGER.debug(jsonData)

            if ATTR_SUCCESS in jsonData and not jsonData[ATTR_SUCCESS]:
                raise FusionSolarOpenApiError(
                    f'Retrieving the data failed with failCode: {jsonData[ATTR_FAIL_CODE]}, message: {jsonData[ATTR_MESSAGE]}'
                )

            # convert encoded html string to JSON
            _LOGGER.debug('Received data for getStationList:')
            _LOGGER.debug(jsonData[ATTR_DATA])

            data = []
            for station in jsonData[ATTR_DATA]:
                data.append(
                    FusionSolarStation(station[ATTR_STATION_CODE], station[ATTR_STATION_NAME])
                )

            return data

        except KeyError as error:
            _LOGGER.error(error)
            _LOGGER.error(response.text)

    def get_station_real_kpi(self, station_codes: list):
        if self._token is None:
            self.login()

        url = self._host + '/thirdData/getStationRealKpi'
        headers = {
            'accept': 'application/json',
            'xsrf-token': self._token,
        }
        json = {
            'stationCodes': ','.join(station_codes),
        }

        try:
            response = post(url, headers=headers, json=json)
            response.raise_for_status()
            jsonData = response.json()
            _LOGGER.debug(jsonData)

            if ATTR_SUCCESS in jsonData and not jsonData[ATTR_SUCCESS]:
                raise FusionSolarOpenApiError(
                    f'Retrieving the data failed with failCode: {jsonData[ATTR_FAIL_CODE]}, message: {jsonData[ATTR_MESSAGE]}'
                )

            # convert encoded html string to JSON
            _LOGGER.debug('Received data for getStationRealKpi:')
            _LOGGER.debug(jsonData[ATTR_DATA])

            return jsonData[ATTR_DATA]

        except KeyError as error:
            _LOGGER.error(error)
            _LOGGER.error(response.text)


class FusionSolarOpenApiError(Exception):
    pass
