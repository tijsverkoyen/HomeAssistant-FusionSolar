"""Shared fixtures for the FusionSolar tests."""
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fusion_solar.const import DOMAIN

from .const import (
    DEV_LIST,
    DEV_REAL_KPI_BY_TYPE,
    KIOSK_API_URL,
    KIOSK_CONFIG,
    KPI_STATION_YEAR,
    OPENAPI_CONFIG,
    OPENAPI_HOST,
    OPENAPI_TOKEN,
    STATION_LIST,
    STATION_REAL_KPI,
    kiosk_response,
)

pytest_plugins = 'pytest_homeassistant_custom_component'


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow Home Assistant to load the integration from custom_components/."""
    yield


@pytest.fixture
def mock_kiosk_api(requests_mock):
    """Serve a successful kiosk response."""
    requests_mock.get(KIOSK_API_URL, json=kiosk_response())
    return requests_mock


@pytest.fixture
def mock_openapi(requests_mock):
    """Serve a complete, successful set of OpenAPI responses (one station, three devices)."""
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/login', json={'success': True}, headers={'xsrf-token': OPENAPI_TOKEN})
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationList', json=STATION_LIST)
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationRealKpi', json=STATION_REAL_KPI)
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getKpiStationYear', json=KPI_STATION_YEAR)
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getDevList', json=DEV_LIST)
    requests_mock.post(
        f'{OPENAPI_HOST}/thirdData/getDevRealKpi',
        json=lambda request, context: DEV_REAL_KPI_BY_TYPE[request.json()['devTypeId']],
    )
    return requests_mock


@pytest.fixture
def kiosk_entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, title='Fusion Solar', data=KIOSK_CONFIG)
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def openapi_entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, title='Fusion Solar', data=OPENAPI_CONFIG)
    entry.add_to_hass(hass)
    return entry


def get_state(hass: HomeAssistant, unique_id: str, platform: str = 'sensor'):
    """Look up an entity's state by unique ID, so tests don't depend on generated entity IDs."""
    entity_id = er.async_get(hass).async_get_entity_id(platform, DOMAIN, unique_id)
    assert entity_id is not None, f'No {platform} entity with unique_id {unique_id}'
    return hass.states.get(entity_id)
