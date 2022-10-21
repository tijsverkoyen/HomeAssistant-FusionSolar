"""API client for FusionSolar OpenAPI."""
import logging

from requests import post

_LOGGER = logging.getLogger(__name__)


class FusionSolarOpenApi:
    def __init__(self, host: str):
        self._host = host
        self._token = None

    def login(self, username: str, password) -> str:
        url = self._host + '/thirdData/login'
        headers = {
            'accept': 'application/json',
        }
        json = {
            'userName': username,
            'systemCode': password,
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


class FusionSolarOpenApiError(Exception):
    pass
