"""Tests for the OpenAPI client, with HTTP mocked by requests-mock."""
import pytest

from custom_components.fusion_solar.fusion_solar.openapi.openapi_api import (
    FusionSolarOpenApi,
    FusionSolarOpenApiAccessFrequencyTooHighError,
    FusionSolarOpenApiError,
)

from .const import (
    DEV_LIST,
    INVERTER_ID,
    INVERTER_REAL_KPI,
    KPI_STATION_YEAR,
    OPENAPI_HOST,
    OPENAPI_TOKEN,
    STATION_CODE,
    STATION_LIST,
    STATION_REAL_KPI,
)

LOGIN_URL = f'{OPENAPI_HOST}/thirdData/login'


@pytest.fixture
def api() -> FusionSolarOpenApi:
    return FusionSolarOpenApi(OPENAPI_HOST, 'api-user', 'api-password')


@pytest.fixture
def login(requests_mock):
    return requests_mock.post(LOGIN_URL, json={'success': True}, headers={'xsrf-token': OPENAPI_TOKEN})


def test_login_returns_token_and_sends_credentials(api, login):
    assert api.login() == OPENAPI_TOKEN
    assert login.last_request.json() == {'userName': 'api-user', 'systemCode': 'api-password'}


def test_login_without_token_header_fails(api, requests_mock):
    requests_mock.post(LOGIN_URL, json={'success': False, 'failCode': 20001})

    with pytest.raises(FusionSolarOpenApiError):
        api.login()


def test_login_http_error_fails(api, requests_mock):
    requests_mock.post(LOGIN_URL, status_code=500)

    with pytest.raises(FusionSolarOpenApiError):
        api.login()


def test_calls_send_token_header(api, login, requests_mock):
    station_list = requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationList', json=STATION_LIST)

    api.get_station_list()

    assert login.call_count == 1
    assert station_list.last_request.headers['xsrf-token'] == OPENAPI_TOKEN


def test_get_station_list(api, login, requests_mock):
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationList', json=STATION_LIST)

    [station] = api.get_station_list()

    assert station.code == STATION_CODE
    assert station.name == 'Rooftop'
    assert station.address == 'Main Street 1'
    assert station.capacity == 8.5
    assert station.contact_person == 'Jane Doe'
    assert station.contact_phone == '+3212345678'


def test_get_station_list_falls_back_to_stations_endpoint(api, login, requests_mock):
    requests_mock.post(
        f'{OPENAPI_HOST}/thirdData/getStationList',
        json={'success': False, 'failCode': 401, 'message': 'no access', 'data': None},
    )
    stations = requests_mock.post(f'{OPENAPI_HOST}/thirdData/stations', json={
        'success': True,
        'failCode': 0,
        'data': {'list': [{
            'plantCode': 'NE=1', 'plantName': 'Plant', 'plantAddress': 'Somewhere',
            'capacity': 5.0, 'contactPerson': 'John',
        }]},
    })

    [station] = api.get_station_list()

    assert stations.last_request.json() == {'pageNo': 1}
    assert (station.code, station.name, station.address, station.capacity, station.contact_person) == \
           ('NE=1', 'Plant', 'Somewhere', 5.0, 'John')


def test_expired_token_triggers_relogin(api, login, requests_mock):
    real_kpi = requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationRealKpi', [
        {'json': {'success': False, 'failCode': 305, 'data': None}},
        {'json': STATION_REAL_KPI},
    ])

    assert api.get_station_real_kpi([STATION_CODE]) == STATION_REAL_KPI['data']
    assert login.call_count == 2
    assert real_kpi.call_count == 2


def test_rate_limit_raises_access_frequency_error(api, login, requests_mock):
    requests_mock.post(
        f'{OPENAPI_HOST}/thirdData/getDevRealKpi',
        json={'success': False, 'failCode': 407, 'data': 'ACCESS_FREQUENCY_IS_TOO_HIGH'},
    )

    with pytest.raises(FusionSolarOpenApiAccessFrequencyTooHighError):
        api.get_dev_real_kpi([str(INVERTER_ID)], 38)


def test_other_fail_code_raises(api, login, requests_mock):
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationRealKpi', json={'success': False, 'failCode': 20400, 'data': None})

    with pytest.raises(FusionSolarOpenApiError):
        api.get_station_real_kpi([STATION_CODE])


def test_response_without_data_raises(api, login, requests_mock):
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationRealKpi', json={'success': True, 'failCode': 0})

    with pytest.raises(FusionSolarOpenApiError):
        api.get_station_real_kpi([STATION_CODE])


def test_get_station_real_kpi_joins_station_codes(api, login, requests_mock):
    real_kpi = requests_mock.post(f'{OPENAPI_HOST}/thirdData/getStationRealKpi', json=STATION_REAL_KPI)

    api.get_station_real_kpi(['NE=1', 'NE=2'])

    assert real_kpi.last_request.json() == {'stationCodes': 'NE=1,NE=2'}


def test_get_kpi_station_year_requests_next_year(api, login, requests_mock, freezer):
    freezer.move_to('2024-06-15 12:00:00')
    year_kpi = requests_mock.post(f'{OPENAPI_HOST}/thirdData/getKpiStationYear', json=KPI_STATION_YEAR)

    assert api.get_kpi_station_year([STATION_CODE]) == KPI_STATION_YEAR['data']
    # 2025-01-01T00:00:00Z in milliseconds
    assert year_kpi.last_request.json() == {'stationCodes': STATION_CODE, 'collectTime': 1735689600000}


def test_get_dev_list(api, login, requests_mock):
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getDevList', json=DEV_LIST)

    devices = api.get_dev_list([STATION_CODE])

    assert [d.device_id for d in devices] == [1000000001, 1000000002, 1000000003]
    inverter = devices[0]
    assert inverter.name == 'Inverter-1'
    assert inverter.station_code == STATION_CODE
    assert inverter.esn_code == 'ESN0001'
    assert inverter.type_id == 38
    assert inverter.inverter_type == 'SUN2000-8KTL-M1'
    assert inverter.software_version == 'V100R001C00SPC140'


def test_get_dev_list_coordinates(api, login, requests_mock):
    requests_mock.post(f'{OPENAPI_HOST}/thirdData/getDevList', json=DEV_LIST)

    inverter = api.get_dev_list([STATION_CODE])[0]

    assert inverter.latitude == 51.05
    assert inverter.longitude == 3.72


def test_get_dev_real_kpi(api, login, requests_mock):
    dev_kpi = requests_mock.post(f'{OPENAPI_HOST}/thirdData/getDevRealKpi', json=INVERTER_REAL_KPI)

    assert api.get_dev_real_kpi(['1', '2'], 38) == INVERTER_REAL_KPI['data']
    assert dev_kpi.last_request.json() == {'devIds': '1,2', 'devTypeId': 38}
