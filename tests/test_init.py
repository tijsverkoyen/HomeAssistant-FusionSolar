"""End-to-end tests: load the integration in Home Assistant against mocked FusionSolar APIs."""
from datetime import timedelta

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.fusion_solar.const import DOMAIN

from .conftest import get_state
from .const import (
    BATTERY_ID,
    INVERTER_ID,
    KIOSK_API_URL,
    KIOSK_ID,
    KIOSK_REAL_KPI,
    OPENAPI_HOST,
    POWER_SENSOR_ID,
    STATION_CODE,
    kiosk_response,
)


async def setup_entry(hass: HomeAssistant, entry):
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED


async def advance(hass: HomeAssistant, seconds: int):
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=seconds))
    await hass.async_block_till_done(wait_background_tasks=True)


# --- Kiosk -----------------------------------------------------------------

async def test_kiosk_setup_creates_sensors(hass: HomeAssistant, kiosk_entry, mock_kiosk_api):
    await setup_entry(hass, kiosk_entry)

    power = get_state(hass, f'{DOMAIN}-{KIOSK_ID}-realtime_power')
    assert power.state == '2.512'
    assert power.attributes['unit_of_measurement'] == 'kW'
    assert power.attributes['device_class'] == 'power'

    expected = {
        'total_current_day_energy': '12.34',
        'total_current_month_energy': '234.5',
        'total_current_year_energy': '3456.7',
        'total_lifetime_energy': '12345.6',
    }
    for suffix, value in expected.items():
        state = get_state(hass, f'{DOMAIN}-{KIOSK_ID}-{suffix}')
        assert state.state == value, suffix
        assert state.attributes['unit_of_measurement'] == 'kWh'
        assert state.attributes['device_class'] == 'energy'
        assert state.attributes['state_class'] == 'total_increasing'

    device = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, KIOSK_ID), kiosk_entry.entry_id)
    assert device.name == 'My Home'
    assert device.model == 'Kiosk'


async def test_kiosk_updates_every_10_minutes(hass: HomeAssistant, kiosk_entry, mock_kiosk_api):
    await setup_entry(hass, kiosk_entry)
    assert mock_kiosk_api.call_count == 1

    mock_kiosk_api.get(KIOSK_API_URL, json=kiosk_response({**KIOSK_REAL_KPI, 'realTimePower': '3.0', 'dailyEnergy': '13'}))

    await advance(hass, 300)
    assert mock_kiosk_api.call_count == 1

    await advance(hass, 600)
    assert mock_kiosk_api.call_count == 2
    assert get_state(hass, f'{DOMAIN}-{KIOSK_ID}-realtime_power').state == '3.0'
    assert get_state(hass, f'{DOMAIN}-{KIOSK_ID}-total_current_day_energy').state == '13.0'


async def test_kiosk_lifetime_energy_ignores_glitch_when_not_producing(
        hass: HomeAssistant, kiosk_entry, mock_kiosk_api
):
    """Just before midnight FusionSolar can report a bogus lifetime total; it is ignored while power is 0."""
    await setup_entry(hass, kiosk_entry)
    lifetime_id = f'{DOMAIN}-{KIOSK_ID}-total_lifetime_energy'

    mock_kiosk_api.get(KIOSK_API_URL, json=kiosk_response(
        {**KIOSK_REAL_KPI, 'realTimePower': '0', 'cumulativeEnergy': '0.5'}
    ))
    await advance(hass, 601)
    assert get_state(hass, lifetime_id).state == '12345.6'

    mock_kiosk_api.get(KIOSK_API_URL, json=kiosk_response(
        {**KIOSK_REAL_KPI, 'realTimePower': '1.2', 'cumulativeEnergy': '12350.0'}
    ))
    await advance(hass, 1202)
    assert get_state(hass, lifetime_id).state == '12350.0'


async def test_kiosk_api_failure_leaves_sensors_unknown(hass: HomeAssistant, kiosk_entry, requests_mock):
    requests_mock.get(KIOSK_API_URL, json={'success': False, 'failCode': 20056})

    await setup_entry(hass, kiosk_entry)

    assert get_state(hass, f'{DOMAIN}-{KIOSK_ID}-total_current_day_energy').state == STATE_UNKNOWN
    assert get_state(hass, f'{DOMAIN}-{KIOSK_ID}-realtime_power').state == STATE_UNKNOWN


async def test_unload_entry(hass: HomeAssistant, kiosk_entry, mock_kiosk_api):
    await setup_entry(hass, kiosk_entry)
    assert kiosk_entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(kiosk_entry.entry_id)
    await hass.async_block_till_done()

    assert kiosk_entry.state is ConfigEntryState.NOT_LOADED
    assert kiosk_entry.entry_id not in hass.data[DOMAIN]


# --- OpenAPI ---------------------------------------------------------------

async def test_openapi_setup_creates_station_entities(hass: HomeAssistant, openapi_entry, mock_openapi):
    await setup_entry(hass, openapi_entry)

    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-total_current_day_energy').state == '21.5'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-total_current_month_energy').state == '310.25'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-total_lifetime_energy').state == '15000.75'

    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-station_name').state == 'Rooftop'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-capacity').state == '8.5'

    # Year KPI: "current year" uses the latest collectTime, "lifetime" sums all years.
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-current_year-inverter_power').state == '5000.0'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-lifetime-inverter_power').state == '9000.0'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-lifetime-reduction_total_tree').state == '22.0'

    entity = er.async_get(hass).async_get(
        er.async_get(hass).async_get_entity_id('sensor', DOMAIN, f'{DOMAIN}-{STATION_CODE}-station_code')
    )
    assert entity.entity_category is EntityCategory.DIAGNOSTIC


async def test_openapi_setup_registers_devices_under_station(hass: HomeAssistant, openapi_entry, mock_openapi):
    await setup_entry(hass, openapi_entry)
    registry = dr.async_get(hass)

    station = registry.async_get_device_by_identifier((DOMAIN, STATION_CODE), openapi_entry.entry_id)
    assert station.name == 'Rooftop'
    assert station.model == 'Station'

    inverter = registry.async_get_device_by_identifier((DOMAIN, INVERTER_ID), openapi_entry.entry_id)
    assert inverter.name == 'Inverter-1'
    assert inverter.model == 'Residential inverter SUN2000-8KTL-M1'
    assert inverter.sw_version == 'V100R001C00SPC140'
    assert inverter.via_device_id == station.id

    for device_id in (BATTERY_ID, POWER_SENSOR_ID):
        device = registry.async_get_device_by_identifier((DOMAIN, device_id), openapi_entry.entry_id)
        assert device.via_device_id == station.id


async def test_openapi_device_realtime_values(hass: HomeAssistant, openapi_entry, mock_openapi):
    await setup_entry(hass, openapi_entry)

    # The first refresh fetches the inverter (first device type) only.
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-realtime_power').state == '3.21'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-active_power').state == '3.21'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-a_u').state == '231.4'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-power_factor').state == '99.0'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-reactive_power').state == '12.0'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-total_cap').state == '9876.5'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-temperature').state == STATE_UNKNOWN  # 'N/A'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-run_state').state == STATE_ON
    assert get_state(hass, f'{DOMAIN}-{BATTERY_ID}-battery_soc').state == STATE_UNKNOWN

    # Static device attributes
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-esn_code').state == 'ESN0001'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-inverter_type').state == 'SUN2000-8KTL-M1'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-device_type').state == 'Residential inverter'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-latitude').state == '51.05'
    assert get_state(hass, f'{DOMAIN}-{INVERTER_ID}-longitude').state == '3.72'


async def test_openapi_device_types_are_polled_in_rotation(hass: HomeAssistant, openapi_entry, mock_openapi):
    await setup_entry(hass, openapi_entry)

    await advance(hass, 63)
    battery_soc = get_state(hass, f'{DOMAIN}-{BATTERY_ID}-battery_soc')
    assert battery_soc.state == '76.0'
    assert battery_soc.attributes['unit_of_measurement'] == '%'
    assert get_state(hass, f'{DOMAIN}-{BATTERY_ID}-ch_discharge_power').state == '-1500.0'
    assert get_state(hass, f'{DOMAIN}-{BATTERY_ID}-run_state').state == STATE_OFF
    assert get_state(hass, f'{DOMAIN}-{POWER_SENSOR_ID}-realtime_power').state == STATE_UNKNOWN

    await advance(hass, 126)
    meter_power = get_state(hass, f'{DOMAIN}-{POWER_SENSOR_ID}-realtime_power')
    assert meter_power.state == '-820.0'
    assert meter_power.attributes['unit_of_measurement'] == 'W'

    dev_kpi_calls = [r.json()['devTypeId'] for r in mock_openapi.request_history if r.path.endswith('getdevrealkpi')]
    assert dev_kpi_calls == [38, 39, 47]


async def test_openapi_disabled_station_is_skipped(hass: HomeAssistant, openapi_entry, mock_openapi):
    dr.async_get(hass).async_get_or_create(
        config_entry_id=openapi_entry.entry_id,
        identifiers={(DOMAIN, STATION_CODE)},
        disabled_by=dr.DeviceEntryDisabler.USER,
    )

    await setup_entry(hass, openapi_entry)

    registry = er.async_get(hass)
    assert registry.async_get_entity_id('sensor', DOMAIN, f'{DOMAIN}-{STATION_CODE}-total_current_day_energy') is None
    station_kpi_calls = [r for r in mock_openapi.request_history if r.path.endswith('getstationrealkpi')]
    assert station_kpi_calls == []


async def test_openapi_no_stations(hass: HomeAssistant, openapi_entry, mock_openapi, caplog):
    mock_openapi.post(f'{OPENAPI_HOST}/thirdData/getStationList', json={'success': True, 'failCode': 0, 'data': []})

    await setup_entry(hass, openapi_entry)

    assert 'No stations found' in caplog.text
    assert hass.states.async_entity_ids('sensor') == []


@pytest.mark.parametrize('fail_code', [20400, 407])
async def test_openapi_station_kpi_error_marks_entities_unavailable(
        hass: HomeAssistant, openapi_entry, mock_openapi, fail_code
):
    mock_openapi.post(
        f'{OPENAPI_HOST}/thirdData/getStationRealKpi',
        json={'success': False, 'failCode': fail_code, 'data': 'error'},
    )

    await setup_entry(hass, openapi_entry)

    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-total_current_day_energy').state == 'unavailable'
