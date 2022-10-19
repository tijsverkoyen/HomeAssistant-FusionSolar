"""FusionSolar Kiosk sensor."""
import homeassistant.helpers.config_validation as cv
import logging
import voluptuous as vol

from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .fusion_solar.const import ATTR_DATA_REALKPI, ATTR_REALTIME_POWER, ATTR_TOTAL_CURRENT_DAY_ENERGY, \
    ATTR_TOTAL_CURRENT_MONTH_ENERGY, ATTR_TOTAL_CURRENT_YEAR_ENERGY, ATTR_TOTAL_LIFETIME_ENERGY
from .fusion_solar.kiosk import Kiosk
from .fusion_solar.kiosk_api import FusionSolarKioksApi
from .fusion_solar.energy_sensor import FusionSolarEnergySensorTotalCurrentDay, \
    FusionSolarEnergySensorTotalCurrentMonth, FusionSolarEnergySensorTotalCurrentYear, \
    FusionSolarEnergySensorTotalLifetime
from .fusion_solar.power_entity import FusionSolarPowerEntityRealtime

from .const import CONF_KIOSK_URL, CONF_KIOSKS, DOMAIN, ID_REALTIME_POWER, NAME_REALTIME_POWER, \
    ID_TOTAL_CURRENT_DAY_ENERGY, NAME_TOTAL_CURRENT_DAY_ENERGY, \
    ID_TOTAL_CURRENT_MONTH_ENERGY, NAME_TOTAL_CURRENT_MONTH_ENERGY, \
    ID_TOTAL_CURRENT_YEAR_ENERGY, NAME_TOTAL_CURRENT_YEAR_ENERGY, \
    ID_TOTAL_LIFETIME_ENERGY, NAME_TOTAL_LIFETIME_ENERGY

KIOSK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_KIOSK_URL): cv.string,
        vol.Required(CONF_NAME): cv.string
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KIOSKS): vol.All(cv.ensure_list, [KIOSK_SCHEMA]),
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async def async_update_data():
        """Fetch data"""
        data = {}
        for kioskConfig in config[CONF_KIOSKS]:
            kiosk = Kiosk(kioskConfig['url'], kioskConfig['name'])
            api = FusionSolarKioksApi(kiosk.apiUrl())
            name = f'{DOMAIN}-{kiosk.id}'
            data[name] = {
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

    for kioskConfig in config[CONF_KIOSKS]:
        kiosk = Kiosk(kioskConfig['url'], kioskConfig['name'])

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
