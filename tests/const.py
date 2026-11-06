"""Sample FusionSolar API payloads shared by the tests."""
import html
import json

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_URL, CONF_USERNAME

from custom_components.fusion_solar.const import CONF_KIOSKS, CONF_OPENAPI_CREDENTIALS

# --- Kiosk -----------------------------------------------------------------

KIOSK_HOST = 'https://eu5.fusionsolar.huawei.com'
KIOSK_ID = 'GHsxCUnPamvx2TZ'
KIOSK_URL = f'{KIOSK_HOST}/singleKiosk.html?kk={KIOSK_ID}'
KIOSK_NAME = 'My Home'
KIOSK_API_URL = f'{KIOSK_HOST}/rest/pvms/web/kiosk/v1/station-kiosk-file?kk={KIOSK_ID}'

KIOSK_REAL_KPI = {
    'realTimePower': '2.512',
    'dailyEnergy': '12.34',
    'monthEnergy': '234.5',
    'yearEnergy': '3456.7',
    'cumulativeEnergy': '12345.6',
}


def kiosk_response(real_kpi=None):
    """Build a kiosk response; the API returns its payload as an HTML-escaped JSON string."""
    data = json.dumps({'realKpi': KIOSK_REAL_KPI if real_kpi is None else real_kpi})
    return {'success': True, 'data': html.escape(data), 'failCode': 0}


KIOSK_CONFIG = {
    CONF_KIOSKS: [{CONF_NAME: KIOSK_NAME, CONF_URL: KIOSK_URL}],
    CONF_OPENAPI_CREDENTIALS: {},
}

# --- OpenAPI ---------------------------------------------------------------

OPENAPI_HOST = 'https://eu5.fusionsolar.huawei.com'
OPENAPI_TOKEN = 'test-xsrf-token'

OPENAPI_CONFIG = {
    CONF_KIOSKS: [],
    CONF_OPENAPI_CREDENTIALS: {
        CONF_HOST: OPENAPI_HOST,
        CONF_USERNAME: 'api-user',
        CONF_PASSWORD: 'api-password',
    },
}

STATION_CODE = 'NE=12345678'

STATION_LIST = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'stationCode': STATION_CODE,
            'stationName': 'Rooftop',
            'stationAddr': 'Main Street 1',
            'capacity': 8.5,
            'buildState': None,
            'combineType': None,
            'aidType': 1,
            'stationLinkman': 'Jane Doe',
            'linkmanPho': '+3212345678',
        }
    ],
}

STATION_REAL_KPI = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'stationCode': STATION_CODE,
            'dataItemMap': {
                'day_power': '21.5',
                'month_power': '310.25',
                'total_power': '15000.75',
                'real_health_state': 3,
                'day_income': '3.250',
                'total_income': '1500.000',
            },
        }
    ],
}

KPI_STATION_YEAR = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'stationCode': STATION_CODE,
            'collectTime': 1672531200000,  # 2023
            'dataItemMap': {'inverter_power': 4000.0, 'installed_capacity': 8.5, 'reduction_total_tree': 10},
        },
        {
            'stationCode': STATION_CODE,
            'collectTime': 1704067200000,  # 2024
            'dataItemMap': {'inverter_power': 5000.0, 'installed_capacity': 8.5, 'reduction_total_tree': 12},
        },
    ],
}

PLANT_TIME_ZONE = 'Europe/Brussels'

# Records start at midnight in the plant's timezone (Europe/Brussels).
JUNE_14 = 1718316000000
JUNE_15 = 1718402400000
MARCH_31 = 1711839600000  # 23 hour day, daylight saving time starts
OCTOBER_27 = 1729980000000  # 25 hour day, daylight saving time ends


def kpi_station_day(*records):
    """Build a getKpiStationDay response from (collectTime, dataItemMap) tuples."""
    return {
        'success': True,
        'failCode': 0,
        'data': [
            {'stationCode': STATION_CODE, 'collectTime': collect_time, 'dataItemMap': data_item_map}
            for collect_time, data_item_map in records
        ],
    }


KPI_STATION_DAY = kpi_station_day(
    (JUNE_14, {'inverter_power': 30.0, 'ongrid_power': 20.0, 'use_power': 15.0, 'power_profit': 6.0,
               'buy_power': 4.0, 'charge_cap': 2.0}),
    (JUNE_15, {'inverter_power': 12.5, 'ongrid_power': None, 'use_power': 8.0, 'power_profit': 2.5,
               'buy_power': 3.0, 'charge_cap': 1.0}),
)

INVERTER_ID = 1000000001
BATTERY_ID = 1000000002
POWER_SENSOR_ID = 1000000003

DEV_LIST = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'id': INVERTER_ID,
            'devName': 'Inverter-1',
            'stationCode': STATION_CODE,
            'esnCode': 'ESN0001',
            'devTypeId': 38,
            'invType': 'SUN2000-8KTL-M1',
            'softwareVersion': 'V100R001C00SPC140',
            'latitude': 51.05,
            'longitude': 3.72,
        },
        {
            'id': BATTERY_ID,
            'devName': 'Battery-1',
            'stationCode': STATION_CODE,
            'esnCode': 'ESN0002',
            'devTypeId': 39,
            'invType': None,
            'softwareVersion': 'V100R002',
            'latitude': None,
            'longitude': None,
        },
        {
            'id': POWER_SENSOR_ID,
            'devName': 'Meter-1',
            'stationCode': STATION_CODE,
            'esnCode': 'ESN0003',
            'devTypeId': 47,
            'invType': None,
            'softwareVersion': None,
            'latitude': None,
            'longitude': None,
        },
    ],
}

INVERTER_REAL_KPI = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'devId': INVERTER_ID,
            'dataItemMap': {
                'inverter_state': 512,
                'a_u': 231.4,
                'active_power': 3.21,
                'power_factor': 0.99,
                'reactive_power': 0.012,
                'day_cap': 18.7,
                'total_cap': 9876.5,
                'temperature': 'N/A',
                'run_state': 1,
            },
        }
    ],
}

BATTERY_REAL_KPI = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'devId': BATTERY_ID,
            'dataItemMap': {
                'battery_status': 2,
                'battery_soc': 76.0,
                'ch_discharge_power': -1500.0,
                'run_state': 0,
            },
        }
    ],
}

POWER_SENSOR_REAL_KPI = {
    'success': True,
    'failCode': 0,
    'data': [
        {
            'devId': POWER_SENSOR_ID,
            'dataItemMap': {
                'meter_status': 1,
                'active_power': -820.0,
                'power_factor': 0.95,
                'run_state': 1,
            },
        }
    ],
}

DEV_REAL_KPI_BY_TYPE = {
    38: INVERTER_REAL_KPI,
    39: BATTERY_REAL_KPI,
    47: POWER_SENSOR_REAL_KPI,
}
