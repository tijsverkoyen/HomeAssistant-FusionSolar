"""Tests for the config flow."""
from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.fusion_solar.const import (
    CONF_KIOSKS,
    CONF_OPENAPI_CREDENTIALS,
    CONF_TYPE,
    CONF_TYPE_KIOSK,
    CONF_TYPE_OPENAPI,
    DOMAIN,
)
from custom_components.fusion_solar.fusion_solar.openapi.openapi_api import FusionSolarOpenApiError

from .const import KIOSK_NAME, KIOSK_URL, OPENAPI_HOST

LOGIN = 'custom_components.fusion_solar.config_flow.FusionSolarOpenApi.login'


@pytest.fixture(autouse=True)
def bypass_setup_entry():
    """Creating an entry must not start the real integration."""
    with patch('custom_components.fusion_solar.async_setup_entry', return_value=True) as mock:
        yield mock


async def start_flow(hass: HomeAssistant, flow_type: str):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER})
    assert result['type'] is FlowResultType.FORM
    assert result['step_id'] == 'choose_type'

    return await hass.config_entries.flow.async_configure(result['flow_id'], {CONF_TYPE: flow_type})


async def test_kiosk_flow_creates_entry(hass: HomeAssistant, bypass_setup_entry):
    result = await start_flow(hass, CONF_TYPE_KIOSK)
    assert result['type'] is FlowResultType.FORM
    assert result['step_id'] == 'kiosk'

    result = await hass.config_entries.flow.async_configure(
        result['flow_id'], {CONF_NAME: KIOSK_NAME, CONF_URL: KIOSK_URL}
    )
    await hass.async_block_till_done()

    assert result['type'] is FlowResultType.CREATE_ENTRY
    assert result['title'] == 'Fusion Solar'
    assert result['data'] == {
        CONF_KIOSKS: [{CONF_NAME: KIOSK_NAME, CONF_URL: KIOSK_URL}],
        CONF_OPENAPI_CREDENTIALS: {},
    }
    assert len(bypass_setup_entry.mock_calls) == 1


async def test_kiosk_flow_add_another(hass: HomeAssistant):
    result = await start_flow(hass, CONF_TYPE_KIOSK)

    result = await hass.config_entries.flow.async_configure(
        result['flow_id'], {CONF_NAME: 'First', CONF_URL: KIOSK_URL, 'add_another': True}
    )
    assert result['type'] is FlowResultType.FORM
    assert result['step_id'] == 'kiosk'

    result = await hass.config_entries.flow.async_configure(
        result['flow_id'], {CONF_NAME: 'Second', CONF_URL: f'{KIOSK_URL}2'}
    )

    assert result['type'] is FlowResultType.CREATE_ENTRY
    assert [k[CONF_NAME] for k in result['data'][CONF_KIOSKS]] == ['First', 'Second']


async def test_openapi_flow_creates_entry(hass: HomeAssistant):
    result = await start_flow(hass, CONF_TYPE_OPENAPI)
    assert result['type'] is FlowResultType.FORM
    assert result['step_id'] == 'openapi'

    user_input = {CONF_HOST: OPENAPI_HOST, CONF_USERNAME: 'api-user', CONF_PASSWORD: 'api-password'}
    with patch(LOGIN, return_value='token') as login:
        result = await hass.config_entries.flow.async_configure(result['flow_id'], user_input)
    await hass.async_block_till_done()

    assert login.call_count == 1
    assert result['type'] is FlowResultType.CREATE_ENTRY
    assert result['data'] == {CONF_KIOSKS: [], CONF_OPENAPI_CREDENTIALS: user_input}


async def test_openapi_flow_invalid_credentials(hass: HomeAssistant):
    result = await start_flow(hass, CONF_TYPE_OPENAPI)

    user_input = {CONF_HOST: OPENAPI_HOST, CONF_USERNAME: 'api-user', CONF_PASSWORD: 'wrong'}
    with patch(LOGIN, side_effect=FusionSolarOpenApiError('nope')):
        result = await hass.config_entries.flow.async_configure(result['flow_id'], user_input)

    assert result['type'] is FlowResultType.FORM
    assert result['step_id'] == 'openapi'
    assert result['errors'] == {'base': 'invalid_credentials'}

    # The user can correct the credentials and finish the flow.
    with patch(LOGIN, return_value='token'):
        result = await hass.config_entries.flow.async_configure(result['flow_id'], {**user_input, CONF_PASSWORD: 'ok'})

    assert result['type'] is FlowResultType.CREATE_ENTRY


async def test_flows_do_not_share_data(hass: HomeAssistant):
    for name in ('First', 'Second'):
        result = await start_flow(hass, CONF_TYPE_KIOSK)
        result = await hass.config_entries.flow.async_configure(
            result['flow_id'], {CONF_NAME: name, CONF_URL: KIOSK_URL}
        )

    assert [k[CONF_NAME] for k in result['data'][CONF_KIOSKS]] == ['Second']
