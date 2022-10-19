"""Constants for FusionSolar Kiosk."""
# Base constants
DOMAIN = 'fusion_solar_kiosk'

# Configuration
CONF_KIOSKS = 'kiosks'
CONF_KIOSK_URL = 'url'

# Fusion Solar Kiosk API response attributes
ATTR_DATA = 'data'
ATTR_FAIL_CODE = 'failCode'
ATTR_SUCCESS = 'success'
ATTR_DATA_REALKPI = 'realKpi'
# Data attributes
ATTR_REALTIME_POWER = 'realTimePower'
ATTR_TOTAL_CURRENT_DAY_ENERGY = 'dailyEnergy'
ATTR_TOTAL_CURRENT_MONTH_ENERGY = 'monthEnergy'
ATTR_TOTAL_CURRENT_YEAR_ENERGY = 'yearEnergy'
ATTR_TOTAL_LIFETIME_ENERGY = 'cumulativeEnergy'

# Possible ID suffixes
ID_REALTIME_POWER = 'realtime_power'
ID_TOTAL_CURRENT_DAY_ENERGY = 'total_current_day_energy'
ID_TOTAL_CURRENT_MONTH_ENERGY = 'total_current_month_energy'
ID_TOTAL_CURRENT_YEAR_ENERGY = 'total_current_year_energy'
ID_TOTAL_LIFETIME_ENERGY = 'total_lifetime_energy'

# Possible Name suffixes
NAME_REALTIME_POWER = 'Realtime Power'
NAME_TOTAL_CURRENT_DAY_ENERGY = 'Total Current Day Energy'
NAME_TOTAL_CURRENT_MONTH_ENERGY = 'Total Current Month Energy'
NAME_TOTAL_CURRENT_YEAR_ENERGY = 'Total Current Year Energy'
NAME_TOTAL_LIFETIME_ENERGY = 'Total Lifetime Energy'
