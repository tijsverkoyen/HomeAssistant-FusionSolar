"""FusionSolar sensor."""
import homeassistant.helpers.config_validation as cv
import logging
import voluptuous as vol

from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_URL, CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .fusion_solar.const import ATTR_REALTIME_POWER, ATTR_TOTAL_CURRENT_DAY_ENERGY, \
    ATTR_TOTAL_CURRENT_MONTH_ENERGY, ATTR_TOTAL_CURRENT_YEAR_ENERGY, ATTR_TOTAL_LIFETIME_ENERGY, \
    ATTR_STATION_CODE, ATTR_STATION_REAL_KPI_DATA_ITEM_MAP, ATTR_STATION_REAL_KPI_TOTAL_CURRENT_DAY_ENERGY, \
    ATTR_STATION_REAL_KPI_TOTAL_CURRENT_MONTH_ENERGY, ATTR_STATION_REAL_KPI_TOTAL_LIFETIME_ENERGY, \
    ATTR_DATA_COLLECT_TIME, ATTR_KPI_YEAR_INVERTER_POWER, ATTR_DEVICE_REAL_KPI_ACTIVE_POWER, \
    PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_GRID_METER, PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER, \
    PARAM_DEVICE_TYPE_ID_POWER_SENSOR, PARAM_DEVICE_TYPE_ID_EMI, PARAM_DEVICE_TYPE_ID_BATTERY, \
    ATTR_DEVICE_REAL_KPI_DEV_ID, \
    ATTR_DEVICE_REAL_KPI_DATA_ITEM_MAP
from .fusion_solar.kiosk.kiosk import FusionSolarKiosk
from .fusion_solar.kiosk.kiosk_api import FusionSolarKioskApi
from .fusion_solar.openapi.openapi_api import FusionSolarOpenApi
from .fusion_solar.energy_sensor import FusionSolarEnergySensorTotalCurrentDay, \
    FusionSolarEnergySensorTotalCurrentMonth, FusionSolarEnergySensorTotalCurrentYear, \
    FusionSolarEnergySensorTotalLifetime
from .fusion_solar.power_entity import FusionSolarPowerEntityRealtime
from .fusion_solar.device_attribute_entity import *
from .fusion_solar.realtime_device_data_sensor import *
from .fusion_solar.station_attribute_entity import *

from .const import CONF_KIOSKS, CONF_OPENAPI_CREDENTIALS, DOMAIN, ID_REALTIME_POWER, NAME_REALTIME_POWER, \
    ID_TOTAL_CURRENT_DAY_ENERGY, NAME_TOTAL_CURRENT_DAY_ENERGY, \
    ID_TOTAL_CURRENT_MONTH_ENERGY, NAME_TOTAL_CURRENT_MONTH_ENERGY, \
    ID_TOTAL_CURRENT_YEAR_ENERGY, NAME_TOTAL_CURRENT_YEAR_ENERGY, \
    ID_TOTAL_LIFETIME_ENERGY, NAME_TOTAL_LIFETIME_ENERGY

KIOSK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONF_NAME): cv.string
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KIOSKS): vol.All(cv.ensure_list, [KIOSK_SCHEMA]),
    }
)

_LOGGER = logging.getLogger(__name__)


async def add_entities_for_kiosk(hass, async_add_entities, kiosk: FusionSolarKiosk):
    _LOGGER.debug(f'Adding entities for kiosk {kiosk.id}')

    async def async_update_kiosk_data():
        """Fetch data"""
        data = {}
        api = FusionSolarKioskApi(kiosk.apiUrl())

        _LOGGER.debug(DOMAIN)
        _LOGGER.debug(kiosk.id)

        data[f'{DOMAIN}-{kiosk.id}'] = await hass.async_add_executor_job(api.getRealTimeKpi, kiosk.id)

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarKiosk',
        update_method=async_update_kiosk_data,
        update_interval=timedelta(seconds=600),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    device_info = {
        'identifiers': {
            (DOMAIN, kiosk.id)
        },
        'name': kiosk.name,
        'manufacturer': 'Huawei FusionSolar',
        'model': 'Kiosk'
    }

    async_add_entities([
        FusionSolarPowerEntityRealtime(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_REALTIME_POWER}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_REALTIME_POWER}',
            ATTR_REALTIME_POWER,
            f'{DOMAIN}-{kiosk.id}',
            device_info
        ),

        FusionSolarEnergySensorTotalCurrentDay(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_DAY_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_DAY_ENERGY}',
            ATTR_TOTAL_CURRENT_DAY_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
            device_info
        ),
        FusionSolarEnergySensorTotalCurrentMonth(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_MONTH_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_MONTH_ENERGY}',
            ATTR_TOTAL_CURRENT_MONTH_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
            device_info
        ),
        FusionSolarEnergySensorTotalCurrentYear(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_YEAR_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_YEAR_ENERGY}',
            ATTR_TOTAL_CURRENT_YEAR_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
            device_info
        ),
        FusionSolarEnergySensorTotalLifetime(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_LIFETIME_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_LIFETIME_ENERGY}',
            ATTR_TOTAL_LIFETIME_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
            device_info
        )
    ])


async def add_entities_for_stations(hass, async_add_entities, stations, api: FusionSolarOpenApi):
    _LOGGER.debug(f'Adding entities for stations')
    station_codes = [station.code for station in stations]

    async def async_update_station_real_kpi_data():
        """Fetch data"""
        data = {}
        response = await hass.async_add_executor_job(api.get_station_real_kpi, station_codes)

        for response_data in response:
            data[f'{DOMAIN}-{response_data[ATTR_STATION_CODE]}'] = response_data[ATTR_STATION_REAL_KPI_DATA_ITEM_MAP]

        _LOGGER.debug(f'async_update_station_real_kpi_data: {data}')

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarOpenAPIStationRealKpi',
        update_method=async_update_station_real_kpi_data,
        update_interval=timedelta(seconds=600),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    for station in stations:
        entities_to_create = [
            {'class': 'FusionSolarStationAttributeEntity', 'name': 'Station Code', 'suffix': 'station_code',
             'value': station.code},
            {'class': 'FusionSolarStationAttributeEntity', 'name': 'Station Name', 'suffix': 'station_name',
             'value': station.name},
            {'class': 'FusionSolarStationAddressEntity', 'name': 'Station Address', 'suffix': 'station_address',
             'value': station.address},
            {'class': 'FusionSolarStationCapacityEntity', 'name': 'Capacity', 'suffix': 'capacity',
             'value': station.capacity},
            {'class': 'FusionSolarStationContactPersonEntity', 'name': 'Contact Person', 'suffix': 'contact_person',
             'value': station.contact_person},
            {'class': 'FusionSolarStationContactPersonPhoneEntity', 'name': 'Contact Phone', 'suffix': 'contact_phone',
             'value': station.contact_phone},
        ]

        entities = []
        for entity_to_create in entities_to_create:
            class_name = globals()[entity_to_create['class']]
            entities.append(
                class_name(station, entity_to_create['name'], entity_to_create['suffix'], entity_to_create['value'], )
            )
        async_add_entities(entities)

        async_add_entities([
            FusionSolarEnergySensorTotalCurrentDay(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_CURRENT_DAY_ENERGY}',
                f'{station.readable_name} - {NAME_TOTAL_CURRENT_DAY_ENERGY}',
                ATTR_STATION_REAL_KPI_TOTAL_CURRENT_DAY_ENERGY,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            ),
            FusionSolarEnergySensorTotalCurrentMonth(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_CURRENT_MONTH_ENERGY}',
                f'{station.readable_name} - {NAME_TOTAL_CURRENT_MONTH_ENERGY}',
                ATTR_STATION_REAL_KPI_TOTAL_CURRENT_MONTH_ENERGY,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            ),
            FusionSolarEnergySensorTotalLifetime(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_LIFETIME_ENERGY}',
                f'{station.readable_name} - {NAME_TOTAL_LIFETIME_ENERGY}',
                ATTR_STATION_REAL_KPI_TOTAL_LIFETIME_ENERGY,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            )
        ])

    async def async_update_station_year_kpi_data():
        data = {}
        collect_times = {}
        response = await hass.async_add_executor_job(api.get_kpi_station_year, station_codes)

        for response_data in response:
            key = f'{DOMAIN}-{response_data[ATTR_STATION_CODE]}'

            if key in collect_times and key in data:
                # Only update if the collectTime is newer
                if response_data[ATTR_DATA_COLLECT_TIME] > collect_times[key]:
                    data[key] = response_data[ATTR_STATION_REAL_KPI_DATA_ITEM_MAP]
                    collect_times[key] = response_data[ATTR_DATA_COLLECT_TIME]
            else:
                data[key] = response_data[ATTR_STATION_REAL_KPI_DATA_ITEM_MAP]
                collect_times[key] = response_data[ATTR_DATA_COLLECT_TIME]

        _LOGGER.debug(f'async_update_station_year_kpi_data: {data}')

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarOpenAPIStationYearKpi',
        update_method=async_update_station_year_kpi_data,
        update_interval=timedelta(seconds=600),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    for station in stations:
        async_add_entities([
            FusionSolarEnergySensorTotalCurrentYear(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_CURRENT_YEAR_ENERGY}',
                f'{station.readable_name} - {NAME_TOTAL_CURRENT_YEAR_ENERGY}',
                ATTR_KPI_YEAR_INVERTER_POWER,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            )
        ])

    devices = await hass.async_add_executor_job(api.get_dev_list, station_codes)
    devices_grouped_per_type_id = {}
    for device in devices:
        if device.type_id not in [PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_EMI,
                                  PARAM_DEVICE_TYPE_ID_GRID_METER, PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER,
                                  PARAM_DEVICE_TYPE_ID_BATTERY, PARAM_DEVICE_TYPE_ID_POWER_SENSOR]:
            continue

        if device.type_id not in devices_grouped_per_type_id:
            devices_grouped_per_type_id[device.type_id] = []
        devices_grouped_per_type_id[device.type_id].append(str(device.device_id))

    async def async_update_device_real_kpi_data():
        data = {}
        for type_id in devices_grouped_per_type_id:
            response = await hass.async_add_executor_job(
                api.get_dev_real_kpi,
                devices_grouped_per_type_id[type_id],
                type_id
            )

            for response_data in response:
                key = f'{DOMAIN}-{response_data[ATTR_DEVICE_REAL_KPI_DEV_ID]}'
                data[key] = response_data[ATTR_DEVICE_REAL_KPI_DATA_ITEM_MAP];

            _LOGGER.debug(f'async_update_device_real_kpi_data: {data}')

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarOpenAPIDeviceRealKpi',
        update_method=async_update_device_real_kpi_data,
        update_interval=timedelta(seconds=60),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    for device in devices:
        entities_to_create = [
            {'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Device ID', 'suffix': 'device_id',
             'value': device.device_id},
            {'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Device name', 'suffix': 'device_name',
             'value': device.name},
            {'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Station code', 'suffix': 'station_code',
             'value': device.station_code},
            {'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Serial number', 'suffix': 'esn_code',
             'value': device.esn_code},
            {'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Device type ID', 'suffix': 'device_type_id',
             'value': device.type_id},
            {'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Device type', 'suffix': 'device_type',
             'value': device.device_type},
            {'class': 'FusionSolarDeviceLatitudeEntity', 'name': 'Latitude', 'suffix': 'latitude',
             'value': device.latitude},
            {'class': 'FusionSolarDeviceLongitudeEntity', 'name': 'Longitude', 'suffix': 'longitude',
             'value': device.longitude},
        ]

        if device.type_id in [PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER]:
            entity_to_create.update({
                'class': 'FusionSolarDeviceAttributeEntity', 'name': 'Inverter model', 'suffix': 'inverter_type',
                'value': device.inverter_type
            })

        entities = []
        for entity_to_create in entities_to_create:
            class_name = globals()[entity_to_create['class']]
            entities.append(
                class_name(device, entity_to_create['name'], entity_to_create['suffix'], entity_to_create['value'], )
            )
        async_add_entities(entities)

        if device.type_id in [PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_GRID_METER,
                              PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER, PARAM_DEVICE_TYPE_ID_POWER_SENSOR]:
            async_add_entities([
                FusionSolarPowerEntityRealtime(
                    coordinator,
                    f'{DOMAIN}-{device.device_id}-{ID_REALTIME_POWER}',
                    f'{device.readable_name} - {NAME_REALTIME_POWER}',
                    ATTR_DEVICE_REAL_KPI_ACTIVE_POWER,
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ),
            ])

        entities_to_create = []

        if device.type_id == PARAM_DEVICE_TYPE_ID_STRING_INVERTER:
            entities_to_create = [
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'inverter_state',
                 'name': 'Inverter status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableInverterStateSensor', 'attribute': 'inverter_state',
                 'name': 'Readable inverter status'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'ab_u', 'name': 'Grid AB voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'bc_u', 'name': 'Grid BC voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'ca_u', 'name': 'Grid CA voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'a_u', 'name': 'Phase A voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'b_u', 'name': 'Phase B voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'c_u', 'name': 'Phase C voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'a_i', 'name': 'Phase A current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'b_i', 'name': 'Phase B current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'c_i', 'name': 'Phase C current'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'efficiency',
                 'name': 'Inverter efficiency % (manufacturer)'},
                {'class': 'FusionSolarRealtimeDeviceDataTemperatureSensor', 'attribute': 'temperature',
                 'name': 'Inverter internal temperature'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerFactorSensor', 'attribute': 'power_factor',
                 'name': 'Power factor'},
                {'class': 'FusionSolarRealtimeDeviceDataFrequencySensor', 'attribute': 'elec_freq',
                 'name': 'Grid frequency'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'active_power',
                 'name': 'Active power'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reactive_power',
                 'name': 'Reactive output power'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'day_cap', 'name': 'Yield Today'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'mppt_power',
                 'name': 'MPPT total input power'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv1_u',
                 'name': 'PV1 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv2_u',
                 'name': 'PV2 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv3_u',
                 'name': 'PV3 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv4_u',
                 'name': 'PV4 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv5_u',
                 'name': 'PV5 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv6_u',
                 'name': 'PV6 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv7_u',
                 'name': 'PV7 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv8_u',
                 'name': 'PV8 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv9_u',
                 'name': 'PV9 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv10_u',
                 'name': 'PV10 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv11_u',
                 'name': 'PV11 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv12_u',
                 'name': 'PV12 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv13_u',
                 'name': 'PV13 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv14_u',
                 'name': 'PV14 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv15_u',
                 'name': 'PV15 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv16_u',
                 'name': 'PV16 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv17_u',
                 'name': 'PV17 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv18_u',
                 'name': 'PV18 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv19_u',
                 'name': 'PV19 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv20_u',
                 'name': 'PV20 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv21_u',
                 'name': 'PV21 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv22_u',
                 'name': 'PV22 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv23_u',
                 'name': 'PV23 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv24_u',
                 'name': 'PV24 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv1_i',
                 'name': 'PV1 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv2_i',
                 'name': 'PV2 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv3_i',
                 'name': 'PV3 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv4_i',
                 'name': 'PV4 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv5_i',
                 'name': 'PV5 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv6_i',
                 'name': 'PV6 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv7_i',
                 'name': 'PV7 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv8_i',
                 'name': 'PV8 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv9_i',
                 'name': 'PV9 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv10_i',
                 'name': 'PV10 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv11_i',
                 'name': 'PV11 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv12_i',
                 'name': 'PV12 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv13_i',
                 'name': 'PV13 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv14_i',
                 'name': 'PV14 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv15_i',
                 'name': 'PV15 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv16_i',
                 'name': 'PV16 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv17_i',
                 'name': 'PV17 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv18_i',
                 'name': 'PV18 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv19_i',
                 'name': 'PV19 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv20_i',
                 'name': 'PV20 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv21_i',
                 'name': 'PV21 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv22_i',
                 'name': 'PV22 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv23_i',
                 'name': 'PV23 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv24_i',
                 'name': 'PV24 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'total_cap', 'name': 'Total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataTimestampSensor', 'attribute': 'open_time',
                 'name': 'Inverter startup time'},
                {'class': 'FusionSolarRealtimeDeviceDataTimestampSensor', 'attribute': 'close_time',
                 'name': 'Inverter shutdown time'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_1_cap',
                 'name': 'MPPT 1 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_2_cap',
                 'name': 'MPPT 2 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_3_cap',
                 'name': 'MPPT 3 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_4_cap',
                 'name': 'MPPT 4 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_5_cap',
                 'name': 'MPPT 5 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_6_cap',
                 'name': 'MPPT 6 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_7_cap',
                 'name': 'MPPT 7 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_8_cap',
                 'name': 'MPPT 8 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_9_cap',
                 'name': 'MPPT 9 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_10_cap',
                 'name': 'MPPT 10 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataStateBinarySensor', 'attribute': 'run_state', 'name': 'Status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableRunStateSensor', 'attribute': 'run_state',
                 'name': 'Readable status'},
            ]

        if device.type_id == PARAM_DEVICE_TYPE_ID_EMI:
            entities_to_create = [
                {'class': 'FusionSolarRealtimeDeviceDataTemperatureSensor', 'attribute': 'temperature',
                 'name': 'Temperature'},
                {'class': 'FusionSolarRealtimeDeviceDataTemperatureSensor', 'attribute': 'pv_temperature',
                 'name': 'PV temperature'},
                {'class': 'FusionSolarRealtimeDeviceDataWindSpeedSensor', 'attribute': 'wind_speed',
                 'name': 'Wind speed'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'wind_direction',
                 'name': 'Wind direction'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'radiant_total',
                 'name': 'Daily irradiation'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'radiant_line', 'name': 'Irradiance'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'horiz_radiant_line',
                 'name': 'Horizontal irradiance'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'horiz_radiant_total',
                 'name': 'Horizontal irradiation'},
                {'class': 'FusionSolarRealtimeDeviceDataStateBinarySensor', 'attribute': 'run_state', 'name': 'Status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableRunStateSensor', 'attribute': 'run_state',
                 'name': 'Readable status'},
            ]

        if device.type_id == PARAM_DEVICE_TYPE_ID_GRID_METER:
            entities_to_create = [
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'ab_u', 'name': 'Grid AB voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'bc_u', 'name': 'Grid BC voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'ca_u', 'name': 'Grid CA voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'a_u', 'name': 'Phase A voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'b_u', 'name': 'Phase B voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'c_u', 'name': 'Phase C voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'a_i', 'name': 'Phase A current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'b_i', 'name': 'Phase B current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'c_i', 'name': 'Phase C current'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'active_power',
                 'name': 'Active power'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerFactorSensor', 'attribute': 'power_factor',
                 'name': 'Power factor'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'active_cap',
                 'name': 'Active energy (forward active energy)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reactive_power',
                 'name': 'Reactive power'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_active_cap',
                 'name': 'Reverse active energy'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'forward_reactive_cap',
                 'name': 'Forward active energy'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_reactive_cap',
                 'name': 'Reverse reactive energy'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'active_power_a',
                 'name': 'Active power PA'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'active_power_b',
                 'name': 'Active power PB'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'active_power_c',
                 'name': 'Active power PC'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reactive_power_a',
                 'name': 'Reactive power QA'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reactive_power_b',
                 'name': 'Reactive power QB'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reactive_power_c',
                 'name': 'Reactive power QC'},
                {'class': 'FusionSolarRealtimeDeviceDataApparentPowerSensor', 'attribute': 'total_apparent_power',
                 'name': 'Total apparent power'},
                {'class': 'FusionSolarRealtimeDeviceDataFrequencySensor', 'attribute': 'grid_frequency',
                 'name': 'Grid frequency'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_active_peak',
                 'name': 'Reverse active energy (peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_active_power',
                 'name': 'Reverse active energy (shoulder)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_active_valley',
                 'name': 'Reverse active energy (off-peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_active_top',
                 'name': 'Reverse active energy (sharp)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'positive_active_peak',
                 'name': 'Forward active energy (peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'positive_active_power',
                 'name': 'Forward active energy (shoulder)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'positive_active_valley',
                 'name': 'Forward active energy (off-peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'positive_active_top',
                 'name': 'Forward active energy (sharp)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reverse_reactive_peak',
                 'name': 'Reverse reactive energy (peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reverse_reactive_power',
                 'name': 'Reverse reactive energy (shoulder)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reverse_reactive_valley',
                 'name': 'Reverse reactive energy (off-peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reverse_reactive_top',
                 'name': 'Reverse reactive energy (sharp)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'positive_reactive_peak',
                 'name': 'Forward reactive energy (peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'positive_reactive_power',
                 'name': 'Forward reactive energy (shoulder)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'positive_reactive_valley',
                 'name': 'Forward reactive energy (off-peak)'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'positive_reactive_top',
                 'name': 'Forward reactive energy (sharp)'},
            ]

        if device.type_id == PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER:
            entities_to_create = [
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'inverter_state',
                 'name': 'Inverter status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableInverterStateSensor', 'attribute': 'inverter_state',
                 'name': 'Readable inverter status'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'ab_u', 'name': 'Grid AB voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'bc_u', 'name': 'Grid BC voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'ca_u', 'name': 'Grid CA voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'a_u', 'name': 'Phase A voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'b_u', 'name': 'Phase B voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'c_u', 'name': 'Phase C voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'a_i', 'name': 'Phase A current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'b_i', 'name': 'Phase B current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'c_i', 'name': 'Phase C current'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'efficiency',
                 'name': 'Inverter efficiency % (manufacturer)'},
                {'class': 'FusionSolarRealtimeDeviceDataTemperatureSensor', 'attribute': 'temperature',
                 'name': 'Inverter internal temperature'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerFactorSensor', 'attribute': 'power_factor',
                 'name': 'Power factor'},
                {'class': 'FusionSolarRealtimeDeviceDataFrequencySensor', 'attribute': 'elec_freq',
                 'name': 'Grid frequency'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'active_power',
                 'name': 'Active power'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerSensor', 'attribute': 'reactive_power',
                 'name': 'Reactive output power'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'day_cap', 'name': 'Yield Today'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerSensor', 'attribute': 'mppt_power',
                 'name': 'MPPT total input power'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv1_u',
                 'name': 'PV1 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv2_u',
                 'name': 'PV2 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv3_u',
                 'name': 'PV3 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv4_u',
                 'name': 'PV4 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv5_u',
                 'name': 'PV5 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv6_u',
                 'name': 'PV6 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv7_u',
                 'name': 'PV7 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'pv8_u',
                 'name': 'PV8 input voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv1_i',
                 'name': 'PV1 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv2_i',
                 'name': 'PV2 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv3_i',
                 'name': 'PV3 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv4_i',
                 'name': 'PV4 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv5_i',
                 'name': 'PV5 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv6_i',
                 'name': 'PV6 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv7_i',
                 'name': 'PV7 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'pv8_i',
                 'name': 'PV8 input current'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'total_cap', 'name': 'Total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataTimestampSensor', 'attribute': 'open_time',
                 'name': 'Inverter startup time'},
                {'class': 'FusionSolarRealtimeDeviceDataTimestampSensor', 'attribute': 'close_time',
                 'name': 'Inverter shutdown time'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_1_cap',
                 'name': 'MPPT 1 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_2_cap',
                 'name': 'MPPT 2 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_3_cap',
                 'name': 'MPPT 3 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'mppt_4_cap',
                 'name': 'MPPT 4 DC total yield'},
                {'class': 'FusionSolarRealtimeDeviceDataStateBinarySensor', 'attribute': 'run_state', 'name': 'Status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableRunStateSensor', 'attribute': 'run_state',
                 'name': 'Readable status'},
            ]

        if device.type_id == PARAM_DEVICE_TYPE_ID_BATTERY:
            entities_to_create = [
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'battery_status',
                 'name': 'Battery running status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableBatteryStatusSensor', 'attribute': 'battery_status',
                 'name': 'Readable battery running status'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerInWattSensor', 'attribute': 'max_charge_power',
                 'name': 'Maximum charge power'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerInWattSensor', 'attribute': 'max_discharge_power',
                 'name': 'Maximum discharge power'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerInWattSensor', 'attribute': 'ch_discharge_power',
                 'name': 'Charge/Discharge power'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'busbar_u',
                 'name': 'Battery voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataBatterySensor', 'attribute': 'battery_soc',
                 'name': 'Battery state of charge (SOC)'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'battery_soh',
                 'name': 'Battery state of health (SOH)'},
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'ch_discharge_model',
                 'name': 'Charge/Discharge mode'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableChargeDischargeModeSensor',
                 'attribute': 'ch_discharge_model', 'name': 'Readable charge/Discharge mode'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'charge_cap',
                 'name': 'Charging capacity'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'discharge_cap',
                 'name': 'Discharging capacity'},
                {'class': 'FusionSolarRealtimeDeviceDataStateBinarySensor', 'attribute': 'run_state', 'name': 'Status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableRunStateSensor', 'attribute': 'run_state',
                 'name': 'Readable status'},
            ]

        if device.type_id == PARAM_DEVICE_TYPE_ID_POWER_SENSOR:
            entities_to_create = [
                {'class': 'FusionSolarRealtimeDeviceDataSensor', 'attribute': 'meter_status', 'name': 'Meter status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableMeterStatusSensor', 'attribute': 'meter_status',
                 'name': 'Meter status'},
                {'class': 'FusionSolarRealtimeDeviceDataVoltageSensor', 'attribute': 'meter_u', 'name': 'Grid voltage'},
                {'class': 'FusionSolarRealtimeDeviceDataCurrentSensor', 'attribute': 'meter_i', 'name': 'Grid current'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerInWattSensor', 'attribute': 'active_power',
                 'name': 'Active power'},
                {'class': 'FusionSolarRealtimeDeviceDataReactivePowerInVarSensor', 'attribute': 'reactive_power',
                 'name': 'Reactive power'},
                {'class': 'FusionSolarRealtimeDeviceDataPowerFactorSensor', 'attribute': 'power_factor',
                 'name': 'Power factor'},
                {'class': 'FusionSolarRealtimeDeviceDataFrequencySensor', 'attribute': 'grid_frequency',
                 'name': 'Grid frequency'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'active_cap',
                 'name': 'Active energy (forward active energy)'},
                {'class': 'FusionSolarRealtimeDeviceDataEnergySensor', 'attribute': 'reverse_active_cap',
                 'name': 'Reverse active energy'},
                {'class': 'FusionSolarRealtimeDeviceDataStateBinarySensor', 'attribute': 'run_state', 'name': 'Status'},
                {'class': 'FusionSolarRealtimeDeviceDataReadableRunStateSensor', 'attribute': 'run_state',
                 'name': 'Readable status'},
            ]

        entities = []
        for entity_to_create in entities_to_create:
            class_name = globals()[entity_to_create['class']]
            entities.append(
                class_name(coordinator, device, entity_to_create['name'], entity_to_create['attribute'])
            )
        async_add_entities(entities)


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)

    for kioskConfig in config[CONF_KIOSKS]:
        kiosk = FusionSolarKiosk(kioskConfig[CONF_URL], kioskConfig[CONF_NAME])
        await add_entities_for_kiosk(hass, async_add_entities, kiosk)

    if config[CONF_OPENAPI_CREDENTIALS]:
        # get stations from openapi
        api = FusionSolarOpenApi(
            config[CONF_OPENAPI_CREDENTIALS][CONF_HOST],
            config[CONF_OPENAPI_CREDENTIALS][CONF_USERNAME],
            config[CONF_OPENAPI_CREDENTIALS][CONF_PASSWORD],
        )
        stations = await hass.async_add_executor_job(api.get_station_list)
        await add_entities_for_stations(hass, async_add_entities, stations, api)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    for kioskConfig in config[CONF_KIOSKS]:
        kiosk = FusionSolarKiosk(kioskConfig[CONF_URL], kioskConfig[CONF_NAME])
        await add_entities_for_kiosk(hass, async_add_entities, kiosk)
