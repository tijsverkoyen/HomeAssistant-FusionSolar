"""Tests for the rate-limited device real-KPI coordinator."""
from unittest.mock import MagicMock

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.fusion_solar.const import DOMAIN
from custom_components.fusion_solar.device_real_kpi_coordinator import DeviceRealKpiDataCoordinator
from custom_components.fusion_solar.fusion_solar.openapi.device import FusionSolarDevice
from custom_components.fusion_solar.fusion_solar.openapi.openapi_api import (
    FusionSolarOpenApiAccessFrequencyTooHighError,
    FusionSolarOpenApiError,
)


def make_device(device_id, type_id, station_code='NE=1'):
    return FusionSolarDevice(device_id, f'dev-{device_id}', station_code, f'esn-{device_id}', type_id, None, None, None, None)


DEVICES = [
    make_device(1, 38),
    make_device(2, 39),
    make_device(3, 38),
    make_device(4, 47),
    make_device(5, 62),  # dongle: no real-time KPI support, must be ignored
]


@pytest.fixture
def api():
    api = MagicMock()
    api.get_dev_real_kpi.side_effect = lambda ids, type_id: [
        {'devId': int(i), 'dataItemMap': {'active_power': float(i)}} for i in ids
    ]
    return api


@pytest.fixture
def coordinator(hass: HomeAssistant, openapi_entry, api):
    return DeviceRealKpiDataCoordinator(hass, api, DEVICES, openapi_entry.entry_id)


async def test_groups_supported_devices_by_type(coordinator):
    assert coordinator.device_ids_grouped_per_type_id() == {38: ['1', '3'], 39: ['2'], 47: ['4']}


async def test_skips_disabled_devices_and_stations(hass: HomeAssistant, openapi_entry, api):
    registry = dr.async_get(hass)
    registry.async_get_or_create(
        config_entry_id=openapi_entry.entry_id,
        identifiers={(DOMAIN, 3)},
        disabled_by=dr.DeviceEntryDisabler.USER,
    )
    registry.async_get_or_create(
        config_entry_id=openapi_entry.entry_id,
        identifiers={(DOMAIN, 'NE=disabled')},
        disabled_by=dr.DeviceEntryDisabler.USER,
    )
    devices = [*DEVICES, make_device(6, 39, station_code='NE=disabled')]

    coordinator = DeviceRealKpiDataCoordinator(hass, api, devices, openapi_entry.entry_id)

    assert coordinator.device_ids_grouped_per_type_id() == {38: ['1'], 39: ['2'], 47: ['4']}


async def test_fetches_one_device_type_per_update(coordinator, api):
    """Each tick only calls getDevRealKpi for one device type, to respect the 1 call/minute limit."""
    results = [await coordinator._async_update_data() for _ in range(4)]

    assert [c.args for c in api.get_dev_real_kpi.call_args_list] == [
        (['1', '3'], 38),
        (['2'], 39),
        (['4'], 47),
        (['1', '3'], 38),
    ]
    assert results[0] == {
        f'{DOMAIN}-1': {'active_power': 1.0},
        f'{DOMAIN}-3': {'active_power': 3.0},
    }
    assert results[1] == {f'{DOMAIN}-2': {'active_power': 2.0}}


async def test_backs_off_after_rate_limit(coordinator, api):
    api.get_dev_real_kpi.side_effect = FusionSolarOpenApiAccessFrequencyTooHighError('407')

    assert await coordinator._async_update_data() is False
    assert coordinator.skip is True
    assert api.get_dev_real_kpi.call_count == 1

    # While backing off, no API calls are made.
    for _ in range(coordinator.counter_limit + 1):
        assert await coordinator._async_update_data() is False
    assert api.get_dev_real_kpi.call_count == 1

    # Once the back-off period has passed it calls the API again and resets the back-off on success.
    api.get_dev_real_kpi.side_effect = None
    api.get_dev_real_kpi.return_value = []
    assert await coordinator._async_update_data() == {}
    assert api.get_dev_real_kpi.call_count == 2
    assert coordinator.skip is False
    assert coordinator.skip_counter == 0


async def test_api_error_raises_update_failed(coordinator, api):
    api.get_dev_real_kpi.side_effect = FusionSolarOpenApiError('boom')

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_no_data_returns_false(coordinator, api):
    api.get_dev_real_kpi.side_effect = None
    api.get_dev_real_kpi.return_value = None

    assert await coordinator._async_update_data() is False


async def test_counter_limit_and_skip_for(hass: HomeAssistant):
    coordinator = DeviceRealKpiDataCoordinator(hass, MagicMock(), [], 'entry')

    # 63 second interval: back off for ceil(60/63)+1 = 2 ticks
    assert coordinator.counter_limit == 2
    assert coordinator.skip_for == 3 * 63
