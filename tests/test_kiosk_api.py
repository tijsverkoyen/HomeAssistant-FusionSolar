"""Tests for the kiosk URL parser and kiosk API client."""
import pytest

from custom_components.fusion_solar.fusion_solar.kiosk.kiosk import FusionSolarKiosk
from custom_components.fusion_solar.fusion_solar.kiosk.kiosk_api import FusionSolarKioskApi

from .const import KIOSK_API_URL, KIOSK_HOST, KIOSK_ID, KIOSK_NAME, KIOSK_REAL_KPI, KIOSK_URL, kiosk_response


def test_kiosk_parses_id_and_api_url():
    kiosk = FusionSolarKiosk(KIOSK_URL, KIOSK_NAME)

    assert kiosk.id == KIOSK_ID
    assert kiosk.name == KIOSK_NAME
    assert kiosk.apiUrl() == KIOSK_HOST


def test_kiosk_api_url_keeps_regional_host():
    kiosk = FusionSolarKiosk('https://region01eu5.fusionsolar.huawei.com/kiosk?kk=abc', 'x')

    assert kiosk.id == 'abc'
    assert kiosk.apiUrl() == 'https://region01eu5.fusionsolar.huawei.com'


def test_kiosk_url_without_kk_raises():
    with pytest.raises(AttributeError):
        FusionSolarKiosk(f'{KIOSK_HOST}/singleKiosk.html', KIOSK_NAME)


def test_get_real_time_kpi_decodes_html_escaped_json(requests_mock):
    requests_mock.get(KIOSK_API_URL, json=kiosk_response())

    data = FusionSolarKioskApi(KIOSK_HOST).getRealTimeKpi(KIOSK_ID)

    assert data == KIOSK_REAL_KPI
    assert requests_mock.last_request.headers['accept'] == 'application/json'


def test_get_real_time_kpi_unsuccessful_response(requests_mock):
    requests_mock.get(KIOSK_API_URL, json={'success': False, 'failCode': 20056})

    assert FusionSolarKioskApi(KIOSK_HOST).getRealTimeKpi(KIOSK_ID) == {'success': False}


def test_get_real_time_kpi_missing_real_kpi(requests_mock):
    requests_mock.get(KIOSK_API_URL, json={'success': True, 'data': '{&quot;other&quot;: 1}'})

    assert FusionSolarKioskApi(KIOSK_HOST).getRealTimeKpi(KIOSK_ID) == {'success': False}
