from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL, CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN, CONF_KIOSKS, CONF_TYPE, CONF_TYPE_KIOSK, CONF_TYPE_OPENAPI, CONF_OPENAPI_CREDENTIALS
from .fusion_solar.openapi.openapi_api import FusionSolarOpenApi, FusionSolarOpenApiError

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)


class FusionSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]] = {
        CONF_KIOSKS: [],
        CONF_OPENAPI_CREDENTIALS: {}
    }

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        return await self.async_step_choose_type(user_input)

    async def async_step_choose_type(self, user_input: Optional[Dict[str, Any]] = None):
        _LOGGER.debug(f'async_step_choose_type: {user_input}')
        errors: Dict[str, str] = {}

        if user_input is not None:
            if user_input[CONF_TYPE] == CONF_TYPE_KIOSK:
                return await self.async_step_kiosk()
            elif user_input[CONF_TYPE] == CONF_TYPE_OPENAPI:
                return await self.async_step_openapi()
            else:
                errors['base'] = 'invalid_type'

        type_listing = {
            CONF_TYPE_KIOSK: 'Kiosk',
            CONF_TYPE_OPENAPI: 'OpenAPI',
        }

        return self.async_show_form(
            step_id="choose_type",
            data_schema=vol.Schema({
                vol.Required(CONF_TYPE, default=CONF_TYPE_KIOSK): vol.In(type_listing)
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

        if user_input is not None:
            try:
                api = FusionSolarOpenApi(
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD]
                )
                response = await self.hass.async_add_executor_job(api.login)

                self.data[CONF_OPENAPI_CREDENTIALS] = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }

                return self.async_create_entry(
                    title="Fusion Solar",
                    data=self.data,
                )

            except FusionSolarOpenApiError as error:
                _LOGGER.debug(error)
                errors["base"] = "invalid_credentials"

        return self.async_show_form(
            step_id="openapi",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default='https://eu5.fusionsolar.huawei.com'): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
