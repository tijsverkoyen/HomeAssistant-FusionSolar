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
    ATTR_STATION_REAL_KPI_TOTAL_CURRENT_MONTH_ENERGY, ATTR_STATION_REAL_KPI_TOTAL_LIFETIME_ENERGY
from .fusion_solar.kiosk.kiosk import Kiosk
from .fusion_solar.kiosk.kiosk_api import FusionSolarKioskApi
from .fusion_solar.openapi.openapi_api import FusionSolarOpenApi
from .fusion_solar.energy_sensor import FusionSolarEnergySensorTotalCurrentDay, \
    FusionSolarEnergySensorTotalCurrentMonth, FusionSolarEnergySensorTotalCurrentYear, \
    FusionSolarEnergySensorTotalLifetime
from .fusion_solar.power_entity import FusionSolarPowerEntityRealtime

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


async def add_entities_for_kiosk(hass, async_add_entities, kiosk: Kiosk):
    _LOGGER.debug(f'Adding entities for kiosk {kiosk.id}')

    async def async_update_data():
        """Fetch data"""
        data = {}
        api = FusionSolarKioskApi(kiosk.apiUrl())
        data[f'{DOMAIN}-{kiosk.id}'] = {
            ATTR_DATA_REALKPI: await hass.async_add_executor_job(api.getRealTimeKpi, kiosk.id)
        }
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarKiosk',
        update_method=async_update_data,
        update_interval=timedelta(seconds=300),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    async_add_entities([
        FusionSolarPowerEntityRealtime(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_REALTIME_POWER}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_REALTIME_POWER}',
            ATTR_REALTIME_POWER,
            f'{DOMAIN}-{kiosk.id}',
        ),

        FusionSolarEnergySensorTotalCurrentDay(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_DAY_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_DAY_ENERGY}',
            ATTR_TOTAL_CURRENT_DAY_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
        ),
        FusionSolarEnergySensorTotalCurrentMonth(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_MONTH_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_MONTH_ENERGY}',
            ATTR_TOTAL_CURRENT_MONTH_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
        ),
        FusionSolarEnergySensorTotalCurrentYear(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_YEAR_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_YEAR_ENERGY}',
            ATTR_TOTAL_CURRENT_YEAR_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
        ),
        FusionSolarEnergySensorTotalLifetime(
            coordinator,
            f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_LIFETIME_ENERGY}',
            f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_LIFETIME_ENERGY}',
            ATTR_TOTAL_LIFETIME_ENERGY,
            f'{DOMAIN}-{kiosk.id}',
        )
    ])


async def add_entities_for_stations(hass, async_add_entities, stations, api: FusionSolarOpenApi):
    _LOGGER.debug(f'Adding entities for stations')
    station_codes = [station.code for station in stations]

    async def async_update_data():
        """Fetch data"""
        data = {}
        response = await hass.async_add_executor_job(api.get_station_real_kpi, station_codes)
        _LOGGER.debug(f'response: {response}')

        for data in response:
            data[f'{DOMAIN}-{data[ATTR_STATION_CODE]}'] = {
                ATTR_DATA_REALKPI: data[ATTR_STATION_REAL_KPI_DATA_ITEM_MAP]
            }

        _LOGGER.debug(f'async_update_data: {data}')

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name='FusionSolarOpenAPIRealKpi',
        update_method=async_update_data,
        update_interval=timedelta(seconds=300),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    for station in stations:
        async_add_entities([
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
            #     FusionSolarEnergySensorTotalCurrentYear(
            #         coordinator,
            #         f'{DOMAIN}-{kiosk.id}-{ID_TOTAL_CURRENT_YEAR_ENERGY}',
            #         f'{kiosk.name} ({kiosk.id}) - {NAME_TOTAL_CURRENT_YEAR_ENERGY}',
            #         ATTR_TOTAL_CURRENT_YEAR_ENERGY,
            #         f'{DOMAIN}-{kiosk.id}',
            #     ),
            FusionSolarEnergySensorTotalLifetime(
                coordinator,
                f'{DOMAIN}-{station.code}-{ID_TOTAL_LIFETIME_ENERGY}',
                f'{station.name} ({station.code}) - {NAME_TOTAL_LIFETIME_ENERGY}',
                ATTR_STATION_REAL_KPI_TOTAL_LIFETIME_ENERGY,
                f'{DOMAIN}-{station.code}',
                station.device_info()
            )
        ])


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)

    for kioskConfig in config[CONF_KIOSKS]:
        kiosk = Kiosk(kioskConfig[CONF_URL], kioskConfig[CONF_NAME])
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

        _LOGGER.debug(stations)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    for kioskConfig in config[CONF_KIOSKS]:
        kiosk = Kiosk(kioskConfig[CONF_URL], kioskConfig[CONF_NAME])
        await add_entities_for_kiosk(hass, async_add_entities, kiosk)
