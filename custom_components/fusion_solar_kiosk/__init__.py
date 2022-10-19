"""
Custom integration to integrate FusionSolar Kiosk with Home Assistant.
"""
from homeassistant.core import HomeAssistant, Config


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up the FusionSolar Kiosk component."""
    return True
