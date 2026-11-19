"""Station KPI sensors: daily plant data (getKpiStationDay), revenue / health state and the optional energy fields."""
from datetime import timedelta

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.fusion_solar.const import DOMAIN

from .conftest import get_state
from .const import (
    KPI_STATION_YEAR,
    MARCH_31,
    OCTOBER_27,
    OPENAPI_HOST,
    PLANT_TIME_ZONE,
    STATION_CODE,
    kpi_station_day,
)

DAY_KPI_URL = f'{OPENAPI_HOST}/thirdData/getKpiStationDay'


def day_unique_id(attribute: str) -> str:
    return f'{DOMAIN}-{STATION_CODE}-current_day-{attribute}'


def day_kpi_calls(requests_mock) -> int:
    return len([r for r in requests_mock.request_history if r.path.endswith('getkpistationday')])


async def setup_entry(hass: HomeAssistant, entry, time_zone: str = PLANT_TIME_ZONE):
    await hass.config.async_set_time_zone(time_zone)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED


async def advance(hass: HomeAssistant, freezer, delta: timedelta):
    freezer.tick(delta)
    async_fire_time_changed(hass)
    await hass.async_block_till_done(wait_background_tasks=True)


# --- getStationRealKpi -----------------------------------------------------

async def test_station_revenue_and_health_state(hass: HomeAssistant, openapi_entry, mock_openapi):
    await setup_entry(hass, openapi_entry)

    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-day_income').state == '3.25'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-total_income').state == '1500.0'

    health = get_state(hass, f'{DOMAIN}-{STATION_CODE}-real_health_state')
    assert health.state == '3'
    assert health.attributes['device_class'] == 'enum'
    assert health.attributes['options'] == ['1', '2', '3']


# --- getKpiStationDay ------------------------------------------------------

async def test_day_sensors_show_todays_record(hass: HomeAssistant, openapi_entry, mock_openapi, freezer):
    freezer.move_to('2024-06-15 12:00:00+00:00')  # 14:00 in Brussels
    await setup_entry(hass, openapi_entry)

    assert get_state(hass, day_unique_id('inverter_power')).state == '12.5'
    assert get_state(hass, day_unique_id('use_power')).state == '8.0'
    assert get_state(hass, day_unique_id('power_profit')).state == '2.5'
    assert get_state(hass, day_unique_id('ongrid_power')).state == STATE_UNKNOWN  # null in the response

    inverter_power = get_state(hass, day_unique_id('inverter_power'))
    assert inverter_power.attributes['state_class'] == 'total_increasing'
    assert inverter_power.attributes['unit_of_measurement'] == 'kWh'


async def test_optional_day_sensors_only_when_returned(hass: HomeAssistant, openapi_entry, mock_openapi, freezer):
    freezer.move_to('2024-06-15 12:00:00+00:00')
    await setup_entry(hass, openapi_entry)

    assert get_state(hass, day_unique_id('buy_power')).state == '3.0'
    assert get_state(hass, day_unique_id('charge_cap')).state == '1.0'

    registry = er.async_get(hass)
    assert registry.async_get_entity_id('sensor', DOMAIN, day_unique_id('discharge_cap')) is None
    assert registry.async_get_entity_id('sensor', DOMAIN, day_unique_id('self_use_power')) is None


async def test_day_sensors_clear_at_midnight_without_api_call(
        hass: HomeAssistant, openapi_entry, mock_openapi, freezer
):
    freezer.move_to('2024-06-15 21:30:00+00:00')  # 23:30 in Brussels
    await setup_entry(hass, openapi_entry)
    assert get_state(hass, day_unique_id('inverter_power')).state == '12.5'

    await advance(hass, freezer, timedelta(minutes=30))  # midnight in Brussels, before the next hourly update

    assert get_state(hass, day_unique_id('inverter_power')).state == STATE_UNKNOWN
    assert day_kpi_calls(mock_openapi) == 1


async def test_day_sensors_on_25_hour_day(hass: HomeAssistant, openapi_entry, mock_openapi, freezer):
    mock_openapi.post(DAY_KPI_URL, json=kpi_station_day((OCTOBER_27, {'inverter_power': 9.0})))
    freezer.move_to('2024-10-27 22:30:00+00:00')  # 23:30 in Brussels, 24.5 hours after the day started

    await setup_entry(hass, openapi_entry)

    assert get_state(hass, day_unique_id('inverter_power')).state == '9.0'


async def test_day_sensors_after_23_hour_day(hass: HomeAssistant, openapi_entry, mock_openapi, freezer):
    # Only yesterday's record is available (today's record isn't created yet).
    mock_openapi.post(DAY_KPI_URL, json=kpi_station_day((MARCH_31, {'inverter_power': 9.0})))
    freezer.move_to('2024-03-31 22:30:00+00:00')  # 00:30 on April 1 in Brussels, 23.5 hours after March 31 started

    await setup_entry(hass, openapi_entry)

    assert get_state(hass, day_unique_id('inverter_power')).state == STATE_UNKNOWN


async def test_day_sensors_when_home_assistant_is_in_another_time_zone(
        hass: HomeAssistant, openapi_entry, mock_openapi, freezer
):
    freezer.move_to('2024-06-15 12:00:00+00:00')

    await setup_entry(hass, openapi_entry, time_zone='America/New_York')

    # Records don't start at midnight in Home Assistant's timezone, so the age of the record is used.
    assert get_state(hass, day_unique_id('inverter_power')).state == '12.5'


async def test_day_sensors_keep_data_when_rate_limited(hass: HomeAssistant, openapi_entry, mock_openapi, freezer):
    freezer.move_to('2024-06-15 12:00:00+00:00')
    await setup_entry(hass, openapi_entry)

    mock_openapi.post(DAY_KPI_URL, json={'success': False, 'failCode': 407, 'data': 'ACCESS_FREQUENCY_IS_TOO_HIGH'})
    await advance(hass, freezer, timedelta(hours=1))

    assert day_kpi_calls(mock_openapi) == 2
    assert get_state(hass, day_unique_id('inverter_power')).state == '12.5'


async def test_day_sensors_not_created_without_access(
        hass: HomeAssistant, openapi_entry, mock_openapi, freezer, caplog
):
    mock_openapi.post(
        DAY_KPI_URL,
        json={'success': False, 'failCode': 401, 'data': None, 'message': 'USER_MUST_HAVE_ACCESS'},
    )
    freezer.move_to('2024-06-15 12:00:00+00:00')

    await setup_entry(hass, openapi_entry)

    registry = er.async_get(hass)
    assert registry.async_get_entity_id('sensor', DOMAIN, day_unique_id('inverter_power')) is None
    assert 'getKpiStationDay is not available for this account' in caplog.text
    # The other station sensors are still created.
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-total_current_day_energy').state == '21.5'

    await advance(hass, freezer, timedelta(hours=3))
    assert day_kpi_calls(mock_openapi) == 1


# --- getKpiStationYear optional fields -------------------------------------

async def test_optional_year_sensors_only_when_returned(hass: HomeAssistant, openapi_entry, mock_openapi):
    await setup_entry(hass, openapi_entry)

    registry = er.async_get(hass)
    assert registry.async_get_entity_id('sensor', DOMAIN, f'{DOMAIN}-{STATION_CODE}-current_year-buy_power') is None
    assert registry.async_get_entity_id('sensor', DOMAIN, f'{DOMAIN}-{STATION_CODE}-lifetime-buy_power') is None


async def test_optional_year_sensors_when_returned(hass: HomeAssistant, openapi_entry, mock_openapi):
    year = {**KPI_STATION_YEAR, 'data': [
        {**record, 'dataItemMap': {**record['dataItemMap'], 'buy_power': 100.0 * (index + 1)}}
        for index, record in enumerate(KPI_STATION_YEAR['data'])
    ]}
    mock_openapi.post(f'{OPENAPI_HOST}/thirdData/getKpiStationYear', json=year)

    await setup_entry(hass, openapi_entry)

    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-current_year-buy_power').state == '200.0'
    assert get_state(hass, f'{DOMAIN}-{STATION_CODE}-lifetime-buy_power').state == '300.0'
