"""
Custom integration to integrate FusionSolar with Home Assistant.
"""
from homeassistant.core import HomeAssistant, Config
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up the FusionSolar component from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the FusionSolar component from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform.
    hass.add_job(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    )
    return True
