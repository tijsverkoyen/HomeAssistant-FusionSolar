"""
Custom integration to integrate FusionSolar Kiosk with Home Assistant.
"""
from homeassistant import core

async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the FusionSolar Kiosk component."""
    return True
