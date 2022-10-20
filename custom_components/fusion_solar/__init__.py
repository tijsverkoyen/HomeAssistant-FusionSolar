"""
Custom integration to integrate FusionSolar with Home Assistant.
"""
from homeassistant.core import HomeAssistant, Config


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up the FusionSolar component."""
    return True
