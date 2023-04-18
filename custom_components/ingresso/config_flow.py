import logging
import voluptuous as vol
from homeassistant import config_entries, core
from .const import CONF_CITY_ID, CONF_CITY_NAME, CONF_PARTNERSHIP
from .const import DOMAIN


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CITY_ID): str,
        vol.Required(CONF_CITY_NAME): str,
        vol.Required(CONF_PARTNERSHIP): str,
    }
)


class IngressoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ingresso.com config flow."""

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"{user_input[CONF_PARTNERSHIP]} - {user_input[CONF_CITY_NAME]}",
                data={
                    CONF_CITY_ID: user_input[CONF_CITY_ID],
                    CONF_CITY_NAME: user_input[CONF_CITY_NAME],
                    CONF_PARTNERSHIP: user_input[CONF_PARTNERSHIP],
                },
            )

        errors["base"] = "invalid_input"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
