from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
from .const import DOMAIN, CONF_KIOSKS

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)


class FusionSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]] = {
        CONF_KIOSKS: [],
    }

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        return await self.async_step_choose_type(user_input)

    async def async_step_choose_type(self, user_input: Optional[Dict[str, Any]] = None):
        _LOGGER.debug(f'async_step_choose_type: {user_input}')
        errors: Dict[str, str] = {}

        if user_input is not None:
            if user_input['type'] == 'kiosk':
                return await self.async_step_kiosk()
            elif user_input['type'] == 'openapi':
                return await self.async_step_openapi()
            else:
                errors['base'] = 'invalid_type'

        type_listing = {
            'kiosk': 'Kiosk',
            'openapi': 'OpenAPI',
        }

        return self.async_show_form(
            step_id="choose_type",
            data_schema=vol.Schema({
                vol.Required("type", default='kiosk'): vol.In(type_listing)
            }),
            errors=errors,
        )

    async def async_step_kiosk(self, user_input: Optional[Dict[str, Any]] = None):
        _LOGGER.debug(f'async_step_kiosk: {user_input}')
        errors: Dict[str, str] = {}

        if user_input is not None:
            self.data[CONF_KIOSKS].append({
                CONF_NAME: user_input[CONF_NAME],
                CONF_URL: user_input[CONF_URL],
            })

            if user_input.get("add_another", False):
                return await self.async_step_kiosk()

            return self.async_create_entry(
                title="Fusion Solar",
                data=self.data,
            )

        return self.async_show_form(
            step_id="kiosk",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_URL): str,
                vol.Optional("add_another"): bool,
            }),
            errors=errors,
        )

    async def async_step_openapi(self, user_input: Optional[Dict[str, Any]] = None):
        _LOGGER.debug(f'async_step_openapi: {user_input}')
        errors: Dict[str, str] = {}

        errors['base'] = 'not_implemented'

        return self.async_show_form(
            step_id="openapi",
            data_schema=vol.Schema({
            }),
            errors=errors,
        )
