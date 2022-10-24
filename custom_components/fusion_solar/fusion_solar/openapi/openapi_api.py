"""API client for FusionSolar OpenAPI."""
import logging

from requests import post

from ..const import ATTR_SUCCESS, ATTR_DATA, ATTR_FAIL_CODE, ATTR_MESSAGE, ATTR_STATION_CODE, \
    ATTR_STATION_NAME, ATTR_PARAMS, ATTR_PARAMS_CURRENT_TIME
from .station import FusionSolarStation

_LOGGER = logging.getLogger(__name__)


class FusionSolarOpenApi:
    def __init__(self, host: str, username: str, password: str):
        self._token = None
        self._last_station_list_current_time = None
        self._host = host
        self._username = username
        self._password = password

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

            raise FusionSolarOpenApiError(f'Could not login with given credentials')
        except Exception as error:
            raise FusionSolarOpenApiError(f'Could not login with given credentials')

    def get_station_list(self):
        url = self._host + '/thirdData/getStationList'
        json = {}
        response = self._do_call(url, json)

        if ATTR_PARAMS in response and ATTR_PARAMS_CURRENT_TIME in response[ATTR_PARAMS]:
            self._last_station_list_current_time = response[ATTR_PARAMS][ATTR_PARAMS_CURRENT_TIME]

        data = []
        for station in response[ATTR_DATA]:
            data.append(
                FusionSolarStation(station[ATTR_STATION_CODE], station[ATTR_STATION_NAME])
            )

        return data

    def get_station_real_kpi(self, station_codes: list):
        url = self._host + '/thirdData/getStationRealKpi'
        json = {
            'stationCodes': ','.join(station_codes),
        }
        response = self._do_call(url, json)

        return response[ATTR_DATA]

    def get_kpi_station_year(self, station_codes: list):
        if self._last_station_list_current_time is None:
            self.get_station_list()

        url = self._host + '/thirdData/getKpiStationYear'
        json = {
            'stationCodes': ','.join(station_codes),
            'collectTime': self._last_station_list_current_time,
        }
        response = self._do_call(url, json)

        return response[ATTR_DATA]

    def _do_call(self, url: str, json: dict):
        if self._token is None:
            self.login()

        headers = {
            'accept': 'application/json',
            'xsrf-token': self._token,
        }

        try:
            response = post(url, headers=headers, json=json)
            response.raise_for_status()
            json_data = response.json()
            _LOGGER.debug(f'JSON data for {url}: {json_data}')

            if ATTR_FAIL_CODE in json_data and json_data[ATTR_FAIL_CODE] == 305:
                _LOGGER.debug('Token expired, trying to login again')
                # token expired
                self._token = None
                return self._do_call(url, json)

            if ATTR_SUCCESS in json_data and not json_data[ATTR_SUCCESS]:
                raise FusionSolarOpenApiError(
                    f'Retrieving the data failed with failCode: {json_data[ATTR_FAIL_CODE]}, message: {json_data[ATTR_MESSAGE]}'
                )

            return json_data

        except KeyError as error:
            _LOGGER.error(error)
            _LOGGER.error(response.text)


class FusionSolarOpenApiError(Exception):
    pass
