"""Tests for the station and device models."""
import pytest

from custom_components.fusion_solar.const import DOMAIN
from custom_components.fusion_solar.fusion_solar.openapi.device import FusionSolarDevice
from custom_components.fusion_solar.fusion_solar.openapi.station import FusionSolarStation


def make_device(type_id=38, name='Inverter-1', esn_code='ESN0001', inverter_type='SUN2000'):
    return FusionSolarDevice('42', name, 'NE=1', esn_code, type_id, inverter_type, 'V1', 3.72, 51.05)


@pytest.mark.parametrize(('type_id', 'expected'), [
    (1, 'String inverter'),
    (10, 'EMI'),
    (17, 'Grid meter'),
    (38, 'Residential inverter'),
    (39, 'Battery'),
    (41, 'ESS'),
    (47, 'Power Sensor'),
    (62, 'Dongle'),
    (23070, 'EMMA'),
    (9999, 'Unknown'),
])
def test_device_type(type_id, expected):
    assert make_device(type_id=type_id).device_type == expected


def test_model_includes_inverter_type_for_residential_inverters():
    assert make_device(type_id=38).model == 'Residential inverter SUN2000'
    assert make_device(type_id=39).model == 'Battery'


@pytest.mark.parametrize(('name', 'esn_code', 'expected'), [
    ('Inverter-1', 'ESN0001', 'Inverter-1 (ESN0001)'),
    ('ESN0001', 'ESN0001', 'ESN0001'),
    ('Inverter-1', '', 'Inverter-1'),
    ('Inverter-1', None, 'Inverter-1'),
])
def test_device_readable_name(name, esn_code, expected):
    assert make_device(name=name, esn_code=esn_code).readable_name == expected


def test_device_info_without_parent():
    info = make_device().device_info()

    assert info['identifiers'] == {(DOMAIN, '42')}
    assert info['manufacturer'] == 'Huawei FusionSolar'
    assert info['model'] == 'Residential inverter SUN2000'
    assert info['sw_version'] == 'V1'
    assert 'via_device_id' not in info


def test_device_info_with_parent():
    device = make_device()
    device.via_device_id = 'registry-id'

    assert device.device_info()['via_device_id'] == 'registry-id'


def test_station_device_info():
    info = FusionSolarStation('NE=1', 'Rooftop').device_info()

    assert info == {
        'identifiers': {(DOMAIN, 'NE=1')},
        'name': 'Rooftop',
        'manufacturer': 'Huawei FusionSolar',
        'model': 'Station',
    }


@pytest.mark.parametrize(('name', 'expected'), [('Rooftop', 'Rooftop'), ('', 'NE=1'), (None, 'NE=1')])
def test_station_readable_name(name, expected):
    assert FusionSolarStation('NE=1', name).readable_name == expected
