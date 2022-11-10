"""FusionSolar sensor."""
import homeassistant.helpers.config_validation as cv
import logging
import voluptuous as vol

from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_URL, CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .fusion_solar.const import ATTR_DATA_REALKPI, ATTR_REALTIME_POWER, ATTR_TOTAL_CURRENT_DAY_ENERGY, \
    ATTR_TOTAL_CURRENT_MONTH_ENERGY, ATTR_TOTAL_CURRENT_YEAR_ENERGY, ATTR_TOTAL_LIFETIME_ENERGY, \
    ATTR_STATION_CODE, ATTR_STATION_REAL_KPI_DATA_ITEM_MAP, ATTR_STATION_REAL_KPI_TOTAL_CURRENT_DAY_ENERGY, \
    ATTR_STATION_REAL_KPI_TOTAL_CURRENT_MONTH_ENERGY, ATTR_STATION_REAL_KPI_TOTAL_LIFETIME_ENERGY, \
    ATTR_DATA_COLLECT_TIME, ATTR_KPI_YEAR_INVERTER_POWER, ATTR_DEVICE_REAL_KPI_ACTIVE_POWER, \
    PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_GRID_METER, PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER, \
    PARAM_DEVICE_TYPE_ID_POWER_SENSOR, ATTR_DEVICE_REAL_KPI_DEV_ID, ATTR_DEVICE_REAL_KPI_DATA_ITEM_MAP, \
    ATTR_DEVICE_TYPE_ID
from .fusion_solar.kiosk.kiosk import FusionSolarKiosk
from .fusion_solar.kiosk.kiosk_api import FusionSolarKioskApi
from .fusion_solar.openapi.openapi_api import FusionSolarOpenApi
from .fusion_solar.energy_sensor import FusionSolarEnergySensorTotalCurrentDay, \
    FusionSolarEnergySensorTotalCurrentMonth, FusionSolarEnergySensorTotalCurrentYear, \
    FusionSolarEnergySensorTotalLifetime
from .fusion_solar.power_entity import FusionSolarPowerEntityRealtime
from .fusion_solar.realtime_device_data_sensor import FusionSolarRealtimeDeviceDataSensor, \
    FusionSolarRealtimeDeviceDataReadableInverterStateSensor, FusionSolarRealtimeDeviceDataVoltageSensor, \
    FusionSolarRealtimeDeviceDataCurrentSensor, FusionSolarRealtimeDeviceDataEnergySensor, \
    FusionSolarRealtimeDeviceDataTemperatureSensor, FusionSolarRealtimeDeviceDataPowerFactorSensor, \
    FusionSolarRealtimeDeviceDataFrequencySensor, FusionSolarRealtimeDeviceDataPowerSensor, \
    FusionSolarRealtimeDeviceDataReactivePowerSensor, FusionSolarRealtimeDeviceDataTimestampSensor, \
    FusionSolarRealtimeDeviceDataReadableStateSensor, FusionSolarRealtimeDeviceDataStateBinarySensor
from .fusion_solar.station_attribute_entity import FusionSolarAttributeEntity, FusionSolarAddressEntity, \
    FusionSolarCapacityEntity, FusionSolarContactPersonEntity, FusionSolarContactPersonPhoneEntity, \
    FusionSolarLatitudeEntity, FusionSolarLongitudeEntity

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
        async_add_entities([
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{station.code}-station-code',
                f'{station.name} ({station.code}) - Station Code',
                station.code,
                station.device_info()
            ),
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{station.code}-station-name',
                f'{station.name} ({station.code}) - Station Name',
                station.name,
                station.device_info()
            ),
            FusionSolarAddressEntity(
                f'{DOMAIN}-{station.code}-station-address',
                f'{station.name} ({station.code}) - Station Address',
                station.address,
                station.device_info()
            ),
            FusionSolarCapacityEntity(
                f'{DOMAIN}-{station.code}-capacity',
                f'{station.name} ({station.code}) - Capacity',
                station.capacity,
                station.device_info()
            ),
            FusionSolarContactPersonEntity(
                f'{DOMAIN}-{station.code}-contact-person',
                f'{station.name} ({station.code}) - Contact Person',
                station.contact_person,
                station.device_info()
            ),
            FusionSolarContactPersonPhoneEntity(
                f'{DOMAIN}-{station.code}-contact-phone',
                f'{station.name} ({station.code}) - Contact Phone',
                station.contact_phone,
                station.device_info()
            ),

            FusionSolarEnergySensorTotalCurrentDay(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_CURRENT_DAY_ENERGY}',
                f'{station.name} ({station.code}) - {NAME_TOTAL_CURRENT_DAY_ENERGY}',
                ATTR_STATION_REAL_KPI_TOTAL_CURRENT_DAY_ENERGY,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            ),
            FusionSolarEnergySensorTotalCurrentMonth(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_CURRENT_MONTH_ENERGY}',
                f'{station.name} ({station.code}) - {NAME_TOTAL_CURRENT_MONTH_ENERGY}',
                ATTR_STATION_REAL_KPI_TOTAL_CURRENT_MONTH_ENERGY,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            ),
            FusionSolarEnergySensorTotalLifetime(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_LIFETIME_ENERGY}',
                f'{station.name} ({station.code}) - {NAME_TOTAL_LIFETIME_ENERGY}',
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
                f'{station.name} ({station.code}) - {NAME_TOTAL_CURRENT_YEAR_ENERGY}',
                ATTR_KPI_YEAR_INVERTER_POWER,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            )
        ])

    devices = await hass.async_add_executor_job(api.get_dev_list, station_codes)
    devices_grouped_per_type_id = {}
    for device in devices:
        if device.type_id not in [PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_GRID_METER,
                                  PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER, PARAM_DEVICE_TYPE_ID_POWER_SENSOR]:
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
        async_add_entities([
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{device.esn_code}-device-id',
                f'{device.name} ({device.esn_code}) - Device ID',
                device.device_id,
                device.device_info()
            ),
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{device.esn_code}-device-name',
                f'{device.name} ({device.esn_code}) - Device Name',
                device.name,
                device.device_info()
            ),
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{device.esn_code}-station-code',
                f'{device.name} ({device.esn_code}) - Station Code',
                device.station_code,
                device.device_info()
            ),
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{device.esn_code}-esn-code',
                f'{device.name} ({device.esn_code}) - Serial Number',
                device.esn_code,
                device.device_info()
            ),
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{device.esn_code}-device-type-id',
                f'{device.name} ({device.esn_code}) - Device Type ID',
                device.type_id,
                device.device_info()
            ),
            FusionSolarAttributeEntity(
                f'{DOMAIN}-{device.esn_code}-device-type',
                f'{device.name} ({device.esn_code}) - Device Type',
                device.device_type,
                device.device_info()
            ),
            FusionSolarLatitudeEntity(
                f'{DOMAIN}-{device.esn_code}-latitude',
                f'{device.name} ({device.esn_code}) - Latitude',
                device.latitude,
                device.device_info()
            ),
            FusionSolarLongitudeEntity(
                f'{DOMAIN}-{device.esn_code}-longitude',
                f'{device.name} ({device.esn_code}) - Longitude',
                device.longitude,
                device.device_info()
            ),
        ])

        if device.type_id in [PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_GRID_METER,
                              PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER, PARAM_DEVICE_TYPE_ID_POWER_SENSOR]:
            async_add_entities([
                FusionSolarPowerEntityRealtime(
                    coordinator,
                    f'{DOMAIN}-{device.esn_code}-{ID_REALTIME_POWER}',
                    f'{device.name} ({device.esn_code}) - {NAME_REALTIME_POWER}',
                    ATTR_DEVICE_REAL_KPI_ACTIVE_POWER,
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ),
            ])

        if device.type_id in [PARAM_DEVICE_TYPE_ID_STRING_INVERTER, PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER]:
            async_add_entities([
                FusionSolarAttributeEntity(
                    f'{DOMAIN}-{device.esn_code}-inverter_type',
                    f'{device.name} ({device.esn_code}) - Inverter Type',
                    device.inverter_type,
                    device.device_info()
                ),
            ])

        if device.type_id == PARAM_DEVICE_TYPE_ID_RESIDENTIAL_INVERTER:
            entities = []

            entities.append(FusionSolarRealtimeDeviceDataSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-inverter_state',
                f'{device.name} ({device.esn_code}) - Inverter State',
                'inverter_state',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))
            entities.append(FusionSolarRealtimeDeviceDataReadableInverterStateSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-readable-inverter_state',
                f'{device.name} ({device.esn_code}) - Readable Inverter State',
                'inverter_state',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

            voltages = [
                {'attribute': 'ab_u', 'name': 'Grid AB Voltage'},
                {'attribute': 'bc_u', 'name': 'Grid BC Voltage'},
                {'attribute': 'ca_u', 'name': 'Grid CA Voltage'},
                {'attribute': 'a_u', 'name': 'Phase A Voltage'},
                {'attribute': 'b_u', 'name': 'Phase B Voltage'},
                {'attribute': 'c_u', 'name': 'Phase C Voltage'},
                {'attribute': 'pv1_u', 'name': 'PV1 Input Voltage'},
                {'attribute': 'pv2_u', 'name': 'PV2 Input Voltage'},
                {'attribute': 'pv3_u', 'name': 'PV3 Input Voltage'},
                {'attribute': 'pv4_u', 'name': 'PV4 Input Voltage'},
                {'attribute': 'pv5_u', 'name': 'PV5 Input Voltage'},
                {'attribute': 'pv6_u', 'name': 'PV6 Input Voltage'},
                {'attribute': 'pv7_u', 'name': 'PV7 Input Voltage'},
                {'attribute': 'pv8_u', 'name': 'PV8 Input Voltage'},
            ]
            for item in voltages:
                entities.append(FusionSolarRealtimeDeviceDataVoltageSensor(
                    coordinator,
                    f'{DOMAIN}-{device.esn_code}-{item["attribute"]}',
                    f'{device.name} ({device.esn_code}) - {item["name"]}',
                    item['attribute'],
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ))

            currents = [
                {'attribute': 'a_i', 'name': 'Phase A Current'},
                {'attribute': 'b_i', 'name': 'Phase B Current'},
                {'attribute': 'c_i', 'name': 'Phase C Current'},
                {'attribute': 'pv1_i', 'name': 'PV1 Input Current'},
                {'attribute': 'pv2_i', 'name': 'PV2 Input Current'},
                {'attribute': 'pv3_i', 'name': 'PV3 Input Current'},
                {'attribute': 'pv4_i', 'name': 'PV4 Input Current'},
                {'attribute': 'pv5_i', 'name': 'PV5 Input Current'},
                {'attribute': 'pv6_i', 'name': 'PV6 Input Current'},
                {'attribute': 'pv7_i', 'name': 'PV7 Input Current'},
                {'attribute': 'pv8_i', 'name': 'PV8 Input Current'},
            ]
            for item in currents:
                entities.append(FusionSolarRealtimeDeviceDataCurrentSensor(
                    coordinator,
                    f'{DOMAIN}-{device.esn_code}-{item["attribute"]}',
                    f'{device.name} ({device.esn_code}) - {item["name"]}',
                    item['attribute'],
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ))

            entities.append(FusionSolarRealtimeDeviceDataCurrentSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-efficiency',
                f'{device.name} ({device.esn_code}) - Inverter efficiency % (manufacturer)',
                'efficiency',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

            entities.append(FusionSolarRealtimeDeviceDataTemperatureSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-temperature',
                f'{device.name} ({device.esn_code}) - Inverter internal temperature',
                'temperature',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

            entities.append(FusionSolarRealtimeDeviceDataPowerFactorSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-power_factor',
                f'{device.name} ({device.esn_code}) - Power factor',
                'power_factor',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

            entities.append(FusionSolarRealtimeDeviceDataFrequencySensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-elec_freq',
                f'{device.name} ({device.esn_code}) - Grid frequency',
                'elec_freq',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

            powers = [
                {'attribute': 'active_power', 'name': 'Active Power'},
                {'attribute': 'mppt_power', 'name': 'MPPT total input power'},
            ]
            for item in powers:
                entities.append(FusionSolarRealtimeDeviceDataPowerSensor(
                    coordinator,
                    f'{DOMAIN}-{device.esn_code}-{item["attribute"]}',
                    f'{device.name} ({device.esn_code}) - {item["name"]}',
                    item['attribute'],
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ))

            entities.append(FusionSolarRealtimeDeviceDataReactivePowerSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-reactive_power',
                f'{device.name} ({device.esn_code}) - Reactive output power',
                'reactive_power',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

            energies = [
                {'attribute': 'day_cap', 'name': 'Yield Today'},
                {'attribute': 'total_cap', 'name': 'Total Yield'},
                {'attribute': 'mppt_1_cap', 'name': 'MPPT 1 DC total yield'},
                {'attribute': 'mppt_2_cap', 'name': 'MPPT 2 DC total yield'},
                {'attribute': 'mppt_3_cap', 'name': 'MPPT 3 DC total yield'},
                {'attribute': 'mppt_4_cap', 'name': 'MPPT 4 DC total yield'},
            ]
            for item in energies:
                entities.append(FusionSolarRealtimeDeviceDataEnergySensor(
                    coordinator,
                    f'{DOMAIN}-{device.esn_code}-{item["attribute"]}',
                    f'{device.name} ({device.esn_code}) - {item["name"]}',
                    item['attribute'],
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ))

            timestamps = [
                {'attribute': 'open_time', 'name': 'Inverter startup time'},
                {'attribute': 'close_time', 'name': 'Inverter shutdown time'},
            ]
            for item in timestamps:
                entities.append(FusionSolarRealtimeDeviceDataTimestampSensor(
                    coordinator,
                    f'{DOMAIN}-{device.esn_code}-{item["attribute"]}',
                    f'{device.name} ({device.esn_code}) - {item["name"]}',
                    item['attribute'],
                    f'{DOMAIN}-{device.device_id}',
                    device.device_info()
                ))

            entities.append(FusionSolarRealtimeDeviceDataReadableStateSensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-readable-run_state',
                f'{device.name} ({device.esn_code}) - Readable status',
                'run_state',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))
            entities.append(FusionSolarRealtimeDeviceDataStateBinarySensor(
                coordinator,
                f'{DOMAIN}-{device.esn_code}-run_state',
                f'{device.name} ({device.esn_code}) - Status',
                'run_state',
                f'{DOMAIN}-{device.device_id}',
                device.device_info()
            ))

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
