"""Grid meter (device type 17) units, based on the getDevRealKpi response of a DTSU666 meter from issue #313."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.fusion_solar.const import DOMAIN

from .conftest import get_state
from .const import OPENAPI_HOST, STATION_CODE

GRID_METER_ID = 1000000017

GRID_METER_DEV_LIST = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'id': GRID_METER_ID,
            'devName': 'Grid meter',
            'stationCode': STATION_CODE,
            'esnCode': 'ESN0017',
            'devTypeId': 17,
            'invType': None,
            'softwareVersion': None,
            'latitude': None,
            'longitude': None,
        },
    ],
}

GRID_METER_REAL_KPI = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'devId': GRID_METER_ID,
            'dataItemMap': {
                'a_u': 236.3, 'b_u': 235.4, 'c_u': 236.6,
                'a_i': 2.0, 'b_i': 10.7, 'c_i': 3.1,
                'active_power': -1897.0,
                'active_power_a': -43.0, 'active_power_b': -2465.0, 'active_power_c': 610.0,
                'reactive_power': 1159.0,
                'total_apparent_power': 3.728,
                'power_factor': 0.853,
                'active_cap': 48247.45,
                'reverse_active_cap': 80452.78,
            },
        }
    ],
}


async def test_grid_meter_active_power_is_in_watt(hass: HomeAssistant, openapi_entry, mock_openapi):
    mock_openapi.post(f'{OPENAPI_HOST}/thirdData/getDevList', json=GRID_METER_DEV_LIST)
    mock_openapi.post(f'{OPENAPI_HOST}/thirdData/getDevRealKpi', json=GRID_METER_REAL_KPI)

    assert await hass.config_entries.async_setup(openapi_entry.entry_id)
    await hass.async_block_till_done()
    assert openapi_entry.state is ConfigEntryState.LOADED

    # Phase B: 235.4 V x 10.7 A is about 2.5 kVA, so -2465 can only be W.
    for attribute, value in [('realtime_power', '-1897.0'), ('active_power', '-1897.0'),
                             ('active_power_a', '-43.0'), ('active_power_b', '-2465.0'),
                             ('active_power_c', '610.0')]:
        state = get_state(hass, f'{DOMAIN}-{GRID_METER_ID}-{attribute}')
        assert state.state == value, attribute
        assert state.attributes['unit_of_measurement'] == 'W', attribute

    # The same response reports apparent power in kVA: 3.728 is the sum of voltage x current over the phases.
    apparent = get_state(hass, f'{DOMAIN}-{GRID_METER_ID}-total_apparent_power')
    assert apparent.state == '3.728'
    assert apparent.attributes['unit_of_measurement'] == 'kVA'
